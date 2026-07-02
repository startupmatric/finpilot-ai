from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta

from app.models import Transaction
from app.schemas.analytics import HealthScore
from app.services.analytics.statistics import get_statistics

def calculate_health_score(db: Session) -> HealthScore:
    """Calculate financial health score"""
    
    stats = get_statistics(db)
    
    if stats.total_transactions == 0:
        return HealthScore(
            score=0,
            savings_rate=0.0,
            spending_stability=0.0,
            income_stability=None,
            debt_ratio=None,
            components={},
            recommendations=["Start tracking your expenses to get health score"]
        )
    
    # 1. Savings Rate (30% weight)
    estimated_income = stats.total_spending * 1.5 if stats.total_spending > 0 else 0
    savings_rate = ((estimated_income - stats.total_spending) / estimated_income * 100) if estimated_income > 0 else 0
    savings_score = min(100, max(0, (savings_rate / 30) * 100))
    
    # 2. Spending Stability (25% weight)
    if stats.average_amount > 0:
        stability_score = max(0, 100 - (stats.std_deviation / stats.average_amount * 50))
        stability_score = min(100, stability_score)
    else:
        stability_score = 50
    
    # 3. Expense Consistency (20% weight)
    thirty_days_ago = date.today() - timedelta(days=30)
    daily_spending = db.query(
        func.date_trunc('day', Transaction.transaction_date).label('day'),
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.transaction_date >= thirty_days_ago
    ).group_by(
        func.date_trunc('day', Transaction.transaction_date)
    ).all()
    
    if daily_spending:
        amounts = [float(d[1]) for d in daily_spending if d[1] is not None]
        if amounts:
            avg_daily = sum(amounts) / len(amounts)
            consistent_days = sum(1 for a in amounts if 0.5 * avg_daily <= a <= 1.5 * avg_daily)
            consistency_score = (consistent_days / len(amounts)) * 100
        else:
            consistency_score = 50
    else:
        consistency_score = 50
    
    components = {
        'savings_rate': round(savings_score, 2),
        'spending_stability': round(stability_score, 2),
        'expense_consistency': round(consistency_score, 2),
        'income_stability': 70.0
    }
    
    weights = {
        'savings_rate': 0.30,
        'spending_stability': 0.25,
        'expense_consistency': 0.20,
        'income_stability': 0.25
    }
    
    final_score = sum(components[k] * weights.get(k, 0) for k in components.keys())
    final_score = round(final_score, 2)
    
    recommendations = []
    if savings_score < 60:
        recommendations.append("Try to increase your savings rate by reducing non-essential spending")
    if stability_score < 60:
        recommendations.append("Your spending varies significantly. Consider creating a budget.")
    if consistency_score < 60:
        recommendations.append("Your daily spending is inconsistent. Try to maintain a steady pace.")
    if final_score < 50:
        recommendations.append("Focus on building an emergency fund of 3-6 months of expenses")
    
    if not recommendations:
        recommendations.append("Great job! You're on track with your finances. Keep it up!")
    
    return HealthScore(
        score=int(final_score),
        savings_rate=round(savings_rate, 2),
        spending_stability=round(stability_score, 2),
        income_stability=70.0,
        debt_ratio=None,
        components=components,
        recommendations=recommendations
    )