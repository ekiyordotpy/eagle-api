from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.hashing import hash_password
from app.exceptions import ConflictError, NotFoundError
from app.models.user import User
from app.schemas.user import CreateUserRequest, UpdateUserRequest


async def create_user(db: AsyncSession, body: CreateUserRequest) -> User:
    result = await db.execute(select(User).where(User.email == body.email))
    if result.scalar_one_or_none() is not None:
        raise ConflictError("A user with this email already exists")

    user = User(
        name=body.name,
        email=body.email,
        phone_number=body.phoneNumber,
        password_hash=hash_password(body.password),
        address_line1=body.address.line1,
        address_line2=body.address.line2,
        address_line3=body.address.line3,
        address_town=body.address.town,
        address_county=body.address.county,
        address_postcode=body.address.postcode,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user(db: AsyncSession, user_id: str) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise NotFoundError("User not found")
    return user


async def update_user(db: AsyncSession, user: User, body: UpdateUserRequest) -> User:
    if body.name is not None:
        user.name = body.name
    if body.email is not None:
        result = await db.execute(select(User).where(User.email == body.email))
        existing = result.scalar_one_or_none()
        if existing is not None and existing.id != user.id:
            raise ConflictError("A user with this email already exists")
        user.email = body.email
    if body.phoneNumber is not None:
        user.phone_number = body.phoneNumber
    if body.address is not None:
        user.address_line1 = body.address.line1
        user.address_line2 = body.address.line2
        user.address_line3 = body.address.line3
        user.address_town = body.address.town
        user.address_county = body.address.county
        user.address_postcode = body.address.postcode

    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user: User) -> None:
    await db.refresh(user, ["accounts"])
    if user.accounts:
        raise ConflictError("Cannot delete a user with existing accounts")
    await db.delete(user)
    await db.commit()
