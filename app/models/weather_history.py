from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
import uuid

class WeatherHistory(Base):
    __tablename__ = "weather_history"
    id = Column(String, primary_key=True, index=True)
    day = Column(Integer, index=True)
    date = Column(DateTime)
    city = Column(String, index=True)
    condition = Column(String)
    condition_icon = Column(String)
    temperature = Column(Float)
    wind_speed = Column(Float)
    humidity = Column(Float)