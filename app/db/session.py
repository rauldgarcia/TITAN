import logging
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from sqlmodel import SQLModel
from app.core.config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
async_session_factory = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def create_database_if_not_exists():
    """
    Connects to the default 'postgres' database to check if 'titan_db' exists.
    If not, it creates the database.
    """
    logger.info("Checking database existence...")
    maintenance_engine = create_async_engine(
        settings.MAINTENANCE_DATABASE_URL, isolation_level="AUTOCOMMIT"
    )

    try:
        async with maintenance_engine.connect() as conn:
            result = await conn.execute(
                text(
                    f"SELECT 1 FROM pg_database WHERE datname='{settings.POSTGRES_DB}'"
                )
            )
            exists = result.scalar()

            if not exists:
                logger.warning(
                    f"Database '{settings.POSTGRES_DB}' does not exist. Creating it now..."
                )
                await conn.execute(text(f"CREATE DATABASE {settings.POSTGRES_DB}"))
                logger.info(f"Database '{settings.POSTGRES_DB}' already exists.")

    except Exception as e:
        logger.error(f"Failed to check/create database: {e}")
        raise e
    finally:
        await maintenance_engine.dispose()


async def init_db():
    """
    Initializes the database:
    1. Ensures the DB exists (using maintenance connection).
    2. Installs extensions (pgvector).
    3. Creates tables.
    Includes retry logic for Docker startup race conditions.
    """
    retries = 5
    wait_seconds = 2

    for attempt in range(retries):
        try:
            await create_database_if_not_exists()

            async with engine.begin() as conn:
                logger.info("Activating 'vector' extension...")
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                logger.info("Creating tables...")
                await conn.run_sync(SQLModel.metadata.create_all)

            logger.info("Database initialized successfully.")
            return

        except Exception as e:
            logger.warning(
                f"Database not ready yet (Attemp {attempt + 1}/{retries}). Detail: {e}"
            )
            if attempt < retries - 1:
                logger.info(f"Waiting {wait_seconds} seconds before retrying...")
                await asyncio.sleep(wait_seconds)
            else:
                logger.critical(
                    "Could not connect to database after multiple attempts."
                )
                raise e


async def get_session() -> AsyncSession:
    async with async_session_factory() as session:
        yield session
