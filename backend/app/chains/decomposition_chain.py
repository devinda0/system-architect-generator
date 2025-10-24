"""
Decomposition Chain

Decomposes containers into detailed components.
"""

from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnablePassthrough
import logging

from app.chains.base_chain import BaseDesignChain
from app.prompts.role_playing import RolePlayingPrompts

logger = logging.getLogger(__name__)


class DecompositionChain(BaseDesignChain):
    """
    Chain for decomposing containers into components.
    
    Breaks down high-level containers into:
    - Detailed components
    - Their responsibilities
    - Internal interactions
    - Data flows
    """
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Create the prompt template for decomposition."""
        
        system_prompt = RolePlayingPrompts.SYSTEM_ARCHITECT
        
        decomposition_prompt = """Let's decompose this container into components systematically:

🔍 Step 1: Analyze Container Responsibilities
Container: {container_name}
Type: {container_type}
Description: {container_description}
Context: {container_context}

- What are the main responsibilities?
- What business capabilities does it provide?
- What are the key workflows?

🧩 Step 2: Identify Components
- Break down responsibilities into cohesive components
- Follow Single Responsibility Principle
- Consider separation of concerns
- Think about maintainability and testability

🔗 Step 3: Define Component Interactions
- How do components communicate?
- What are the data flows?
- What are the dependencies?

📦 Step 4: Structure and Organization
- Group related components into modules/layers
- Define clear boundaries
- Plan for extensibility

{context}

Generate component decomposition in the following JSON format:

{{
  "components": [
    {{
      "id": "unique_component_id",
      "name": "Component Name",
      "type": "service|controller|repository|model|utility|facade|gateway",
      "description": "Component purpose and responsibilities",
      "responsibilities": ["responsibility1", "responsibility2"],
      "interfaces": [
        {{
          "name": "Interface/API name",
          "type": "public|internal",
          "methods": ["method1", "method2"]
        }}
      ],
      "dependencies": [
        {{
          "component_id": "other_component_id",
          "type": "uses|calls|depends_on",
          "description": "Why this dependency exists"
        }}
      ],
      "data_handled": ["data_type1", "data_type2"]
    }}
  ],
  "component_layers": {{
    "presentation": ["component_ids"],
    "business_logic": ["component_ids"],
    "data_access": ["component_ids"],
    "infrastructure": ["component_ids"]
  }},
  "internal_flows": [
    {{
      "name": "Flow name (e.g., User Authentication)",
      "steps": [
        {{
          "component": "component_id",
          "action": "What happens",
          "order": 1
        }}
      ]
    }}
  ],
  "design_patterns": [
    {{
      "pattern": "Pattern name (e.g., Repository, Factory, Strategy)",
      "applied_to": ["component_ids"],
      "rationale": "Why this pattern is used"
    }}
  ]
}}

Provide ONLY the JSON output, no additional text:"""

        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", decomposition_prompt),
        ])
    
    def _build_chain(self) -> Runnable:
        """Build the LCEL chain for decomposition."""
        
        prompt = self._create_prompt()
        
        async def add_context(inputs: Dict[str, Any]) -> Dict[str, Any]:
            """Add RAG context to inputs."""
            if self.use_rag and self.retriever:
                # Create a query for RAG
                query = f"{inputs.get('container_type', '')} component architecture design patterns best practices"
                context = await self._get_rag_context(query)
                return {
                    **inputs,
                    "context": f"\n--- Relevant Component Design Knowledge ---\n{context}\n" if context else ""
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
    
    async def decompose_container(
        self,
        container_name: str,
        container_type: str,
        container_description: str,
        container_context: str = "",
    ) -> Dict[str, Any]:
        """
        Decompose a container into components.
        
        Args:
            container_name: Name of the container
            container_type: Type of container
            container_description: Description of the container
            container_context: Additional context
            
        Returns:
            Dictionary containing components and their relationships
        """
        logger.info(f"Decomposing container: {container_name}")
        
        result = await self.ainvoke({
            "container_name": container_name,
            "container_type": container_type,
            "container_description": container_description,
            "container_context": container_context,
        })
        
        logger.info(f"Container decomposition completed for {container_name}")
        return result
