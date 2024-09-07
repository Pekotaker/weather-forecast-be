import os
from functools import lru_cache

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):

    days: int = 4
    url: str = "http://api.weatherapi.com/v1/forecast.json"

    sql_host: str = os.getenv("SQL_HOST")
    sql_db: str = os.getenv("SQL_DB")
    sql_user: str = os.getenv("SQL_USER")
    sql_pass: str = os.getenv("SQL_PASS")
    sql_port: int = int(os.getenv("SQL_PORT", 5432))
    database_url: PostgresDsn = (
        f"postgresql+asyncpg://{sql_user}:{sql_pass}@{sql_host}/{sql_db}"
    )
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM")
    jwt_expire: int = os.getenv("JWT_EXPIRE")
    api_key: str = os.getenv("API_KEY")
    
    #smtp config

    mail_username: str = os.getenv("APP_EMAIL", "")
    mail_password: str = os.getenv("APP_EMAIL_PASSWORD", "")
    mail_port: int = os.getenv("APP_EMAIL_PORT", 587)
    mail_server: str = os.getenv("APP_EMAIL_SERVER", "smtp.gmail.com")




@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
