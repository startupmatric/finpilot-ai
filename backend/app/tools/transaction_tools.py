from typing import Optional, Dict, List, Any
from sqlalchemy.orm import Session
from datetime import date, datetime

from app.models import Transaction

class TransactionTools:
    """Tools for querying transactions"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_recent_transactions(self, limit: int = 10, category: Optional[str] = None) -> Dict:
        """Get recent transactions"""
        query = self.db.query(Transaction).order_by(Transaction.transaction_date.desc())
        if category:
            query = query.filter(Transaction.category == category)
        transactions = query.limit(limit).all()
        
        return {
            "transactions": [
                {
                    "id": t.id,
                    "merchant": t.merchant,
                    "amount": t.amount,
                    "category": t.category,
                    "date": t.transaction_date.isoformat(),
                    "description": t.description
                } for t in transactions
            ]
        }
    
    def get_transactions_by_merchant(self, merchant: str, limit: int = 10) -> Dict:
        """Get transactions for a specific merchant"""
        transactions = self.db.query(Transaction).filter(
            Transaction.merchant.ilike(f"%{merchant}%")
        ).order_by(Transaction.transaction_date.desc()).limit(limit).all()
        
        return {
            "merchant": merchant,
            "transactions": [
                {
                    "id": t.id,
                    "amount": t.amount,
                    "category": t.category,
                    "date": t.transaction_date.isoformat(),
                    "description": t.description
                } for t in transactions
            ]
        }
    
    def get_transactions_by_date_range(self, start_date: date, end_date: date) -> Dict:
        """Get transactions within a date range"""
        transactions = self.db.query(Transaction).filter(
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        ).order_by(Transaction.transaction_date.desc()).all()
        
        return {
            "transactions": [
                {
                    "id": t.id,
                    "merchant": t.merchant,
                    "amount": t.amount,
                    "category": t.category,
                    "date": t.transaction_date.isoformat(),
                    "description": t.description
                } for t in transactions
            ],
            "total": len(transactions)
        }
    
    def get_transaction_summary(self) -> Dict:
        """Get a summary of all transactions"""
        total = self.db.query(Transaction).count()
        total_amount = self.db.query(
            self.db.query(Transaction.amount).subquery()
        ).with_entities(
            func.sum(Transaction.amount)
        ).scalar() or 0
        
        # Get date range
        date_range = self.db.query(
            func.min(Transaction.transaction_date),
            func.max(Transaction.transaction_date)
        ).first()
        
        return {
            "total_transactions": total,
            "total_amount": float(total_amount),
            "date_range": {
                "start": date_range[0].isoformat() if date_range[0] else None,
                "end": date_range[1].isoformat() if date_range[1] else None
            }
        }