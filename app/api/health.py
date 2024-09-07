import logging

from fastapi import APIRouter, status, Request, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import func, select, or_, and_
from app.databases.postgresql import get_db
from sqlalchemy.exc import OperationalError

from app.biz.meta import init_metadata

logger = logging.getLogger("full_info")
router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/checkDBConnection")
async def db_connection_check(db_session: AsyncSession = Depends(get_db)):
    try:
        # Execute a query to check for the existence of any tables in the current schema
        query = text(
            """
            SELECT *
                FROM information_schema.tables
                WHERE table_schema = current_schema()
            """
        )
        result = await db_session.execute(query)
        result = result.scalar()
        return f"Connected with database {result}"
    except OperationalError as e:
        # Handle the database connection error here
        logger.error(f"Database connection error: {e}")
        # You can log the error or raise a custom exception
        raise CustomDatabaseError("Error checking database connection")


@router.get("/resetDB")
async def reset_db(db_session: AsyncSession = Depends(get_db)):
    try:
        # Reset the database
        query = text(
            """
            DROP TABLE IF EXISTS weather_history;
            """
        )

        await db_session.execute(query)
        await db_session.commit()
        await init_metadata(db_session)

        return {"message": "Database reset successfully"}
    except OperationalError as e:
        # Handle the database connection error here
        logger.error(f"Database reset error: {e}")
        # You can log the error or raise a custom exception
        raise CustomDatabaseError("Error resetting database")

class CustomDatabaseError(Exception):
    pass


