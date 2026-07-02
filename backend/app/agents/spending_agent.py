from typing import Dict, Any
from sqlalchemy.orm import Session
from app.graph.state import AgentState
from app.tools.analytics_tools import AnalyticsTools

class SpendingAgent:
    """Agent that handles spending-related queries"""
    
    def __init__(self, db: Session):
        self.db = db
        self.tools = AnalyticsTools(db)
    
    def process(self, state: AgentState) -> AgentState:
        """Process spending queries"""
        question = state.get("question", "").lower()
        results = {}
        
        # Determine which tools to call
        if "category" in question or "food" in question:
            results["category"] = self.tools.get_spending_by_category()
        
        if "total" in question or "all" in question:
            results["total"] = self.tools.get_total_spending()
        
        if "month" in question or "monthly" in question:
            results["monthly"] = self.tools.get_monthly_spending()
        
        # If no specific filters, get category breakdown
        if not results:
            results["category"] = self.tools.get_spending_by_category()
        
        state["tool_results"] = results
        state["tool_calls"] = list(results.keys())
        
        return state