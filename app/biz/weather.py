from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import sqlalchemy
from fastapi import FastAPI, Request
from app import config
from app.models.weather_history import WeatherHistory
from sqlalchemy import select
from app.utils.fetchData import fetchData
import uuid

logger = logging.getLogger("full_info")
global_settings = config.get_settings()

async def get_weather_history(city: str, db_session: AsyncSession):
    """
    Get the weather history for a specific city and day.
    """
    try:
        stmt = (
            select(WeatherHistory)
            .where(WeatherHistory.city == city)
        )
        result = await db_session.execute(stmt)
        result = result.scalars().all()
        if result:
            return result
        else:
            logger.info("Fetching weather history from external API")
            response = await fetchData(city, global_settings.days)
            if response is None:
                return "No data found"
            data = response
            current = WeatherHistory(
                id=str(uuid.uuid4()), 
                day=0,
                city=city,
                temperature=data["current"]["temp_c"],
                wind_speed=data["current"]["wind_kph"],
                humidity=data["current"]["humidity"],
                condition=data["current"]["condition"]["text"],
                condition_icon=data["current"]["condition"]["icon"]
            )
            db_session.add(current)
            i = 1
            returnValue = [current]
            for item in data["forecast"]["forecastday"]:
                day = WeatherHistory(
                    id=str(uuid.uuid4()),
                    day=i,
                    city=city,
                    temperature=item["day"]["avgtemp_c"],
                    wind_speed=item["day"]["maxwind_kph"],
                    humidity=item["day"]["avghumidity"],
                    condition=item["day"]["condition"]["text"],
                    condition_icon=item["day"]["condition"]["icon"]
                )
                db_session.add(day)
                returnValue.append(day)
                i += 1
            await db_session.commit()
            return returnValue     
    except Exception as e:
        logger.error(f"Error getting weather history: {e}")
        raise e
    
async def get_current_location_weather(db_session: AsyncSession, request: Request):
    client_host = request.client.host
    try:
        stmt = (
            select(WeatherHistory)
            .where(WeatherHistory.city == client_host)
        )
        result = await db_session.execute(stmt)
        result = result.scalars().all()
        if result:
            return result
        else:
            logger.info("Fetching current location weather from external API")
            response = await fetchData(client_host, global_settings.days)
            if response is None:
                return "No data found"
            data = response
            current = WeatherHistory(
                id=str(uuid.uuid4()),
                day=0,
                city=client_host,
                temperature=data["current"]["temp_c"],
                wind_speed=data["current"]["wind_kph"],
                humidity=data["current"]["humidity"],
                condition=data["current"]["condition"]["text"],
                condition_icon=data["current"]["condition"]["icon"]
            )
            db_session.add(current)
            i = 1
            returnValue = [current]
            for item in data["forecast"]["forecastday"]:
                day = WeatherHistory(
                    id=str(uuid.uuid4()),
                    day=i,
                    city=client_host,
                    temperature=item["day"]["avgtemp_c"],
                    wind_speed=item["day"]["maxwind_kph"],
                    humidity=item["day"]["avghumidity"],
                    condition=item["day"]["condition"]["text"],
                    condition_icon=item["day"]["condition"]["icon"]
                )
                db_session.add(day)
                returnValue.append(day)
                i += 1
            await db_session.commit()
            return returnValue
    except Exception as e:
        logger.error(f"Error getting current location weather: {e}")
        raise e
    

    
