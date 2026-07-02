from typing import Dict, Any, List
from sqlalchemy.orm import Session
from langchain_core.tools import tool
from app.tools.analytics_tools import AnalyticsTools
from app.tools.transaction_tools import TransactionTools

class ToolRegistry:
    def __init__(self, db: Session):
        self.db = db
        self.analytics = AnalyticsTools(db)
        self.transactions = TransactionTools(db)
        
        self.tools = {
            "get_total_spending": self.get_total_spending,
            "get_spending_by_category": self.get_spending_by_category,
            "get_monthly_spending": self.get_monthly_spending,
            "get_top_merchants": self.get_top_merchants,
            "get_statistics": self.get_statistics,
            "get_budget_status": self.get_budget_status,
            "get_health_score": self.get_health_score,
            "get_recent_transactions": self.get_recent_transactions,
        }
    
    def get_total_spending(self, **kwargs) -> Dict:
        return self.analytics.get_total_spending(**kwargs)
    
    def get_spending_by_category(self, **kwargs) -> Dict:
        return self.analytics.get_spending_by_category(**kwargs)
    
    def get_monthly_spending(self, **kwargs) -> Dict:
        return self.analytics.get_monthly_spending(**kwargs)
    
    def get_top_merchants(self, **kwargs) -> Dict:
        return self.analytics.get_top_merchants(**kwargs)
    
    def get_statistics(self, **kwargs) -> Dict:
        return self.analytics.get_statistics(**kwargs)
    
    def get_budget_status(self, **kwargs) -> Dict:
        return self.analytics.get_budget_status(**kwargs)
    
    def get_health_score(self, **kwargs) -> Dict:
        return self.analytics.get_health_score(**kwargs)
    
    def get_recent_transactions(self, **kwargs) -> Dict:
        return self.transactions.get_recent_transactions(**kwargs)
    
    def get_tool_definitions(self) -> List[Dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_spending_by_category",
                    "description": "Get spending breakdown by category",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_total_spending",
                    "description": "Get total spending",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_top_merchants",
                    "description": "Get top merchants by spending",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Number of merchants to return"
                            }
                        },
                        "required": []
                    }
                }
            }
            # Add more tools as needed
        ]