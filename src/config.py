import os


class Settings:
    # General
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY")

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")
