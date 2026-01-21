import logging
import os
import torch
from langchain_ollama import ChatOllama
from langchain_google_vertexai import ChatVertexAI, VertexAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)


class LLMFactory:
    @staticmethod
    def get_llm(temperature=0, json_mode=False):
        """
        Returns the LLM configured according to the environment (Local vs Prod).
        """
        env = os.getenv("ENVIRONMENT", "local").lower()

        if env == "production":
            logger.info("Using Vertex AI (Gemini Flash lite)")
            model_name = "gemini-2.5-flash-lite"
            return ChatVertexAI(
                model_name=model_name,
                temperature=temperature,
                convert_system_message_to_human=True,
            )
        else:
            logger.info("Using Ollama (Llama 3.2)")
            fmt = "json" if json_mode else None
            return ChatOllama(model="llama3.2", temperature=temperature, format=fmt)

    @staticmethod
    def get_embeddings():
        """
        Returns the Embeddings model according to the environment.
        """
        env = os.getenv("ENVIRONMENT", "local").lower()

        if env == "production":
            logger.info("Using Vertex AI Embeddings")
            return VertexAIEmbeddings(model_name="models/text-embedding-004")
        else:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Using Local HuggingFace Embeddings on {device.upper()}")
            return HuggingFaceEmbeddings(
                model_name="all-mpnet-base-v2", model_kwargs={"device": device}
            )
