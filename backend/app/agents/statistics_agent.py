from typing import Dict, Any
from sqlalchemy.orm import Session
from app.graph.state import AgentState
from app.tools.analytics_tools import AnalyticsTools

class StatisticsAgent:
    """Agent that handles statistics-related queries"""
    
    def __init__(self, db: Session):
        self.db = db
        self.tools = AnalyticsTools(db)
    
    def process(self, state: AgentState) -> AgentState:
        """Process statistics queries"""
        results = {}
        
        # Get statistics
        results["statistics"] = self.tools.get_statistics()
        
        # Also get category breakdown for context
        results["category"] = self.tools.get_spending_by_category()
        
        state["tool_results"] = results
        state["tool_calls"] = list(results.keys())
        
        return state
