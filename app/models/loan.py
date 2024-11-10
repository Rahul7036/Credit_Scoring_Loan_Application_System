from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum
from bson import ObjectId

class LoanStatus(str, Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"

class StatusChange(BaseModel):
    status: LoanStatus
    changed_at: datetime
    changed_by: str
    notes: Optional[str] = None

class LoanBase(BaseModel):
    amount: float
    purpose: str
    duration_months: int
    user_email: str

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True
    )

class LoanCreate(LoanBase):
    pass

class Loan(LoanBase):
    id: str = Field(alias="_id")
    user_email: str = Field(..., alias="email")
    status: LoanStatus = LoanStatus.PENDING
    credit_score: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    status_history: List[StatusChange] = []

    @classmethod
    def from_mongo(cls, data: dict) -> Optional["Loan"]:
        if not data:
            return None
        
        if "_id" in data:
            data["id"] = str(data["_id"])
        
        return cls(
            id=str(data["_id"]),
            user_email=data.get("user_email", data.get("email", "Unknown")),
            amount=data.get("amount", 0),
            purpose=data.get("purpose", "Not specified"),
            duration_months=data.get("duration_months", 0),
            status=data.get("status", LoanStatus.PENDING),
            credit_score=data.get("credit_score"),
            created_at=data.get("created_at", datetime.utcnow()),
            updated_at=data.get("updated_at"),
            status_history=data.get("status_history", [])
        )

class LoanStatusUpdate(BaseModel):
    status: LoanStatus
    notes: Optional[str] = None
