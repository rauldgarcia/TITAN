import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def mock_graph_execution():
    """
    It intercepts the creation and execution of TitanGraph within the endpoints.
    It allows us to simulate agent responses without touching the database or the LLM.
    """
    with patch("app.main.TitanGraph") as MockGraphClass:
        mock_instance = MockGraphClass.return_value
        mock_compiled_app = MagicMock()
        mock_compiled_app.ainvoke = AsyncMock()
        mock_compiled_app.aget_state = AsyncMock()
        mock_compiled_app.aupdate_state = AsyncMock()

        mock_instance.get = AsyncMock(return_value=mock_compiled_app)

        mock_state_snapshot = MagicMock()
        mock_state_snapshot.values = {"next_step": "human_intervention", "loop_step": 1}
        mock_state_snapshot.next = ("human_intervention",)
        mock_compiled_app.aget_state.return_value = mock_state_snapshot

        yield mock_compiled_app


@pytest.mark.asyncio
async def test_agent_chat_success(client, mock_graph_execution):
    """
    Scenario: The agent completes successfully and generates a report.
    """
    mock_graph_execution.ainvoke.return_value = {
        "generation": "<html>Report</html>",
        "sources": ["doc1"],
        "next_step": "reporter_agent",
    }

    payload = {"question": "Analyze Apple", "thread_id": "test_1"}
    response = await client.post("/chat/agent", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    assert data["answer"] == "<html>Report</html>"
    assert len(data["sources"]) == 1


@pytest.mark.asyncio
async def test_agent_chat_hitl_pause(client, mock_graph_execution):
    """
    Scenario: The agent fails at the Quant and pauses asking for help.
    """
    mock_graph_execution.ainvoke.return_value = {
        "generation": None,
        "next_step": "human_intervention",
        "error_message": "Division by zero",
    }

    payload = {"question": "Calculate error", "thread_id": "test_fail"}
    response = await client.post("/chat/agent", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "PAUSED"
    assert "human intervention" in data["message"]
    assert data["error"] == "Division by zero"


@pytest.mark.asyncio
async def test_agent_resume_success(client, mock_graph_execution):
    """
    Scenario: The user submits the correction and the agent continues.
    """
    mock_graph_execution.ainvoke.return_value = {
        "generation": "<html>Corrected Report</html>",
        "next_step": "reporter_agent",
    }

    payload = {"thread_id": "test_fail", "new_instructions": "The value is 100"}
    response = await client.post("/agent/resume", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Resumed"
    assert data["answer"] == "<html>Corrected Report</html>"
