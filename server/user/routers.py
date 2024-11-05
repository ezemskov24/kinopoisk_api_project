from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import ACCESS_TOKEN_EXPIRE_MINUTES
from .schemas import UserResponse, UserCreate, UserLogin, Token
from .models import User
from database.db_connection import get_db
from .utils import hash_password, verify_password, create_access_token, get_current_user

user_router: APIRouter = APIRouter()


@user_router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Регистрация нового пользователя.

    Args:
        user (UserCreate): Данные для регистрации нового пользователя.
        db (AsyncSession): Асинхронная сессия базы данных.

    Raises:
        HTTPException: Если email или имя пользователя уже зарегистрированы.

    Returns:
        UserResponse: Данные зарегистрированного пользователя.
    """
    user_by_email = await db.execute(select(User).where(User.email == user.email))
    exiting_user_by_email = user_by_email.scalar_one_or_none()
    if exiting_user_by_email:
        raise HTTPException(status_code=400, detail="Email is already registered")

    user_by_username = await db.execute(
        select(User).where(User.username == user.username)
    )
    existing_user_by_username = user_by_username.scalar_one_or_none()
    if existing_user_by_username:
        raise HTTPException(status_code=400, detail="Username is already registered")

    hashed_password = hash_password(user.password)
    new_user = User(
        username=user.username, email=user.email, hashed_password=hashed_password
    )

    db.add(new_user)
    await db.commit()

    return new_user


@user_router.post("/login", response_model=Token)
async def login_user(user: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Вход пользователя в систему.

    Args:
        user (UserLogin): Данные для входа пользователя.
        db (AsyncSession): Асинхронная сессия базы данных.

    Raises:
        HTTPException: Если email или пароль неверны.

    Returns:
        Token: Объект с токеном доступа и типом токена.
    """
    user_by_email = await db.execute(select(User).where(User.email == user.email))
    exiting_user_by_email = user_by_email.scalar_one_or_none()

    if exiting_user_by_email is None or not verify_password(
        user.password, exiting_user_by_email.hashed_password
    ):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": exiting_user_by_email.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@user_router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """
    Получение профиля текущего пользователя.

    Args:
        current_user (User): Текущий пользователь, извлеченный из токена.

    Returns:
        UserResponse: Данные профиля текущего пользователя.
    """
    return current_user
