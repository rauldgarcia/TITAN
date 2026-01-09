import logging
import torch
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._initialize_model()
        return cls._instance

    @classmethod
    def _initialize_model(cls):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Loading Embedding Model on: {device.upper()}")

        try:
            cls._model = SentenceTransformer("all-mpnet-base-v2", device=device)
            logger.info("Embedding Model loaded successfully.")
        except Exception as e:
            logger.critical(f"Failded to load embedding model: {e}")

    def generate_embedding(self, text: str) -> list[float]:
        if not text or not text.strip():
            return []

        clean_text = text.replace("\n", " ")
        embedding = self._model.encode(clean_text, show_progress_bar=False)
        return embedding.tolist()


embedder = EmbeddingService()
