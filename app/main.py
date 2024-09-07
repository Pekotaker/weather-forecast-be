from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

import logging
from fastapi import FastAPI
from app.utils.logging import _configure_logging
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.weather import router as weather_router
from app.api.subscribe import router as subscribe_router

from asgi_correlation_id import CorrelationIdMiddleware

logger = logging.getLogger("root")

# Create the FastAPI app
app = FastAPI(title="Weather Forecast API", version="0.1")

from app.biz.meta import init_metadata
from app.databases.postgresql import AsyncSessionFactory
@app.on_event("startup")
async def startup_event():
    _configure_logging()
    async with AsyncSessionFactory() as db_session:
        await init_metadata(db_session)
    logger.info("Application started")

origins = [
    "http://localhost:3000",  # Replace with the origin of your client-side application
    "*",
]

app.add_middleware(
    CorrelationIdMiddleware,
    header_name="X-Request-ID",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

app.include_router(health_router)
app.include_router(weather_router)
app.include_router(subscribe_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Weather Forecast API!"}

# Sample endpoint to get weather
# @app.get("/weather")
# def get_weather(city: str):
#     # Fetch weather data from external API (placeholder)
#     return {"city": city, "temperature": "25°C"}

# Multithreading 
import threading
import time
import requests
import asyncio
from app.config import settings

global_settings = settings

async def print_time(threadName, delay):
    logger.info(f"Starting {threadName}")
    while True:
        time.sleep(delay)
        logger.info(f"{threadName}: {time.ctime(time.time())}")
        url = global_settings.backend_url + "/subscription/sendMailDaily"
        requests.get(url)

def between_callback(threadName, delay):
    asyncio.run(print_time(threadName, delay))

# Create two threads as follows
try:
    _thread = threading.Thread(target=between_callback, args=("Daily mail sending", 30))
    _thread.start()
except:
    print("Error: unable to start thread")



