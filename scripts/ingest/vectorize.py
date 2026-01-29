import sys
import os
import asyncio
import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter

sys.path.append(os.getcwd())

from app.db.session import async_session_factory, init_db
from app.models.report import FinancialReport
from app.services.embedder import embedder

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("TITAN_VECTORIZER")


async def process_file(file_path: str, session):
    filename = os.path.basename(file_path)
    logger.info(f"Processing file: {filename}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        parts = filename.split("_")
        ticker = parts[0] if len(parts) > 0 else "UNKOWN"
        report_type = parts[1] if len(parts) > 1 else "10-K"
        year = 2025

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=150, separators=["\n\n", "\n", ".", " ", ""]
        )
        chunks = splitter.split_text(text)

        logger.info(f"Split into {len(chunks)} chunks. Generating embeddings...")

        new_records = []
        for i, chunk in enumerate(chunks):
            vector = embedder.generate_embedding(chunk)
            record = FinancialReport(
                company_ticker=ticker,
                year=year,
                report_type=report_type,
                section=f"chunk_{i}",
                content=chunk,
                embedding=vector,
            )
            new_records.append(record)

        session.add_all(new_records)
        await session.commit()
        logger.info(f"Persisted {len(new_records)} vectors for {ticker}.")

    except Exception as e:
        logger.error(f"Error processing {filename}: {e}")
        await session.rollback()


async def main():
    logger.info("Initializing Database Infrastructure...")
    await init_db()
    logger.info("Database ready.")

    processed_dir = os.path.join(os.getcwd(), "data", "processed")

    if not os.path.exists(processed_dir):
        logger.error(f"Directory not found: {processed_dir}. Run clean_data.py first.")
        return

    files = [f for f in os.listdir(processed_dir) if f.endswith(".txt")]

    if not files:
        logger.warning("No files found to vectorize.")
        return

    logger.info(f"Starting Vectorization Job for {len(files)} files...")

    async with async_session_factory() as session:
        for file in files:
            full_path = os.path.join(processed_dir, file)
            await process_file(full_path, session)

    logger.info("Vectorization Job Completed.")


if __name__ == "__main__":
    asyncio.run(main())
