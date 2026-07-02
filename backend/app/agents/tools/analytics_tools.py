
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import date, datetime
import json

from app.services.analytics import (
    spending as spending_service,
    merchant as merchant_service,
    monthly as monthly_service,
    statistics as statistics_service,
    budget as budget_service,
    health_score as health_score_service
)

class AnalyticsTools:
    """Tools for querying financial analytics"""
    
    def __init__(self, db: Session):
        self.db = db
        self.tools = {
            "get_total_spending": self.get_total_spending,
            "get_spending_by_category": self.get_spending_by_category,
            "get_monthly_spending": self.get_monthly_spending,
            "get_top_merchants": self.get_top_merchants,
            "get_statistics": self.get_statistics,
            "get_budget_status": self.get_budget_status,
            "get_health_score": self.get_health_score,
            "get_category_breakdown": self.get_category_breakdown,
        }
    
    def get_tool_definitions(self):
        """Return tool definitions for LangGraph"""
        return [
            {
                "name": "get_total_spending",
                "description": "Get total spending for a date range. Use this to answer questions about total expenses.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                        "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"}
                    }
                }
            },
            {
                "name": "get_spending_by_category",
                "description": "Get spending breakdown by category. Use this to answer questions about spending in specific categories.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                        "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"}
                    }
                }
            },
            {
                "name": "get_monthly_spending",
                "description": "Get monthly spending trends. Use this to answer questions about spending over time.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "months": {"type": "integer", "description": "Number of months to analyze"}
                    }
                }
            },
            {
                "name": "get_top_merchants",
                "description": "Get top merchants by spending. Use this to answer questions about where money is being spent.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Number of merchants to return"}
                    }
                }
            },
            {
                "name": "get_statistics",
                "description": "Get comprehensive statistics about transactions. Use this for general spending questions.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_budget_status",
                "description": "Get current budget status. Use this for budget-related questions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "budget": {"type": "number", "description": "Monthly budget amount"}
                    }
                }
            },
            {
                "name": "get_health_score",
                "description": "Get financial health score. Use this for questions about financial wellness.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_category_breakdown",
                "description": "Get detailed category breakdown with percentages. Use this for detailed spending analysis.",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    
    def get_total_spending(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict:
        """Get total spending"""
        start = date.fromisoformat(start_date) if start_date else None
        end = date.fromisoformat(end_date) if end_date else None
        total = spending_service.get_total_spending(self.db, start, end)
        return {"total_spending": total, "currency": "INR"}
    
    def get_spending_by_category(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict:
        """Get spending by category"""
        start = date.fromisoformat(start_date) if start_date else None
        end = date.fromisoformat(end_date) if end_date else None
        result = spending_service.get_spending_by_category(self.db, start, end)
        return {
            "summary": [s.model_dump() for s in result.summary],
            "total_spending": result.total_spending,
            "currency": "INR"
        }
    
    def get_monthly_spending(self, months: int = 6) -> Dict:
        """Get monthly spending trends"""
        result = spending_service.get_monthly_spending(self.db, months)
        return {"monthly_data": result, "currency": "INR"}
    
    def get_top_merchants(self, limit: int = 5) -> Dict:
        """Get top merchants"""
        result = merchant_service.get_top_merchants(self.db, limit)
        return {"merchants": [m.model_dump() for m in result], "currency": "INR"}
    
    def get_statistics(self) -> Dict:
        """Get transaction statistics"""
        result = statistics_service.get_statistics(self.db)
        return {"statistics": result.model_dump()}
    
    def get_budget_status(self, budget: Optional[float] = None) -> Dict:
        """Get budget status"""
        result = budget_service.get_budget_status(self.db, budget)
        return {"budget_status": result.model_dump()}
    
    def get_health_score(self) -> Dict:
        """Get financial health score"""
        result = health_score_service.calculate_health_score(self.db)
        return {"health_score": result.model_dump()}
    
    def get_category_breakdown(self) -> Dict:
        """Get detailed category breakdown"""
        result = spending_service.get_spending_by_category(self.db)
        return {
            "category_breakdown": [s.model_dump() for s in result.summary],
            "total": result.total_spending,
            "currency": "INR"
        }