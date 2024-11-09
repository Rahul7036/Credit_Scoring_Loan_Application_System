from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from ..models.user import UserCreate, User, UserInDB
from passlib.context import CryptContext
from datetime import timedelta
from ..dependencies.database import get_database
from ..utils.auth import (
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register", response_model=User)
async def register_user(
    user: UserCreate,
    db = Depends(get_database)
):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create user document
    user_in_db = UserInDB(
        email=user.email,
        full_name=user.full_name,
        hashed_password=pwd_context.hash(user.password)
    )
    
    # Insert into database
    result = await db.users.insert_one(user_in_db.model_dump())
    
    # Fetch and return created user
    created_user = await db.users.find_one({"_id": result.inserted_id})
    if created_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return User.from_mongo(created_user)

@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db = Depends(get_database)
):
    user = await db.users.find_one({"email": form_data.username})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not pwd_context.verify(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return User.from_mongo(current_user)

@router.post("/create-admin")
async def create_admin_user(
    user: UserCreate,
    db = Depends(get_database)
):
    # In production, you should secure this endpoint
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create admin user
    user_in_db = UserInDB(
        email=user.email,
        full_name=user.full_name,
        hashed_password=pwd_context.hash(user.password),
        is_admin=True
    )
    
    result = await db.users.insert_one(user_in_db.model_dump())
    return {"message": "Admin user created successfully"}
