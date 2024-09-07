from fastapi import Depends
from app.databases.postgresql import get_db

from sqlalchemy.ext.asyncio import AsyncSession

from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import sqlalchemy
import uuid
from fastapi import FastAPI, Request
from sqlalchemy import select
from pydantic import EmailStr, BaseModel
from app import config
from app.models.subscribed_emails import SubscribedEmails
from app.utils.fetchData import fetchData
from app.utils.sendMails import send_email, EmailSchema
from app.biz.weather import get_weather_history
from datetime import datetime, timedelta
from starlette.responses import JSONResponse

logger = logging.getLogger("full_info")
global_settings = config.get_settings()

async def get_subscribers(db_session: AsyncSession):
    """
    Get all subscribers.
    """
    try:
        stmt = (
            select(SubscribedEmails)
        )
        result = await db_session.execute(stmt)
        result = result.scalars().all()
        return result
    except Exception as e:
        logger.error(f"Error getting subscribers: {e}")
        raise e

async def subscribe(email: EmailStr, db_session: AsyncSession, request, city = None):
    """
    Subscribe to weather updates for the given city.
    """
    try:
        stmt = (
            select(SubscribedEmails)
            .where(SubscribedEmails.email == email)
        )
        result = await db_session.execute(stmt)
        result = result.scalars().all()
        if result:
            return "Email already subscribed"
        else:
            if city == None:
                city = request.client.host

            _id = str(uuid.uuid4())
            stmt = SubscribedEmails(
                id=_id,
                email=email,
                location=city
            )
            db_session.add(stmt)
            await db_session.commit()

            # Send email
            message = """
            <html>
            <body>
            <h2>Thank you for subscribing to our weather updates!</h2>
            <p>You will receive daily weather updates for your subscribed location.</p>
            <p>To unsubscribe, click <a href="http://localhost:8000/subscription/unsubscribe/{}">here</a>.</p>
            <p>Regards,</p>
            </body>
            </html>
            """.format(_id)

            EMAILS = EmailSchema(
                email=[email],
            )
            await send_email(EMAILS, message)
            return "Subscribed"        

    except Exception as e:
        logger.error(f"Error subscribing: {e}")
        raise e
    

async def unsubscribe(id: str, db_session: AsyncSession):
    """
    Unsubscribe from weather updates for the given city.
    """
    try:
        stmt = (
            select(SubscribedEmails)
            .where(SubscribedEmails.id == id)
        )
        result = await db_session.execute(stmt)
        result = result.scalars().all()
        if result:
            stmt = (
                SubscribedEmails.__table__.delete()
                .where(SubscribedEmails.id == id)
            )
            await db_session.execute(stmt)
            await db_session.commit()

            # Send email
            message = """
            <html>
            <body>
            <h2>You have successfully unsubscribed from our weather updates!</h2>
            <p>You will no longer receive daily weather updates.</p>
            <p>Regards,</p>
            </body>
            </html>
            """

            EMAILS = EmailSchema(
                email=[result[0].email],
            )
            await send_email(EMAILS, message)
            return "Unsubscribed"
        else:
            return "Email not found"
    except Exception as e:
        logger.error(f"Error unsubscribing: {e}")
        raise e


async def send_mail_daily(db_session: AsyncSession):
    try:
        subscribers = await get_subscribers(db_session)
        if not subscribers:
            return "No subscribers found"
        for subscriber in subscribers:
            city = subscriber.location
            response = await get_weather_history(city, db_session)
            if response is None:
                response = await fetchData(city, global_settings.days)
            if response == "No data found":
                return "No data found"
            data = response
            date = datetime.now().strftime("%d-%m-%Y")
            message = f"""
            <html>
            <body>
            <h1>Weather Update</h1>
            <p>City: {city}</p>
            <p>Date: {date}</p>
            <p>Current Temperature: {data[0].temperature}°C</p>
            <p>Current Wind Speed: {data[0].wind_speed} km/h</p>
            <p>Current Humidity: {data[0].humidity}%</p>
            <p>Current Condition: {data[0].condition}</p>
            <img src="{data[0].condition_icon}" alt="Weather Icon">
            <h2>Forecast</h2>
            """
            for item in data[1:]:

                date = datetime.now() + timedelta(days=item.day)
                date = date.strftime("%d-%m-%Y")
                
                message += f"""
                <p>Day {item.day}</p>
                <p>Date: {date}</p>
                <p>Temperature: {item.temperature}°C</p>
                <p>Wind Speed: {item.wind_speed} km/h</p>
                <p>Humidity: {item.humidity}%</p>
                <p>Condition: {item.condition}</p>
                <img src="{item.condition_icon}" alt="Weather Icon">
                """
            message += "</body></html>"
            email = EmailSchema(email=[subscriber.email])
            await send_email(email, message)
        return "Email sent to all subscribers"
    except Exception as e:
        logger.error(f"Error sending daily email: {e}")
        return JSONResponse(content={"message": "Error sending daily email"}, status_code=400)