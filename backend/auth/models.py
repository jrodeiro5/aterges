from pydantic import BaseModel, EmailStr
from typing import Optional

class UserSignup(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user: dict
    token: str

class User(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    created_at: Optional[str] = None
