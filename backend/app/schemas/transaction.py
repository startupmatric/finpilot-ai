from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional

class TransactionBase(BaseModel):
    merchant: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    amount: float = Field(..., gt=0)
    category: str = Field(..., min_length=1, max_length=100)
    transaction_date: date

class TransactionCreate(TransactionBase):
    user_id: int  # ✅ Add this

class TransactionUpdate(BaseModel):
    merchant: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    transaction_date: Optional[date] = None

class TransactionResponse(TransactionBase):
    id: int
    user_id: int  # ✅ Add this
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True