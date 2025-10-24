"""
Technology Suggestion Chain

Suggests appropriate technology stack for architecture elements.
"""

from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnablePassthrough
import logging

from app.chains.base_chain import BaseDesignChain
from app.prompts.role_playing import RolePlayingPrompts
from app.prompts.chain_of_thought import ChainOfThoughtPrompts

logger = logging.getLogger(__name__)


class TechSuggestionChain(BaseDesignChain):
    """
    Chain for suggesting technology stack for architecture elements.
    
    Recommends specific technologies based on:
    - Element type and responsibilities
    - Project requirements
    - Industry best practices
    - Compatibility with other components
    """
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Create the prompt template for technology suggestion."""
        
        system_prompt = RolePlayingPrompts.SYSTEM_ARCHITECT
        
        tech_decision_prompt = """Let's make this technical decision systematically:

📋 Step 1: Understand Requirements
- What is the element type and its responsibilities?
- What are the performance, scalability, and security needs?
- What constraints exist (budget, team expertise, existing infrastructure)?

🔎 Step 2: Identify Technology Options
- List viable technology options for this element
- Consider both established and modern technologies
- Think about the ecosystem and community support

📊 Step 3: Evaluate Each Option
For each technology option, consider:
- Performance characteristics
- Scalability potential
- Learning curve and team expertise
- Community support and documentation
- Integration capabilities
- Cost (licensing, infrastructure, maintenance)
- Long-term viability

⚖️ Step 4: Make Recommendation
- Select the best option with clear justification
- Explain trade-offs
- Provide alternative options
- Include implementation considerations

Element Information:
Element Name: {element_name}
Element Type: {element_type}
Description: {element_description}
Current Context: {element_context}

{context}

Generate your technology recommendation in the following JSON format:

{{
  "primary_recommendation": {{
    "technology": "Technology Name",
    "version": "Recommended version",
    "rationale": "Why this technology is recommended",
    "pros": ["advantage1", "advantage2"],
    "cons": ["limitation1", "limitation2"],
    "use_cases": ["When to use this technology"]
  }},
  "alternative_options": [
    {{
      "technology": "Alternative Technology",
      "version": "Version",
      "rationale": "Why this is a good alternative",
      "when_to_choose": "Scenarios where this is better"
    }}
  ],
  "implementation_guidance": {{
    "setup_steps": ["step1", "step2"],
    "dependencies": ["dependency1", "dependency2"],
    "configuration_tips": ["tip1", "tip2"],
    "best_practices": ["practice1", "practice2"]
  }},
  "integration_considerations": {{
    "compatibility": ["Compatible with X", "Works well with Y"],
    "potential_issues": ["Watch out for Z"],
    "monitoring_recommendations": ["Monitor A", "Track B"]
  }}
}}

Provide ONLY the JSON output, no additional text:"""

        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", tech_decision_prompt),
        ])
    
    def _build_chain(self) -> Runnable:
        """Build the LCEL chain for technology suggestion."""
        
        prompt = self._create_prompt()
        
        async def add_context(inputs: Dict[str, Any]) -> Dict[str, Any]:
            """Add RAG context to inputs."""
            if self.use_rag and self.retriever:
                # Create a query combining element info for better RAG results
                query = f"{inputs.get('element_type', '')} {inputs.get('element_name', '')} technology stack best practices"
                context = await self._get_rag_context(query)
                return {
                    **inputs,
                    "context": f"\n--- Relevant Technology Knowledge ---\n{context}\n" if context else ""
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
    
    async def suggest_technology(
        self,
        element_name: str,
        element_type: str,
        element_description: str,
        element_context: str = "",
    ) -> Dict[str, Any]:
        """
        Suggest technology for an architecture element.
        
        Args:
            element_name: Name of the element
            element_type: Type of element (container, component, etc.)
            element_description: Description of the element
            element_context: Additional context about the element
            
        Returns:
            Dictionary containing technology recommendations
        """
        logger.info(f"Suggesting technology for {element_name} ({element_type})")
        
        result = await self.ainvoke({
            "element_name": element_name,
            "element_type": element_type,
            "element_description": element_description,
            "element_context": element_context,
        })
        
        logger.info(f"Technology suggestion completed for {element_name}")
        return result
