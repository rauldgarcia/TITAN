import sys
import os
import asyncio
import json
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    Faithfulness,
    AnswerRelevancy,
    ContextPrecision,
)
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFaceEmbeddings

sys.path.append(os.getcwd())

from app.db.session import async_session_factory
from app.services.retriever import RetrievalService
from app.services.rag import RAGService

judge_llm = LangchainLLMWrapper(ChatOllama(model="llama3.2", temperature=0))
judge_embeddings = LangchainEmbeddingsWrapper(
    HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")
)


async def generate_responses(dataset_path):
    """
    Run TITAN to answer the dataset questions.
    """
    with open(dataset_path, "r") as f:
        data = json.load(f)

    results = {
        "user_input": [],
        "response": [],
        "retrieved_contexts": [],
        "reference": [],
    }

    print("Generating answers with TITAN...")

    async with async_session_factory() as session:
        retriever = RetrievalService(session)
        rag = RAGService(retriever)

        for item in data:
            q = item["question"]
            gt = item["ground_truth"]

            print(f"Processing: {q[:30]}...")

            response_data = await rag.answer_question(q)
            chunks = await retriever.search_relevant_chunks(q)
            context_list = [c.content for c in chunks]

            if not context_list:
                print(
                    "WARNING: No context found. Ragas metrics might fail for this row."
                )
                context_list = ["No context available."]

            results["user_input"].append(q)
            results["response"].append(response_data["answer"])
            results["retrieved_contexts"].append(context_list)
            results["reference"].append(gt)

    return Dataset.from_dict(results)


def run_evaluation():
    dataset = asyncio.run(generate_responses("data/evaluation_set.json"))

    print("\n Starting RAGAS Evaluation (This may take some time)...")

    metrics = [
        Faithfulness(),
        AnswerRelevancy(),
        ContextPrecision(),
    ]

    results = evaluate(
        dataset=dataset, metrics=metrics, llm=judge_llm, embeddings=judge_embeddings
    )

    df = results.to_pandas()
    print("\n EVALUATION RESULTS:")
    print(df[["user_input", "faithfulness", "answer_relevancy", "context_precision"]])

    print("\n GLOBAL AVERAGES:")
    print(results)

    os.makedirs("data/reports", exist_ok=True)
    df.to_csv("data/reports/rag_evaluation.csv", index=False)
    print("\n Report saved in data/reports/rag_evaluation.csv")


if __name__ == "__main__":
    run_evaluation()
