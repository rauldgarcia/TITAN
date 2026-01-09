import sys
import os
import logging
from concurrent.futures import ProcessPoolExecutor

sys.path.append(os.getcwd())
from app.services.parser import SECParser

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("TITAN_CLEANER")


def process_file(file_info):
    """
    Worker function for parallel processing.
    """
    input_path, output_path = file_info

    try:
        if os.path.exists(output_path):
            return f"Skipped (Exists): {os.path.basename(output_path)}"

        with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
            raw_content = f.read()

        cleaned_text = SECParser.clean_html(raw_content)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(cleaned_text)

        return f"Cleaned: {os.path.basename(output_path)}"

    except Exception as e:
        return f"Error processing {input_path}: {e}"


def main():
    raw_data_dir = os.path.join(os.getcwd(), "data", "sec_filings")
    processed_dir = os.path.join(os.getcwd(), "data", "processed")
    os.makedirs(processed_dir, exist_ok=True)

    logger.info("Starting Data Cleaning Job...")

    files_to_process = []

    for root, dirs, files in os.walk(raw_data_dir):
        for file in files:
            if file.endswith(".txt") or file.endswith(".html"):
                input_path = os.path.join(root, file)

                parts = input_path.split(os.sep)
                try:
                    ticker_idx = parts.index("sec-edgar-filings") + 1
                    ticker = parts[ticker_idx]
                    filing_type = parts[ticker_idx + 1]
                    uuid_folder = parts[-2]

                    new_filename = f"{ticker}_{filing_type}_{uuid_folder}.txt"
                    output_path = os.path.join(processed_dir, new_filename)

                    files_to_process.append((input_path, output_path))

                except (ValueError, IndexError):
                    continue

    logger.info(f"Found {len(files_to_process)} files to clean.")

    with ProcessPoolExecutor() as executor:
        results = executor.map(process_file, files_to_process)

        for result in results:
            if "Error" in result:
                logger.error(result)
            else:
                logger.info(result)

    logger.info("Cleaning Job Completed.")


if __name__ == "__main__":
    main()
