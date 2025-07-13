from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from decimal import Decimal

from app.db import models
from app.schemas import loan as loan_schema
from app.db.database import get_db_read, get_db_write
from app.services.cache import get_cache, invalidate_cache, set_cache
from app.services.messaging import publish_event
from app.api.deps import get_current_user
from app.schemas.token import TokenData

router = APIRouter()

ACCOUNT_STATEMENT_CACHE_KEY_PREFIX = "account_statement::"

@router.post("/", response_model=loan_schema.Loan, status_code=status.HTTP_201_CREATED)
def create_loan(
    loan: loan_schema.LoanCreate, 
    db: Session = Depends(get_db_write),
    current_user: TokenData = Depends(get_current_user)
):
    db_client = db.query(models.Client).filter(models.Client.id == loan.client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")

    loan_data = loan.dict()
    loan_data['current_balance'] = loan_data['amount'] # Saldo inicial es el monto total
    
    db_loan = models.Loan(**loan_data)
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    
    # Publicar evento
    publish_event("loan_created", db_loan.id, loan_schema.Loan.from_orm(db_loan).dict())
    
    # Invalidar el estado de cuenta del cliente en caché
    invalidate_cache(f"{ACCOUNT_STATEMENT_CACHE_KEY_PREFIX}{db_loan.client_id}")
    
    return db_loan

@router.post("/{loan_id}/payments", response_model=loan_schema.Payment, status_code=status.HTTP_201_CREATED)
def register_payment(
    loan_id: UUID, 
    payment: loan_schema.PaymentCreate, 
    db: Session = Depends(get_db_write),
    current_user: TokenData = Depends(get_current_user)
):
    db_loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not db_loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    if db_loan.status != 'ACTIVE':
        raise HTTPException(status_code=400, detail=f"Loan is not active. Status: {db_loan.status}")

    if payment.amount > db_loan.current_balance:
        raise HTTPException(status_code=400, detail="Payment amount cannot be greater than the current balance")

    # Registrar pago
    db_payment = models.Payment(loan_id=loan_id, amount=payment.amount)
    db.add(db_payment)
    
    # Actualizar saldo del préstamo
    db_loan.current_balance -= payment.amount
    if db_loan.current_balance <= Decimal('0.0'):
        db_loan.current_balance = Decimal('0.0')
        db_loan.status = 'PAID_OFF'
        
    db.commit()
    db.refresh(db_payment)
    
    # Publicar evento
    publish_event("payment_registered", db_payment.id, loan_schema.Payment.from_orm(db_payment).dict())

    # Invalidar el estado de cuenta del cliente en caché
    invalidate_cache(f"{ACCOUNT_STATEMENT_CACHE_KEY_PREFIX}{db_loan.client_id}")
    
    return db_payment

@router.get("/clients/{client_id}/account-statement", response_model=loan_schema.AccountStatement)
def get_client_account_statement(client_id: UUID, db: Session = Depends(get_db_read)):
    cache_key = f"{ACCOUNT_STATEMENT_CACHE_KEY_PREFIX}{client_id}"
    
    # 1. Intentar obtener de la caché
    cached_statement = get_cache(cache_key)
    if cached_statement:
        return cached_statement

    # 2. Si no, consultar la BD (réplica)
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")

    active_loans = db.query(models.Loan).filter(models.Loan.client_id == client_id, models.Loan.status == 'ACTIVE').all()
    
    loan_ids = [loan.id for loan in db_client.loans]
    payment_history = db.query(models.Payment).filter(models.Payment.loan_id.in_(loan_ids)).order_by(models.Payment.payment_date.desc()).all()

    statement = {
        "client_id": db_client.id,
        "full_name": db_client.full_name,
        "email": db_client.email,
        "rfc": db_client.rfc,
        "active_loans": active_loans,
        "payment_history": payment_history
    }
    
    # 3. Guardar en caché y retornar
    set_cache(cache_key, statement, expire_seconds=300) # Cache por 5 minutos

    return statement