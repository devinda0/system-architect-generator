"""
Project API Schemas

Pydantic schemas for Project API endpoints.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ProjectCreateRequest(BaseModel):
    """Request schema for creating a new project."""
    name: str = Field(..., min_length=1, max_length=200, description="Project name")
    description: Optional[str] = Field(None, max_length=2000, description="Project description")
    tags: List[str] = Field(default_factory=list, max_length=20, description="Project tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ProjectUpdateRequest(BaseModel):
    """Request schema for updating a project."""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Project name")
    description: Optional[str] = Field(None, max_length=2000, description="Project description")
    tags: Optional[List[str]] = Field(None, max_length=20, description="Project tags")
    status: Optional[str] = Field(None, pattern="^(active|archived|deleted)$", description="Project status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ProjectResponse(BaseModel):
    """Response schema for a single project."""
    id: str = Field(..., description="Project ID")
    user_id: str = Field(..., description="Owner user ID")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    tags: List[str] = Field(default_factory=list, description="Project tags")
    status: str = Field(..., description="Project status")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    design_count: int = Field(..., description="Number of designs in project")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Response schema for listing projects."""
    projects: List[ProjectResponse] = Field(..., description="List of projects")
    total: int = Field(..., description="Total number of projects")
    skip: int = Field(..., description="Number of projects skipped")
    limit: int = Field(..., description="Maximum number of projects returned")


class ProjectDetailResponse(ProjectResponse):
    """Detailed response schema for a single project including designs."""
    recent_designs: List[Dict[str, Any]] = Field(default_factory=list, description="Recent designs in project")
    
    class Config:
        from_attributes = True
