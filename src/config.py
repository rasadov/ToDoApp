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
    DATABASE_URL = os.getenv("DATABASE_URL")
