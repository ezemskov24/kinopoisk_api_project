from fastapi import HTTPException
import aiohttp
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import KINOPOISK_API_KEY
from movie.models import FavoriteMovie

HEADERS = {
    "X-API-KEY": KINOPOISK_API_KEY,
    "Content-Type": "application/json",
}


async def search_movies_by_keyword(keyword: str, user):
    """
    Поиск фильмов по ключевому слову.

    Args:
        keyword (str): Ключевое слово для поиска фильмов.
        user (User): Пользователь, выполняющий поиск.

    Raises:
        HTTPException: Если запрос к API завершился с ошибкой.

    Returns:
        dict: Ответ от API с результатами поиска фильмов.
    """
    url = "https://kinopoiskapiunofficial.tech/api/v2.1/films/search-by-keyword"
    params = {"keyword": keyword}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS, params=params) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=response.status, detail="Ошибка при поиске фильмов"
                )
            return await response.json()


async def search_movie_by_id(kinopoisk_id: int, user):
    """
    Получение информации о фильме по его id.

    Args:
        kinopoisk_id (int): Идентификатор фильма для запроса.
        user (User): Пользователь, запрашивающий информацию о фильме.

    Raises:
        HTTPException: Если запрос к API завершился с ошибкой.

    Returns:
        dict: Ответ от API с информацией о фильме.
    """
    url = f"https://kinopoiskapiunofficial.tech/api/v2.2/films/{kinopoisk_id}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=response.status, detail="Ошибка при поиске фильма"
                )
            return await response.json()


async def get_existing_favorite(user_id: int, movie_id: int, db: AsyncSession):
    """
    Проверка существования избранного фильма у пользователя.

    Args:
        user_id (int): Идентификатор пользователя.
        movie_id (int): Идентификатор фильма для проверки.
        db (AsyncSession): Асинхронная сессия базы данных.

    Returns:
        FavoriteMovie: Объект избранного фильма, если найден, иначе None.
    """
    existing_favorite = await db.execute(
        select(FavoriteMovie).where(
            FavoriteMovie.user_id == user_id, FavoriteMovie.movie_id == movie_id
        )
    )
    return existing_favorite.scalar_one_or_none()
