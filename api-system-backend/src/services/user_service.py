from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from src.services.base import BaseService
from src.repositories.user_repository import UserRepository
from src.models.user import UserCreate, UserUpdate, UserLogin
from src.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from datetime import timedelta
from src.core.config import settings

class UserService(BaseService):
    """User service implementing business logic"""
    
    def __init__(self, repository: UserRepository):
        super().__init__(repository)
        self.repository = repository
    
    async def create(self, user_data: UserCreate) -> str:
        """Create new user"""
        # Check if email already exists
        if await self.repository.email_exists(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username already exists
        if await self.repository.username_exists(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Prepare user document
        user_dict = user_data.model_dump()
        user_dict["hashed_password"] = hashed_password
        del user_dict["password"]
        
        return await self.repository.create(user_dict)
    
    async def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        return await self.repository.get_by_id(user_id)
    
    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        return await self.repository.get_by_email(email)
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all users"""
        return await self.repository.get_all(skip=skip, limit=limit, filters={"is_active": True})
    
    async def update(self, user_id: str, user_data: UserUpdate) -> bool:
        """Update user"""
        # Check if user exists
        existing_user = await self.repository.get_by_id(user_id)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        update_dict = user_data.model_dump(exclude_unset=True)
        
        # Check email uniqueness if email is being updated
        if "email" in update_dict:
            if await self.repository.email_exists(update_dict["email"], user_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Check username uniqueness if username is being updated
        # if "username" in update_dict:
        #     if await self.repository.username_exists(update_dict["username"], user_id):
        #         raise HTTPException(
        #             status_code=status.HTTP_400_BAD_REQUEST,
        #             detail="Username already taken"
        #         )
        
        return await self.repository.update(user_id, update_dict)
    
    async def deactivate(self, user_id: str) -> bool:
        """Deactivate user (soft delete)"""
        return await self.repository.deactivate(user_id)
    
    async def activate(self, user_id: str) -> bool:
        """Activate user (soft delete)"""
        return await self.repository.activate(user_id)
    
    async def authenticate(self, login_data: UserLogin) -> Optional[Dict[str, Any]]:
        """Authenticate user and return token"""
        user = await self.repository.get_by_email(login_data.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        if user.get("is_locked", False):
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account is locked"
            )
        
        if not verify_password(login_data.password, user["hashed_password"]):
            # Increment failed attempts
            await self.repository.increment_failed_attempts(user["_id"])
            
            # Lock account after 5 failed attempts
            if user.get("failed_login_attempts", 0) >= 4:
                await self.repository.lock_user(user["_id"])
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Reset failed attempts and update last login
        await self.repository.reset_failed_attempts(user["_id"])
        await self.repository.update_last_login(user["_id"])
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=user["_id"], expires_delta=access_token_expires
        )

        refresh_token = create_refresh_token(subject=user["_id"])

     
        # Remove sensitive data
        user_response = user.copy()
        del user_response["hashed_password"]
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": user_response
        }
    
    async def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Change user password"""
        user = await self.repository.get_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not verify_password(current_password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        hashed_password = get_password_hash(new_password)
        return await self.repository.update(user_id, {"hashed_password": hashed_password})