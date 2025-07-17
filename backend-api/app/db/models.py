from sqlalchemy import Column, String, Numeric, ForeignKey, UUID, Integer, TIMESTAMP  
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import uuid

class Client(Base):
    __tablename__ = "clients"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    rfc = Column(String(13), unique=True, index=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    loans = relationship("Loan", back_populates="client")

class Loan(Base):
    __tablename__ = "loans"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    interest_rate = Column(Numeric(5, 4), nullable=False)
    term_months = Column(Integer, nullable=False)
    status = Column(String(20), default='ACTIVE', nullable=False)
    granted_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    current_balance = Column(Numeric(15, 2), nullable=False)
    client = relationship("Client", back_populates="loans")
    payments = relationship("Payment", back_populates="loan")

class Payment(Base):
    __tablename__ = "payments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_id = Column(UUID(as_uuid=True), ForeignKey("loans.id"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    payment_date = Column(TIMESTAMP(timezone=True), server_default=func.now())
    loan = relationship("Loan", back_populates="payments")