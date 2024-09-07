import requests
from app.config import settings
import logging

global_settings = settings
logger = logging.getLogger("full_info")

async def fetchData(city: str, days: int):
    """
    Fetch the weather data from http://api.weatherapi.com/v1.
    """
    try:
        key = global_settings.api_key
        url = f"{global_settings.url}?key={key}&q={city}&days={days}"
        response = requests.get(url)
        if response.status_code != 200:
            return None
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching weather data: {e}")
        raise e