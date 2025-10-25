"""
AI Action API Schemas

Pydantic schemas for AI Design Engine action endpoints.
"""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


class AIActionRequest(BaseModel):
    """Request schema for AI design actions."""
    action_type: Literal[
        "initial_generation",
        "tech_suggestion",
        "decomposition",
        "api_suggestion",
        "refactor"
    ] = Field(..., description="Type of AI action to perform")
    
    # For initial generation
    requirements: Optional[str] = Field(None, description="User requirements for initial generation")
    
    # For tech suggestion
    element_id: Optional[str] = Field(None, description="Element ID for tech suggestion")
    element_type: Optional[str] = Field(None, description="Element type")
    element_name: Optional[str] = Field(None, description="Element name")
    element_description: Optional[str] = Field(None, description="Element description")
    
    # For decomposition
    container_id: Optional[str] = Field(None, description="Container ID to decompose")
    container_name: Optional[str] = Field(None, description="Container name")
    container_description: Optional[str] = Field(None, description="Container description")
    container_technology: Optional[str] = Field(None, description="Container technology")
    
    # For API suggestion
    source_component_id: Optional[str] = Field(None, description="Source component ID")
    target_component_id: Optional[str] = Field(None, description="Target component ID")
    source_component_name: Optional[str] = Field(None, description="Source component name")
    target_component_name: Optional[str] = Field(None, description="Target component name")
    interaction_purpose: Optional[str] = Field(None, description="Purpose of interaction")
    
    # For refactor
    current_design: Optional[Dict[str, Any]] = Field(None, description="Current design structure")
    refactor_goals: Optional[List[str]] = Field(None, description="Refactoring goals")
    constraints: Optional[List[str]] = Field(None, description="Constraints to consider")
    
    # Common fields
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Action options")


class AIActionResponse(BaseModel):
    """Response schema for AI design actions."""
    action_type: str = Field(..., description="Type of action performed")
    success: bool = Field(..., description="Whether action was successful")
    result: Dict[str, Any] = Field(..., description="Action result data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    error: Optional[str] = Field(None, description="Error message if failed")


class ElementUpdateRequest(BaseModel):
    """Request schema for updating a design element."""
    name: Optional[str] = Field(None, description="Element name")
    description: Optional[str] = Field(None, description="Element description")
    technology: Optional[str] = Field(None, description="Element technology")
    tags: Optional[List[str]] = Field(None, description="Element tags")
    properties: Optional[Dict[str, Any]] = Field(None, description="Element properties")


class ElementUpdateResponse(BaseModel):
    """Response schema for element update."""
    success: bool = Field(..., description="Whether update was successful")
    element_id: str = Field(..., description="Updated element ID")
    message: str = Field(..., description="Status message")
    updated_element: Optional[Dict[str, Any]] = Field(None, description="Updated element data")


class DesignTreeResponse(BaseModel):
    """Response schema for design tree structure."""
    design_id: str = Field(..., description="Design ID")
    project_id: str = Field(..., description="Project ID")
    title: str = Field(..., description="Design title")
    description: Optional[str] = Field(None, description="Design description")
    diagram_type: str = Field(..., description="C4 diagram type")
    version: int = Field(..., description="Design version")
    elements: List[Dict[str, Any]] = Field(..., description="All design elements")
    relationships: List[Dict[str, Any]] = Field(..., description="All relationships")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Design metadata")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    created_by_ai: bool = Field(..., description="Whether created by AI")
    ai_model: Optional[str] = Field(None, description="AI model used if created by AI")
    
    class Config:
        from_attributes = True
