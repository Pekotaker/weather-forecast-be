from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker

from app import config
from app.utils.logging import AppLogger
import json
from functools import partial
global_settings = config.get_settings()
logger = AppLogger.__call__().get_logger()

engine = create_async_engine(
    global_settings.database_url.unicode_string(),
    future=True,
    echo=False,
    pool_size=65,
    max_overflow=10,
    pool_pre_ping=True,
   json_serializer=partial(json.dumps, ensure_ascii=False)
)

# expire_on_commit=False will prevent attributes from being expired
# after commit.
AsyncSessionFactory = async_sessionmaker(
    engine, autoflush=False, expire_on_commit=False
)


# Dependency
async def get_db() -> AsyncGenerator:
    async with AsyncSessionFactory() as session:
        logger.debug(f"ASYNC Pool: {engine.pool.status()}")
        yield session
