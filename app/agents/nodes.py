import logging
from app.agents.state import AgentState
from app.services.retriever import RetrievalService
from app.services.rag import RAGService
from app.core.config import settings
from app.schemas.report_schema import FinancialSummary
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.output_parsers import JsonOutputParser
from langchain_experimental.utilities import PythonREPL
from langchain_core.tools import Tool
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)
templates_env = Environment(loader=FileSystemLoader("app/templates"))

class AgentNodes:
    def __init__(self, session):
        self.retriever_service = RetrievalService(session)
        self.grader_llm = ChatOllama(model="llama3.2", temperature=0, format="json")
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

        prompt = PromptTemplate(
            template="""
        You are a Financial Analyst.
        Analyze the following context and extract the key information to fill the report.

        Context: {context}

        {format_instructions}

        Ensure the 'severity' of risk is strictly 'High', 'Medium', or 'Low'.
        """,
        input_variable=["context"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
        )

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

        code_gen_prompt = f"""
        You are a Python Data Scientist. Write python code to solve: {question}.
        Assume you have varaible like 'revenue', 'debt' printed out if provided in context.
        Just output the python code. No markdown backticks.
        """
        code = self.grader_llm.invoke(code_gen_prompt).content

        try:
            logger.info(f"Executing Code: {code[:50]}...")
            result = self.repl.run(code)
            logger.info(f"Calculating Result: {result}")
            return {"documents": [f"Python Calculation Result: {result}"], "question": question}
        
        except Exception as e:
            return {"documents": [f"Error calculating: {e}"], "question": question}