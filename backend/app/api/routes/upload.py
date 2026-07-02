from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict

from app.database import get_db
from app.services.csv_import import CSVImportService
from app.auth.dependencies import get_current_active_user
from app.models import User

router = APIRouter()

@router.post("/upload", response_model=Dict)
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # ✅ Get current user
):
    """
    Upload a CSV file containing transaction data.
    
    Required columns:
    - merchant: str
    - amount: float
    - transaction_date: date (YYYY-MM-DD)
    
    Optional columns:
    - description: str
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported"
        )
    
    # Read file content
    content = await file.read()
    
    if not content:
        raise HTTPException(
            status_code=400,
            detail="File is empty"
        )
    
    # ✅ Import transactions with user_id
    import_service = CSVImportService(db)
    result = import_service.import_from_file(content, file.filename, current_user.id)
    
    if not result['success']:
        raise HTTPException(
            status_code=400,
            detail=result.get('error', 'Import failed')
        )
    
    # Prepare response
    response = {
        "message": "CSV imported successfully",
        "rows_imported": result['rows_imported']
    }
    
    if result.get('errors'):
        response["warnings"] = {
            "count": len(result['errors']),
            "details": result['errors'][:10]
        }
    
    return response