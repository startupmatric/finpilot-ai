from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
import statistics

from app.models import Transaction
from app.schemas.analytics import StatisticsSummary

def get_statistics(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> StatisticsSummary:
    """Get comprehensive statistics for all transactions"""
    
    query = db.query(Transaction)
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)
    
    amounts = [float(r[0]) for r in query.with_entities(Transaction.amount).all()]
    
    if not amounts:
        return StatisticsSummary(
            total_transactions=0,
            total_spending=0.0,
            average_amount=0.0,
            median_amount=0.0,
            largest_amount=0.0,
            smallest_amount=0.0,
            std_deviation=0.0,
            date_range={"start": None, "end": None}
        )
    
    date_range = query.with_entities(
        func.min(Transaction.transaction_date),
        func.max(Transaction.transaction_date)
    ).first()
    
    return StatisticsSummary(
        total_transactions=len(amounts),
        total_spending=sum(amounts),
        average_amount=round(statistics.mean(amounts), 2),
        median_amount=round(statistics.median(amounts), 2),
        largest_amount=round(max(amounts), 2),
        smallest_amount=round(min(amounts), 2),
        std_deviation=round(statistics.stdev(amounts), 2) if len(amounts) > 1 else 0.0,
        date_range={
            "start": date_range[0],
            "end": date_range[1]
        }
    )