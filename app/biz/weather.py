from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import sqlalchemy
from fastapi import FastAPI, Request
from app import config
from app.models.weather_history import WeatherHistory
from sqlalchemy import select, func
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
            .order_by(WeatherHistory.day.asc())
        )
        result = await db_session.execute(stmt)
        result = result.scalars().all()
        if result:
            if result[0].date.date() == datetime.now().date():
                return result
            else:
                # update the data
                logger.info([result[0].date.date(), datetime.now().date()])
                logger.info("Outdated data, fetching new data from external API")
                response = await fetchData(city, global_settings.days)

                if response is None:
                    return "No data found"
                
                data = response
                i = 0
                for item in data["forecast"]["forecastday"]:
                    result[i].date = datetime.strptime(item["date"], "%Y-%m-%d")
                    result[i].temperature = item["day"]["avgtemp_c"]
                    result[i].wind_speed = item["day"]["maxwind_kph"]
                    result[i].humidity = item["day"]["avghumidity"]
                    result[i].condition = item["day"]["condition"]["text"]
                    result[i].condition_icon = item["day"]["condition"]["icon"]
                    i += 1
                await db_session.commit()
                return result
        else:
            logger.info("Fetching weather history from external API")
            response = await fetchData(city, global_settings.days)
            if response is None:
                return "No data found"
            data = response
            i = 0
            returnValue = []
            for item in data["forecast"]["forecastday"]:
                day = WeatherHistory(
                    id=str(uuid.uuid4()),
                    day=i,
                    city=response["location"]["name"],
                    date=datetime.strptime(item["date"], "%Y-%m-%d"),
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
    logger.info(f"Client host: {client_host}")
    try:
        stmt = (
            select(WeatherHistory)
            .where(WeatherHistory.city == client_host)
            .order_by(WeatherHistory.day.asc())
        )
        result = await db_session.execute(stmt)
        result = result.scalars().all()
        if result:
            if result[0].date.date() == datetime.now().date():
                return result
            else:
                # update the data
                logger.info("Outdated data, fetching current location weather from external API")
                response = await fetchData(client_host, global_settings.days)

                if response is None:
                    return "No data found"
                
                data = response
                i = 0
                for item in data["forecast"]["forecastday"]:
                    result[i].date = datetime.strptime(item["date"], "%Y-%m-%d")
                    result[i].temperature = item["day"]["avgtemp_c"]
                    result[i].wind_speed = item["day"]["maxwind_kph"]
                    result[i].humidity = item["day"]["avghumidity"]
                    result[i].condition = item["day"]["condition"]["text"]
                    result[i].condition_icon = item["day"]["condition"]["icon"]
                    i += 1
                await db_session.commit()
                return result
        else:
            logger.info("Fetching current location weather from external API")
            response = await fetchData(client_host, global_settings.days)
            if response is None:
                return "No data found"
            data = response
            i = 0
            returnValue = []
            for item in data["forecast"]["forecastday"]:
                day = WeatherHistory(
                    id=str(uuid.uuid4()),
                    day=i,
                    date=datetime.strptime(item["date"], "%Y-%m-%d"),
                    city=response["location"]["name"],
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
    

    
