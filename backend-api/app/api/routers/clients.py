from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db import models
from app.schemas import client as client_schema
from app.db.database import get_db_read, get_db_write
from app.services.cache import get_cache, set_cache, invalidate_cache
from app.services.messaging import publish_event
from app.api.deps import get_current_user
from app.schemas.token import TokenData

router = APIRouter()

CACHE_KEY_PREFIX = "client_rfc::"

@router.post("/", response_model=client_schema.Client, status_code=status.HTTP_201_CREATED)
def create_client(
    client: client_schema.ClientCreate, 
    db: Session = Depends(get_db_write),
    current_user: TokenData = Depends(get_current_user) # Endpoint protegido
):
    db_client_rfc = db.query(models.Client).filter(models.Client.rfc == client.rfc).first()
    if db_client_rfc:
        raise HTTPException(status_code=400, detail="RFC already registered")
    
    db_client_email = db.query(models.Client).filter(models.Client.email == client.email).first()
    if db_client_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_client = models.Client(**client.dict())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    
    # Publicar evento
    publish_event("client_created", db_client.id, client.dict())
    
    return db_client

@router.get("/{client_rfc}", response_model=client_schema.Client)
def read_client_by_rfc(client_rfc: str, db: Session = Depends(get_db_read)):
    cache_key = f"{CACHE_KEY_PREFIX}{client_rfc}"
    
    # 1. Intentar obtener de la caché
    cached_client = get_cache(cache_key)
    if cached_client:
        return cached_client

    # 2. Si no está en caché, obtener de la BD (réplica)
    db_client = db.query(models.Client).filter(models.Client.rfc == client_rfc).first()
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")

    # 3. Guardar en caché y retornar
    client_data = client_schema.Client.from_orm(db_client).dict()
    set_cache(cache_key, client_data, expire_seconds=600) # Cache por 10 minutos
    
    return client_data

@router.get("/", response_model=List[client_schema.Client])
def read_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_read)):
    clients = db.query(models.Client).offset(skip).limit(limit).all()
    return clients

@router.put("/{client_id}", response_model=client_schema.Client)
def update_client(
    client_id: UUID,
    client_update: client_schema.ClientUpdate,
    db: Session = Depends(get_db_write),
    current_user: TokenData = Depends(get_current_user) # Endpoint protegido
):
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")

    update_data = client_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_client, key, value)
    
    db.commit()
    db.refresh(db_client)

    # Invalidar caché si el RFC cambia (aunque no permitimos cambiarlo)
    invalidate_cache(f"{CACHE_KEY_PREFIX}{db_client.rfc}")
    
    # Publicar evento
    publish_event("client_updated", db_client.id, update_data)
    
    return db_client