from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta

from app.models import Transaction
from app.schemas.analytics import MonthlySummary

def get_monthly_summary(db: Session, months: int = 12) -> List[MonthlySummary]:
    """Get monthly spending summary"""
    start_date = date.today() - timedelta(days=months*31)
    
    results = db.query(
        func.date_trunc('month', Transaction.transaction_date).label('month'),
        func.sum(Transaction.amount).label('total'),
        func.count(Transaction.id).label('count'),
        func.avg(Transaction.amount).label('average')
    ).filter(
        Transaction.transaction_date >= start_date
    ).group_by(
        func.date_trunc('month', Transaction.transaction_date)
    ).order_by(
        func.date_trunc('month', Transaction.transaction_date)
    ).all()
    
    summaries = []
    previous_total = None
    
    for month, total, count, avg in results:
        growth = None
        if previous_total is not None and previous_total > 0:
            growth = ((float(total) - previous_total) / previous_total) * 100
        
        summaries.append(MonthlySummary(
            month=month.strftime("%Y-%m"),
            total=float(total),
            transaction_count=count,
            average_per_transaction=float(avg) if avg else 0.0,
            growth_from_previous=round(growth, 2) if growth is not None else None
        ))
        previous_total = float(total)
    
    return summaries

def get_monthly_growth(db: Session) -> Dict[str, float]:
    """Calculate month-over-month growth rates"""
    summaries = get_monthly_summary(db, months=12)
    
    growth_rates = {}
    for i in range(1, len(summaries)):
        current = summaries[i]
        previous = summaries[i-1]
        
        if previous.total > 0:
            growth = ((current.total - previous.total) / previous.total) * 100
            growth_rates[current.month] = round(growth, 2)
    
    return growth_rates

def get_monthly_average(db: Session, months: int = 12) -> float:
    """Get average monthly spending"""
    summaries = get_monthly_summary(db, months)
    if not summaries:
        return 0.0
    
    total = sum(s.total for s in summaries)
    return round(total / len(summaries), 2)