
from typing import Dict, Any, List, Optional
from typing_extensions import TypedDict

class AgentState(TypedDict):
    """State shared across all LangGraph nodes"""
    question: str
    intent: str
    agent: str
    tool_calls: List[str]
    tool_results: Dict[str, Any]
    response: str
    error: Optional[str]
    context: Dict[str, Any]