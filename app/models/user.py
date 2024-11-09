from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from bson import ObjectId

class MongoBaseModel(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )

class UserBase(MongoBaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    is_admin: bool = False

class User(UserBase):
    created_at: datetime
    is_active: bool = True
    is_admin: bool = False

    @classmethod
    def from_mongo(cls, data: dict) -> Optional["User"]:
        if not data:
            return None
        return cls(
            email=data["email"],
            full_name=data["full_name"],
            created_at=data["created_at"],
            is_active=data.get("is_active", True),
            is_admin=data.get("is_admin", False)
        )