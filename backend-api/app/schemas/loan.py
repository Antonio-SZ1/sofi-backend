from pydantic import BaseModel, EmailStr, Field
from typing import List
from uuid import UUID
from datetime import datetime
from decimal import Decimal

class PaymentBase(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Amount paid")

class PaymentCreate(PaymentBase):
    pass

class Payment(PaymentBase):
    id: UUID
    payment_date: datetime
    
    class Config:
        orm_mode = True

class LoanBase(BaseModel):
    amount: Decimal = Field(..., gt=0)
    interest_rate: Decimal = Field(..., ge=0, le=1)
    term_months: int = Field(..., gt=0)

class LoanCreate(LoanBase):
    client_id: UUID

class Loan(LoanBase):
    id: UUID
    client_id: UUID
    status: str
    granted_at: datetime
    current_balance: Decimal
    
    class Config:
        orm_mode = True


class AccountStatement(BaseModel):
    client_id: UUID
    full_name: str
    email: EmailStr
    rfc: str
    active_loans: List[Loan]
    payment_history: List[Payment]