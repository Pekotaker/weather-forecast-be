from fastapi import APIRouter, Depends, status, Request, HTTPException,Query, FastAPI

from sqlalchemy.ext.asyncio import AsyncSession
from app.databases.postgresql import get_db
from pydantic import EmailStr
import app.biz.subscribe as SubscribeBiz
import logging

logger = logging.getLogger("full_info")

router = APIRouter(prefix="/subscription", tags=["Subscription"])

@router.post("/subscribe")
async def subscribe(
    email: EmailStr,
    request: Request,
    city: str = None, 
    db_session: AsyncSession = Depends(get_db)
):
    """
    Subscribe to weather updates for the given city.
    """
    result = await SubscribeBiz.subscribe(email, db_session, request, city)
    return result

@router.get("/unsubscribe/{id}")
async def unsubscribe(
    id: str,
    db_session: AsyncSession = Depends(get_db)
):
    """
    Unsubscribe from weather updates for the given city.
    """
    result = await SubscribeBiz.unsubscribe(id, db_session)
    return result

@router.get("/sendMailDaily")
async def send_mail_daily(
    request: Request,
    db_session: AsyncSession = Depends(get_db)
):
    """
    Send weather updates to all subscribers.
    """
    IP = request.client.host
    if IP != "127.0.0.1":
        return HTTPException(status_code=401, detail="Unauthorized access")
    result = await SubscribeBiz.send_mail_daily(db_session)
    return result
