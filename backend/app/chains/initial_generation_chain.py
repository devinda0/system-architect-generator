"""
Initial Generation Chain

Generates the initial SystemContext and high-level Containers from user requirements.
"""

from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnablePassthrough
import logging

from app.chains.base_chain import BaseDesignChain
from app.prompts.role_playing import RolePlayingPrompts
from app.prompts.chain_of_thought import ChainOfThoughtPrompts

logger = logging.getLogger(__name__)


class InitialGenerationChain(BaseDesignChain):
    """
    Chain for generating initial system architecture from requirements.
    
    This chain creates:
    - SystemContext: The overall system and its external interactions
    - Containers: High-level containers (applications, databases, etc.)
    """
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Create the prompt template for initial generation."""
        
        system_prompt = RolePlayingPrompts.SYSTEM_ARCHITECT
        
        architecture_cot = """Let's design this system architecture step by step:

Step 1: Requirements Analysis
- Analyze the functional requirements
- Identify non-functional requirements (scalability, security, performance)
- Note any constraints or preferences

Step 2: System Context
- Define the system boundary
- Identify external actors (users, external systems)
- Define key interactions and integrations

Step 3: Container Architecture
- Identify major containers (web apps, mobile apps, APIs, databases)
- Define their primary responsibilities
- Plan their interactions

Step 4: Technology Considerations
- Consider appropriate technology choices
- Ensure compatibility and integration
- Balance performance, cost, and maintainability

Now, let's analyze the requirements:

Requirements:
{requirements}

{context}

Generate a complete system architecture in the following JSON format:

{{
  "system_context": {{
    "name": "System Name",
    "description": "High-level description of the system",
    "external_actors": [
      {{
        "name": "Actor Name",
        "type": "user|external_system|third_party",
        "description": "Actor description"
      }}
    ],
    "key_features": ["feature1", "feature2"]
  }},
  "containers": [
    {{
      "id": "unique_container_id",
      "name": "Container Name",
      "type": "web_application|mobile_app|api|database|message_broker|cache",
      "description": "Container purpose and responsibilities",
      "technology_suggestions": ["tech1", "tech2"],
      "interactions": [
        {{
          "target": "other_container_id",
          "type": "http|grpc|message|data",
          "description": "Interaction description"
        }}
      ]
    }}
  ],
  "design_rationale": {{
    "architecture_pattern": "Pattern used (e.g., Microservices, Monolithic, Event-Driven)",
    "key_decisions": ["decision1", "decision2"],
    "trade_offs": ["tradeoff1", "tradeoff2"]
  }}
}}

Provide ONLY the JSON output, no additional text:"""

        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", architecture_cot),
        ])
    
    def _build_chain(self) -> Runnable:
        """Build the LCEL chain for initial generation."""
        
        prompt = self._create_prompt()
        
        async def add_context(inputs: Dict[str, Any]) -> Dict[str, Any]:
            """Add RAG context to inputs."""
            if self.use_rag and self.retriever:
                requirements = inputs.get("requirements", "")
                context = await self._get_rag_context(requirements)
                return {
                    **inputs,
                    "context": f"\n--- Relevant Knowledge Base Context ---\n{context}\n" if context else ""
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
    
    async def generate_initial_design(self, requirements: str) -> Dict[str, Any]:
        """
        Generate initial system design from requirements.
        
        Args:
            requirements: User requirements as text
            
        Returns:
            Dictionary containing system_context and containers
        """
        logger.info("Generating initial system design")
        
        result = await self.ainvoke({
            "requirements": requirements
        })
        
        logger.info("Initial system design generated successfully")
        return result
