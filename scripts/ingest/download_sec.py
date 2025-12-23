import sys
import os
import logging
from sec_edgar_downloader import Downloader
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("TITAN_ETL")

def download_10k_filings(tickers: list[str], amount: int = 1):
    """
    Downloads the latest 10-K filings (Annual Reports) for specified companies.

    The data is stored in 'data/sec_filings' following the structure:
    ticker/10-K/filing_id/full-submission.txt

    Args:
        tickers: List of stock symbols (e.g., ['AAPL', 'NVDA']).
        amount: Number of historical reports to download per company.
    """

    base_dir = os.path.abspath(os.path.join(os.getcwd(), "data", "sec_filings"))
    os.makedirs(base_dir, exist_ok=True)

    logger.info(f"Storage Directory set to: {base_dir}")

    dl = Downloader("TitanPlatform", "admin@titan-demo.com", base_dir)

    success_count = 0

    for ticker in tickers:
        try:
            logger.info(f"Starting download for {ticker} (Limit: {amount})...")
            num_downloaded = dl.get("10-K", ticker, limit=amount)

            if num_downloaded > 0:
                logger.info(f"Successfully downloaded {num_downloaded} filings for {ticker}.")
                success_count += 1
            else:
                logger.warning(f"No filings found for {ticker}.")

        except Exception as e:
            logger.error(f"Critical error downloading {ticker}: {e}")

    return success_count

if __name__ == "__main__":
    TARGET_COMPANIES = ["AAPL", "TSLA", "MSFT"]

    start_time = datetime.now()
    logger.info("Starting SEC Extraction Job...")

    total_companies = download_10k_filings(TARGET_COMPANIES, amount=1)

    duration = datetime.now() - start_time
    logger.info(f"ETL Job Completed. Processed {total_companies}/{len(TARGET_COMPANIES)} companies in {duration}.")