
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.graph.state import AgentState
from app.tools.analytics_tools import AnalyticsTools

class MerchantAgent:
    """Agent that handles merchant-related queries"""
    
    def __init__(self, db: Session):
        self.db = db
        self.tools = AnalyticsTools(db)
    
    def process(self, state: AgentState) -> AgentState:
        """Process merchant queries"""
        question = state.get("question", "").lower()
        results = {}
        
        # Get top merchants
        if "top" in question:
            limit = 5
            results["top_merchants"] = self.tools.get_top_merchants(limit)
        else:
            # Default: show top merchants
            results["top_merchants"] = self.tools.get_top_merchants(5)
        
        state["tool_results"] = results
        state["tool_calls"] = list(results.keys())
        
        return state