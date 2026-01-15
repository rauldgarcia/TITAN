import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, text
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock, patch
from app.main import app
from app.agents.nodes import AgentNodes
from app.core.config import settings


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def nodes_with_mocks(mock_session):
    """
    Initialize AgentNodes with all external tools mocked.
    """
    with (
        patch("app.agents.nodes.RetrievalService"),
        patch("app.agents.nodes.ChatOllama"),
        patch("app.agents.nodes.TavilySearchResults"),
        patch("app.agents.nodes.PythonREPL"),
        patch("app.agents.nodes.load_mcp_tools"),
    ):
        nodes = AgentNodes(mock_session)

        nodes.repl = MagicMock()
        return nodes


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """
    Create a real database session for integration testing.
    Ensure that the tables exist before starting.
    """
    test_engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)

    async with test_engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session_factory = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_factory() as session:
        yield session

    await test_engine.dispose()
