import pandas as pd
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from datetime import datetime

from app.models import Transaction
from app.services.validator import validate_transaction_data, ValidationError
from app.services.categorizer import categorize_transaction

class CSVImportService:
    def __init__(self, db: Session):
        self.db = db
        self.imported_count = 0
        self.errors = []
        
    def import_from_file(self, file_content: bytes, filename: str, user_id: int) -> Dict:
        """
        Import transactions from a CSV file.
        Returns: {success_count, errors}
        """
        try:
            # Read CSV using pandas
            df = pd.read_csv(pd.io.common.BytesIO(file_content))
            
            # Check required columns
            required_columns = ['merchant', 'amount', 'transaction_date']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return {
                    'success': False,
                    'error': f'Missing required columns: {", ".join(missing_columns)}',
                    'rows_imported': 0
                }
            
            # Process each row
            for index, row in df.iterrows():
                row_number = index + 2
                row_dict = row.to_dict()
                
                # Validate row
                is_valid, cleaned_data, validation_errors = validate_transaction_data(
                    row_dict, row_number
                )
                
                if not is_valid:
                    self.errors.extend(validation_errors)
                    continue
                
                # Categorize transaction
                category = categorize_transaction(cleaned_data['merchant'])
                
                # ✅ Create transaction - updated_at will be auto-set by SQLAlchemy
                transaction = Transaction(
                    user_id=user_id,
                    merchant=cleaned_data['merchant'],
                    description=cleaned_data.get('description'),
                    amount=cleaned_data['amount'],
                    category=category,
                    transaction_date=cleaned_data['transaction_date']
                    # updated_at is not needed - it will be set automatically
                )
                
                self.db.add(transaction)
                self.imported_count += 1
            
            # Commit all successful transactions
            self.db.commit()
            
            return {
                'success': True,
                'rows_imported': self.imported_count,
                'errors': [e.to_dict() for e in self.errors]
            }
            
        except pd.errors.EmptyDataError:
            return {
                'success': False,
                'error': 'CSV file is empty',
                'rows_imported': 0
            }
        except Exception as e:
            self.db.rollback()
            return {
                'success': False,
                'error': f'Error processing CSV: {str(e)}',
                'rows_imported': 0
            }