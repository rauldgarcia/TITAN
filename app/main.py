from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("TITAN System: INITIATING...")
    yield
    print("TITAN System: SHUTTING DOWN...")

app = FastAPI(
    title="TITAN Platform",
    description="Financial Intelligence Multi-Agent System",
    version="0.1.0",
    lifespan=lifespan
)

@app.get("/health", tags=["System"])
async def health_check():
    """
    Endpoint to verify that the system works
    """
    return {
        "status": "active",
        "system": "TITAN",
        "environment": "development"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)