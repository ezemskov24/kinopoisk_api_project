import os

from dotenv import load_dotenv

load_dotenv()


KINOPOISK_API_KEY: str = os.environ.get('KINOPOISK_API_KEY')

SECRET_KEY: str = os.environ.get('SECRET_KEY')
ALGORITHM: str = os.environ.get('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES'))


def get_database_url():
    if os.environ.get("ENV") == "test":
        return os.environ.get("DATABASE_URL_TEST")
    else:
        return os.environ.get("DATABASE_URL")
