import logging
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class ChronosClient:
    """
    Async HTTP client for the CHRONOS ML Forecasting API.

    Local:      http://localhost:8001  (run CHRONOS alongside TITAN)
    Production: https://chronos-api-842951566749.us-central1.run.app
    """

    @staticmethod
    async def get_forecast(ticker: str) -> dict | None:
        """
        Calls the CHRONOS /forecast/{ticker} endpoint and returns the
        structured prediction dict, or None if the service is unavailable.

        Returns:
            {
                "ticker": "AAPL",
                "target_date": "2026-04-14T00:00:00",
                "predicted_close": 258.53,
                "model_used": "Ridge",
                "model_run_id": "gs://...",
                "environment": "production"
            }
        """
        url = f"{settings.CHRONOS_API_URL}/forecast/{ticker.upper()}"
        logger.info(f"Calling CHRONOS API: GET {url}")

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                logger.info(
                    f"CHRONOS forecast received: {ticker} → "
                    f"${data.get('predicted_close', '?')} "
                    f"({data.get('model_used', '?')})"
                )
                return data

        except httpx.TimeoutException:
            logger.warning(f"CHRONOS API timed out for ticker {ticker}.")
            return None
        except httpx.HTTPStatusError as e:
            logger.warning(f"CHRONOS API returned HTTP {e.response.status_code} for {ticker}.")
            return None
        except Exception as e:
            logger.error(f"Unexpected error calling CHRONOS for {ticker}: {e}")
            return None
