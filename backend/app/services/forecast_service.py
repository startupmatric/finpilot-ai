from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date, timedelta
import statistics

from app.models import Transaction
from app.services.analytics.spending import get_total_spending

class ForecastService:
    """Predict future spending using statistical methods"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def forecast_monthly(self) -> Dict[str, Any]:
        """Forecast end-of-month spending"""
        
        today = date.today()
        month_start = date(today.year, today.month, 1)
        current_spent = get_total_spending(self.db, month_start, today)
        
        last_3_months = self._get_average_monthly_spending(3)
        
        day_of_month = today.day
        
        # If no data for current month, use historical average
        if current_spent == 0 and last_3_months > 0:
            days_in_month = self._days_in_month(today)
            daily_average = last_3_months / 30  # Approximate daily average
            projected = daily_average * days_in_month
            
            return {
                "current_month": {
                    "month": today.strftime("%B %Y"),
                    "spent_so_far": 0.0,
                    "days_elapsed": day_of_month,
                    "days_remaining": days_in_month - day_of_month,
                    "note": "No transactions this month yet. Using historical average."
                },
                "forecast": {
                    "projected_total": round(projected, 2),
                    "average_daily_spending": round(daily_average, 2),
                    "remaining_daily_allowed": round(daily_average, 2),
                    "confidence": 60
                },
                "comparison": {
                    "last_3_months_average": round(last_3_months, 2),
                    "difference": 0,
                    "trend": "stable"
                }
            }
        
        # If no data at all
        if current_spent == 0 and last_3_months == 0:
            return {
                "current_month": {
                    "month": today.strftime("%B %Y"),
                    "spent_so_far": 0.0,
                    "days_elapsed": day_of_month,
                    "days_remaining": self._days_in_month(today) - day_of_month,
                    "note": "No transaction data available. Upload some transactions first."
                },
                "forecast": {
                    "projected_total": 0.0,
                    "average_daily_spending": 0.0,
                    "remaining_daily_allowed": 0.0,
                    "confidence": 0
                },
                "comparison": {
                    "last_3_months_average": 0.0,
                    "difference": 0.0,
                    "trend": "no_data"
                }
            }
        
        # Normal case - have current month data
        daily_average = current_spent / day_of_month if day_of_month > 0 else 0
        days_in_month = self._days_in_month(today)
        projected_monthly = daily_average * days_in_month
        
        # Adjust with seasonality
        if last_3_months > 0 and current_spent > 0:
            expected_daily = last_3_months / 30
            if expected_daily > 0:
                seasonality_factor = daily_average / expected_daily
                adjusted_forecast = projected_monthly * seasonality_factor
            else:
                adjusted_forecast = projected_monthly
        else:
            adjusted_forecast = projected_monthly
        
        return {
            "current_month": {
                "month": today.strftime("%B %Y"),
                "spent_so_far": round(current_spent, 2),
                "days_elapsed": day_of_month,
                "days_remaining": days_in_month - day_of_month
            },
            "forecast": {
                "projected_total": round(adjusted_forecast, 2),
                "average_daily_spending": round(daily_average, 2),
                "remaining_daily_allowed": round((adjusted_forecast - current_spent) / (days_in_month - day_of_month), 2) if days_in_month > day_of_month else 0,
                "confidence": self._calculate_confidence(last_3_months, current_spent, day_of_month)
            },
            "comparison": {
                "last_3_months_average": round(last_3_months, 2),
                "difference": round(adjusted_forecast - last_3_months, 2),
                "trend": "increasing" if adjusted_forecast > last_3_months * 1.05 else "decreasing" if adjusted_forecast < last_3_months * 0.95 else "stable"
            }
        }
    
    def forecast_category(self, category: str) -> Dict[str, Any]:
        """Forecast spending for a specific category"""
        
        today = date.today()
        month_start = date(today.year, today.month, 1)
        
        current_spent = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.category == category,
            Transaction.transaction_date >= month_start,
            Transaction.transaction_date <= today
        ).scalar() or 0
        
        historical = self.db.query(func.avg(Transaction.amount)).filter(
            Transaction.category == category,
            Transaction.transaction_date >= today - timedelta(days=90)
        ).scalar() or 0
        
        days_elapsed = today.day
        days_remaining = self._days_in_month(today) - days_elapsed
        
        # If no current data, use historical
        if current_spent == 0 and historical > 0:
            daily_avg = historical / 30
            forecast = daily_avg * self._days_in_month(today)
        elif current_spent > 0:
            daily_avg = current_spent / days_elapsed if days_elapsed > 0 else 0
            forecast = daily_avg * self._days_in_month(today)
        else:
            daily_avg = 0
            forecast = 0
        
        return {
            "category": category,
            "current_spent": round(float(current_spent), 2),
            "forecast": round(float(forecast), 2),
            "remaining_budget": round(float(daily_avg * days_remaining), 2) if days_remaining > 0 else 0,
            "historical_average": round(float(historical), 2),
            "note": "Using historical data" if current_spent == 0 and historical > 0 else None
        }
    
    def forecast_cashflow(self, budget: float) -> Dict[str, Any]:
        """Forecast end-of-month cash position"""
        monthly_forecast = self.forecast_monthly()
        
        projected = monthly_forecast["forecast"]["projected_total"]
        remaining = budget - projected
        
        suggestions = []
        if remaining < 0:
            suggestions.append(f"⚠️ You're projected to exceed your budget by ₹{abs(remaining):,.2f}. Consider reducing discretionary spending.")
            suggestions.append("Focus on essential expenses only for the remainder of the month.")
        elif remaining < 1000:
            suggestions.append(f"⚠️ Only ₹{remaining:,.2f} remaining. Be cautious with additional spending.")
            suggestions.append("Track daily expenses closely to stay within budget.")
        else:
            suggestions.append(f"✅ You're on track with ₹{remaining:,.2f} remaining.")
            suggestions.append("Consider saving the surplus for next month.")
        
        return {
            "budget": budget,
            "projected_spending": monthly_forecast["forecast"]["projected_total"],
            "projected_remaining": round(remaining, 2),
            "status": "good" if remaining > 1000 else "warning" if remaining > 0 else "critical",
            "daily_burn_rate": monthly_forecast["forecast"]["average_daily_spending"],
            "suggestions": suggestions,
            "note": monthly_forecast["current_month"].get("note")
        }
    
    def _get_average_monthly_spending(self, months: int) -> float:
        """Get average monthly spending for the last N months"""
        today = date.today()
        monthly_totals = []
        
        for i in range(months):
            # Calculate month start and end
            if i == 0:
                # Current month up to today
                month_start = date(today.year, today.month, 1)
                month_end = today
            else:
                # Previous months
                month_start = date(today.year, today.month - i, 1)
                if today.month - i == 12:
                    month_end = date(today.year + 1, 1, 1) - timedelta(days=1)
                else:
                    month_end = date(today.year, today.month - i + 1, 1) - timedelta(days=1)
            
            total = self.db.query(func.sum(Transaction.amount)).filter(
                Transaction.transaction_date >= month_start,
                Transaction.transaction_date <= month_end
            ).scalar() or 0
            
            if total > 0:
                monthly_totals.append(float(total))
        
        if not monthly_totals:
            return 0.0
        
        return statistics.mean(monthly_totals)
    
    def _days_in_month(self, date_obj: date) -> int:
        """Get number of days in a month"""
        if date_obj.month == 12:
            next_month = date(date_obj.year + 1, 1, 1)
        else:
            next_month = date(date_obj.year, date_obj.month + 1, 1)
        return (next_month - date(date_obj.year, date_obj.month, 1)).days
    
    def _calculate_confidence(self, historical_avg: float, current_spent: float, days_elapsed: int) -> int:
        """Calculate confidence score for the forecast"""
        confidence = 70
        
        if current_spent == 0 and historical_avg == 0:
            return 0
        
        # More days elapsed = higher confidence
        if days_elapsed > 25:
            confidence += 15
        elif days_elapsed > 15:
            confidence += 10
        elif days_elapsed > 7:
            confidence += 5
        
        # Historical data improves confidence
        if historical_avg > 0:
            confidence += 5
        
        return min(95, confidence)