import pytest
import httpx
from unittest.mock import patch, AsyncMock
from app.services.chronos_client import ChronosClient
from app.core.config import settings


@pytest.mark.asyncio
async def test_get_forecast_success():
    """Test successful JSON parsing from CHRONOS API."""
    mock_response = httpx.Response(
        200,
        json={"ticker": "AAPL", "predicted_close": 150.0},
        request=httpx.Request("GET", f"{settings.CHRONOS_API_URL}/forecast/AAPL"),
    )

    with patch(
        "httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_response
    ):
        result = await ChronosClient.get_forecast("AAPL")

    assert result is not None
    assert result["ticker"] == "AAPL"
    assert result["predicted_close"] == 150.0


@pytest.mark.asyncio
async def test_get_forecast_http_error():
    """Test handling of 4xx/5xx HTTP errors."""
    request = httpx.Request("GET", f"{settings.CHRONOS_API_URL}/forecast/AAPL")
    mock_response = httpx.Response(404, request=request)

    with patch(
        "httpx.AsyncClient.get",
        new_callable=AsyncMock,
        side_effect=httpx.HTTPStatusError(
            "Not found", request=request, response=mock_response
        ),
    ):
        result = await ChronosClient.get_forecast("AAPL")

    assert result is None


@pytest.mark.asyncio
async def test_get_forecast_timeout():
    """Test handling of request timeouts to CHRONOS."""
    with patch(
        "httpx.AsyncClient.get",
        new_callable=AsyncMock,
        side_effect=httpx.TimeoutException("Timeout"),
    ):
        result = await ChronosClient.get_forecast("AAPL")

    assert result is None
