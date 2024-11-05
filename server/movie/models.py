from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from database.db_connection import Base


class FavoriteMovie(Base):
    """
    Модель FavoriteMovie представляет собой таблицу для хранения
    избранных фильмов пользователей.

    Attributes:
        id (int): Уникальный идентификатор записи.
        user_id (int): Идентификатор пользователя, который добавил фильм в избранное.
        movie_id (int): Идентификатор избранного фильма.

    Relationships:
        user (User): Связь с моделью User, представляющая пользователя,
        который добавил фильм в избранное. Используется для обратной связи
        с пользователем через атрибут favorite_movies.
    """

    __tablename__ = "favorite_movie"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    movie_id = Column(Integer, nullable=False)

    user = relationship("User", back_populates="favorite_movies")
