from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from datetime import datetime
from bson import ObjectId
from ..models.loan import LoanCreate, Loan, LoanStatus, LoanStatusUpdate, StatusChange
from ..dependencies.database import get_database
from ..utils.auth import get_current_user

router = APIRouter(
    prefix="/loans",
    tags=["loans"]
)

@router.post("/apply", response_model=Loan)
async def apply_for_loan(
    loan: LoanCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    loan_dict = loan.model_dump()
    current_time = datetime.utcnow()
    
    initial_status = StatusChange(
        status=LoanStatus.PENDING,
        changed_at=current_time,
        changed_by=current_user["email"],
        notes="Loan application submitted"
    )
    
    loan_dict["user_email"] = current_user["email"]
    
    loan_dict.update({
        "status": LoanStatus.PENDING,
        "created_at": current_time,
        "credit_score": None,
        "status_history": [initial_status.model_dump()]
    })
    
    result = await db.loans.insert_one(loan_dict)
    created_loan = await db.loans.find_one({"_id": result.inserted_id})
    
    return Loan.from_mongo(created_loan)

@router.patch("/{loan_id}/status", response_model=Loan)
async def update_loan_status(
    loan_id: str,
    status_update: LoanStatusUpdate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    # First check if the loan exists
    loan = await db.loans.find_one({"_id": ObjectId(loan_id)})
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found"
        )
    
    # Create status change record
    status_change = StatusChange(
        status=status_update.status,
        changed_at=datetime.utcnow(),
        changed_by=current_user["email"],
        notes=status_update.notes
    )
    
    # Update the loan
    result = await db.loans.update_one(
        {"_id": ObjectId(loan_id)},
        {
            "$set": {
                "status": status_update.status,
                "updated_at": datetime.utcnow()
            },
            "$push": {
                "status_history": status_change.model_dump()
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Loan status update failed"
        )
    
    updated_loan = await db.loans.find_one({"_id": ObjectId(loan_id)})
    return Loan.from_mongo(updated_loan)

@router.get("/status-history/{loan_id}", response_model=List[StatusChange])
async def get_loan_status_history(
    loan_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    loan = await db.loans.find_one({
        "_id": ObjectId(loan_id),
        "user_email": current_user["email"]
    })
    
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found"
        )
    
    return loan.get("status_history", [])

@router.get("/my-loans", response_model=List[Loan])
async def get_my_loans(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    cursor = db.loans.find({"user_email": current_user["email"]})
    loans = await cursor.to_list(length=None)
    return [Loan.from_mongo(loan) for loan in loans]

@router.get("/{loan_id}", response_model=Loan)
async def get_loan(
    loan_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    from bson import ObjectId
    
    loan = await db.loans.find_one({
        "_id": ObjectId(loan_id),
        "user_email": current_user["email"]
    })
    
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found"
        )
    
    return Loan.from_mongo(loan)
