import logging
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_experimental.utilities import PythonREPL
from jinja2 import Environment, FileSystemLoader

from app.agents.state import AgentState
from app.services.retriever import RetrievalService
from app.core.config import settings
from app.schemas.report_schema import FinancialSummary
from app.core.prompts import (
    GRADER_PROMPT, 
    GENERATOR_PROMPT, 
    REPORT_PROMPT, 
    QUANT_PROMPT
)

logger = logging.getLogger(__name__)
templates_env = Environment(loader=FileSystemLoader("app/templates"))

class AgentNodes:
    def __init__(self, session):
        self.retriever_service = RetrievalService(session)
        self.grader_llm = ChatOllama(model="llama3.2", temperature=0, format="json")
        self.generator_llm = ChatOllama(model="3.2", temperature=0)
        self.web_search_tool = TavilySearchResults(max_results=3, tavily_api_key=settings.TAVILY_API_KEY)
        self.repl = PythonREPL()

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

        grader_chain = GRADER_PROMPT | self.grader_llm | JsonOutputParser()

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

        chain = GENERATOR_PROMPT | generator_llm
        reponse = await chain.ainvoke({"context": context, "question": question})

        return {"generation": reponse.content, "question": question}
    
    async def web_search(self, state: AgentState) -> AgentState:
        """
        Node: Performs a web search when initial retrieval is insufficent.
        """
        logger.info("---WEB SEARCH---")
        question = state["question"]

        logger.info(f"Internal documents insufficient. Searching web for: '{question}'")

        search_results = await self.web_search_tool.ainvoke({"query": question})

        web_docs = [res["content"] for res in search_results]

        return {"documents": web_docs, "question": question}
    
    async def generate_report(self, state: AgentState) -> AgentState:
        """
        Node: Generates a structured HTML report using the filtered documents.
        """
        logger.info("---GENERATE REPORT (JINJA2)---")
        question = state["question"]
        documents = state["documents"]

        context = "\n\n".join(documents) if documents else "No internal data found."
        parser = JsonOutputParser(pydantic_object=FinancialSummary)

        prompt = REPORT_PROMPT.partial(format_instructions=parser.get_format_instructions())

        chain = prompt | self.grader_llm | parser

        try:
            logger.info("Extracting structured data...")
            json_data = await chain.ainvoke({"context": context})

            logger.info("Rendering HTML...")
            template = templates_env.get_template("financial_report.html")
            html_output = template.render(data=json_data)

            return {"generation": html_output, "question": question}
        
        except Exception as e:
            logger.error(f"Reporting failed: {e}")
            return {"generation": f"Error generating report: {str(e)}", "question": question}

    async def run_python_analysis(self, state: AgentState) -> AgentState:
        """
        Node: Executes python code to perform financial calculations.
        Used when the query implies math (e.g., 'Calculate current ratio').
        """
        logger.info("---QUANT ANALYST (PYTHON)---")
        question = state["question"]

        chain = QUANT_PROMPT | self.grader_llm | StrOutputParser

        code = await chain.ainvoke({"question": question})

        try:
            logger.info(f"Executing Code: {code[:50]}...")
            result = self.repl.run(code)
            logger.info(f"Calculating Result: {result}")
            return {"documents": [f"Python Calculation Result: {result}"], "question": question}
        
        except Exception as e:
            return {"documents": [f"Error calculating: {e}"], "question": question}
        
def decide_to_generate_or_search(state: AgentState) -> str:
    """
    Determines wheter to generate an answer or perform a web search.
    If any relevant documents were found, proceed to generation.
    Otherwise, fall back to web search.
    """
    logger.info("---ASSESSING DOCUMENT QUALITY---")

    if not state["documents"]:
        logger.warning("No relevant documents found in DB. Falling back to web search.")
        return "web_search"
    else:
        logger.info("Sufficient documents found. Proceeding to generation.")
        return "generate"