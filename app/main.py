from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from .routers import auth, loans, admin
from .dependencies.database import create_indexes
from fastapi.openapi.utils import get_openapi

app = FastAPI(title="Credit Scoring System")

@app.on_event("startup")
async def startup_db_client():
    # Initialize MongoDB
    app.mongodb_client = AsyncIOMotorClient("mongodb://admin:password123@mongodb:27017")
    app.mongodb = app.mongodb_client.credit_scoring_db
    
    # Create indexes
    await create_indexes(app.mongodb)
    
    # Initialize Redis cache
    redis = aioredis.from_url("redis://redis:6379", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

app.include_router(auth.router)
app.include_router(loans.router)
app.include_router(admin.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Credit Scoring System"}

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Credit Scoring System API",
        version="1.0.0",
        description="API for credit scoring and loan application system",
        routes=app.routes,
    )
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
