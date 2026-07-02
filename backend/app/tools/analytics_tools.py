from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from datetime import date

from app.services.analytics import (
    spending as spending_service,
    merchant as merchant_service,
    monthly as monthly_service,
    statistics as statistics_service,
    budget as budget_service,
    health_score as health_score_service
)

class AnalyticsTools:
    """Exposed tools for agents to call"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_total_spending(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict:
        """Get total spending for a date range"""
        total = spending_service.get_total_spending(self.db, start_date, end_date)
        return {"total_spending": total, "currency": "INR"}
    
    def get_spending_by_category(self) -> Dict:
        """Get spending breakdown by category"""
        result = spending_service.get_spending_by_category(self.db)
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
        """Get top merchants by spending"""
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
        """Get detailed category breakdown with percentages"""
        result = spending_service.get_spending_by_category(self.db)
        return {
            "category_breakdown": [s.model_dump() for s in result.summary],
            "total": result.total_spending,
            "currency": "INR"
        }