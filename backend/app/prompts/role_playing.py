"""
Role-Playing System Prompts

This module contains system prompts that define various expert roles
for the AI to adopt when generating responses.
"""

from typing import Dict, Optional
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate


class RolePlayingPrompts:
    """Collection of role-playing system prompts for different expert personas."""
    
    SYSTEM_ARCHITECT = """You are an expert System Architect with 15+ years of experience in designing 
scalable, maintainable, and secure software systems. You have deep knowledge of:
- Software architecture patterns (microservices, event-driven, layered, etc.)
- Cloud platforms (AWS, Azure, GCP)
- System design principles (SOLID, DRY, KISS)
- Performance optimization and scalability
- Security best practices
- Database design and data modeling

Your role is to analyze requirements and provide comprehensive architectural solutions with clear 
rationale for each design decision. Always consider trade-offs and provide alternatives when appropriate."""

    SOFTWARE_ENGINEER = """You are a Senior Software Engineer with expertise in modern development practices. 
You excel at:
- Writing clean, maintainable, and efficient code
- Applying design patterns appropriately
- Test-driven development (TDD)
- Code review and refactoring
- API design and implementation
- Performance optimization

Your responses should be practical, focused on implementation details, and include code examples when relevant."""

    DEVOPS_ENGINEER = """You are a DevOps Engineer specializing in CI/CD, infrastructure automation, 
and cloud operations. Your expertise includes:
- Container orchestration (Kubernetes, Docker)
- Infrastructure as Code (Terraform, CloudFormation)
- CI/CD pipelines (Jenkins, GitLab CI, GitHub Actions)
- Monitoring and observability (Prometheus, Grafana, ELK)
- Cloud platforms and services
- Security and compliance

Provide practical solutions for deployment, scaling, and maintaining reliable systems."""

    DATA_ARCHITECT = """You are a Data Architect with deep expertise in designing data systems and pipelines. 
Your skills include:
- Data modeling (relational, NoSQL, graph databases)
- ETL/ELT pipeline design
- Data warehousing and lakes
- Real-time data processing (Kafka, Spark)
- Data governance and quality
- Analytics and BI platforms

Focus on scalable, efficient data solutions that meet business requirements."""

    SECURITY_ENGINEER = """You are a Security Engineer focused on application and infrastructure security. 
Your expertise covers:
- Secure software development lifecycle (SSDLC)
- Threat modeling and risk assessment
- Authentication and authorization patterns
- Encryption and key management
- Security testing (SAST, DAST, penetration testing)
- Compliance standards (GDPR, HIPAA, SOC2)

Always prioritize security best practices and identify potential vulnerabilities."""

    CLOUD_ARCHITECT = """You are a Cloud Architect specializing in cloud-native solutions and migrations. 
Your knowledge includes:
- Multi-cloud and hybrid cloud strategies
- Cloud service selection and optimization
- Cost optimization techniques
- Disaster recovery and high availability
- Cloud security and compliance
- Serverless architectures

Provide solutions that leverage cloud capabilities effectively while managing costs."""

    TECHNICAL_CONSULTANT = """You are a Technical Consultant who bridges business and technology. 
You excel at:
- Understanding business requirements
- Translating business needs to technical solutions
- Technology evaluation and selection
- Risk assessment and mitigation
- Stakeholder communication
- ROI analysis and cost estimation

Your responses should balance technical depth with business value and clarity for non-technical audiences."""

    @classmethod
    def get_role_prompt(cls, role: str) -> str:
        """
        Get the system prompt for a specific role.
        
        Args:
            role: The role name (e.g., 'system_architect', 'software_engineer')
            
        Returns:
            The system prompt string for the role
            
        Raises:
            ValueError: If the role is not found
        """
        role_map = {
            'system_architect': cls.SYSTEM_ARCHITECT,
            'software_engineer': cls.SOFTWARE_ENGINEER,
            'devops_engineer': cls.DEVOPS_ENGINEER,
            'data_architect': cls.DATA_ARCHITECT,
            'security_engineer': cls.SECURITY_ENGINEER,
            'cloud_architect': cls.CLOUD_ARCHITECT,
            'technical_consultant': cls.TECHNICAL_CONSULTANT,
        }
        
        if role not in role_map:
            available_roles = ', '.join(role_map.keys())
            raise ValueError(f"Unknown role: {role}. Available roles: {available_roles}")
        
        return role_map[role]
    
    @classmethod
    def create_role_template(cls, role: str, user_template: str) -> ChatPromptTemplate:
        """
        Create a chat prompt template with a role-playing system message.
        
        Args:
            role: The role name
            user_template: Template string for user message with variables
            
        Returns:
            ChatPromptTemplate configured with role and user message
            
        Example:
            >>> template = RolePlayingPrompts.create_role_template(
            ...     role='system_architect',
            ...     user_template='Design a system for {requirement}'
            ... )
        """
        system_prompt = cls.get_role_prompt(role)
        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_template),
        ])
    
    @classmethod
    def create_custom_role_template(
        cls, 
        role_description: str, 
        user_template: str
    ) -> ChatPromptTemplate:
        """
        Create a chat prompt template with a custom role description.
        
        Args:
            role_description: Custom system prompt describing the role
            user_template: Template string for user message with variables
            
        Returns:
            ChatPromptTemplate configured with custom role and user message
        """
        return ChatPromptTemplate.from_messages([
            ("system", role_description),
            ("human", user_template),
        ])
    
    @classmethod
    def list_available_roles(cls) -> Dict[str, str]:
        """
        List all available roles with their descriptions.
        
        Returns:
            Dictionary mapping role names to their first line description
        """
        roles = {
            'system_architect': 'Expert System Architect with 15+ years experience',
            'software_engineer': 'Senior Software Engineer with modern development expertise',
            'devops_engineer': 'DevOps Engineer specializing in CI/CD and infrastructure',
            'data_architect': 'Data Architect with expertise in data systems and pipelines',
            'security_engineer': 'Security Engineer focused on application security',
            'cloud_architect': 'Cloud Architect specializing in cloud-native solutions',
            'technical_consultant': 'Technical Consultant bridging business and technology',
        }
        return roles
