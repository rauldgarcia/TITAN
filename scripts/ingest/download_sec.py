import os
import sys
import logging
import requests
import time
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("TITAN_ETL")

SEC_HEADERS = {
    "User-Agent": "TitanIntelligence rauld.garcia95@gmail.com",
    "Accept-Encoding": "gzip, deflate",
    "Host": "www.sec.gov",
}


def get_cik_from_ticker(ticker: str) -> str:
    """
    Obtains the CIK (SEC Unique ID) given a Ticker.
    """
    try:
        url = "https://www.sec.gov/files/company_tickers.json"
        response = requests.get(url, headers=SEC_HEADERS)
        response.raise_for_status()
        data = response.json()

        for entry in data.values():
            if entry["ticker"] == ticker.upper():
                return str(entry["click_str"]).zfill(10)

        raise ValueError(f"Ticker {ticker} not found in SEC database.")

    except Exception as e:
        logger.info(f"Error fetching CIK for {ticker}: {e}")
        return None


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

    for ticker in tickers:
        try:
            logger.info(f"Looking for CIK for {ticker}...")
            cik = get_cik_from_ticker(ticker)
            if not cik:
                continue

            logger.info(f"Retrieving report history for {ticker} (CIK: {cik})...")
            submissions_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            resp = requests.get(submissions_url, headers=SEC_HEADERS)
            resp.raise_for_status()
            filings = resp.json()["filings"]["recent"]

            count = 0

            for i, form in enumerate(filings["form"]):
                if form == "10-K":
                    accession_number = filings["accessionNumber"][i]
                    primary_document = filings["primaryDocument"][i]
                    accession_no_dash = accession_number.replace("-", "")
                    doc_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_no_dash}/{primary_document}"

                    save_path = os.path.join(
                        base_dir,
                        "sec_edgar_filings",
                        ticker,
                        "10-K",
                        accession_number,
                        "full-submission.txt",
                    )
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)

                    if not os.path.exists(save_path):
                        logger.info(f"Descargando 10-K ({accession_number})...")
                        doc_resp = requests.get(doc_url, headers=SEC_HEADERS)
                        doc_resp.raise_for_status()

                        with open(save_path, "wb") as f:
                            f.write(doc_resp.content)

                    else:
                        logger.info(f"File already exists: {accession_number}")

                    count += 1
                    time.sleep(0.2)  # Respect SEC rate limit (10 req/s)

                    if count >= amount:
                        break

        except Exception:
            logger.errorf("Download failed for {ticker}: {e}")


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    TARGET_COMPANIES = ["AAPL", "TSLA", "MSFT"]

    start_time = datetime.now()
    logger.info("Starting SEC Extraction Job...")

    total_companies = download_10k_filings(TARGET_COMPANIES, amount=1)

    duration = datetime.now() - start_time
    logger.info(
        f"ETL Job Completed. Processed {total_companies}/{len(TARGET_COMPANIES)} companies in {duration}."
    )
