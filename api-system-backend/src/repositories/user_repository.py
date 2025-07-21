from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from src.repositories.base import BaseRepository
from src.models.user import User, UserCreate, UserUpdate
from bson import ObjectId

class UserRepository(BaseRepository):
    """User repository implementing specific user operations"""
    
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection)
    
    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        document = await self.collection.find_one({"email": email, "is_active": True})
        if document:
            document["_id"] = str(document["_id"])
        return document
    
    async def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        document = await self.collection.find_one({"username": username, "is_active": True})
        if document:
            document["_id"] = str(document["_id"])
        return document
    
    async def email_exists(self, email: str, exclude_id: Optional[str] = None) -> bool:
        """Check if email already exists"""
        query = {"email": email, "is_active": True}
        if exclude_id:
            query["_id"] = {"$ne": ObjectId(exclude_id)}
        return await self.exists(query)
    
    async def username_exists(self, username: str, exclude_id: Optional[str] = None) -> bool:
        """Check if username already exists"""
        query = {"username": username, "is_active": True}
        if exclude_id:
            query["_id"] = {"$ne": ObjectId(exclude_id)}
        return await self.exists(query)
    
    async def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        from datetime import datetime
        return await self.update(user_id, {"last_login": datetime.utcnow()})
    
    async def increment_failed_attempts(self, user_id: str) -> bool:
        """Increment failed login attempts"""
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$inc": {"failed_login_attempts": 1}}
        )
        return result.modified_count > 0
    
    async def reset_failed_attempts(self, user_id: str) -> bool:
        """Reset failed login attempts"""
        return await self.update(user_id, {"failed_login_attempts": 0})
    
    async def lock_user(self, user_id: str) -> bool:
        """Lock user account"""
        return await self.update(user_id, {"is_locked": True})
    
    async def unlock_user(self, user_id: str) -> bool:
        """Unlock user account"""
        return await self.update(user_id, {"is_locked": False, "failed_login_attempts": 0})