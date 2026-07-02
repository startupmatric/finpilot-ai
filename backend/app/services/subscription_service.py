from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from collections import Counter

from app.models import Transaction

class SubscriptionService:
    """Detect and track recurring subscriptions"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def detect_subscriptions(self, months: int = 3) -> List[Dict[str, Any]]:
        """Detect recurring subscriptions from transaction history"""
        
        cutoff_date = datetime.now().date() - timedelta(days=months*30)
        
        merchant_counts = self.db.query(
            Transaction.merchant,
            func.count(Transaction.id).label('count'),
            func.avg(Transaction.amount).label('avg_amount'),
            func.max(Transaction.transaction_date).label('last_date'),
            func.min(Transaction.transaction_date).label('first_date')
        ).filter(
            Transaction.transaction_date >= cutoff_date
        ).group_by(
            Transaction.merchant
        ).having(
            func.count(Transaction.id) >= 2
        ).all()
        
        subscriptions = []
        
        for merchant, count, avg_amount, last_date, first_date in merchant_counts:
            amount_std = self._calculate_amount_std(merchant)
            frequency = self._detect_frequency(merchant, last_date, first_date, count)
            
            if frequency and amount_std < avg_amount * 0.15:
                subscriptions.append({
                    "merchant": merchant,
                    "amount": round(float(avg_amount), 2),
                    "frequency": frequency,
                    "last_charge": last_date.isoformat() if last_date else None,
                    "next_charge": self._calculate_next_charge(last_date, frequency) if last_date else None,
                    "confidence": self._calculate_confidence(count, amount_std)
                })
        
        return sorted(subscriptions, key=lambda x: x['amount'], reverse=True)
    
    def _calculate_amount_std(self, merchant: str) -> float:
        """Calculate standard deviation of amounts for a merchant"""
        amounts = self.db.query(Transaction.amount).filter(
            Transaction.merchant == merchant
        ).all()
        
        if len(amounts) < 2:
            return 0
        
        values = [float(a[0]) for a in amounts]
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _detect_frequency(self, merchant: str, last_date, first_date, count: int) -> str:
        """Detect the frequency of transactions"""
        if not last_date or not first_date or count < 2:
            return "Unknown"
        
        days_between = (last_date - first_date).days
        
        if count >= 3 and days_between / (count - 1) <= 35:
            return "Monthly"
        if count >= 4 and days_between / (count - 1) <= 10:
            return "Weekly"
        if count >= 2 and days_between / (count - 1) <= 100:
            return "Quarterly"
        
        return "Irregular"
    
    def _calculate_next_charge(self, last_date, frequency: str) -> str:
        """Calculate the next expected charge date"""
        if not last_date:
            return None
        
        if frequency == "Monthly":
            next_date = last_date + timedelta(days=30)
        elif frequency == "Weekly":
            next_date = last_date + timedelta(days=7)
        elif frequency == "Quarterly":
            next_date = last_date + timedelta(days=90)
        else:
            return None
        
        return next_date.isoformat()
    
    def _calculate_confidence(self, count: int, std_dev: float) -> float:
        """Calculate confidence score for subscription detection"""
        confidence = min(90, 50 + count * 10)
        if std_dev > 100:
            confidence -= 20
        return min(95, confidence)