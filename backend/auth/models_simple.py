from pydantic import BaseModel, Field
from typing import Optional
import re

def validate_email(email: str) -> str:
    """Simple email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValueError('Invalid email format')
    return email.lower()

class UserSignup(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=6, max_length=100)
    
    def __init__(self, **data):
        if 'email' in data:
            data['email'] = validate_email(data['email'])
        super().__init__(**data)

class UserLogin(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=1, max_length=100)
    
    def __init__(self, **data):
        if 'email' in data:
            data['email'] = validate_email(data['email'])
        super().__init__(**data)

class UserResponse(BaseModel):
    user: dict
    token: str

class User(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    created_at: Optional[str] = None
