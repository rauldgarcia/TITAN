from psycopg_pool import AsyncConnectionPool
from app.core.config import settings

pool = None


async def open_pool():
    global pool
    pool = AsyncConnectionPool(
        conninfo=settings.LANGGRAPH_DB_URL, max_size=20, kwargs={"autocommit": True}
    )
    await pool.open()


async def close_pool():
    global pool
    if pool:
        await pool.close()


def get_pool():
    return pool
