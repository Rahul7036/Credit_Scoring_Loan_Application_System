from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

async def get_database(request: Request):
    return request.app.mongodb 

async def create_indexes(db):
    # Create indexes for frequently queried fields
    await db.users.create_index("email", unique=True)
    await db.loans.create_index("email")
    await db.loans.create_index("status")
    await db.loans.create_index([("email", 1), ("status", 1)]) 