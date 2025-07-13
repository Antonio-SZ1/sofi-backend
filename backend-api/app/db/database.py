import logging
import time
from typing import Iterator 

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_db_engine(db_url: str, pool_size: int = 5, max_overflow: int = 10):
    """Crea un motor de base de datos con reintentos de conexión."""
    engine = None
    last_exception = None
    for i in range(5): 
        try:
            engine = create_engine(
                db_url,
                pool_size=pool_size,
                max_overflow=max_overflow
            )
       
            with engine.connect() as connection:
                logger.info(f"Successfully connected to the database at {db_url.split('@')[1]}")
                return engine
        except Exception as e:
            logger.warning(f"Database connection attempt {i+1}/5 failed for {db_url.split('@')[1]}: {e}")
            last_exception = e
            time.sleep(5)
    
    logger.error(f"Could not connect to the database after several retries: {last_exception}")
    raise last_exception

engine_primary = create_db_engine(settings.DATABASE_URL_PRIMARY)
engine_replica = create_db_engine(settings.DATABASE_URL_REPLICA)

SessionPrimary = sessionmaker(autocommit=False, autoflush=False, bind=engine_primary)
SessionReplica = sessionmaker(autocommit=False, autoflush=False, bind=engine_replica)

Base = declarative_base()

# --- Dependencias para las Sesiones de BD ---

def get_db_write() -> Iterator[Session]:
    """
    Dependencia que proporciona una sesión de base de datos para operaciones de escritura (primario).
    """
    db = SessionPrimary()
    try:
        yield db
    finally:
        db.close()

def get_db_read() -> Iterator[Session]: 
    """
    Dependencia que proporciona una sesión de base de datos para operaciones de lectura (réplica).
    """
    db = SessionReplica()
    try:
        yield db
    finally:
        db.close()