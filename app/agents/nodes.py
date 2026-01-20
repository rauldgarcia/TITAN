import logging
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_experimental.utilities import PythonREPL
from jinja2 import Environment, FileSystemLoader
from typing import Literal

from app.agents.state import AgentState
from app.services.retriever import RetrievalService
from app.core.config import settings
from app.schemas.report_schema import FinancialSummary
from app.core.mcp_client import load_mcp_tools
from app.core.prompts import (
    GRADER_PROMPT,
    GENERATOR_PROMPT,
    REPORT_PROMPT,
    QUANT_PROMPT,
    SUPERVISOR_PROMPT,
)

logger = logging.getLogger(__name__)
templates_env = Environment(loader=FileSystemLoader("app/templates"))


class AgentNodes:
    def __init__(self, session):
        self.retriever_service = RetrievalService(session)
        self.router_llm = ChatOllama(model="llama3.2", temperature=0, format="json")
        self.gen_llm = ChatOllama(model="llama3.2", temperature=0)
        self.web_search_tool = TavilySearchResults(
            max_results=3, tavily_api_key=settings.TAVILY_API_KEY
        )
        self.repl = PythonREPL()
        self.market_tools = []

    async def retrieve(self, state: AgentState) -> AgentState:
        """
        Node: Retrieves documents from Vecto DB based on the question.
        """
        logger.info("---RETRIEVE---")
        question = state["question"]

        documents = await self.retriever_service.search_relevant_chunks(
            question, limit=4
        )

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

        grader_chain = GRADER_PROMPT | self.router_llm | JsonOutputParser()

        filtered_docs = []
        filtered_sources = []

        for i, doc in enumerate(documents):
            try:
                grade = await grader_chain.ainvoke(
                    {"question": question, "document": doc}
                )
                score = grade.get("score", "no")

                if score == "yes":
                    logger.info("---GRADE: DOCUMENT RELEVANT---")
                    filtered_docs.append(doc)
                    filtered_sources.append(sources[i])
                else:
                    logger.info("---GRADE: DOCUMENT NOT RELEVANT (FILTERED)---")

            except Exception as e:
                logger.warning(f"Grader error: {e}")
                continue

        return {
            "documents": filtered_docs,
            "sources": filtered_sources,
            "question": question,
        }

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
                "question": question,
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

        prompt = REPORT_PROMPT.partial(
            format_instructions=parser.get_format_instructions()
        )

        chain = prompt | self.router_llm | parser

        try:
            logger.info("Extracting structured data...")
            json_data = await chain.ainvoke({"context": context})

            logger.info("Rendering HTML...")
            template = templates_env.get_template("financial_report.html")
            html_output = template.render(data=json_data)

            return {"generation": html_output, "question": question}

        except Exception as e:
            logger.error(f"Reporting failed: {e}")
            return {
                "generation": f"Error generating report: {str(e)}",
                "question": question,
            }

    async def run_python_analysis(self, state: AgentState) -> AgentState:
        """
        Node: Executes python code to perform financial calculations.
        Used when the query implies math (e.g., 'Calculate current ratio').
        """
        logger.info("---QUANT ANALYST (PYTHON)---")
        question = state["question"]

        chain = QUANT_PROMPT | self.router_llm | StrOutputParser

        code = await chain.ainvoke({"question": question})

        try:
            logger.info(f"Executing Code: {code[:50]}...")
            result = self.repl.run(code)
            logger.info(f"Calculating Result: {result}")
            return {
                "documents": [f"Python Calculation Result: {result}"],
                "question": question,
            }

        except Exception as e:
            return {"documents": [f"Error calculating: {e}"], "question": question}

    async def supervisor_node(self, state: AgentState) -> AgentState:
        logger.info("---SUPERVISOR: ROUTING---")
        question = state["question"]
        docs = state.get("documents", [])
        current_step = state.get("loop_step", 0)
        logger.info(f"Loop Step: {current_step}")

        chain = SUPERVISOR_PROMPT | self.router_llm | JsonOutputParser()

        if current_step > 0 and docs:
            logger.info(
                "Supervisor Logic: Data present and loop active -> Forcing Reporter."
            )
            return {"next_step": "reporter_agent", "loop_step": current_step + 1}

        try:
            result = await chain.ainvoke({"question": question, "len_docs": len(docs)})
            next_step = result.get("next_step", "reporter_agent")
            logger.info(f"Supervisor decided: {next_step}")
            return {"next_step": next_step, "loop_step": current_step + 1}
        except Exception as e:
            logger.error(f"Supervisor failed: {e}. Defaulting to reporter.")
            return {"next_step": "reporter_agent", "loop_step": current_step + 1}

    async def quant_agent(self, state: AgentState) -> AgentState:
        logger.info("--- QUANT AGENT: CODING ---")
        question = state["question"]

        chain = QUANT_PROMPT | self.gen_llm | StrOutputParser()
        code = await chain.ainvoke({"question": question})

        code = code.replace("```python", "").replace("```", "").strip()

        try:
            logger.info(f"Executing: \n {code}")
            result = self.repl.run(code)

            if "Error" in result or "Traceback" in result:
                raise Exception(result)

            output_msg = f"Python Analysis Result for '{question}': \n{result}"
            logger.info(f"Result: {result}")

            current_docs = state.get("documents", [])
            current_docs.append(output_msg)
            return {"documents": current_docs, "error_message": None}

        except Exception as e:
            error_msg = f"Quant execution failed: {str(e)}"
            logger.error(f"{error_msg}. ESCALATING TO HUMAN.")
            return {"error_message": error_msg, "next_step": "human_intervention"}

    async def initialize_tools(self):
        if not self.market_tools:
            self.market_tools = await load_mcp_tools()

    async def market_agent(self, state: AgentState) -> AgentState:
        logger.info("---MARKET AGENT (MCP)---")
        question = state["question"]
        await self.initialize_tools()

        if not self.market_tools:
            return {"documents": ["Error: Market tools unavailable."]}

        words = question.split()
        ticker = next((w for w in words if w.isupper() and len(w) <= 5), "AAPL")
        results = []

        for tool in self.market_tools:
            try:
                res = await tool.coroutine(ticker)
                results.append(f"[{tool.name}]: {res}")
            except Exception as e:
                logger.error(f"Tool error: {e}")

        return {"documents": results}

    async def human_node(self, state: AgentState) -> AgentState:
        """
        This node doesn't do anything automatically.
        It's a placeholder where the graph will pause.
        When the human 'resume', this node executes and clears the error.
        """
        logger.info("---HUMAN INTERVENTION NODE---")
        logger.info("Human has updated the state. Resuming workflow...")
        return {"error_message": None, "next_step": "reporter_agent"}

    async def route_supervisor(
        self, state: AgentState
    ) -> Literal[
        "retrieve",
        "quant_agent",
        "market_agent",
        "human_intervention",
        "reporter_agent",
    ]:
        next_node = state.get("next_step")
        current_step = state.get("loop_step", 0)
        max_loops = 15

        if current_step >= max_loops:
            logger.warning(
                "Max loops ({max_loops}) reached. Forcing report generation."
            )
            return "reporter_agent"

        logger.info(f"Router directing to: {next_node}")

        if next_node == "research_agent":
            return "retrieve"
        elif next_node == "quant_agent":
            return "quant_agent"
        elif next_node == "market_agent":
            return "market_agent"
        elif next_node == "human_intervention":
            return "human_intervention"
        elif next_node == "reporter_agent":
            return "reporter_agent"
        else:
            return "reporter_agent"

    async def route_search(
        self, state: AgentState
    ) -> Literal["web_search", "supervisor"]:
        """
        Determines wheter to generate an answer or perform a web search.
        If any relevant documents were found, proceed to generation.
        Otherwise, fall back to web search.
        """
        logger.info("---ASSESSING DOCUMENT QUALITY---")

        if not state["documents"]:
            logger.warning(
                "No relevant documents found in DB. Falling back to web search."
            )
            return "web_search"
        else:
            logger.info("Sufficient documents found. Proceeding to generation.")
            return "supervisor"

    async def route_quant(
        self, state: AgentState
    ) -> Literal["human_intervention", "supervisor"]:
        if state.get("next_step") == "human_intervention":
            return "human_intervention"
        return "supervisor"
