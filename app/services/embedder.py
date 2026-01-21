import logging
from app.core.llm import LLMFactory

logger = logging.getLogger(__name__)


class EmbeddingService:
    _instance = None
    _embedder_model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._initialize_model()
        return cls._instance

    @classmethod
    def _initialize_model(cls):
        try:
            cls._embedder_model = LLMFactory.get_embeddings()
            logger.info("Embedding Model initialized via Factory.")
        except Exception as e:
            logger.critical(f"Failded to load embedding model: {e}")

    def generate_embedding(self, text: str) -> list[float]:
        if not text or not text.strip():
            return []

        clean_text = text.replace("\n", " ")

        return self._embedder_model.embed_query(clean_text)


embedder = EmbeddingService()
