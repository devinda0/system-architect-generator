"""
Tests for Prompt Templates Library
"""

import pytest
from app.prompts import (
    RolePlayingPrompts,
    ChainOfThoughtPrompts,
    StructuredOutputPrompts,
)
from langchain_core.prompts import ChatPromptTemplate


class TestRolePlayingPrompts:
    """Tests for role-playing prompts."""
    
    def test_get_role_prompt_system_architect(self):
        """Test getting system architect role prompt."""
        prompt = RolePlayingPrompts.get_role_prompt('system_architect')
        assert 'System Architect' in prompt
        assert '15+' in prompt
        assert 'architecture patterns' in prompt.lower()
    
    def test_get_role_prompt_invalid(self):
        """Test getting invalid role raises error."""
        with pytest.raises(ValueError) as exc_info:
            RolePlayingPrompts.get_role_prompt('invalid_role')
        assert 'Unknown role' in str(exc_info.value)
    
    def test_list_available_roles(self):
        """Test listing available roles."""
        roles = RolePlayingPrompts.list_available_roles()
        assert isinstance(roles, dict)
        assert 'system_architect' in roles
        assert 'software_engineer' in roles
        assert 'devops_engineer' in roles
        assert len(roles) >= 7
    
    def test_create_role_template(self):
        """Test creating a role-based template."""
        template = RolePlayingPrompts.create_role_template(
            role='system_architect',
            user_template='Design a system for {requirement}'
        )
        assert isinstance(template, ChatPromptTemplate)
        
        # Test formatting
        messages = template.format_messages(requirement='e-commerce platform')
        assert len(messages) == 2  # system + human message
        assert 'System Architect' in messages[0].content
        assert 'e-commerce platform' in messages[1].content
    
    def test_create_custom_role_template(self):
        """Test creating a custom role template."""
        template = RolePlayingPrompts.create_custom_role_template(
            role_description='You are a testing expert',
            user_template='Create tests for {feature}'
        )
        assert isinstance(template, ChatPromptTemplate)
        
        messages = template.format_messages(feature='user authentication')
        assert 'testing expert' in messages[0].content
        assert 'user authentication' in messages[1].content
    
    def test_all_predefined_roles_accessible(self):
        """Test that all predefined roles can be accessed."""
        roles = [
            'system_architect',
            'software_engineer',
            'devops_engineer',
            'data_architect',
            'security_engineer',
            'cloud_architect',
            'technical_consultant',
        ]
        
        for role in roles:
            prompt = RolePlayingPrompts.get_role_prompt(role)
            assert isinstance(prompt, str)
            assert len(prompt) > 100  # Should be substantial


class TestChainOfThoughtPrompts:
    """Tests for chain-of-thought prompts."""
    
    def test_create_cot_template_basic(self):
        """Test creating basic COT template."""
        template = ChainOfThoughtPrompts.create_cot_template(
            template_type='basic'
        )
        assert isinstance(template, ChatPromptTemplate)
        
        messages = template.format_messages(
            question='How do I optimize database queries?'
        )
        assert 'step by step' in messages[0].content.lower()
    
    def test_create_cot_template_architecture(self):
        """Test creating architecture design COT template."""
        template = ChainOfThoughtPrompts.create_cot_template(
            template_type='architecture_design'
        )
        messages = template.format_messages(
            requirement='Build a scalable API'
        )
        assert 'Requirements Analysis' in messages[0].content
        assert 'scalable API' in messages[0].content
    
    def test_create_cot_template_invalid(self):
        """Test creating COT template with invalid type."""
        with pytest.raises(ValueError) as exc_info:
            ChainOfThoughtPrompts.create_cot_template(
                template_type='invalid_type'
            )
        assert 'Unknown template type' in str(exc_info.value)
    
    def test_list_available_templates(self):
        """Test listing available COT templates."""
        templates = ChainOfThoughtPrompts.list_available_templates()
        assert isinstance(templates, dict)
        assert 'basic' in templates
        assert 'architecture_design' in templates
        assert 'problem_solving' in templates
        assert 'technical_decision' in templates
        assert len(templates) >= 7
    
    def test_create_custom_cot(self):
        """Test creating custom COT template."""
        steps = [
            'Analyze the problem',
            'Generate solutions',
            'Select best option',
        ]
        template_str = ChainOfThoughtPrompts.create_custom_cot(
            steps=steps,
            question_var='problem'
        )
        
        assert 'Step 1: Analyze the problem' in template_str
        assert 'Step 2: Generate solutions' in template_str
        assert 'Step 3: Select best option' in template_str
        assert '{problem}' in template_str
    
    def test_all_cot_templates_have_steps(self):
        """Test that all COT templates include step-by-step reasoning."""
        template_types = [
            'basic',
            'architecture_design',
            'problem_solving',
            'technical_decision',
            'code_review',
            'debugging',
            'optimization',
        ]
        
        for template_type in template_types:
            template = ChainOfThoughtPrompts.create_cot_template(template_type)
            # Get the template string to check content
            messages = template.format_messages(**{
                'question': 'test',
                'requirement': 'test',
                'problem': 'test',
                'decision': 'test',
                'code': 'test',
                'issue': 'test',
                'target': 'test',
            })
            content = messages[0].content.lower()
            # Should mention steps or systematic approach
            assert 'step' in content or 'systematic' in content


