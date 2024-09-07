from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.models.base import Base

class SubscribedEmails(Base):
    __tablename__ = "subscribed_emails"
    id = Column(String, primary_key=True, index=True)
    email = Column(String, index=True)
    location = Column(String)
    # status = Column(Boolean, default=True) # True = subscribed, False = unsubscribed

