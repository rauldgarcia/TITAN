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


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
async def setup_test_db():
    """
    Session Fixture: Runs ONCE at the start of all tests.
    1. Deletes the previous test database.
    2. Creates a new database, 'titan_test_db'.
    """
    sys_engine = create_async_engine(
        settings.MAINTENANCE_DATABASE_URL, isolation_level="AUTOCOMMIT"
    )

    async with sys_engine.connect() as conn:
        await conn.execute(
            text("""
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = 'titan_test_db'
        AND pid <> pg_backend_pid();
        """)
        )

        await conn.execute(text("DROP DATABASE IF EXISTS titan_test_db"))
        await conn.execute(text("CREATE DATABASE titan_test_db"))

    await sys_engine.dispose()
    return settings.TEST_DATABASE_URL


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
async def db_session(setup_test_db):
    """
    Function fixture: Runs in EVERY test.
    Connects to 'titan_test_db', creates the tables, hands off the session, and then rolls back.
    """
    test_db_url = setup_test_db
    test_engine = create_async_engine(test_db_url, echo=False, future=True)

    async with test_engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session_factory = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_factory() as session:
        yield session

    await test_engine.dispose()
