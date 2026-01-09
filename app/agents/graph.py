from langgraph.graph import END, StateGraph
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
import logging
from app.agents.state import AgentState
from app.agents.nodes import AgentNodes
from app.core.db_pool import get_pool

logger = logging.getLogger(__name__)


class TitanGraph:
    def __init__(self, session):
        self.session = session
        self.nodes = AgentNodes(session)

    async def get(self):
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
        workflow.add_node("human_intervention", self.nodes.human_node)

        workflow.set_entry_point("supervisor")
        workflow.add_conditional_edges("supervisor", self.nodes.route_supervisor)
        workflow.add_edge("retrieve", "grade_documents")
        workflow.add_conditional_edges("grade_documents", self.nodes.route_search)
        workflow.add_edge("web_search", "supervisor")
        workflow.add_edge("market_agent", "supervisor")
        workflow.add_conditional_edges("quant_agent", self.nodes.route_quant)
        workflow.add_edge("human_intervention", "supervisor")
        workflow.add_edge("reporter_agent", END)

        pool = get_pool()
        checkpointer = AsyncPostgresSaver(pool)
        await checkpointer.setup()
        app = workflow.compile(
            checkpointer=checkpointer, interrupt_before=["human_intervention"]
        )

        return app
