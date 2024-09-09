from fastapi import APIRouter, Depends, status, Request, HTTPException,Query, FastAPI

from sqlalchemy.ext.asyncio import AsyncSession
from app.databases.postgresql import get_db
import app.biz.weather as weatherBiz
import logging

logger = logging.getLogger("full_info")

router = APIRouter(prefix="/weather", tags=["Weather"])

@router.get("/getWeatherHistory")
async def get_weather_history(
    city: str, 
    request: Request,
    db_session: AsyncSession = Depends(get_db)
):
    """
    Get the weather forecast for the given city.
    """
    result = await weatherBiz.get_weather_history(city, db_session, request)
    return result

@router.get("/getCurrentLocationWeather")
async def get_current_location_weather(
    request: Request,
    db_session: AsyncSession = Depends(get_db)
):
    """
    Get the current weather for the given city.
    """
    result = await weatherBiz.get_current_location_weather(db_session, request)
    return result