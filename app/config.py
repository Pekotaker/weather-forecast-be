import os
from functools import lru_cache

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):

    days: int = 14
    url: str = "http://api.weatherapi.com/v1/forecast.json"

    render_url: str = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8000")
    vercel_url: str = os.getenv("VERCEL_URL", "http://localhost:8000")
    url_in_used: str = render_url if render_url != "http://localhost:8000" else "https://" + vercel_url
    backend_url: str = url_in_used if "localhost" not in url_in_used else "http://localhost:8000"
    sql_host: str = os.getenv("SQL_HOST")
    sql_db: str = os.getenv("SQL_DB")
    sql_user: str = os.getenv("SQL_USER")
    sql_pass: str = os.getenv("SQL_PASS")
    sql_port: int = int(os.getenv("SQL_PORT", 5432))
    database_url: PostgresDsn = (
        f"postgresql+asyncpg://{sql_user}:{sql_pass}@{sql_host}/{sql_db}"
    )
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
