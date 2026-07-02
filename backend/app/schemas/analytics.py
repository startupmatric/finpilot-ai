from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime, date

class CategorySummary(BaseModel):
    """Spending breakdown by category"""
    category: str
    total: float
    percentage: float
    transaction_count: int

class CategorySpendingResponse(BaseModel):
    """Response for category spending"""
    summary: List[CategorySummary]
    total_spending: float
    period: str  # 'all', 'month', 'week', 'day'

class MerchantSummary(BaseModel):
    """Merchant spending summary"""
    merchant: str
    total: float
    transaction_count: int
    average: float
    last_transaction: Optional[date]

class MonthlySummary(BaseModel):
    """Monthly spending summary"""
    month: str  # Format: "YYYY-MM"
    total: float
    transaction_count: int
    average_per_transaction: float
    growth_from_previous: Optional[float]

class BudgetStatus(BaseModel):
    """Budget tracking status"""
    budget: float
    spent: float
    remaining: float
    percentage_used: float
    days_remaining: int
    daily_allowance: float
    on_track: bool

class StatisticsSummary(BaseModel):
    """Statistical summary of all transactions"""
    total_transactions: int
    total_spending: float
    average_amount: float
    median_amount: float
    largest_amount: float
    smallest_amount: float
    std_deviation: float
    date_range: Dict[str, Optional[date]]

class HealthScore(BaseModel):
    """Financial health score"""
    score: int = Field(..., ge=0, le=100, description="Overall health score out of 100")
    savings_rate: float
    spending_stability: float
    income_stability: Optional[float]
    debt_ratio: Optional[float]
    components: Dict[str, float]
    recommendations: List[str]

class DailySpending(BaseModel):
    """Daily spending breakdown"""
    date: date
    total: float
    transaction_count: int
    categories: Dict[str, float]