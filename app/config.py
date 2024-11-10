from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # MongoDB settings
    MONGODB_URL: str = "mongodb://admin:password123@mongodb:27017"
    DB_NAME: str = "credit_scoring_db"
    
    # Redis settings
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # JWT settings
    SECRET_KEY: str = "secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
