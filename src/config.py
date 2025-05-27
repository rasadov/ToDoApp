import os
import dotenv

dotenv.load_dotenv()


class Settings:
    # General
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    REFRESH_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7))

    # Database
    DB_HOST = os.getenv("POSTGRES_HOST")
    DB_PORT = os.getenv("POSTGRES_PORT", 5432)
    DB_NAME = os.getenv("POSTGRES_DB")
    DB_USER = os.getenv("POSTGRES_USER")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
