from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.exceptions import ForbiddenError
from app.schemas.user import CreateUserRequest, UpdateUserRequest, UserResponse
from app.services import user_service

router = APIRouter(prefix="/v1/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(body: CreateUserRequest, db: AsyncSession = Depends(get_db)):
    user = await user_service.create_user(db, body)
    return UserResponse.from_orm(user)


@router.get("/{userId}", response_model=UserResponse)
async def get_user(
    userId: str,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user),
):
    if userId != current_user_id:
        raise ForbiddenError("You do not have permission to access this user")
    user = await user_service.get_user(db, userId)
    return UserResponse.from_orm(user)


@router.patch("/{userId}", response_model=UserResponse)
async def update_user(
    userId: str,
    body: UpdateUserRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user),
):
    if userId != current_user_id:
        raise ForbiddenError("You do not have permission to update this user")
    user = await user_service.get_user(db, userId)
    updated = await user_service.update_user(db, user, body)
    return UserResponse.from_orm(updated)


@router.delete("/{userId}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    userId: str,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user),
):
    if userId != current_user_id:
        raise ForbiddenError("You do not have permission to delete this user")
    user = await user_service.get_user(db, userId)
    await user_service.delete_user(db, user)
