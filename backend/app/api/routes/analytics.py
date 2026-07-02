from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, datetime

from app.database import get_db
from app.services.analytics import (
    spending as spending_service,
    merchant as merchant_service,
    monthly as monthly_service,
    statistics as statistics_service,
    budget as budget_service,
    health_score as health_score_service
)
from app.schemas.analytics import (
    CategorySpendingResponse,
    MerchantSummary,
    MonthlySummary,
    StatisticsSummary,
    BudgetStatus,
    HealthScore
)

# NEW SERVICES
from app.services.coach_service import CoachService
from app.services.subscription_service import SubscriptionService
from app.services.forecast_service import ForecastService

router = APIRouter()

# ============ Spending Analytics ============
@router.get("/analytics/spending/total", response_model=dict)
def get_total_spending(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get total spending for a date range"""
    total = spending_service.get_total_spending(db, start_date, end_date)
    return {
        "total_spending": total,
        "start_date": start_date,
        "end_date": end_date
    }

@router.get("/analytics/spending/category", response_model=CategorySpendingResponse)
def get_spending_by_category(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get spending breakdown by category"""
    return spending_service.get_spending_by_category(db, start_date, end_date)

@router.get("/analytics/spending/daily")
def get_daily_spending(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get daily spending for the last N days"""
    return spending_service.get_daily_spending(db, days)

@router.get("/analytics/spending/monthly")
def get_monthly_spending(
    months: int = Query(12, ge=1, le=36),
    db: Session = Depends(get_db)
):
    """Get monthly spending for the last N months"""
    return spending_service.get_monthly_spending(db, months)

# ============ Merchant Analytics ============
@router.get("/analytics/merchant/top", response_model=List[MerchantSummary])
def get_top_merchants(
    limit: int = Query(10, ge=1, le=50),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get top merchants by spending"""
    return merchant_service.get_top_merchants(db, limit, start_date, end_date)

@router.get("/analytics/merchant/{merchant}/total")
def get_merchant_total(
    merchant: str,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get total spending for a specific merchant"""
    total = merchant_service.get_merchant_total(db, merchant, start_date, end_date)
    return {
        "merchant": merchant,
        "total_spending": total,
        "start_date": start_date,
        "end_date": end_date
    }

@router.get("/analytics/merchant/{merchant}/history")
def get_merchant_history(
    merchant: str,
    months: int = Query(6, ge=1, le=24),
    db: Session = Depends(get_db)
):
    """Get monthly history for a specific merchant"""
    return merchant_service.get_merchant_history(db, merchant, months)

# ============ Monthly Analytics ============
@router.get("/analytics/monthly/summary", response_model=List[MonthlySummary])
def get_monthly_summary(
    months: int = Query(12, ge=1, le=36),
    db: Session = Depends(get_db)
):
    """Get monthly spending summary"""
    return monthly_service.get_monthly_summary(db, months)

@router.get("/analytics/monthly/growth")
def get_monthly_growth(
    db: Session = Depends(get_db)
):
    """Get month-over-month growth rates"""
    return monthly_service.get_monthly_growth(db)

@router.get("/analytics/monthly/average")
def get_monthly_average(
    months: int = Query(12, ge=1, le=36),
    db: Session = Depends(get_db)
):
    """Get average monthly spending"""
    average = monthly_service.get_monthly_average(db, months)
    return {
        "average_monthly_spending": average,
        "months_analyzed": months
    }

# ============ Statistics ============
@router.get("/analytics/statistics", response_model=StatisticsSummary)
def get_statistics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get comprehensive statistics for all transactions"""
    return statistics_service.get_statistics(db, start_date, end_date)

# ============ Budget ============
@router.get("/analytics/budget", response_model=BudgetStatus)
def get_budget_status(
    budget: Optional[float] = Query(None, description="Monthly budget amount"),
    month: Optional[date] = Query(None, description="Month to analyze (default: current month)"),
    db: Session = Depends(get_db)
):
    """Get current budget status"""
    return budget_service.get_budget_status(db, budget, month)

# ============ Health Score ============
@router.get("/analytics/health", response_model=HealthScore)
def get_health_score(
    db: Session = Depends(get_db)
):
    """Get financial health score"""
    return health_score_service.calculate_health_score(db)

# ====================================================
# ============ NEW ENDPOINTS ==========================
# ====================================================

@router.get("/analytics/coach/weekly")
def get_weekly_coaching(
    db: Session = Depends(get_db)
):
    """
    Get personalized weekly financial coaching report.
    
    Returns:
    - Financial health score
    - Spending breakdown
    - Insights and recommendations
    - Savings opportunities
    - Natural language summary
    """
    coach = CoachService(db)
    return coach.generate_weekly_report()

@router.get("/analytics/subscriptions")
def get_subscriptions(
    months: int = Query(3, ge=1, le=12, description="Number of months to analyze"),
    db: Session = Depends(get_db)
):
    """
    Detect recurring subscriptions from transaction history.
    
    Returns:
    - Merchant name
    - Amount
    - Frequency (Monthly, Weekly, Quarterly)
    - Last charge date
    - Next expected charge
    - Confidence score
    """
    service = SubscriptionService(db)
    return service.detect_subscriptions(months)

@router.get("/analytics/forecast/monthly")
def get_monthly_forecast(
    db: Session = Depends(get_db)
):
    """
    Get monthly spending forecast.
    
    Returns:
    - Current month spending progress
    - Projected total spending
    - Average daily spending
    - Remaining daily allowance
    - Trend comparison
    - Confidence score
    """
    service = ForecastService(db)
    return service.forecast_monthly()

@router.get("/analytics/forecast/category/{category}")
def get_category_forecast(
    category: str,
    db: Session = Depends(get_db)
):
    """
    Get category-specific spending forecast.
    
    Returns:
    - Current spending in category
    - Projected total spending
    - Remaining budget for category
    - Historical average comparison
    """
    service = ForecastService(db)
    return service.forecast_category(category)

@router.get("/analytics/forecast/cashflow")
def get_cashflow_forecast(
    budget: float = Query(50000, description="Monthly budget"),
    db: Session = Depends(get_db)
):
    """
    Get cashflow forecast.
    
    Returns:
    - Budget amount
    - Projected spending
    - Projected remaining
    - Status (good/warning/critical)
    - Daily burn rate
    - Suggestions
    """
    service = ForecastService(db)
    return service.forecast_cashflow(budget)

@router.get("/analytics/forecast/categories")
def get_all_category_forecasts(
    db: Session = Depends(get_db)
):
    """
    Get forecasts for all categories.
    """
    service = ForecastService(db)
    
    from app.models import Transaction
    categories = db.query(Transaction.category).distinct().all()
    categories = [c[0] for c in categories]
    
    forecasts = {}
    for category in categories:
        forecasts[category] = service.forecast_category(category)
    
    return {
        "categories": forecasts,
        "total_forecast": sum(f["forecast"] for f in forecasts.values())
    }

@router.get("/analytics/ping")
def analytics_ping():
    """Test route to verify analytics router is working"""
    return {
        "status": "ok",
        "message": "Analytics router is working!",
        "available_routes": [
            "/analytics/spending/total",
            "/analytics/spending/category",
            "/analytics/spending/daily",
            "/analytics/spending/monthly",
            "/analytics/merchant/top",
            "/analytics/merchant/{merchant}/total",
            "/analytics/merchant/{merchant}/history",
            "/analytics/monthly/summary",
            "/analytics/monthly/growth",
            "/analytics/monthly/average",
            "/analytics/statistics",
            "/analytics/budget",
            "/analytics/health",
            "/analytics/coach/weekly",
            "/analytics/subscriptions",
            "/analytics/forecast/monthly",
            "/analytics/forecast/category/{category}",
            "/analytics/forecast/cashflow",
            "/analytics/forecast/categories"
        ]
    }