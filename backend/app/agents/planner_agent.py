from typing import Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.services.analytics import spending as spending_service

class FinancialPlannerAgent:
    """Agent that helps users achieve financial goals"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_plan(self, goal: str, target_amount: float, timeframe_months: int) -> Dict[str, Any]:
        """Create a financial plan to achieve a goal"""
        
        # Calculate required monthly savings
        monthly_savings = target_amount / timeframe_months
        
        # Get current spending
        total_spending = spending_service.get_total_spending(self.db)
        
        # Get category breakdown for suggestions
        category_spending = spending_service.get_spending_by_category(self.db)
        
        # Identify areas for reduction
        savings_areas = []
        for cat in category_spending.summary[:3]:
            if cat.total > 1000:
                potential = cat.total * 0.15
                savings_areas.append({
                    "category": cat.category,
                    "current_spending": cat.total,
                    "potential_savings": potential,
                    "percentage_reduction": 15
                })
        
        # Create monthly plan
        monthly_plan = {
            "monthly_savings_needed": monthly_savings,
            "months": timeframe_months,
            "target": target_amount,
            "current_spending": total_spending,
            "savings_opportunities": savings_areas,
            "weekly_tasks": self._generate_weekly_tasks(savings_areas, monthly_savings),
            "milestones": self._generate_milestones(target_amount, timeframe_months)
        }
        
        return {
            "goal": goal,
            "target_amount": target_amount,
            "timeframe_months": timeframe_months,
            "plan": monthly_plan
        }
    
    def _generate_weekly_tasks(self, savings_areas: List, monthly_savings: float) -> List[Dict]:
        tasks = []
        for area in savings_areas[:2]:
            tasks.append({
                "task": f"Reduce {area['category']} spending by {area['percentage_reduction']}%",
                "saving": area['potential_savings'],
                "frequency": "weekly"
            })
        return tasks
    
    def _generate_milestones(self, target: float, months: int) -> List[Dict]:
        milestones = []
        for month in range(1, months + 1, 3):
            milestones.append({
                "month": month,
                "target": round(target * (month / months), 2),
                "description": f"Reach {round(target * (month / months) / 1000)}K by month {month}"
            })
        return milestones