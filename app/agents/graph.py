from langgraph.graph import END, StateGraph
from app.agents.state import AgentState
from app.agents.nodes import AgentNodes
import logging

logger = logging.getLogger(__name__)

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

class TitanGraph:
    def __init__(self, session):
        self.nodes = AgentNodes(session)

    def build_graph(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("retrieve", self.nodes.retrieve)
        workflow.add_node("grade_documents", self.nodes.grade_documents)
        workflow.add_node("web_search", self.nodes.web_search)
        workflow.add_node("generate", self.nodes.generate_report)

        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "grade_documents")
        workflow.add_conditional_edges("grade_documents", decide_to_generate_or_search, {
            "web_search": "web_search",
            "generate": "generate"
        })
        workflow.add_edge("web_search", "generate")
        workflow.add_edge("generate", END)

        return workflow.compile()