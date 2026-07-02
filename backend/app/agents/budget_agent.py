
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.graph.state import AgentState
from app.tools.analytics_tools import AnalyticsTools

class BudgetAgent:
    """Agent that handles budget-related queries"""
    
    def __init__(self, db: Session):
        self.db = db
        self.tools = AnalyticsTools(db)
    
    def process(self, state: AgentState) -> AgentState:
        """Process budget queries"""
        results = {}
        
        # Get budget status
        results["budget"] = self.tools.get_budget_status()
        
        state["tool_results"] = results
        state["tool_calls"] = list(results.keys())
        
        return state