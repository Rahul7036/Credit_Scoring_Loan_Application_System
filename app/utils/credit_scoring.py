from typing import List
from ..models.loan import Loan, LoanStatus

CREDIT_SCORE_THRESHOLD = 60.0  # Minimum score for admin review

def calculate_amount_score(amount: float) -> float:
    """
    Calculate score based on loan amount
    Lower amounts get higher scores (less risk)
    """
    if amount <= 5000:
        return 40.0
    elif amount <= 10000:
        return 30.0
    elif amount <= 20000:
        return 20.0
    else:
        return 10.0

def calculate_duration_score(duration_months: int) -> float:
    """
    Calculate score based on loan duration
    Shorter durations get higher scores
    """
    if duration_months <= 6:
        return 30.0
    elif duration_months <= 12:
        return 25.0
    elif duration_months <= 24:
        return 20.0
    else:
        return 15.0

def calculate_purpose_score(purpose: str) -> float:
    """
    Calculate score based on loan purpose
    Different purposes have different risk levels
    """
    purpose_scores = {
        "education": 30.0,
        "home renovation": 25.0,
        "business": 20.0,
        "debt consolidation": 15.0,
        "other": 10.0
    }
    return purpose_scores.get(purpose.lower(), 10.0)

def calculate_history_score(previous_loans: List[Loan]) -> float:
    """
    Calculate score based on previous loan history
    """
    if not previous_loans:
        return 20.0  # New borrower score
    
    completed_loans = sum(1 for loan in previous_loans 
                         if loan.status == "approved")
    
    if completed_loans >= 2:
        return 30.0
    elif completed_loans == 1:
        return 25.0
    else:
        return 15.0

async def calculate_credit_score(
    loan: Loan,
    previous_loans: List[Loan]
) -> float:
    """
    Calculate overall credit score
    Returns a score between 0 and 100
    """
    amount_score = calculate_amount_score(loan.amount)
    duration_score = calculate_duration_score(loan.duration_months)
    purpose_score = calculate_purpose_score(loan.purpose)
    history_score = calculate_history_score(previous_loans)
    
    total_score = amount_score + duration_score + purpose_score + history_score
    # Normalize to 0-100 range
    normalized_score = (total_score / 130.0) * 100
    
    return round(normalized_score, 2) 

async def evaluate_loan_eligibility(credit_score: float) -> str:
    if credit_score < CREDIT_SCORE_THRESHOLD:
        return LoanStatus.REJECTED
    return LoanStatus.IN_REVIEW