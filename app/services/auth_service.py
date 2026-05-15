from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import (
    get_password_hash,
    verify_password,
    validate_password_strength,
)
from app.core.exceptions import DuplicateError, NotFoundError


class AuthService:
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        is_valid, msg = validate_password_strength(user_data.password)
        if not is_valid:
            raise ValueError(msg)

        result = await db.execute(
            select(User).where(User.username == user_data.username)
        )
        if result.scalar_one_or_none():
            raise DuplicateError("Username")

        result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise DuplicateError("Email")

        hashed_pwd = get_password_hash(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_pwd,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, password: str) -> User | None:
        result = await db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            return None

        return user

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_user(db: AsyncSession, user: User, update_data: UserUpdate) -> User:
        if update_data.username is not None:
            result = await db.execute(
                select(User).where(User.username == update_data.username, User.id != user.id)
            )
            if result.scalar_one_or_none():
                raise DuplicateError("Username")
            user.username = update_data.username

        if update_data.email is not None:
            result = await db.execute(
                select(User).where(User.email == update_data.email, User.id != user.id)
            )
            if result.scalar_one_or_none():
                raise DuplicateError("Email")
            user.email = update_data.email

        await db.commit()
        await db.refresh(user)
        return user
