import logging
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class Settings(BaseSettings):
    PROYECT_NAME: str = "TITAN Platform"
    VERSION: str = "0.1.0"

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    TAVILY_API_KEY: str
    ENVIRONMENT: str = "local"

    INSTANCE_CONNECTION_NAME: Optional[str] = None

    @property
    def DATABASE_URL(self) -> str:
        """
        Dynamically builds the database URL.
        Uses Unix Sockets if INSTANCE_CONNECTION_NAME is present (Cloud Run),
        otherwise uses standard TCP (Local/Docker Dev).
        """
        if self.INSTANCE_CONNECTION_NAME:
            return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@/{self.POSTGRES_DB}?host=/cloudsql/{self.INSTANCE_CONNECTION_NAME}"

        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def TEST_DATABASE_URL(self) -> str:
        """URL pointing to a dedicated test database (e.g., titan_test_db)."""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/titan_test_db"

    @property
    def MAINTENANCE_DATABASE_URL(self) -> str:
        """System database URL used for administrative tasks."""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/postgres"

    @property
    def LANGGRAPH_DB_URL(self) -> str:
        """
        Database URL for LangGraph persistence (Psycopg 3).
        Same logic as DATABASE_URL but without the '+asyncpg' prefix.
        """
        if self.INSTANCE_CONNECTION_NAME:
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@/{self.POSTGRES_DB}?host=/cloudsql/{self.INSTANCE_CONNECTION_NAME}"

        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
