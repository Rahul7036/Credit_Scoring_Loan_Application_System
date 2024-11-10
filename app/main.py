from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from fastapi.responses import RedirectResponse
from .routers import auth, loans, admin
from .dependencies.database import create_indexes
from fastapi.openapi.utils import get_openapi
from .utils.auth import get_current_user

app = FastAPI(title="Credit Scoring System")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/admin/register")
async def register_page(request: Request):
    return templates.TemplateResponse("adminRegister.html", {"request": request})
@app.get("/admin/dashboard")
async def register_page(request: Request):
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})

@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard")
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": None 
    })

@app.get("/apply-loan")
async def apply_loan_page(request: Request):
    return templates.TemplateResponse("loan_application.html", {"request": request})

@app.get("/admin/dashboard")
async def admin_dashboard_page(request: Request):
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "stats": {"total_loans": 0, "pending_count": 0, "total_amount": 0},
        "loans": []
    })

@app.get("/loan/view/{loan_id}")
async def loan_details_page(request: Request, loan_id: str):
    return templates.TemplateResponse("loan_details.html", {
        "request": request,
        "loan_id": loan_id
    })

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
