import logging
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
    POSTGRES_PORT: str
    POSTGRES_DB: str
    TAVILY_API_KEY: str

    @property
    def DATABASE_URL(self) -> str:
        """URL for the main application database (titan_db)."""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def TEST_DATABASE_URL(self) -> str:
        """URL pointing to a dedicated test database (e.g., titan_test_db)."""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/titan_test_db"

    @property
    def MAINTENANCE_DATABASE_URL(self) -> str:
        """Used to create/delete other databases"""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/postgres"

    @property
    def LANGGRAPH_DB_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
