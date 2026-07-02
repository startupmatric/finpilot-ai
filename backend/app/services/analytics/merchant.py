from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta

from app.models import Transaction
from app.schemas.analytics import MerchantSummary

def get_top_merchants(
    db: Session, 
    limit: int = 10,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[MerchantSummary]:
    """Get top merchants by spending"""
    query = db.query(
        Transaction.merchant,
        func.sum(Transaction.amount).label('total'),
        func.count(Transaction.id).label('count'),
        func.avg(Transaction.amount).label('average'),
        func.max(Transaction.transaction_date).label('last_date')
    )
    
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)
    
    results = query.group_by(Transaction.merchant).order_by(
        func.sum(Transaction.amount).desc()
    ).limit(limit).all()
    
    return [
        MerchantSummary(
            merchant=r[0],
            total=float(r[1]),
            transaction_count=r[2],
            average=float(r[3]) if r[3] else 0.0,
            last_transaction=r[4]
        ) for r in results
    ]

def get_merchant_total(
    db: Session, 
    merchant: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> float:
    """Get total spending for a specific merchant"""
    query = db.query(func.sum(Transaction.amount)).filter(
        Transaction.merchant.ilike(f"%{merchant}%")
    )
    
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)
    
    total = query.scalar()
    return float(total) if total else 0.0

def get_merchant_history(
    db: Session,
    merchant: str,
    months: int = 6
) -> List[Dict]:
    """Get monthly history for a specific merchant"""
    from sqlalchemy import func
    
    results = db.query(
        func.date_trunc('month', Transaction.transaction_date).label('month'),
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.merchant.ilike(f"%{merchant}%")
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
            "total": float(r[1])
        } for r in results
    ]