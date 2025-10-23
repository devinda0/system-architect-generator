"""
Chain-of-Thought Templates

This module provides templates that guide the AI through step-by-step reasoning
processes for complex problem-solving and decision-making.
"""

from typing import Optional, List
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate


class ChainOfThoughtPrompts:
    """Collection of chain-of-thought prompts for structured reasoning."""
    
    BASIC_COT = """Let's approach this problem step by step:

1. First, let me understand the core requirements
2. Then, I'll identify the key challenges
3. Next, I'll explore possible solutions
4. Finally, I'll provide a recommendation with reasoning

Now, let's work through this systematically:

{question}"""

    ARCHITECTURE_DESIGN_COT = """Let's design this system architecture step by step:

Step 1: Requirements Analysis
- What are the functional requirements?
- What are the non-functional requirements (performance, scalability, security)?
- What are the constraints (budget, timeline, technology)?

Step 2: Component Identification
- What are the main components/services needed?
- How will they interact with each other?
- What are the data flows?

Step 3: Technology Selection
- What technologies are appropriate for each component?
- What are the pros and cons of each choice?
- How do they integrate together?

Step 4: Scalability and Performance
- How will the system handle growth?
- What are the potential bottlenecks?
- What caching/optimization strategies are needed?

Step 5: Security and Reliability
- What security measures are required?
- How will we ensure high availability?
- What disaster recovery plans are needed?

Step 6: Final Architecture
- Synthesize all considerations into a cohesive design
- Document trade-offs and alternatives
- Provide implementation roadmap

Now let's apply this to your requirement:
{requirement}"""

    PROBLEM_SOLVING_COT = """Let's solve this problem using a systematic approach:

🔍 Step 1: Problem Understanding
- What is the core problem we're trying to solve?
- What are the given constraints?
- What would success look like?

🧩 Step 2: Break Down the Problem
- What are the sub-problems?
- Are there any dependencies between them?
- Which parts are most critical?

💡 Step 3: Generate Solutions
- What are possible approaches?
- What are the trade-offs for each?
- Are there any proven patterns we can use?

⚖️ Step 4: Evaluate Options
- Compare solutions based on key criteria
- Consider short-term vs long-term implications
- Identify risks and mitigation strategies

✅ Step 5: Recommendation
- Select the best approach with clear justification
- Outline implementation steps
- Define success metrics

Problem to solve:
{problem}"""

    TECHNICAL_DECISION_COT = """Let's make this technical decision systematically:

📋 Step 1: Define Decision Criteria
- What are the must-have requirements?
- What are the nice-to-have features?
- What constraints must we work within?

🔎 Step 2: Identify Options
- What are all viable alternatives?
- What are the key differences between them?
- Are there any hybrid approaches?

📊 Step 3: Analyze Each Option
For each option, consider:
- Technical capabilities and limitations
- Learning curve and team expertise
- Community support and ecosystem
- Cost (licensing, infrastructure, maintenance)
- Scalability and performance characteristics
- Integration with existing systems
- Long-term viability and support

⚡ Step 4: Risk Assessment
- What risks does each option present?
- How likely are these risks?
- What are the mitigation strategies?

🎯 Step 5: Make Recommendation
- Select the best option with detailed reasoning
- Provide implementation considerations
- Suggest evaluation metrics

Decision to make:
{decision}"""

    CODE_REVIEW_COT = """Let's review this code systematically:

1️⃣ First Pass: Overall Structure
- Is the code well-organized and modular?
- Does it follow appropriate design patterns?
- Is the architecture sound?

2️⃣ Second Pass: Code Quality
- Is the code readable and maintainable?
- Are variables and functions well-named?
- Is there appropriate commenting/documentation?

3️⃣ Third Pass: Logic and Correctness
- Does the code do what it's supposed to do?
- Are there any logical errors or edge cases?
- Is error handling appropriate?

4️⃣ Fourth Pass: Performance
- Are there any obvious performance issues?
- Is the algorithm efficient?
- Are resources managed properly?

5️⃣ Fifth Pass: Security
- Are there any security vulnerabilities?
- Is input validation adequate?
- Are sensitive data handled properly?

6️⃣ Final Assessment
- Summary of findings
- Priority of issues (critical, major, minor)
- Specific recommendations for improvement

Code to review:
{code}"""

    DEBUGGING_COT = """Let's debug this issue step by step:

🐛 Step 1: Understand the Issue
- What is the expected behavior?
- What is the actual behavior?
- When did this issue first occur?

🔍 Step 2: Gather Information
- What error messages or logs are available?
- Can the issue be reproduced consistently?
- What changed recently that might be related?

🧪 Step 3: Form Hypotheses
- What are the most likely causes?
- Can we eliminate any possibilities?
- Are there similar known issues?

🔬 Step 4: Test Hypotheses
- How can we verify each hypothesis?
- What experiments or checks can we perform?
- What would prove or disprove each theory?

🛠️ Step 5: Identify Root Cause
- What is the underlying problem?
- Why did it occur?
- Are there related issues?

✨ Step 6: Solution and Prevention
- How can we fix the immediate issue?
- How can we prevent this in the future?
- What monitoring or tests should we add?

Issue to debug:
{issue}"""

    OPTIMIZATION_COT = """Let's optimize this systematically:

📊 Step 1: Baseline Measurement
- What are the current performance metrics?
- Where are the bottlenecks?
- What are the optimization goals?

🎯 Step 2: Identify Optimization Targets
- Which areas have the most impact?
- What is the effort vs benefit ratio?
- Are there quick wins available?

🔧 Step 3: Optimization Strategies
For each target:
- What optimization techniques apply?
- What are the trade-offs?
- How much improvement can we expect?

⚡ Step 4: Implementation Plan
- Prioritize optimizations by impact/effort
- Define measurable success criteria
- Plan validation and testing

✅ Step 5: Validation
- How will we measure improvements?
- Are there any negative side effects?
- Did we meet our goals?

Area to optimize:
{target}"""

    @classmethod
    def create_cot_template(cls, template_type: str, **kwargs) -> ChatPromptTemplate:
        """
        Create a chain-of-thought prompt template.
        
        Args:
            template_type: Type of COT template to use
            **kwargs: Additional template variables
            
        Returns:
            ChatPromptTemplate configured with the specified COT approach
            
        Example:
            >>> template = ChainOfThoughtPrompts.create_cot_template(
            ...     template_type='architecture_design',
            ...     requirement='Build a scalable e-commerce platform'
            ... )
        """
        templates = {
            'basic': cls.BASIC_COT,
            'architecture_design': cls.ARCHITECTURE_DESIGN_COT,
            'problem_solving': cls.PROBLEM_SOLVING_COT,
            'technical_decision': cls.TECHNICAL_DECISION_COT,
            'code_review': cls.CODE_REVIEW_COT,
            'debugging': cls.DEBUGGING_COT,
            'optimization': cls.OPTIMIZATION_COT,
        }
        
        if template_type not in templates:
            available = ', '.join(templates.keys())
            raise ValueError(f"Unknown template type: {template_type}. Available: {available}")
        
        template = templates[template_type]
        return ChatPromptTemplate.from_template(template)
    
    @classmethod
    def create_custom_cot(cls, steps: List[str], question_var: str = "question") -> str:
        """
        Create a custom chain-of-thought template with specified steps.
        
        Args:
            steps: List of step descriptions
            question_var: Variable name for the question/input
            
        Returns:
            Formatted COT template string
            
        Example:
            >>> steps = [
            ...     "Analyze the input",
            ...     "Identify patterns",
            ...     "Generate solution"
            ... ]
            >>> template = ChainOfThoughtPrompts.create_custom_cot(steps)
        """
        cot = "Let's approach this step by step:\n\n"
        for i, step in enumerate(steps, 1):
            cot += f"Step {i}: {step}\n"
        cot += f"\nNow let's apply this process:\n{{{question_var}}}"
        return cot
    
    @classmethod
    def list_available_templates(cls) -> dict:
        """
        List all available COT template types.
        
        Returns:
            Dictionary mapping template types to descriptions
        """
        return {
            'basic': 'General purpose step-by-step reasoning',
            'architecture_design': 'Systematic approach to system architecture design',
            'problem_solving': 'Structured problem decomposition and solution',
            'technical_decision': 'Framework for making technical decisions',
            'code_review': 'Comprehensive code review process',
            'debugging': 'Systematic debugging methodology',
            'optimization': 'Performance optimization approach',
        }
