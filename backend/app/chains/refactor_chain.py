"""
Refactor Chain

Refactors architecture elements based on user feedback and requests.
"""

from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnablePassthrough
import logging

from app.chains.base_chain import BaseDesignChain
from app.prompts.role_playing import RolePlayingPrompts

logger = logging.getLogger(__name__)


class RefactorChain(BaseDesignChain):
    """
    Chain for refactoring architecture elements.
    
    Handles:
    - User feedback incorporation
    - Design improvements
    - Optimization suggestions
    - Alternative approaches
    """
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Create the prompt template for refactoring."""
        
        system_prompt = RolePlayingPrompts.SYSTEM_ARCHITECT
        
        refactor_prompt = """Let's refactor this architecture element based on the user's request:

📋 Current Element:
Name: {element_name}
Type: {element_type}
Description: {element_description}
Current Design: {current_design}

🎯 Refactoring Request:
{refactor_request}

Additional Context: {element_context}

🔍 Step 1: Analyze Current Design
- What are the strengths of the current design?
- What are the limitations or issues?
- What aspects align with the refactor request?

💡 Step 2: Understand the Request
- What is the user trying to achieve?
- What problems are they trying to solve?
- Are there any implicit requirements?

🎨 Step 3: Design the Refactoring
- How can we address the user's concerns?
- What changes are needed?
- What will be the impact of these changes?
- Are there any risks or trade-offs?

✅ Step 4: Validate the Solution
- Does it solve the original problem?
- Does it maintain or improve existing functionality?
- Is it aligned with best practices?
- Are there any unintended consequences?

{context}

Generate the refactored design in the following JSON format:

{{
  "refactored_element": {{
    "name": "Updated element name (if changed)",
    "type": "Element type",
    "description": "Updated description",
    "changes_summary": "High-level summary of what changed",
    "updated_design": {{
      "structure": {{}},
      "key_changes": ["change1", "change2"],
      "new_features": ["feature1", "feature2"],
      "removed_features": ["removed1", "removed2"]
    }}
  }},
  "rationale": {{
    "why_changed": "Explanation of why changes were made",
    "benefits": ["benefit1", "benefit2"],
    "trade_offs": ["tradeoff1", "tradeoff2"],
    "risks": ["risk1", "risk2"]
  }},
  "migration_strategy": {{
    "approach": "How to migrate from old to new design",
    "steps": ["step1", "step2"],
    "considerations": ["consideration1", "consideration2"],
    "rollback_plan": "How to revert if needed"
  }},
  "impact_analysis": {{
    "affected_components": ["component1", "component2"],
    "breaking_changes": ["change1", "change2"],
    "compatibility_notes": ["note1", "note2"],
    "testing_recommendations": ["test1", "test2"]
  }},
  "alternatives_considered": [
    {{
      "approach": "Alternative approach name",
      "description": "What this approach would do",
      "pros": ["pro1", "pro2"],
      "cons": ["con1", "con2"],
      "why_not_chosen": "Reason for not selecting this"
    }}
  ],
  "implementation_guidance": {{
    "priority": "high|medium|low",
    "estimated_effort": "Effort estimation",
    "prerequisites": ["prerequisite1", "prerequisite2"],
    "next_steps": ["step1", "step2"]
  }}
}}

Provide ONLY the JSON output, no additional text:"""

        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", refactor_prompt),
        ])
    
    def _build_chain(self) -> Runnable:
        """Build the LCEL chain for refactoring."""
        
        prompt = self._create_prompt()
        
        async def add_context(inputs: Dict[str, Any]) -> Dict[str, Any]:
            """Add RAG context to inputs."""
            if self.use_rag and self.retriever:
                # Create a query based on the refactor request
                query = f"{inputs.get('element_type', '')} refactoring {inputs.get('refactor_request', '')} best practices"
                context = await self._get_rag_context(query)
                return {
                    **inputs,
                    "context": f"\n--- Relevant Refactoring Knowledge ---\n{context}\n" if context else ""
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
        Refactor an architecture element.
        
        Args:
            element_name: Name of the element
            element_type: Type of element
            element_description: Description of the element
            current_design: Current design as dictionary
            refactor_request: User's refactor request
            element_context: Additional context
            
        Returns:
            Dictionary containing refactored design
        """
        logger.info(f"Refactoring element: {element_name}")
        
        # Convert current_design to JSON string for the prompt
        import json
        current_design_str = json.dumps(current_design, indent=2)
        
        result = await self.ainvoke({
            "element_name": element_name,
            "element_type": element_type,
            "element_description": element_description,
            "current_design": current_design_str,
            "refactor_request": refactor_request,
            "element_context": element_context,
        })
        
        logger.info(f"Refactoring completed for {element_name}")
        return result