class TestStructuredOutputPrompts:
    """Tests for structured output prompts."""
    
    def test_create_json_output_template(self):
        """Test creating JSON output template."""
        schema = {
            'name': 'string',
            'age': 'number',
            'active': 'boolean'
        }
        template = StructuredOutputPrompts.create_json_output_template(
            schema=schema
        )
        assert isinstance(template, ChatPromptTemplate)
        
        messages = template.format_messages(input='Generate user data')
        content = messages[0].content
        assert 'JSON' in content
        assert 'name' in content
        assert 'Generate user data' in content
    
    def test_create_structured_template_architecture(self):
        """Test creating architecture diagram template."""
        template = StructuredOutputPrompts.create_structured_template(
            template_type='architecture_diagram'
        )
        messages = template.format_messages(
            requirement='Build a microservices system'
        )
        content = messages[0].content
        assert 'components' in content
        assert 'connections' in content
        assert 'microservices system' in content
    
    def test_create_structured_template_api(self):
        """Test creating API specification template."""
        template = StructuredOutputPrompts.create_structured_template(
            template_type='api_specification'
        )
        messages = template.format_messages(
            requirement='REST API for user management'
        )
        content = messages[0].content
        assert 'endpoints' in content
        assert 'REST API' in content
    
    def test_create_structured_template_invalid(self):
        """Test creating template with invalid type."""
        with pytest.raises(ValueError) as exc_info:
            StructuredOutputPrompts.create_structured_template(
                template_type='invalid_type'
            )
        assert 'Unknown template' in str(exc_info.value)
    
    def test_list_available_templates(self):
        """Test listing available structured templates."""
        templates = StructuredOutputPrompts.list_available_templates()
        assert isinstance(templates, dict)
        assert 'json' in templates
        assert 'yaml' in templates
        assert 'architecture_diagram' in templates
        assert 'api_specification' in templates
        assert len(templates) >= 10
    
    def test_create_custom_json_template(self):
        """Test creating custom JSON template."""
        schema = {'field1': 'value1', 'field2': 'value2'}
        requirements = ['Valid JSON', 'Include all fields']
        
        template_str = StructuredOutputPrompts.create_custom_json_template(
            description='Generate custom data',
            schema=schema,
            requirements=requirements
        )
        
        assert 'Generate custom data' in template_str
        assert 'field1' in template_str
        assert 'Valid JSON' in template_str
        assert '{input}' in template_str
    
    def test_all_structured_templates_specify_format(self):
        """Test that all templates specify output format."""
        template_types = [
            'json',
            'yaml',
            'architecture_diagram',
            'api_specification',
            'database_schema',
            'comparison_table',
            'decision_matrix',
            'test_cases',
        ]
        
        for template_type in template_types:
            template = StructuredOutputPrompts.create_structured_template(
                template_type
            )
            messages = template.format_messages(**{
                'input': 'test',
                'requirement': 'test',
                'columns': 'test',
                'options': 'test',
                'decision': 'test',
                'feature': 'test',
                'yaml_schema': 'test',
                'json_schema': '{}',
            })
            content = messages[0].content.lower()
            # Should specify format or structure
            format_keywords = ['json', 'yaml', 'table', 'format', 'structure']
            assert any(keyword in content for keyword in format_keywords)


class TestIntegration:
    """Integration tests combining different prompt types."""
    
    def test_role_with_cot(self):
        """Test combining role-playing with chain-of-thought."""
        role_prompt = RolePlayingPrompts.get_role_prompt('system_architect')
        
        from langchain_core.prompts import ChatPromptTemplate
        template = ChatPromptTemplate.from_messages([
            ("system", role_prompt),
            ("human", ChainOfThoughtPrompts.ARCHITECTURE_DESIGN_COT),
        ])
        
        messages = template.format_messages(
            requirement='Build a scalable system'
        )
        assert len(messages) == 2
        assert 'System Architect' in messages[0].content
        assert 'Requirements Analysis' in messages[1].content
    
    def test_cot_with_structured_output(self):
        """Test combining COT with structured output."""
        # This would be done by appending structured output instructions
        # to a COT template
        cot = ChainOfThoughtPrompts.PROBLEM_SOLVING_COT
        structured = "\n\nProvide your final answer in JSON format with keys: problem, solution, steps"
        
        combined = cot + structured
        assert 'Problem Understanding' in combined
        assert 'JSON format' in combined


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
