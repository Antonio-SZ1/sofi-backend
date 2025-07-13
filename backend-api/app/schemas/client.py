from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class ClientBase(BaseModel):
    full_name: str
    email: EmailStr
    rfc: str = Field(..., min_length=12, max_length=13)

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

class Client(ClientBase):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True