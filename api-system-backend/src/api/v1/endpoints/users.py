from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query

from src.models.user import UserCreate, UserUpdate, UserResponse
from src.repositories.user_repository import UserRepository
from src.services.user_service import UserService
from src.db.database import get_database
from src.api.deps import get_current_active_user, require_permissions
from src.utils.serializers import serialize_doc, serialize_docs
from fastapi.responses import JSONResponse

from bson import ObjectId
from datetime import datetime

router = APIRouter()

# Defaults para todos los usuarios
USER_DEFAULTS = {
    "is_verified": False,
    "last_login": None,
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
}


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db = Depends(get_database),
    current_user: dict = Depends(require_permissions(["admin"]))
):
    """
    Get all users (Admin only)
    """
    user_repository = UserRepository(db.users)

    user_service = UserService(user_repository)

    users = await user_service.get_all(skip=skip, limit=limit)
 
    for user in users:
        user.pop("hashed_password", None)

    return serialize_docs(users, UserResponse, defaults=USER_DEFAULTS)


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get current user profile
    """
    user_doc = current_user.copy()
    user_doc.pop("hashed_password", None)

    return serialize_doc(user_doc, UserResponse, defaults=USER_DEFAULTS)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db = Depends(get_database),
    current_user: dict = Depends(require_permissions(["admin"]))
):
    """
    Get user by ID (Admin only)
    """
    user_repository = UserRepository(db.users)
    user_service = UserService(user_repository)

    user = await user_service.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.pop("hashed_password", None)

    return serialize_doc(user, UserResponse, defaults=USER_DEFAULTS)


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db = Depends(get_database),
    current_user: dict = Depends(require_permissions(["admin"]))
):
    """
    Create new user (Admin only)
    """
    user_repository = UserRepository(db.users)
    user_service = UserService(user_repository)

    user_id = await user_service.create(user_data)
    user = await user_service.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

    user.pop("hashed_password", None)

    return serialize_doc(user, UserResponse, defaults=USER_DEFAULTS)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db = Depends(get_database),
    current_user: dict = Depends(require_permissions(["admin"]))
):
    """
    Update user (Admin only)
    """
    user_repository = UserRepository(db.users)
    user_service = UserService(user_repository)

    success = await user_service.update(user_id, user_data)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user = await user_service.get_by_id(user_id)
    user.pop("hashed_password", None)

    return serialize_doc(user, UserResponse, defaults=USER_DEFAULTS)


@router.put("/deactivate/{user_id}")
async def deactivate_user(
    user_id: str,
    db = Depends(get_database),
    current_user: dict = Depends(require_permissions(["admin"]))
):
    """
    Deactivate user (Admin only)
    """
    user_repository = UserRepository(db.users)
    user_service = UserService(user_repository)

    success = await user_service.deactivate(user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return JSONResponse(
            status_code=200,
            content={"message": "User deactivate successfully"}
        )


@router.put("/activate/{user_id}")
async def activate_user(
    user_id: str,
    db = Depends(get_database),
    current_user: dict = Depends(require_permissions(["admin"]))
):
    """
    Activate user (Admin only)
    """
    user_repository = UserRepository(db.users)
    user_service = UserService(user_repository)

    success = await user_service.activate(user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return JSONResponse(
            status_code=200,
            content={"message": "User activate successfully"}
    )


@router.put("/me/profile", response_model=UserResponse)
async def update_current_user_profile(
    user_data: UserUpdate,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Update current user profile
    """
    user_repository = UserRepository(db.users)
    user_service = UserService(user_repository)

    success = await user_service.update(current_user["_id"], user_data)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )

    user = await user_service.get_by_id(current_user["_id"])
    user.pop("hashed_password", None)

    return serialize_doc(user, UserResponse, defaults=USER_DEFAULTS)
