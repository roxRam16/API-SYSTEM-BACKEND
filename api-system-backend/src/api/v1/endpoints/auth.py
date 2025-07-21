# src/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from src.models.user import UserLogin, UserCreate, Token, UserResponse
from src.repositories.user_repository import UserRepository
from src.services.user_service import UserService
from src.db.database import get_database
from src.api.deps import verify_token, security
from src.services.token_blacklist import add_token_to_blacklist
from src.utils.token_utils import create_access_token, create_refresh_token
from src.core.config import settings


router = APIRouter()

@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(
    login_data: UserLogin,
    db=Depends(get_database)
):
    user_repository = UserRepository(db.users)
    user_service = UserService(user_repository)

    result = await user_service.authenticate(login_data)

    return result  # 👈 YA ES EL OBJETO Token COMPLETO


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db=Depends(get_database)
):
    user_repository = UserRepository(db.users)
    user_service = UserService(user_repository)

    user_id = await user_service.create(user_data)

    if not user_id:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user")

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "User registered successfully"})


@router.post("/refresh", status_code=200)
async def refresh_token(refreshtoken: str):
    payload = verify_token(refreshtoken)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    user_id = payload.get("sub")
    new_access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)

    return {
        "access_token": new_access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    add_token_to_blacklist(token)
    return {"message": "Successfully logged out"}
