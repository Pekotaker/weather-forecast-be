from datetime import datetime
from typing import Any
import random
import uuid
from app import config
import sqlalchemy
import requests

from sqlalchemy import text
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.weather_history import WeatherHistory
from app.models.subscribed_emails import SubscribedEmails
from app.utils.fetchData import fetchData
from datetime import datetime, timedelta

import logging

logger = logging.getLogger("full_info")
global_settings = config.get_settings()

async def add_sample_data(db_session: AsyncSession):   
    """
    Reset the table, then fetch the data from http://api.weatherapi.com/v1 
    and insert it into the WeatherHistory table.
    """
    try:
        # Delete from WeatherHistory
        stmt = (
            WeatherHistory.__table__.delete()
        )
        await db_session.execute(stmt)

        # Fetch data from external API
        
        city = "Ho Chi Minh City"
        response = await fetchData(city, global_settings.days)
        if response is None:
            return "No data found"

        # Insert sample data
        data = response
        i = 0
        for item in data["forecast"]["forecastday"]:
            day = WeatherHistory(
                id=str(uuid.uuid4()),
                day=i,
                date=datetime.strptime(item["date"], "%Y-%m-%d"),
                city=city,
                temperature=item["day"]["avgtemp_c"],
                wind_speed=item["day"]["maxwind_kph"],
                humidity=item["day"]["avghumidity"],
                condition=item["day"]["condition"]["text"],
                condition_icon=item["day"]["condition"]["icon"]
            )
            db_session.add(day)
            i += 1
        await db_session.commit()
    except Exception as e:
        logger.error(f"Error adding sample data: {e}")
        raise e
    

# async def init_metadata(db_session: AsyncSession):
#     """ Drop all tables """

#     try:
#         query1 = text("DROP TABLE IF EXISTS weather_history;")
#         query2 = text("DROP TABLE IF EXISTS subscribed_emails;")
#         await db_session.execute(query1)
#         await db_session.execute(query2)
#         await db_session.commit()
#     except Exception as e:
#         logger.error(f"Error initializing metadata: {e}")
#         raise e
    
async def init_metadata(db_session: AsyncSession):
    " Check if the table exists, if not, create it and add sample data "

    async with db_session.begin():
        conn = await db_session.connection()
        if conn:
            checkWeatherTable = await conn.run_sync(lambda sync_conn: sqlalchemy.inspect(sync_conn).has_table(WeatherHistory.__tablename__))
            if not checkWeatherTable:
                logger.info("Creating table WeatherHistory")
                await conn.run_sync(WeatherHistory.metadata.create_all)
                await add_sample_data(db_session)
            else:
                logger.info("Table WeatherHistory already exists")

        conn = await db_session.connection()  
        if conn:
            checkEmailTable = await conn.run_sync(lambda sync_conn: sqlalchemy.inspect(sync_conn).has_table(SubscribedEmails.__tablename__))
            if not checkEmailTable:
                logger.info("Creating table SubscribedEmails")
                await conn.run_sync(SubscribedEmails.metadata.create_all)
            else:
                logger.info("Table SubscribedEmails already exists")




    