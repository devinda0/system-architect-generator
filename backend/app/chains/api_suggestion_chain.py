"""
API Suggestion Chain

Suggests API endpoints and specifications for components.
"""

from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnablePassthrough
import logging

from app.chains.base_chain import BaseDesignChain
from app.prompts.role_playing import RolePlayingPrompts

logger = logging.getLogger(__name__)


class APISuggestionChain(BaseDesignChain):
    """
    Chain for suggesting API endpoints for components.
    
    Generates:
    - RESTful API endpoints
    - Request/response schemas
    - Authentication requirements
    - Rate limiting considerations
    """
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Create the prompt template for API suggestion."""
        
        system_prompt = RolePlayingPrompts.SYSTEM_ARCHITECT
        
        api_design_prompt = """Let's design API endpoints for this component:

📋 Component Information:
Component: {component_name}
Type: {component_type}
Description: {component_description}
Responsibilities: {component_responsibilities}
Context: {component_context}

🎯 Step 1: Identify API Requirements
- What resources does this component manage?
- What operations are needed (CRUD, custom actions)?
- Who are the consumers of this API?
- What are the security requirements?

📐 Step 2: Design RESTful Endpoints
- Follow REST best practices
- Use appropriate HTTP methods
- Design clear, consistent URL patterns
- Plan for versioning

📝 Step 3: Define Request/Response Schemas
- What data is needed for each operation?
- What validation is required?
- What should be returned?
- Plan for error responses

🔒 Step 4: Security and Performance
- What authentication is needed?
- What rate limiting is appropriate?
- What caching strategies can be used?
- What monitoring is required?

{context}

Generate API specification in the following JSON format:

{{
  "api_base_path": "/api/v1/resource",
  "endpoints": [
    {{
      "path": "/resource",
      "method": "GET|POST|PUT|DELETE|PATCH",
      "summary": "Brief description",
      "description": "Detailed description of what this endpoint does",
      "parameters": [
        {{
          "name": "param_name",
          "in": "query|path|header|body",
          "type": "string|number|boolean|array|object",
          "required": true,
          "description": "Parameter description",
          "example": "example_value"
        }}
      ],
      "request_body": {{
        "required": true,
        "content_type": "application/json",
        "schema": {{
          "type": "object",
          "properties": {{}},
          "required": []
        }},
        "example": {{}}
      }},
      "responses": {{
        "200": {{
          "description": "Success response",
          "schema": {{}},
          "example": {{}}
        }},
        "400": {{
          "description": "Bad request",
          "example": {{"error": "Validation failed"}}
        }},
        "401": {{
          "description": "Unauthorized",
          "example": {{"error": "Authentication required"}}
        }},
        "500": {{
          "description": "Server error",
          "example": {{"error": "Internal server error"}}
        }}
      }},
      "authentication": "none|api_key|bearer_token|oauth2",
      "rate_limit": "100 requests per minute",
      "tags": ["tag1", "tag2"]
    }}
  ],
  "authentication_schemes": [
    {{
      "type": "bearer",
      "description": "JWT authentication",
      "implementation_notes": ["Use JWT tokens", "Tokens expire in 1 hour"]
    }}
  ],
  "error_handling": {{
    "standard_errors": [
      {{
        "code": "ERROR_CODE",
        "message": "Error message",
        "http_status": 400
      }}
    ],
    "error_response_format": {{
      "error": "Error code",
      "message": "Human readable message",
      "details": {{}},
      "timestamp": "ISO 8601 timestamp"
    }}
  }},
  "versioning_strategy": "URL path versioning (/api/v1, /api/v2)",
  "rate_limiting": {{
    "strategy": "Token bucket",
    "limits": {{
      "default": "100 requests per minute",
      "authenticated": "1000 requests per minute"
    }}
  }},
  "documentation_url": "/api/v1/docs",
  "openapi_spec_url": "/api/v1/openapi.json"
}}

Provide ONLY the JSON output, no additional text:"""

        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", api_design_prompt),
        ])
    
    def _build_chain(self) -> Runnable:
        """Build the LCEL chain for API suggestion."""
        
        prompt = self._create_prompt()
        
        async def add_context(inputs: Dict[str, Any]) -> Dict[str, Any]:
            """Add RAG context to inputs."""
            if self.use_rag and self.retriever:
                # Create a query for RAG
                query = f"RESTful API design best practices {inputs.get('component_type', '')} endpoints"
                context = await self._get_rag_context(query)
                return {
                    **inputs,
                    "context": f"\n--- Relevant API Design Knowledge ---\n{context}\n" if context else ""
                }
            return {**inputs, "context": ""}
        
        # Build chain: Add Context -> Prompt -> LLM -> Parser
        chain = (
            RunnablePassthrough.assign(context=add_context)
            | prompt
            | self.llm
            | self.output_parser
        )
        
        return chain
    
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
            component_description: Description of the component
            component_responsibilities: Component responsibilities
            component_context: Additional context
            
        Returns:
            Dictionary containing API specifications
        """
        logger.info(f"Suggesting API endpoints for {component_name}")
        
        result = await self.ainvoke({
            "component_name": component_name,
            "component_type": component_type,
            "component_description": component_description,
            "component_responsibilities": component_responsibilities,
            "component_context": component_context,
        })
        
        logger.info(f"API suggestion completed for {component_name}")
        return result
