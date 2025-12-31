from typing import Annotated, TypedDict, List
from operator import add

class AgentState(TypedDict):
    """
    Represents the state of out financial agent graph
    """
    question: str
    documents: List[str]
    generation: str
    sources: List[str]