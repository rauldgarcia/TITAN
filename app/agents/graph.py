from langgraph.graph import END, StateGraph
from app.agents.state import AgentState
from app.agents.nodes import AgentNodes

class TitanGraph:
    def __init__(self, session):
        self.nodes = AgentNodes(session)

    def build_graph(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("retrieve", self.nodes.retrieve)
        workflow.add_node("grade_documents", self.nodes.grade_documents)
        workflow.add_node("generate", self.nodes.generate)

        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "grade_documents")
        workflow.add_edge("grade_documents", "generate")
        workflow.add_edge("generate", END)

        return workflow.compile()