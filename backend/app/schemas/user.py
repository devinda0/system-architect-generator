from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any

class UserCreate(BaseModel):
    username: str
    email: str
    password: str = Field(..., min_length=6, max_length=72, description="Password must be between 6 and 72 characters")
    full_name: Optional[str] = None
    profile: Optional[Dict[str, Any]] = None
    
    @field_validator('password')
    @classmethod
    def validate_password_bytes(cls, v: str) -> str:
        """Validate that password doesn't exceed bcrypt's 72-byte limit when encoded."""
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password is too long when encoded (max 72 bytes for bcrypt)')
        return v

class User(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: str
    updated_at: str
    profile: Optional[Dict[str, Any]] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    profile: Optional[Dict[str, Any]] = None
