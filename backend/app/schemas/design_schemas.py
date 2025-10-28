"""
Design Schemas

Pydantic schemas for Design Engine API requests and responses.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


# Request Schemas

class InitialDesignRequest(BaseModel):
    """Request schema for initial design generation."""

    requirements: str = Field(
        ...,
        description="User requirements as text",
        min_length=10,
        example="Build an e-commerce platform with user authentication, product catalog, shopping cart, and payment processing"
    )
    use_rag: bool = Field(
        default=True,
        description="Whether to use RAG for knowledge grounding"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Model temperature for generation"
    )


class TechSuggestionRequest(BaseModel):
    """Request schema for technology suggestion."""
    
    element_name: str = Field(..., description="Name of the element")
    element_type: str = Field(..., description="Type of element (container, component, etc.)")
    element_description: str = Field(..., description="Description of the element")
    element_context: Optional[str] = Field(default="", description="Additional context")
    use_rag: bool = Field(default=True, description="Whether to use RAG")


class DecompositionRequest(BaseModel):
    """Request schema for container decomposition."""
    
    container_name: str = Field(..., description="Name of the container")
    container_type: str = Field(..., description="Type of container")
    container_description: str = Field(..., description="Description of the container")
    container_context: Optional[str] = Field(default="", description="Additional context")
    use_rag: bool = Field(default=True, description="Whether to use RAG")


class APISuggestionRequest(BaseModel):
    """Request schema for API endpoint suggestion."""
    
    component_name: str = Field(..., description="Name of the component")
    component_type: str = Field(..., description="Type of component")
    component_description: str = Field(..., description="Description of the component")
    component_responsibilities: str = Field(..., description="Component responsibilities")
    component_context: Optional[str] = Field(default="", description="Additional context")
    use_rag: bool = Field(default=True, description="Whether to use RAG")


class RefactorRequest(BaseModel):
    """Request schema for element refactoring."""
    
    element_name: str = Field(..., description="Name of the element")
    element_type: str = Field(..., description="Type of element")
    element_description: str = Field(..., description="Description of the element")
    current_design: Dict[str, Any] = Field(..., description="Current design as dictionary")
    refactor_request: str = Field(..., description="User's refactoring request")
    element_context: Optional[str] = Field(default="", description="Additional context")
    use_rag: bool = Field(default=True, description="Whether to use RAG")


# Response Schemas

class ExternalActor(BaseModel):
    """External actor in the system context."""
    
    name: str
    type: str
    description: str


class SystemContext(BaseModel):
    """System context definition."""
    
    name: str
    description: str
    external_actors: List[ExternalActor]
    key_features: List[str]


class ContainerInteraction(BaseModel):
    """Interaction between containers."""
    
    target: str
    type: str
    description: str


class Container(BaseModel):
    """Container definition."""
    
    id: str
    name: str
    type: str
    description: str
    technology_suggestions: List[str]
    interactions: List[ContainerInteraction]


class DesignRationale(BaseModel):
    """Design rationale and decisions."""
    
    architecture_pattern: str
    key_decisions: List[str]
    trade_offs: List[str]


class InitialDesignResponse(BaseModel):
    """Response schema for initial design generation."""
    
    system_context: SystemContext
    containers: List[Container]
    design_rationale: DesignRationale


class TechnologyRecommendation(BaseModel):
    """Primary technology recommendation."""
    
    technology: str
    version: str
    rationale: str
    pros: List[str]
    cons: List[str]
    use_cases: List[str]


class AlternativeTechnology(BaseModel):
    """Alternative technology option."""
    
    technology: str
    version: str
    rationale: str
    when_to_choose: str


class ImplementationGuidance(BaseModel):
    """Implementation guidance for technology."""
    
    setup_steps: List[str]
    dependencies: List[str]
    configuration_tips: List[str]
    best_practices: List[str]


class IntegrationConsiderations(BaseModel):
    """Integration considerations for technology."""
    
    compatibility: List[str]
    potential_issues: List[str]
    monitoring_recommendations: List[str]


class TechSuggestionResponse(BaseModel):
    """Response schema for technology suggestion."""
    
    primary_recommendation: TechnologyRecommendation
    alternative_options: List[AlternativeTechnology]
    implementation_guidance: ImplementationGuidance
    integration_considerations: IntegrationConsiderations


class ComponentInterface(BaseModel):
    """Component interface definition."""
    
    name: str
    type: str
    methods: List[str]


class ComponentDependency(BaseModel):
    """Component dependency."""
    
    component_id: str
    type: str
    description: str


class Component(BaseModel):
    """Component definition."""
    
    id: str
    name: str
    type: str
    description: str
    responsibilities: List[str]
    interfaces: List[ComponentInterface]
    dependencies: List[ComponentDependency]
    data_handled: List[str]


class ComponentLayers(BaseModel):
    """Component organization into layers."""
    
    presentation: List[str]
    business_logic: List[str]
    data_access: List[str]
    infrastructure: List[str]


class FlowStep(BaseModel):
    """Step in an internal flow."""
    
    component: str
    action: str
    order: int


class InternalFlow(BaseModel):
    """Internal component flow."""
    
    name: str
    steps: List[FlowStep]


class DesignPattern(BaseModel):
    """Applied design pattern."""
    
    pattern: str
    applied_to: List[str]
    rationale: str


class DecompositionResponse(BaseModel):
    """Response schema for container decomposition."""
    
    components: List[Component]
    component_layers: ComponentLayers
    internal_flows: List[InternalFlow]
    design_patterns: List[DesignPattern]


class APIParameter(BaseModel):
    """API parameter definition."""
    
    name: str
    in_: str = Field(..., alias="in")
    type: str
    required: bool
    description: str
    example: Any


class RequestBody(BaseModel):
    """Request body definition."""
    
    required: bool
    content_type: str
    schema: Dict[str, Any]
    example: Dict[str, Any]


class APIResponse(BaseModel):
    """API response definition."""
    
    description: str
    schema: Optional[Dict[str, Any]] = None
    example: Optional[Dict[str, Any]] = None


class APIEndpoint(BaseModel):
    """API endpoint definition."""
    
    path: str
    method: str
    summary: str
    description: str
    parameters: List[APIParameter]
    request_body: Optional[RequestBody] = None
    responses: Dict[str, APIResponse]
    authentication: str
    rate_limit: str
    tags: List[str]


class AuthenticationScheme(BaseModel):
    """Authentication scheme definition."""
    
    type: str
    description: str
    implementation_notes: List[str]


class StandardError(BaseModel):
    """Standard error definition."""
    
    code: str
    message: str
    http_status: int


class ErrorHandling(BaseModel):
    """Error handling configuration."""
    
    standard_errors: List[StandardError]
    error_response_format: Dict[str, Any]


class RateLimitConfig(BaseModel):
    """Rate limiting configuration."""
    
    strategy: str
    limits: Dict[str, str]


class APISuggestionResponse(BaseModel):
    """Response schema for API suggestion."""
    
    api_base_path: str
    endpoints: List[APIEndpoint]
    authentication_schemes: List[AuthenticationScheme]
    error_handling: ErrorHandling
    versioning_strategy: str
    rate_limiting: RateLimitConfig
    documentation_url: str
    openapi_spec_url: str


class RefactoredElement(BaseModel):
    """Refactored element definition."""
    
    name: str
    type: str
    description: str
    changes_summary: str
    updated_design: Dict[str, Any]


class Rationale(BaseModel):
    """Refactoring rationale."""
    
    why_changed: str
    benefits: List[str]
    trade_offs: List[str]
    risks: List[str]


class MigrationStrategy(BaseModel):
    """Migration strategy."""
    
    approach: str
    steps: List[str]
    considerations: List[str]
    rollback_plan: str


class ImpactAnalysis(BaseModel):
    """Impact analysis of refactoring."""
    
    affected_components: List[str]
    breaking_changes: List[str]
    compatibility_notes: List[str]
    testing_recommendations: List[str]


class Alternative(BaseModel):
    """Alternative approach considered."""
    
    approach: str
    description: str
    pros: List[str]
    cons: List[str]
    why_not_chosen: str


class ImplementationGuidanceRefactor(BaseModel):
    """Implementation guidance for refactoring."""
    
    priority: str
    estimated_effort: str
    prerequisites: List[str]
    next_steps: List[str]


class RefactorResponse(BaseModel):
    """Response schema for refactoring."""
    
    refactored_element: RefactoredElement
    rationale: Rationale
    migration_strategy: MigrationStrategy
    impact_analysis: ImpactAnalysis
    alternatives_considered: List[Alternative]
    implementation_guidance: ImplementationGuidanceRefactor


class ChainInfo(BaseModel):
    """Information about a chain."""
    
    purpose: str
    input: str
    output: str


class EngineInfoResponse(BaseModel):
    """Response schema for engine information."""
    
    engine_version: str
    rag_enabled: bool
    model: str
    chains: Dict[str, ChainInfo]
