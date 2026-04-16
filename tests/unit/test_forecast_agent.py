import pytest
from unittest.mock import patch, AsyncMock
from app.agents.state import AgentState


@pytest.mark.asyncio
async def test_forecast_agent_success(nodes_with_mocks):
    """
    Test that forecast_agent correctly extracts the ticker, calls CHRONOS,
    and updates the state with the forecast documents and raw data.
    """
    state_input: AgentState = {
        "question": "What is the valuation for MSFT today?",
        "documents": ["Initial document."],
        "generation": "",
        "sources": [],
        "next_step": None,
        "loop_step": 0,
        "error_message": None,
        "forecast_data": None,
    }

    mock_forecast = {
        "ticker": "MSFT",
        "target_date": "2026-04-14T00:00:00",
        "predicted_close": 425.50,
        "model_used": "XGBoost",
        "environment": "test",
    }

    with patch(
        "app.agents.nodes.ChronosClient.get_forecast",
        new_callable=AsyncMock,
        return_value=mock_forecast,
    ):
        result_state = await nodes_with_mocks.forecast_agent(state_input)

    assert "forecast_data" in result_state
    assert result_state["forecast_data"] == mock_forecast

    docs = result_state["documents"]
    assert len(docs) == 2  # 1 initial + 1 forecast summary
    assert "Predicted close price for MSFT" in docs[-1]
    assert "$425.50" in docs[-1]


@pytest.mark.asyncio
async def test_forecast_agent_service_unavailable(nodes_with_mocks):
    """
    Test that forecast_agent handles service downtime gracefully by appending
    a warning to documents and continuing.
    """
    state_input: AgentState = {
        "question": "Forecast TSLA",
        "documents": [],
        "generation": "",
        "sources": [],
        "next_step": None,
        "loop_step": 0,
        "error_message": None,
        "forecast_data": None,
    }

    with patch(
        "app.agents.nodes.ChronosClient.get_forecast",
        new_callable=AsyncMock,
        return_value=None,  # Simulates timeout/error
    ):
        result_state = await nodes_with_mocks.forecast_agent(state_input)

    assert result_state["forecast_data"] is None
    docs = result_state["documents"]
    assert len(docs) == 1
    assert "Service unavailable for TSLA" in docs[0]
