"""
Design Engine Service

Central orchestrator for AI-driven architecture design using specialized chains.
"""

from typing import Dict, Any, Optional
import logging

from app.chains.initial_generation_chain import InitialGenerationChain
from app.chains.tech_suggestion_chain import TechSuggestionChain
from app.chains.decomposition_chain import DecompositionChain
from app.chains.api_suggestion_chain import APISuggestionChain
from app.chains.refactor_chain import RefactorChain
from app.services.knowledge_base_service import KnowledgeBaseService

logger = logging.getLogger(__name__)


class DesignEngineService:
    """
    AI Design Engine orchestrating specialized chains for architecture generation.
    
    The engine owns multiple specialized LangChain chains, each responsible for
    specific design tasks. All chains leverage RAG for knowledge-grounded outputs.
    
    Attributes:
        initial_generation_chain: Generates initial SystemContext and Containers
        tech_suggestion_chain: Suggests technology stacks for elements
        decomposition_chain: Decomposes containers into components
        api_suggestion_chain: Suggests API endpoints for components
        refactor_chain: Refactors elements based on user feedback
    """
    
    def __init__(
        self,
        kb_service: Optional[KnowledgeBaseService] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        use_rag: bool = True,
    ):
        """
        Initialize the Design Engine.
        
        Args:
            kb_service: Knowledge base service for RAG
            model_name: Gemini model name (defaults to config)
            temperature: Model temperature for generation
            use_rag: Whether to use RAG for knowledge grounding
        """
        self.kb_service = kb_service
        self.model_name = model_name
        self.temperature = temperature
        self.use_rag = use_rag
        
        # Initialize specialized chains
        logger.info("Initializing Design Engine specialized chains")
        
        self.initial_generation_chain = InitialGenerationChain(
            kb_service=kb_service,
            model_name=model_name,
            temperature=temperature,
            use_rag=use_rag,
        )
        
        self.tech_suggestion_chain = TechSuggestionChain(
            kb_service=kb_service,
            model_name=model_name,
            temperature=temperature,
            use_rag=use_rag,
        )
        
        self.decomposition_chain = DecompositionChain(
            kb_service=kb_service,
            model_name=model_name,
            temperature=temperature,
            use_rag=use_rag,
        )
        
        self.api_suggestion_chain = APISuggestionChain(
            kb_service=kb_service,
            model_name=model_name,
            temperature=temperature,
            use_rag=use_rag,
        )
        
        self.refactor_chain = RefactorChain(
            kb_service=kb_service,
            model_name=model_name,
            temperature=temperature,
            use_rag=use_rag,
        )
        
        logger.info("Design Engine initialized successfully")
    
    async def generate_initial_design(self, requirements: str) -> Dict[str, Any]:
        """
        Generate initial system design from user requirements.
        
        Creates the root SystemContext and immediate Container children.
        
        Args:
            requirements: User requirements as text
            
        Returns:
            Dictionary containing:
                - system_context: SystemContext definition
                - containers: List of Container definitions
                - design_rationale: Explanation of design decisions
        
        Example:
            >>> engine = DesignEngineService(kb_service=kb_service)
            >>> design = await engine.generate_initial_design(
            ...     "Build an e-commerce platform with user auth, product catalog, and payments"
            ... )
            >>> print(design['system_context']['name'])
            'E-Commerce Platform'
        """
        logger.info("Generating initial design from requirements")
        return await self.initial_generation_chain.generate_initial_design(requirements)
    
    async def suggest_technology(
        self,
        element_name: str,
        element_type: str,
        element_description: str,
        element_context: str = "",
    ) -> Dict[str, Any]:
        """
        Suggest technology stack for an architecture element.
        
        Args:
            element_name: Name of the element
            element_type: Type (container, component, etc.)
            element_description: Element description
            element_context: Additional context
            
        Returns:
            Dictionary containing:
                - primary_recommendation: Main technology recommendation
                - alternative_options: Alternative technologies
                - implementation_guidance: Setup and configuration tips
                - integration_considerations: Compatibility notes
        
        Example:
            >>> tech = await engine.suggest_technology(
            ...     element_name="User Service",
            ...     element_type="microservice",
            ...     element_description="Handles user authentication and profiles"
            ... )
            >>> print(tech['primary_recommendation']['technology'])
            'Node.js with Express'
        """
        logger.info(f"Suggesting technology for element: {element_name}")
        return await self.tech_suggestion_chain.suggest_technology(
            element_name=element_name,
            element_type=element_type,
            element_description=element_description,
            element_context=element_context,
        )
    
    async def suggest_sub_components(
        self,
        container_name: str,
        container_type: str,
        container_description: str,
        container_context: str = "",
    ) -> Dict[str, Any]:
        """
        Decompose a container into detailed components.
        
        Args:
            container_name: Name of the container
            container_type: Type of container
            container_description: Container description
            container_context: Additional context
            
        Returns:
            Dictionary containing:
                - components: List of component definitions
                - component_layers: Organization into architectural layers
                - internal_flows: Component interaction flows
                - design_patterns: Applied design patterns
        
        Example:
            >>> components = await engine.suggest_sub_components(
            ...     container_name="API Gateway",
            ...     container_type="web_application",
            ...     container_description="Main API entry point"
            ... )
            >>> print(len(components['components']))
            5
        """
        logger.info(f"Decomposing container: {container_name}")
        return await self.decomposition_chain.decompose_container(
            container_name=container_name,
            container_type=container_type,
            container_description=container_description,
            container_context=container_context,
        )
    
    async def suggest_api_endpoints(
        self,
        component_name: str,
        component_type: str,
        component_description: str,
        component_responsibilities: str,
        component_context: str = "",
    ) -> Dict[str, Any]:
        """
        Suggest API endpoints for a component.
        
        Args:
            component_name: Name of the component
            component_type: Type of component
            component_description: Component description
            component_responsibilities: Component responsibilities
            component_context: Additional context
            
        Returns:
            Dictionary containing:
                - api_base_path: Base API path
                - endpoints: List of endpoint definitions
                - authentication_schemes: Authentication methods
                - error_handling: Error handling strategy
                - rate_limiting: Rate limiting configuration
        
        Example:
            >>> api = await engine.suggest_api_endpoints(
            ...     component_name="User Controller",
            ...     component_type="controller",
            ...     component_description="User management",
            ...     component_responsibilities="CRUD operations for users"
            ... )
            >>> print(api['endpoints'][0]['path'])
            '/api/v1/users'
        """
        logger.info(f"Suggesting API endpoints for component: {component_name}")
        return await self.api_suggestion_chain.suggest_api_endpoints(
            component_name=component_name,
            component_type=component_type,
            component_description=component_description,
            component_responsibilities=component_responsibilities,
            component_context=component_context,
        )
    
    async def refactor_element(
        self,
        element_name: str,
        element_type: str,
        element_description: str,
        current_design: Dict[str, Any],
        refactor_request: str,
        element_context: str = "",
    ) -> Dict[str, Any]:
        """
        Refactor an architecture element based on user request.
        
        Args:
            element_name: Name of the element
            element_type: Type of element
            element_description: Element description
            current_design: Current design as dictionary
            refactor_request: User's refactoring request
            element_context: Additional context
            
        Returns:
            Dictionary containing:
                - refactored_element: Updated element design
                - rationale: Explanation of changes
                - migration_strategy: How to migrate
                - impact_analysis: Impact on other components
                - alternatives_considered: Alternative approaches
        
        Example:
            >>> refactored = await engine.refactor_element(
            ...     element_name="Auth Service",
            ...     element_type="microservice",
            ...     element_description="Authentication service",
            ...     current_design={"auth_method": "JWT"},
            ...     refactor_request="Add OAuth2 support"
            ... )
            >>> print(refactored['refactored_element']['changes_summary'])
            'Added OAuth2 provider integration'
        """
        logger.info(f"Refactoring element: {element_name}")
        return await self.refactor_chain.refactor_element(
            element_name=element_name,
            element_type=element_type,
            element_description=element_description,
            current_design=current_design,
            refactor_request=refactor_request,
            element_context=element_context,
        )
    
    def get_chain_info(self) -> Dict[str, Any]:
        """
        Get information about available chains.
        
        Returns:
            Dictionary describing available chains and their purposes
        """
        return {
            "engine_version": "1.0.0",
            "rag_enabled": self.use_rag,
            "model": self.model_name or "default",
            "chains": {
                "initial_generation": {
                    "purpose": "Generate initial SystemContext and Containers",
                    "input": "User requirements text",
                    "output": "System context and container definitions",
                },
                "tech_suggestion": {
                    "purpose": "Suggest technology stack for elements",
                    "input": "Element details",
                    "output": "Technology recommendations with rationale",
                },
                "decomposition": {
                    "purpose": "Decompose containers into components",
                    "input": "Container details",
                    "output": "Component definitions and relationships",
                },
                "api_suggestion": {
                    "purpose": "Suggest API endpoints for components",
                    "input": "Component details",
                    "output": "API specification with endpoints",
                },
                "refactor": {
                    "purpose": "Refactor elements based on feedback",
                    "input": "Element and refactor request",
                    "output": "Refactored design with migration plan",
                },
            },
        }
