from typing import Optional, Dict, List, Any  # ✅ Add these imports
from sqlalchemy.orm import Session
from datetime import date, datetime
from app.models import Transaction

class TransactionTools:
    """Tools for querying transactions"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_tool_definitions(self) -> List[Dict]:
        return [
            {
                "name": "get_recent_transactions",
                "description": "Get recent transactions. Use this for questions about recent spending.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Number of transactions to return"},
                        "category": {"type": "string", "description": "Filter by category"}
                    }
                }
            },
            {
                "name": "get_transactions_by_merchant",
                "description": "Get transactions for a specific merchant.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "merchant": {"type": "string", "description": "Merchant name"},
                        "limit": {"type": "integer", "description": "Number of transactions to return"}
                    }
                }
            }
        ]
    
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