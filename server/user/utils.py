from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from user.models import User
from config import SECRET_KEY, ALGORITHM
from database.db_connection import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Хеширование пароля с использованием bcrypt.

    Args:
        password (str): Пароль для хеширования.

    Returns:
        str: Хешированный пароль.
    """
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    """
    Проверка соответствия введенного пароля и хешированного пароля.

    Args:
        plain_password (str): Введенный пользователем пароль.
        hashed_password (str): Хешированный пароль.

    Returns:
        bool: True, если пароли совпадают, иначе False.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Создание JWT токена.

    Args:
        data (dict): Данные для кодирования в токене (например, email пользователя).
        expires_delta (timedelta | None): Время истечения токена. Если не указано, токен будет действителен 15 минут.

    Returns:
        str: Сгенерированный JWT токен.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    """
    Извлечение текущего пользователя из JWT токена.

    Args:
        token (str): JWT токен, предоставленный пользователем.
        db (AsyncSession): Асинхронная сессия базы данных.

    Raises:
        HTTPException: Если не удалось проверить учетные данные или пользователь не найден.

    Returns:
        User: Объект пользователя, извлеченный из базы данных.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
        if user_email is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception

    user = await db.execute(select(User).where(User.email == user_email))
    user = user.scalar_one_or_none()
    if user is None:
        raise credentials_exception

    return user
