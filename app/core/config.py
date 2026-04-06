import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = os.getenv("APP_NAME", "MyApp")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    REFRESH_SECRET_KEY: str = os.getenv("REFRESH_SECRET_KEY", "")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    # Logging settings
    LOG_DIR: str = os.getenv("LOG_DIR", "./logs/")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_MAX_SIZE: int = int(os.getenv("LOG_MAX_SIZE", 10485760))  # 10MB default
    LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", 10))
    LOG_FORMAT: str = os.getenv(
        "LOG_FORMAT", 
        "%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(funcName)s() | %(message)s"
    )
    LOG_DATE_FORMAT: str = os.getenv("LOG_DATE_FORMAT", "%Y-%m-%d %H:%M:%S")
    
    DEBUG: bool = True

settings = Settings()