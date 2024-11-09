from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from datetime import datetime
from bson import ObjectId
from ..models.loan import Loan, LoanStatus, LoanStatusUpdate, StatusChange
from ..dependencies.database import get_database
from ..utils.auth import get_current_admin
from ..utils.credit_scoring import calculate_credit_score, calculate_amount_score, calculate_duration_score, calculate_purpose_score, calculate_history_score
from fastapi_cache.decorator import cache

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

@router.get("/loans", response_model=List[Loan])
@cache(expire=60)  # Cache for 60 seconds
async def get_all_loans(
    status: LoanStatus = None,
    current_admin: dict = Depends(get_current_admin),
    db = Depends(get_database)
):
    query = {}
    if status:
        query["status"] = status
        
    cursor = db.loans.find(query)
    loans = await cursor.to_list(length=None)
    return [Loan.from_mongo(loan) for loan in loans]

@router.patch("/loans/{loan_id}/review", response_model=Loan)
async def review_loan(
    loan_id: str,
    status_update: LoanStatusUpdate,
    current_admin: dict = Depends(get_current_admin),
    db = Depends(get_database)
):
    try:
        loan = await db.loans.find_one({"_id": ObjectId(loan_id)})
        if not loan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Loan not found"
            )
        
        status_change = StatusChange(
            status=status_update.status,
            changed_at=datetime.utcnow(),
            changed_by=current_admin["email"],
            notes=status_update.notes
        )
        
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
                detail="Loan review failed"
            )
        
        updated_loan = await db.loans.find_one({"_id": ObjectId(loan_id)})
        return Loan.from_mongo(updated_loan)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {str(e)}"
        )

@router.get("/loans/{loan_id}", response_model=Loan)
async def get_loan_details(
    loan_id: str,
    current_admin: dict = Depends(get_current_admin),
    db = Depends(get_database)
):
    loan = await db.loans.find_one({"_id": ObjectId(loan_id)})
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found"
        )
    return Loan.from_mongo(loan)

@router.get("/stats")
async def get_loan_stats(
    current_admin: dict = Depends(get_current_admin),
    db = Depends(get_database)
):
    pipeline = [
        {
            "$group": {
                "_id": "$status",
                "count": {"$sum": 1},
                "total_amount": {"$sum": "$amount"}
            }
        }
    ]
    
    stats = await db.loans.aggregate(pipeline).to_list(length=None)
    return {
        "loan_stats": stats,
        "total_loans": sum(stat["count"] for stat in stats),
        "total_amount": sum(stat["total_amount"] for stat in stats)
    }

@router.post("/loans/{loan_id}/calculate-score", response_model=Loan)
async def calculate_loan_score(
    loan_id: str,
    current_admin: dict = Depends(get_current_admin),
    db = Depends(get_database)
):
    # Get the current loan
    loan = await db.loans.find_one({"_id": ObjectId(loan_id)})
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found"
        )
    
    # Get previous loans for this user
    previous_loans_cursor = db.loans.find({
        "email": loan["email"],
        "_id": {"$ne": ObjectId(loan_id)}
    })
    previous_loans = await previous_loans_cursor.to_list(length=None)
    previous_loans = [Loan.from_mongo(loan) for loan in previous_loans]
    
    # Calculate credit score
    current_loan = Loan.from_mongo(loan)
    credit_score = await calculate_credit_score(current_loan, previous_loans)
    
    # Update loan with credit score
    result = await db.loans.update_one(
        {"_id": ObjectId(loan_id)},
        {
            "$set": {
                "credit_score": credit_score,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update credit score"
        )
    
    # Get updated loan
    updated_loan = await db.loans.find_one({"_id": ObjectId(loan_id)})
    return Loan.from_mongo(updated_loan)

@router.get("/loans/{loan_id}/score-details")
async def get_loan_score_details(
    loan_id: str,
    current_admin: dict = Depends(get_current_admin),
    db = Depends(get_database)
):
    loan = await db.loans.find_one({"_id": ObjectId(loan_id)})
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found"
        )
    
    current_loan = Loan.from_mongo(loan)
    previous_loans_cursor = db.loans.find({
        "email": loan["email"],
        "_id": {"$ne": ObjectId(loan_id)}
    })
    previous_loans = await previous_loans_cursor.to_list(length=None)
    previous_loans = [Loan.from_mongo(loan) for loan in previous_loans]
    
    return {
        "amount_score": calculate_amount_score(current_loan.amount),
        "duration_score": calculate_duration_score(current_loan.duration_months),
        "purpose_score": calculate_purpose_score(current_loan.purpose),
        "history_score": calculate_history_score(previous_loans),
        "total_score": current_loan.credit_score,
        "previous_loans_count": len(previous_loans)
    }
