from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, Index, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    merchant = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    amount = Column(Float, nullable=False)
    category = Column(String(100), nullable=False)
    transaction_date = Column(Date, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True,  # ✅ Make this nullable
        onupdate=func.now()
    )
    
    __table_args__ = (
        Index('idx_transaction_date', 'transaction_date'),
        Index('idx_category', 'category'),
        Index('idx_merchant', 'merchant'),
        Index('idx_user_id', 'user_id'),
    )
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, merchant='{self.merchant}', amount={self.amount})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "merchant": self.merchant,
            "description": self.description,
            "amount": self.amount,
            "category": self.category,
            "transaction_date": self.transaction_date.isoformat() if self.transaction_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }