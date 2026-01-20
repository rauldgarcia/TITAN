from typing import TypedDict, List, Optional


class AgentState(TypedDict):
    """
    Represents the state of our financial agent graph
    """

    question: str
    documents: List[str]
    generation: str
    sources: List[str]
    next_step: Optional[str]
    loop_step: int
    error_message: Optional[str]
