from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database.db_connection import Base


class User(Base):
    """
    Модель User представляет собой таблицу для хранения информации о пользователях.

    Attributes:
        id (int): Уникальный id пользователя. Автоматически увеличивается при добавлении нового пользователя.
        username (str): Уникальное имя пользователя. Не может быть пустым.
        email (str): Уникальный адрес электронной почты пользователя. Не может быть пустым.
        hashed_password (str): Хэшированный пароль пользователя. Используется для аутентификации.

    Relationships:
        favorite_movies (List[FavoriteMovie]): Связь с моделью FavoriteMovie, представляющая
        избранные фильмы пользователя. Используется для связи с избранными фильмами.
    """
    __tablename__ = "user"

    id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String)

    favorite_movies = relationship("FavoriteMovie", back_populates="user")
