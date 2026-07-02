from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re

class ValidationError:
    def __init__(self, row_number: int, field: str, error: str):
        self.row_number = row_number
        self.field = field
        self.error = error
    
    def to_dict(self):
        return {
            "row": self.row_number,
            "field": self.field,
            "error": self.error
        }

def validate_transaction_data(row: Dict, row_number: int) -> Tuple[bool, Optional[Dict], List[ValidationError]]:
    """
    Validate a single transaction row.
    Returns: (is_valid, cleaned_data, errors)
    """
    errors = []
    cleaned_data = {}
    
    # Validate merchant
    merchant = row.get('merchant', '').strip()
    if not merchant:
        errors.append(ValidationError(row_number, 'merchant', 'Merchant is required'))
    elif len(merchant) > 255:
        errors.append(ValidationError(row_number, 'merchant', 'Merchant name too long (max 255 characters)'))
    else:
        cleaned_data['merchant'] = merchant
    
    # Validate amount
    amount_str = str(row.get('amount', '')).strip()
    if not amount_str:
        errors.append(ValidationError(row_number, 'amount', 'Amount is required'))
    else:
        try:
            amount = float(amount_str)
            if amount <= 0:
                errors.append(ValidationError(row_number, 'amount', 'Amount must be positive'))
            elif amount > 1_000_000_000:
                errors.append(ValidationError(row_number, 'amount', 'Amount exceeds maximum allowed value'))
            else:
                cleaned_data['amount'] = round(amount, 2)
        except ValueError:
            errors.append(ValidationError(row_number, 'amount', 'Amount must be a valid number'))
    
    # Validate transaction_date
    date_str = str(row.get('transaction_date', '')).strip()
    if not date_str:
        errors.append(ValidationError(row_number, 'transaction_date', 'Transaction date is required'))
    else:
        try:
            # Try multiple date formats
            date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y%m%d']
            parsed_date = None
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt).date()
                    break
                except ValueError:
                    continue
            
            if parsed_date is None:
                errors.append(ValidationError(row_number, 'transaction_date', 'Invalid date format. Use YYYY-MM-DD'))
            else:
                cleaned_data['transaction_date'] = parsed_date
        except Exception:
            errors.append(ValidationError(row_number, 'transaction_date', 'Invalid date format'))
    
    # ✅ Validate description (optional) - ADD THIS
    description = row.get('description', '').strip()
    if description and len(description) > 1000:
        errors.append(ValidationError(row_number, 'description', 'Description too long (max 1000 characters)'))
    else:
        cleaned_data['description'] = description if description else None
    
    return len(errors) == 0, cleaned_data, errors