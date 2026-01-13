import pytest
from app.agents.state import AgentState


@pytest.mark.asyncio
async def test_route_supervisor_logic(nodes_with_mocks):
    """
    Test that the Supervisor directs to the correct node according to the string 'next_step'.
    """
    state_research = AgentState(next_step="research_agent", loop_step=0, documents=[])
    decision = await nodes_with_mocks.route_supervisor(state_research)
    assert decision == "retrieve"

    state_unknown = AgentState(next_step="quant_agent", loop_step=0)
    decision = await nodes_with_mocks.route_supervisor(state_unknown)
    assert decision == "quant_agent"


@pytest.mark.asyncio
async def test_circuit_breaker_logic(nodes_with_mocks):
    """
    CRITICAL: Test that the 'Circuit Breaker' stops infinite loops.
    If loop_step >= 15, it must force 'reporter_agent' to ignore the supervisor.
    """
    state_loop = AgentState(next_step="research_agent", loop_step=15, documents=[])
    decision = await nodes_with_mocks.route_supervisor(state_loop)
    assert decision == "reporter_agent"


@pytest.mark.asyncio
async def test_route_search_logic(nodes_with_mocks):
    """
    Test the CRAG (Corrective RAG) logic.
    """
    state_empty = AgentState(documents=[])
    decision = await nodes_with_mocks.route_search(state_empty)
    assert decision == "web_search"

    state_full = AgentState(documents=["doc1", "doc2"])
    decision = await nodes_with_mocks.route_search(state_full)
    assert decision == "supervisor"


@pytest.mark.asyncio
async def test_route_quant_hitl(nodes_with_mocks):
    """
    Test that the Quant Agent activates human intervention if necessary.
    """
    state_error = AgentState(next_step="human_intervention")
    decision = await nodes_with_mocks.route_quant(state_error)
    assert decision == "human_intervention"

    state_success = AgentState(next_step="supervisor")
    decision = await nodes_with_mocks.route_quant(state_success)
    assert decision == "supervisor"
