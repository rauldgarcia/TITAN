from typing import TypedDict, List, Optional, Annotated
import operator

class AgentState(TypedDict):
    """
    Represents the state of our financial agent graph
    """
    question: str
    documents: List[str]
    generation: str
    sources: List[str]
    next_step: Optional[str]
    loop_step: Annotated[int, operator.add]