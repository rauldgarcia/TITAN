import logging
from app.core.llm import LLMFactory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.services.retriever import RetrievalService

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self, retrieval_service: RetrievalService):
        self.retriever = retrieval_service
        self.llm = LLMFactory.get_llm(temperature=0)

    async def answer_question(self, question: str) -> dict:
        """
        Orchestrates the RAG pipeline
        """
        chunks = await self.retriever.search_relevant_chunks(question, limit=4)

        if not chunks:
            return {
                "answer": "I couldn't find any relevant information in the financial reports to answer your question.",
                "sources": [],
            }

        context_text = "\n\n".join(
            [f"[Source: {c.company_ticker} {c.year} 10-K]: {c.content}" for c in chunks]
        )

        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are TITAN, a Senior Financial Auditor AI.
            Answer the user's question strictly based on the provided context below.

            Guidelines:
            - If the answer is not in the context, day "Data not found in available reports."
            - Cite the company ticker when making claims (e.g., "According to Apple's 10-K...").
            - Keep the tone professional, concise, and factual.
            
            Context:
            {context}
            """,
                ),
                ("user", "{question}"),
            ]
        )

        chain = prompt_template | self.llm | StrOutputParser()

        logger.info("Generating answer with Ollama...")
        response = await chain.ainvoke({"context": context_text, "question": question})

        return {
            "answer": response,
            "sources": [f"{c.company_ticker} ({c.section})" for c in chunks],
        }
