import logging
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.report import FinancialReport
from app.services.embedder import embedder

logger = logging.getLogger(__name__)


class RetrievalService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def search_relevant_chunks(
        self, query: str, limit: int = 5, threshold: float = 0.5
    ) -> list[FinancialReport]:
        """
        Performs Semantic Search using pgvector cosine distance.

        Args:
            query: The user's question.
            limit: Number of chunks to retrieve.
            threshold: (Optional) Max distance to consider relevant.
        """

        if not query:
            return []

        query_vector = embedder.generate_embedding(query)

        if not query_vector:
            logger.warning("Could not generate embedding for query.")
            return []

        statement = (
            select(FinancialReport)
            .order_by(FinancialReport.embedding.cosine_distance(query_vector))
            .limit(limit)
        )

        try:
            results = await self.session.execute(statement)
            chunks = results.scalars().all()

            logger.info(
                f"Found {len(chunks)} relevant chunks for query: '{query[:30]}...'"
            )
            return chunks

        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
