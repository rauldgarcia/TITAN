import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.agents.nodes import AgentNodes
from app.agents.state import AgentState

@pytest.fixture
def mock_session():
    """
    Simulate a database session.
    """
    return AsyncMock()

@pytest.fixture
def nodes_with_mocks(mock_session):
    """
    Initialize AgentNodes with all external tools mocked.
    """
    with patch("app.agents.nodes.RetrievalService"), \
        patch("app.agents.nodes.ChatOllama"), \
        patch("app.agents.nodes.TavilySearchResults"), \
        patch("app.agents.nodes.PythonREPL"), \
        patch("app.agents.nodes.load_mcp_tools"):

        nodes = AgentNodes(mock_session)

        nodes.repl = MagicMock()
        return nodes

@pytest.mark.asyncio
async def test_quant_agent_success(nodes_with_mocks):
    """
    Test that the Quant Agent executes code and returns the result.
    """
    nodes_with_mocks.repl.run.return_value = "Result: 500" 

    with patch("langchain_core.runnables.base.RunnableSequence.ainvoke", new_callable=AsyncMock) as mock_chain:
        mock_chain.return_value = "print('Result: 500')"
        state = AgentState(question="Calc 250*2", documents=[], loop_step=0)
        result_state = await nodes_with_mocks.quant_agent(state)
        assert "documents" in result_state
        assert "Result: 500" in result_state["documents"][0]
        assert result_state.get("error_message") is None

@pytest.mark.asyncio
async def test_quant_agent_failure_handling(nodes_with_mocks):
    """
    Test that if the code fails, the Human-in-the-Loop is activated.
    """
    nodes_with_mocks.repl.run.return_value = "SyntaxError: unexpected EOF"

    with patch("langchain_core.runnables.base.RunnableSequence.ainvoke", new_callable=AsyncMock) as mock_chain:
        mock_chain.return_value = "bad_code"
        state = AgentState(question="Calc Error", documents=[], loop_state=0)
        result_state = await nodes_with_mocks.quant_agent(state)

        assert result_state.get("next_step") == "human_intervention"
        assert "Quant execution failed" in result_state["error_message"]

@pytest.mark.asyncio
async def test_supervisor_force_reporter(nodes_with_mocks):
    """
    Test the deterministic logic: If there is already data and loop > 0, force report.
    """
    state = AgentState(
        question="Analyze Apple",
        documents=["Some financial data"],
        loop_step=1,
        next_step=None
    )
    result = await nodes_with_mocks.supervisor_node(state)

    assert result["next_step"] == "reporter_agent"
    assert result["loop_step"] == 1