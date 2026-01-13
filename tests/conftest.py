import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock, patch
from app.main import app
from app.agents.nodes import AgentNodes


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
