import logging
from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from sqlalchemy.sql import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import init_db, get_session
from app.models.report import FinancialReport

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("TITAN System: INITIATING...")
    try:
        await init_db()
        logger.info("System Ready.")
    except Exception as e:
        logger.error(f"Critical Startup Error: {e}")
    yield
    logger.info("TITAN System: SHUTTING DOWN...")

app = FastAPI(
    title="TITAN Platform",
    description="Financial Intelligence Multi-Agent System",
    version="0.1.0",
    lifespan=lifespan
)

@app.get("/health", tags=["System"])
async def health_check(session: AsyncSession = Depends(get_session)):
    """
    Endpoint to verify that the system works
    """
    try:
        result = await session.execute(text("SELECT 1"))
        return {
            "status": "active",
            "system": "TITAN",
            "database": "connected",
            "environment": "development",
            "db_check": result.scalar()
        }
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "degraded",
            "database": "unreachable",
            "detail": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)