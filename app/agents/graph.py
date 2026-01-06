from langgraph.graph import END, StateGraph
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from app.agents.state import AgentState
from app.agents.nodes import AgentNodes, decide_to_generate_or_search
from app.core.db_pool import get_pool

class TitanGraph:
    def __init__(self, session):
        self.session = session
        self.nodes = AgentNodes(session)

    async def run(self, input_data: dict, config: dict):
        """
        Executes the workflow using the global connection pool for persistence.
        """
        workflow = StateGraph(AgentState)

        workflow.add_node("retrieve", self.nodes.retrieve)
        workflow.add_node("grade_documents", self.nodes.grade_documents)
        workflow.add_node("web_search", self.nodes.web_search)
        workflow.add_node("generate", self.nodes.generate_report)

        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "grade_documents")
        workflow.add_conditional_edges(
            "grade_documents", decide_to_generate_or_search, {
                "web_search": "web_search",
                "generate": "generate"
                }
            )
        workflow.add_edge("web_search", "generate")
        workflow.add_edge("generate", END)

        pool = get_pool()
        checkpointer = AsyncPostgresSaver(pool)
        await checkpointer.setup()
        app = workflow.compile(checkpointer=checkpointer)

        return await app.ainvoke(input_data, config)