from langgraph.graph import END, StateGraph
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
import logging
from app.agents.state import AgentState
from app.agents.nodes import AgentNodes, decide_to_search_or_not
from app.core.db_pool import get_pool
from app.core.config import settings

logger = logging.getLogger(__name__)

class TitanGraph:
    def __init__(self, session):
        self.session = session
        self.nodes = AgentNodes(session)

    def route_supervisor(self, state:AgentState):
        next_node = state.get("next_step")
        current_step = state.get("loop_step", 0)
        MAX_LOOPS = 15

        if current_step >= MAX_LOOPS:
            logger.warning("Max loops ({MAX_LOOPS}) reached. Forcing report generation.")
            return "reporter_agent"

        logger.info(f"Router directing to: {next_node}")

        if next_node == "research_agent":
            return "retrieve"
        elif next_node == "quant_agent":
            return "quant_agent"
        elif next_node == "market_agent":
            return "market_agent"
        elif next_node == "reporter_agent":
            return "reporter_agent"
        else:
            return "reporter_agent"
    
    async def run(self, input_data: dict, config: dict):
        """
        Executes the workflow using the global connection pool for persistence.
        """
        workflow = StateGraph(AgentState)

        workflow.add_node("supervisor", self.nodes.supervisor_node)
        workflow.add_node("quant_agent", self.nodes.quant_agent)
        workflow.add_node("reporter_agent", self.nodes.generate_report)

        workflow.add_node("retrieve", self.nodes.retrieve)
        workflow.add_node("grade_documents", self.nodes.grade_documents)
        workflow.add_node("web_search", self.nodes.web_search)
        workflow.add_node("market_agent", self.nodes.market_agent)

        workflow.set_entry_point("supervisor")

        workflow.add_conditional_edges(
            "supervisor", self.route_supervisor, {
                "retrieve": "retrieve",
                "quant_agent": "quant_agent",
                "reporter_agent": "reporter_agent",
                "market_agent": "market_agent"
                }
            )

        workflow.add_edge("retrieve", "grade_documents")

        workflow.add_conditional_edges(
            "grade_documents", decide_to_search_or_not, {
                "web_search": "web_search",
                "supervisor": "supervisor"
                }
            )
        
        workflow.add_edge("web_search", "supervisor")
        workflow.add_edge("quant_agent", "supervisor")
        workflow.add_edge("market_agent", "supervisor")

        workflow.add_edge("reporter_agent", END)

        pool = get_pool()
        checkpointer = AsyncPostgresSaver(pool)
        await checkpointer.setup()
        app = workflow.compile(checkpointer=checkpointer)

        return await app.ainvoke(input_data, config)