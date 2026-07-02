from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta

from app.models import Transaction
from app.schemas.analytics import CategorySummary, CategorySpendingResponse

def get_total_spending(db: Session, start_date: Optional[date] = None, end_date: Optional[date] = None) -> float:
    """Get total spending for a date range"""
    query = db.query(Transaction)
    
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)
    
    total = query.with_entities(func.sum(Transaction.amount)).scalar()
    return float(total) if total else 0.0

def get_spending_by_category(
    db: Session, 
    start_date: Optional[date] = None, 
    end_date: Optional[date] = None
) -> CategorySpendingResponse:
    """Get spending breakdown by category"""
    query = db.query(
        Transaction.category,
        func.sum(Transaction.amount).label('total'),
        func.count(Transaction.id).label('count')
    )
    
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)
    
    results = query.group_by(Transaction.category).all()
    
    total_spending = get_total_spending(db, start_date, end_date)
    
    summary = []
    for category, total, count in results:
        percentage = (float(total) / total_spending * 100) if total_spending > 0 else 0
        summary.append(CategorySummary(
            category=category,
            total=float(total),
            percentage=round(percentage, 2),
            transaction_count=count
        ))
    
    summary.sort(key=lambda x: x.total, reverse=True)
    
    return CategorySpendingResponse(
        summary=summary,
        total_spending=total_spending,
        period="all"
    )

def get_daily_spending(
    db: Session, 
    days: int = 30
) -> List[Dict]:
    """Get daily spending for the last N days"""
    start_date = date.today() - timedelta(days=days)
    
    results = db.query(
        Transaction.transaction_date,
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.transaction_date >= start_date
    ).group_by(
        Transaction.transaction_date
    ).order_by(
        Transaction.transaction_date
    ).all()
    
    return [
        {
            "date": r[0].isoformat(),
            "total": float(r[1])
        } for r in results
    ]

def get_weekly_spending(db: Session, weeks: int = 12) -> List[Dict]:
    """Get weekly spending for the last N weeks"""
    results = db.query(
        func.date_trunc('week', Transaction.transaction_date).label('week'),
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.transaction_date >= date.today() - timedelta(weeks=weeks)
    ).group_by(
        func.date_trunc('week', Transaction.transaction_date)
    ).order_by(
        func.date_trunc('week', Transaction.transaction_date)
    ).all()
    
    return [
        {
            "week": r[0].strftime("%Y-%W"),
            "week_start": r[0].date().isoformat(),
            "total": float(r[1])
        } for r in results
    ]

def get_monthly_spending(db: Session, months: int = 12) -> List[Dict]:
    """Get monthly spending for the last N months"""
    results = db.query(
        func.date_trunc('month', Transaction.transaction_date).label('month'),
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.transaction_date >= date.today() - timedelta(days=months*30)
    ).group_by(
        func.date_trunc('month', Transaction.transaction_date)
    ).order_by(
        func.date_trunc('month', Transaction.transaction_date)
    ).all()
    
    return [
        {
            "month": r[0].strftime("%Y-%m"),
            "month_name": r[0].strftime("%B %Y"),
            "total": float(r[1])
        } for r in results
    ]