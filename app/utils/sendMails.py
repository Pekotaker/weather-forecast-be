from fastapi import FastAPI
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
from starlette.requests import Request
from starlette.responses import JSONResponse
from pydantic import EmailStr, BaseModel
from typing import List
from app.config import settings
import logging


logger = logging.getLogger("full_info")
global_settings = settings


class EmailSchema(BaseModel):
   email: List[EmailStr]

conf = ConnectionConfig(
    MAIL_USERNAME=global_settings.mail_username,
    MAIL_PASSWORD=global_settings.mail_password,
    MAIL_PORT=global_settings.mail_port if global_settings.mail_port else 587,
    MAIL_SERVER=global_settings.mail_server if global_settings.mail_server else "smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    MAIL_FROM=global_settings.mail_username,

)

async def send_email(email: EmailSchema, message: str):
    try: 
        message = MessageSchema(
            subject="Weather Update",
            recipients=email.email,
            body=message,
            subtype="html"
        )

        fm = FastMail(conf)
        logger.info(f"Sending email to {email}")
        await fm.send_message(message)
        logger.info(f"Email sent to {email}")
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return JSONResponse(content={"message": "Error sending email"}, status_code=400)

    return JSONResponse(content={"message": "Email sent"}, status_code=200)