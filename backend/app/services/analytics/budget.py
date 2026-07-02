from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta

from app.models import Transaction
from app.schemas.analytics import BudgetStatus

DEFAULT_MONTHLY_BUDGET = 50000.0

def get_budget_status(
    db: Session,
    budget: Optional[float] = None,
    month: Optional[date] = None
) -> BudgetStatus:
    """Get current budget status"""
    
    if budget is None:
        budget = DEFAULT_MONTHLY_BUDGET
    
    if month is None:
        month = date.today()
    
    month_start = date(month.year, month.month, 1)
    if month.month == 12:
        month_end = date(month.year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = date(month.year, month.month + 1, 1) - timedelta(days=1)
    
    total_spent = db.query(func.sum(Transaction.amount)).filter(
        Transaction.transaction_date >= month_start,
        Transaction.transaction_date <= month_end
    ).scalar() or 0.0
    
    remaining = budget - total_spent
    
    today = date.today()
    days_in_month = (month_end - month_start).days + 1
    days_remaining = (month_end - today).days if today <= month_end else 0
    
    daily_allowance = remaining / days_remaining if days_remaining > 0 else 0.0
    
    return BudgetStatus(
        budget=budget,
        spent=float(total_spent),
        remaining=float(remaining),
        percentage_used=round((total_spent / budget * 100) if budget > 0 else 0, 2),
        days_remaining=max(0, days_remaining),
        daily_allowance=round(daily_allowance, 2),
        on_track=remaining >= 0
    )