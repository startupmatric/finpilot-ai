
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.graph.state import AgentState
from app.llm.groq_client import groq_client
from app.llm.prompts import get_system_prompt

class SupervisorAgent:
    """Supervisor that routes queries to appropriate agents"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def route(self, state: AgentState) -> AgentState:
        """Route the question to the appropriate agent"""
        question = state.get("question", "").lower()
        
        # Determine intent
        if any(word in question for word in ["spend", "spent", "spending", "cost", "expense"]):
            state["intent"] = "spending"
            state["agent"] = "spending"
        elif any(word in question for word in ["merchant", "store", "shop", "vendor", "top"]):
            state["intent"] = "merchant"
            state["agent"] = "merchant"
        elif any(word in question for word in ["budget", "bud", "remaining", "left"]):
            state["intent"] = "budget"
            state["agent"] = "budget"
        elif any(word in question for word in ["stat", "average", "mean", "median", "summary"]):
            state["intent"] = "statistics"
            state["agent"] = "statistics"
        elif any(word in question for word in ["health", "score", "wellness", "advice"]):
            state["intent"] = "health"
            state["agent"] = "coach"
        else:
            state["intent"] = "general"
            state["agent"] = "coach"
        
        return state