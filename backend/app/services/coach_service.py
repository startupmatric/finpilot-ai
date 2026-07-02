from typing import Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.services.analytics import (
    spending as spending_service,
    merchant as merchant_service,
    statistics as statistics_service,
    budget as budget_service,
    health_score as health_score_service
)
from app.llm.groq_client import groq_client

class CoachService:
    """Service that generates personalized financial coaching"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_weekly_report(self) -> Dict[str, Any]:
        """Generate a comprehensive weekly financial report"""
        
        # Gather all analytics
        stats = statistics_service.get_statistics(self.db)
        category_spending = spending_service.get_spending_by_category(self.db)
        top_merchants = merchant_service.get_top_merchants(self.db, limit=5)
        health = health_score_service.calculate_health_score(self.db)
        budget = budget_service.get_budget_status(self.db)
        
        # Calculate insights
        insights = self._generate_insights(category_spending, stats, health)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            category_spending, top_merchants, budget, health
        )
        
        # Build the report
        report = {
            "period": "weekly",
            "date": datetime.now().isoformat(),
            "health_score": health.score,
            "total_spending": stats.total_spending,
            "transaction_count": stats.total_transactions,
            "average_transaction": stats.average_amount,
            "top_expense": {
                "merchant": top_merchants[0].merchant if top_merchants else None,
                "amount": top_merchants[0].total if top_merchants else 0
            },
            "category_breakdown": [
                {
                    "category": c.category,
                    "amount": c.total,
                    "percentage": c.percentage
                } for c in category_spending.summary[:3]
            ],
            "budget_status": {
                "spent": budget.spent,
                "remaining": budget.remaining,
                "percentage_used": budget.percentage_used
            },
            "insights": insights,
            "recommendations": recommendations,
            "savings_opportunities": self._calculate_savings_opportunities(
                category_spending, top_merchants
            )
        }
        
        # Generate natural language summary
        report["summary"] = self._generate_summary(report)
        
        return report
    
    def _generate_insights(self, category_spending, stats, health) -> list:
        """Generate insights from the data"""
        insights = []
        
        # Category insight
        if category_spending.summary:
            top = category_spending.summary[0]
            insights.append(f"Your largest spending category is {top.category} at ₹{top.total:,.2f} ({top.percentage}%)")
        
        # Health insight
        if health.score > 70:
            insights.append(f"Your financial health score of {health.score}/100 is good, but there's room for improvement")
        elif health.score > 50:
            insights.append(f"Your financial health score of {health.score}/100 is average. Focus on reducing discretionary spending")
        else:
            insights.append(f"Your financial health score of {health.score}/100 needs attention. Consider creating a budget")
        
        # Spending insight
        if stats.total_transactions > 0:
            if stats.average_amount > 1000:
                insights.append(f"Your average transaction of ₹{stats.average_amount:,.2f} is relatively high")
            else:
                insights.append(f"Your average transaction of ₹{stats.average_amount:,.2f} is reasonable")
        
        return insights
    
    def _generate_recommendations(self, category_spending, top_merchants, budget, health) -> list:
        """Generate personalized recommendations"""
        recommendations = []
        
        # Category-based recommendations
        for cat in category_spending.summary[:2]:
            if cat.percentage > 40:
                recommendations.append(
                    f"Your spending on {cat.category} is {cat.percentage}% of total. Consider reducing it by 10-15%"
                )
        
        # Merchant-based recommendations
        for merchant in top_merchants[:2]:
            if merchant.total > 2000:
                recommendations.append(
                    f"You've spent ₹{merchant.total:,.2f} at {merchant.merchant}. Consider alternatives or reducing frequency"
                )
        
        # Budget recommendations
        if budget.percentage_used > 70:
            recommendations.append(
                f"You've used {budget.percentage_used}% of your budget. Be mindful of remaining spending"
            )
        elif budget.percentage_used < 30:
            recommendations.append(
                f"You're on track! Only {budget.percentage_used}% of your budget used. Keep it up!"
            )
        
        # Health recommendations
        if health.score < 60:
            recommendations.extend(health.recommendations[:2])
        
        return recommendations[:5]
    
    def _calculate_savings_opportunities(self, category_spending, top_merchants) -> list:
        """Identify specific savings opportunities"""
        opportunities = []
        
        for cat in category_spending.summary:
            if cat.category in ["Food & Dining", "Shopping"] and cat.total > 1000:
                savings = cat.total * 0.15
                opportunities.append({
                    "area": cat.category,
                    "current": cat.total,
                    "potential_savings": savings,
                    "suggestion": f"Reduce {cat.category} spending by 15% to save ₹{savings:,.2f} monthly"
                })
        
        for merchant in top_merchants[:2]:
            if merchant.total > 1500:
                opportunities.append({
                    "area": f"{merchant.merchant} spending",
                    "current": merchant.total,
                    "potential_savings": merchant.total * 0.2,
                    "suggestion": f"Reduce {merchant.merchant} spending by 20% to save ₹{merchant.total * 0.2:,.2f}"
                })
        
        return opportunities[:3]
    
    def _generate_summary(self, report: dict) -> str:
        """Generate a natural language summary"""
        
        if not groq_client.is_available():
            return "Weekly financial report ready. Check the data below for insights."
        
        prompt = f"""
        Create a friendly, encouraging weekly financial summary based on this data:
        
        Health Score: {report['health_score']}/100
        Total Spending: ₹{report['total_spending']:,.2f}
        Transactions: {report['transaction_count']}
        Average Transaction: ₹{report['average_transaction']:,.2f}
        Top Expense: {report['top_expense']['merchant']} - ₹{report['top_expense']['amount']:,.2f}
        
        Top Categories:
        {chr(10).join([f"- {c['category']}: ₹{c['amount']:,.2f} ({c['percentage']}%)" for c in report['category_breakdown']])}
        
        Budget Status: {report['budget_status']['percentage_used']}% used, ₹{report['budget_status']['remaining']:,.2f} remaining
        
        Insights:
        {chr(10).join([f"- {i}" for i in report['insights']])}
        
        Recommendations:
        {chr(10).join([f"- {r}" for r in report['recommendations']])}
        
        Write a brief, encouraging summary (3-4 sentences) for the user.
        """
        
        try:
            return groq_client.generate_response(
                "You are a friendly financial coach. Be encouraging and specific.",
                prompt
            )
        except:
            return f"Your weekly report shows healthy spending patterns with a health score of {report['health_score']}/100. You've spent ₹{report['total_spending']:,.2f} this week. Keep up the good habits!"