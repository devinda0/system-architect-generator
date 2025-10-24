"""
MongoDB Collection Schemas

This module defines Pydantic models for MongoDB collections:
- Users: User account information
- Projects: Architecture projects
- Designs: C4 architecture designs
- Feedback: User feedback on designs
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, field_validator
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom type for MongoDB ObjectId in Pydantic models."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


# ==================== User Schema ====================

class UserBase(BaseModel):
    """Base schema for User."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: bool = Field(default=True)
    role: str = Field(default="user", pattern="^(user|admin|premium)$")


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    role: Optional[str] = Field(None, pattern="^(user|admin|premium)$")
    password: Optional[str] = Field(None, min_length=8, max_length=100)


class UserInDB(UserBase):
    """Schema for user stored in database."""
    id: str = Field(alias="_id")
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserResponse(UserBase):
    """Schema for user response (without sensitive data)."""
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


# ==================== Project Schema ====================

class ProjectBase(BaseModel):
    """Base schema for Project."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    tags: List[str] = Field(default_factory=list, max_length=20)
    status: str = Field(default="active", pattern="^(active|archived|deleted)$")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating project information."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    tags: Optional[List[str]] = Field(None, max_length=20)
    status: Optional[str] = Field(None, pattern="^(active|archived|deleted)$")
    metadata: Optional[Dict[str, Any]] = None


class ProjectInDB(ProjectBase):
    """Schema for project stored in database."""
    id: str = Field(alias="_id")
    user_id: str
    created_at: datetime
    updated_at: datetime
    design_count: int = Field(default=0)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ProjectResponse(ProjectBase):
    """Schema for project response."""
    id: str = Field(alias="_id")
    user_id: str
    created_at: datetime
    updated_at: datetime
    design_count: int
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


# ==================== Design Schema ====================

class C4Element(BaseModel):
    """Schema for C4 architecture elements."""
    id: str
    type: str = Field(..., pattern="^(system|container|component|code)$")
    name: str
    description: Optional[str] = None
    technology: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)


class C4Relationship(BaseModel):
    """Schema for relationships between C4 elements."""
    id: str
    source_id: str
    target_id: str
    description: Optional[str] = None
    technology: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class DesignBase(BaseModel):
    """Base schema for Design."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    version: int = Field(default=1, ge=1)
    diagram_type: str = Field(
        ...,
        pattern="^(system_context|container|component|code|deployment)$"
    )
    elements: List[C4Element] = Field(default_factory=list)
    relationships: List[C4Relationship] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list, max_length=20)


class DesignCreate(DesignBase):
    """Schema for creating a new design."""
    project_id: str


class DesignUpdate(BaseModel):
    """Schema for updating design information."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    diagram_type: Optional[str] = Field(
        None,
        pattern="^(system_context|container|component|code|deployment)$"
    )
    elements: Optional[List[C4Element]] = None
    relationships: Optional[List[C4Relationship]] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = Field(None, max_length=20)


class DesignInDB(DesignBase):
    """Schema for design stored in database."""
    id: str = Field(alias="_id")
    project_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    created_by_ai: bool = Field(default=False)
    ai_model: Optional[str] = None
    parent_version_id: Optional[str] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class DesignResponse(DesignBase):
    """Schema for design response."""
    id: str = Field(alias="_id")
    project_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    created_by_ai: bool
    ai_model: Optional[str]
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


# ==================== Feedback Schema ====================

class FeedbackBase(BaseModel):
    """Base schema for Feedback."""
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=2000)
    feedback_type: str = Field(
        default="general",
        pattern="^(general|bug|feature_request|improvement|other)$"
    )
    tags: List[str] = Field(default_factory=list, max_length=10)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FeedbackCreate(FeedbackBase):
    """Schema for creating new feedback."""
    design_id: str


class FeedbackUpdate(BaseModel):
    """Schema for updating feedback."""
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=2000)
    feedback_type: Optional[str] = Field(
        None,
        pattern="^(general|bug|feature_request|improvement|other)$"
    )
    tags: Optional[List[str]] = Field(None, max_length=10)
    metadata: Optional[Dict[str, Any]] = None
    status: Optional[str] = Field(
        None,
        pattern="^(new|reviewed|resolved|dismissed)$"
    )


class FeedbackInDB(FeedbackBase):
    """Schema for feedback stored in database."""
    id: str = Field(alias="_id")
    design_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    status: str = Field(default="new", pattern="^(new|reviewed|resolved|dismissed)$")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class FeedbackResponse(FeedbackBase):
    """Schema for feedback response."""
    id: str = Field(alias="_id")
    design_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    status: str
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


# ==================== Helper Functions ====================

def convert_objectid_to_str(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert MongoDB ObjectId to string in document.
    
    Args:
        doc: MongoDB document
        
    Returns:
        Document with ObjectId converted to string
    """
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


def prepare_document_for_insert(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare document for MongoDB insertion.
    
    Args:
        data: Document data
        
    Returns:
        Document ready for insertion
    """
    now = datetime.utcnow()
    data["created_at"] = now
    data["updated_at"] = now
    return data


def prepare_document_for_update(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare document for MongoDB update.
    
    Args:
        data: Update data
        
    Returns:
        Document ready for update
    """
    data["updated_at"] = datetime.utcnow()
    return data
