from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.db_connection import get_db
from movie.models import FavoriteMovie
from movie.utils import (
    search_movies_by_keyword,
    search_movie_by_id,
    get_existing_favorite,
)
from user.models import User
from user.utils import get_current_user

movie_router: APIRouter = APIRouter()


@movie_router.get("/movies/search")
async def get_movies_by_keyword(keyword: str, user: User = Depends(get_current_user)):
    """
    Поиск фильмов по ключевому слову.

    Args:
        keyword (str): Ключевое слово для поиска фильмов.
        user (User): Пользователь, выполняющий поиск. Получается через зависимость get_current_user.

    Returns:
        List[Movie]: Список фильмов, соответствующих ключевому слову.
    """
    return await search_movies_by_keyword(keyword, user)


@movie_router.get("/movies/{kinopoisk_id}")
async def get_movies_by_movie_id(movie_id: int, user: User = Depends(get_current_user)):
    """
    Получение информации о фильме по его ID.

    Args:
        movie_id (int): Идентификатор фильма (kinopoisk_id).
        user (User): Пользователь, запрашивающий информацию о фильме. Получается через зависимость get_current_user.

    Returns:
        Movie: Информация о фильме.
    """
    return await search_movie_by_id(movie_id, user)


@movie_router.post("/movies/favorites/{kinopoisk_id}")
async def add_movie_to_favorite(
    kinopoisk_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Добавление фильма в избранное.

    Args:
        kinopoisk_id (int): Идентификатор фильма, который нужно добавить в избранное.
        user (User): Пользователь, добавляющий фильм в избранное. Получается через зависимость get_current_user.
        db (AsyncSession): Асинхронная сессия базы данных.

    Raises:
        HTTPException: Если фильм уже находится в избранном.

    Returns:
        FavoriteMovie: Объект добавленного фильма в избранное.
    """
    existing_favorite = await get_existing_favorite(user.id, kinopoisk_id, db)

    if existing_favorite:
        raise HTTPException(status_code=400, detail="Movie is already in favorites.")

    new_favorite_movie = FavoriteMovie(user_id=user.id, movie_id=kinopoisk_id)
    db.add(new_favorite_movie)
    await db.commit()

    return new_favorite_movie


@movie_router.delete("/movies/favorites/{kinopoisk_id}")
async def delete_movie_from_favorite(
    kinopoisk_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Удаление фильма из избранного.

    Args:
        kinopoisk_id (int): Идентификатор фильма, который нужно удалить из избранного.
        user (User): Пользователь, удаляющий фильм из избранного. Получается через зависимость get_current_user.
        db (AsyncSession): Асинхронная сессия базы данных.

    Raises:
        HTTPException: Если фильм не найден в избранном.

    Returns:
        Dict: Сообщение об успешном удалении фильма из избранного.
    """
    existing_favorite = await get_existing_favorite(user.id, kinopoisk_id, db)

    if existing_favorite is None:
        raise HTTPException(status_code=400, detail="Movie is not in favorites.")

    await db.delete(existing_favorite)
    await db.commit()

    return {"detail": f"Movie {kinopoisk_id} removed from favorites."}


@movie_router.get("/movies/favorites/all")
async def get_favorites(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    Получение списка всех избранных фильмов пользователя.

    Args:
        user (User): Пользователь, запрашивающий избранные фильмы. Получается через зависимость get_current_user.
        db (AsyncSession): Асинхронная сессия базы данных.

    Returns:
        List[Movie]: Список всех избранных фильмов.
    """
    favorites_query = await db.execute(
        select(FavoriteMovie.movie_id).where(FavoriteMovie.user_id == user.id)
    )
    movie_ids = favorites_query.scalars().all()
    movies_data = []
    for movie_id in movie_ids:
        result = await search_movie_by_id(movie_id, user)
        movies_data.append(result)

    return movies_data
