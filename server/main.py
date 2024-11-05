from contextlib import asynccontextmanager

from fastapi import FastAPI

from user.routers import user_router
from movie.routers import movie_router
from database.db_connection import engine, Base


@asynccontextmanager
async def lifespan(application: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app: FastAPI = FastAPI(lifespan=lifespan)

app.include_router(user_router)
app.include_router(movie_router)
