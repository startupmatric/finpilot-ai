from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.models import Transaction
from app.schemas import TransactionResponse
from app.auth.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/transactions", response_model=List[TransactionResponse])
def get_transactions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    merchant: Optional[str] = Query(None, description="Filter by merchant (partial match)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    start_date: Optional[date] = Query(None, description="Filter transactions from this date"),
    end_date: Optional[date] = Query(None, description="Filter transactions up to this date"),
    min_amount: Optional[float] = Query(None, ge=0, description="Minimum amount filter"),
    max_amount: Optional[float] = Query(None, ge=0, description="Maximum amount filter"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # ✅ User authentication
):
    """
    Get all transactions for the authenticated user with optional filters.
    """
    # ✅ Filter by current user
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)
    
    if merchant:
        query = query.filter(Transaction.merchant.ilike(f"%{merchant}%"))
    if category:
        query = query.filter(Transaction.category == category)
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)
    if min_amount is not None:
        query = query.filter(Transaction.amount >= min_amount)
    if max_amount is not None:
        query = query.filter(Transaction.amount <= max_amount)
    
    query = query.order_by(Transaction.transaction_date.desc())
    transactions = query.offset(skip).limit(limit).all()
    
    return transactions

@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # ✅ User authentication
):
    """
    Get a single transaction by ID for the authenticated user.
    """
    # ✅ Filter by current user
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return transaction

@router.get("/categories", response_model=List[str])
def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # ✅ User authentication
):
    """
    Get all unique categories for the authenticated user.
    """
    # ✅ Filter by current user
    categories = db.query(Transaction.category).distinct().filter(
        Transaction.user_id == current_user.id
    ).all()
    return [c[0] for c in categories]