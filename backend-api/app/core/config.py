import os
from dotenv import load_dotenv

load_dotenv()

class Settings:

    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    
    DATABASE_URL_PRIMARY: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@postgres-primary:5432/{POSTGRES_DB}"
    
    DATABASE_URL_REPLICA: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@postgres-replica:5432/{POSTGRES_DB}"

    SECRET_KEY: str = os.getenv("API_SECRET_KEY")
    ALGORITHM: str = os.getenv("API_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("API_ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    RABBITMQ_HOST: str = os.getenv("RABBITMQ_HOST", "rabbitmq")
    
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))


settings = Settings()