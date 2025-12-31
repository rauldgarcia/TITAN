import logging
from app.agents.state import AgentState
from app.services.retriever import RetrievalService
from app.services.rag import RAGService
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import JsonOutputParser

logger = logging.getLogger(__name__)

class AgentNodes:
    def __init__(self, session):
        self.retriever_service = RetrievalService(session)
        self.grader_llm = ChatOllama(model="llama3.2", temperature=0, format="json")

    async def retrieve(self, state: AgentState) -> AgentState:
        """
        Node: Retrieves documents from Vecto DB based on the question.
        """
        logger.info("---RETRIEVE---")
        question = state["question"]

        documents = await self.retriever_service.search_relevant_chunks(question, limit=4)

        doc_contents = [doc.content for doc in documents]
        doc_sources = [f"{doc.company_ticker} ({doc.section})" for doc in documents]

        return {"documents": doc_contents, "sources": doc_sources, "question": question}
    
    async def grade_documents(self, state: AgentState) -> AgentState:
        """
        Node: Evaluates retrieved documents for relevance (Preference Alignment cia Engineering).
        Filters out noise.
        """
        logger.info("---CHECK RELEVANCE---")
        question = state["question"]
        documents = state["documents"]
        sources = state["sources"]

        prompt = ChatPromptTemplate.from_template(
            """
            You are a grader assessing relenvace of a retrieved document to a user question. \n
            Here is the retrieved document: \n\n {document} \n\n
            Here is the user question: {question} \n
            If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
            Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question. \n
            Provide the binary score as a JSON with a single key 'score' and no premable or explanation.
            """
        )

        grader_chain = prompt | self.grader_llm | JsonOutputParser()

        filtered_docs = []
        filtered_sources = []

        for i, doc in enumerate(documents):
            try:
                grade = await grader_chain.ainvoke({"question": question, "document": doc})
                score = grade.get("score", "no")

                if score == "yes":
                    logger.info(f"---GRADE: DOCUMENT RELEVANT---")
                    filtered_docs.append(doc)
                    filtered_sources.append(sources[i])
                else:
                    logger.info(f"---GRADE: DOCUMENT NOT RELEVANT (FILTERED)---")

            except Exception as e:
                logger.warning(f"Grader error: {e}")
                continue

        return {"documents": filtered_docs, "sources": filtered_sources, "question": question}
    
    async def generate(self, state: AgentState) -> AgentState:
        """
        Node: Generates the final answer using filtered documents.
        """
        logger.info("---GENERATE---")
        question = state["question"]
        documents = state["documents"]

        if not documents:
            return {
                "generation": "I could not find relevant financial data to answer your question after filtering", 
                "question": question
                }
        
        context = "\n\n".join(documents)

        generator_llm = ChatOllama(model="llama3.2", temperature=0)

        prompt = ChatPromptTemplate.from_template(
            """
            You are TITAN, a Senior Financial Auditor. Use the following context to answer the question.
            If you don't know the answer, just say that you don't know.
            Keep the answer professional and detailed.

            Context: {context}
            Question: {question}
            """
        )

        chain = prompt | generator_llm
        reponse = await chain.ainvoke({"context": context, "question": question})

        return {"generation": reponse.content, "question": question}