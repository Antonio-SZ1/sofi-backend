import redis
import json
from app.core.config import settings

redis_pool = redis.ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, decode_responses=True)

def get_redis_client():
    return redis.Redis(connection_pool=redis_pool)

def set_cache(key: str, value: dict, expire_seconds: int = 300):
    """Guarda un valor en el cache de Redis."""
    r = get_redis_client()
    r.set(key, json.dumps(value, default=str), ex=expire_seconds)

def get_cache(key: str) -> dict | None:
    """Obtiene un valor del cache de Redis."""
    r = get_redis_client()
    cached_value = r.get(key)
    if cached_value:
        return json.loads(cached_value)
    return None

def invalidate_cache(key: str):
    """Invalida (elimina) una clave del cache de Redis."""
    r = get_redis_client()
    r.delete(key)