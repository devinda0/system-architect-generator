"""
Structured Output Templates

This module provides templates for generating responses in specific structured formats
like JSON, YAML, Markdown tables, and other machine-readable formats.
"""

from typing import Optional, List, Dict, Any
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate


class StructuredOutputPrompts:
    """Collection of templates for generating structured outputs."""
    
    JSON_OUTPUT = """Generate a response in valid JSON format following this exact structure:

{json_schema}

Requirements:
- Output must be valid JSON
- Include all required fields
- Use appropriate data types
- Validate against the schema
- No additional text outside the JSON

Input:
{input}

Output the JSON only, with no additional explanation:"""

    YAML_OUTPUT = """Generate a response in valid YAML format following this structure:

{yaml_schema}

Requirements:
- Output must be valid YAML
- Use proper indentation (2 spaces)
- Include all required fields
- Follow YAML best practices
- No additional text outside the YAML

Input:
{input}

Output the YAML only:"""

    MARKDOWN_TABLE = """Generate a response as a Markdown table with the following columns:

{columns}

Requirements:
- Use proper Markdown table syntax
- Include a header row with column names
- Align columns appropriately
- Include all data rows
- Add a summary row if applicable

Input:
{input}

Output the Markdown table:"""

    ARCHITECTURE_DIAGRAM_JSON = """Generate a system architecture diagram description in JSON format.

Output Structure:
{{
  "title": "System Architecture Name",
  "components": [
    {{
      "id": "unique_id",
      "name": "Component Name",
      "type": "service|database|cache|queue|gateway|frontend|backend",
      "description": "Component description",
      "technology": "Technology stack",
      "responsibilities": ["responsibility1", "responsibility2"]
    }}
  ],
  "connections": [
    {{
      "from": "component_id",
      "to": "component_id",
      "type": "http|grpc|message|data_flow",
      "description": "Connection description",
      "protocol": "Protocol used"
    }}
  ],
  "external_systems": [
    {{
      "name": "External System Name",
      "type": "third_party|cloud_service|legacy",
      "integration_method": "Integration approach"
    }}
  ],
  "data_stores": [
    {{
      "name": "Database/Storage Name",
      "type": "relational|nosql|cache|object_storage",
      "purpose": "What data it stores",
      "technology": "Specific technology"
    }}
  ]
}}

Requirement:
{requirement}

Generate the architecture JSON:"""

    API_SPECIFICATION = """Generate an API specification in the following JSON format:

{{
  "api_name": "API Name",
  "version": "1.0.0",
  "base_url": "/api/v1",
  "endpoints": [
    {{
      "path": "/resource",
      "method": "GET|POST|PUT|DELETE|PATCH",
      "description": "Endpoint description",
      "parameters": [
        {{
          "name": "param_name",
          "type": "string|number|boolean|object|array",
          "required": true,
          "description": "Parameter description",
          "location": "query|path|body|header"
        }}
      ],
      "request_body": {{
        "content_type": "application/json",
        "schema": {{}},
        "example": {{}}
      }},
      "responses": [
        {{
          "status_code": 200,
          "description": "Success response",
          "schema": {{}},
          "example": {{}}
        }}
      ],
      "authentication": "none|api_key|bearer|oauth2",
      "rate_limit": "Requests per period"
    }}
  ]
}}

API Requirement:
{requirement}

Generate the API specification JSON:"""

    DATABASE_SCHEMA = """Generate a database schema in JSON format:

{{
  "database_name": "Database Name",
  "tables": [
    {{
      "name": "table_name",
      "description": "Table purpose",
      "columns": [
        {{
          "name": "column_name",
          "type": "VARCHAR(255)|INT|BIGINT|BOOLEAN|TIMESTAMP|JSON|TEXT",
          "nullable": false,
          "primary_key": false,
          "unique": false,
          "default": null,
          "description": "Column purpose"
        }}
      ],
      "indexes": [
        {{
          "name": "index_name",
          "columns": ["column1", "column2"],
          "type": "btree|hash|gin|gist",
          "unique": false
        }}
      ],
      "foreign_keys": [
        {{
          "column": "column_name",
          "references_table": "other_table",
          "references_column": "id",
          "on_delete": "CASCADE|SET NULL|RESTRICT",
          "on_update": "CASCADE|SET NULL|RESTRICT"
        }}
      ]
    }}
  ],
  "relationships": [
    {{
      "from_table": "table1",
      "to_table": "table2",
      "type": "one_to_one|one_to_many|many_to_many",
      "description": "Relationship description"
    }}
  ]
}}

Data Requirements:
{requirement}

Generate the database schema JSON:"""

    COMPARISON_TABLE = """Generate a comparison table in Markdown format comparing the given options.

Format:
| Feature | Option 1 | Option 2 | Option 3 |
|---------|----------|----------|----------|
| Feature 1 | Value | Value | Value |
| Feature 2 | Value | Value | Value |

Include these comparison aspects:
- Key features
- Performance characteristics
- Cost implications
- Ease of use
- Scalability
- Community support
- Best use cases
- Limitations

Options to compare:
{options}

Generate the comparison table:"""

    DECISION_MATRIX = """Generate a decision matrix in Markdown format.

Format:
| Criteria | Weight | Option 1 Score | Option 1 Weighted | Option 2 Score | Option 2 Weighted |
|----------|--------|----------------|-------------------|----------------|-------------------|
| Criteria 1 | X% | Score (1-10) | Calculated | Score (1-10) | Calculated |

Include:
- Clear criteria relevant to the decision
- Appropriate weights (must sum to 100%)
- Scores with brief justification
- Total weighted scores
- Recommendation based on results

Decision:
{decision}

Generate the decision matrix:"""

    TEST_CASES = """Generate test cases in JSON format:

{{
  "test_suite": "Suite Name",
  "feature": "Feature being tested",
  "test_cases": [
    {{
      "test_id": "TC001",
      "description": "What is being tested",
      "type": "unit|integration|e2e|performance|security",
      "priority": "high|medium|low",
      "preconditions": ["Condition 1", "Condition 2"],
      "steps": [
        {{
          "step_number": 1,
          "action": "Action to perform",
          "expected_result": "Expected outcome"
        }}
      ],
      "test_data": {{}},
      "expected_result": "Overall expected result",
      "assertions": ["Assertion 1", "Assertion 2"]
    }}
  ]
}}

Feature to test:
{feature}

Generate the test cases JSON:"""

    DEPLOYMENT_CONFIG = """Generate a deployment configuration in YAML format:

Structure:
```yaml
deployment:
  name: deployment-name
  environment: dev|staging|production
  
  infrastructure:
    provider: aws|azure|gcp|kubernetes
    region: region-name
    
  services:
    - name: service-name
      image: image:tag
      replicas: 3
      resources:
        cpu: 500m
        memory: 512Mi
      environment_variables:
        - name: VAR_NAME
          value: value
      health_check:
        path: /health
        interval: 30s
        
  networking:
    load_balancer: true
    ssl: true
    domains:
      - domain.com
      
  monitoring:
    enabled: true
    alerts:
      - metric: cpu_usage
        threshold: 80
        
  backup:
    enabled: true
    frequency: daily
```

Deployment Requirements:
{requirement}

Generate the deployment YAML:"""

    @classmethod
    def create_json_output_template(
        cls, 
        schema: Dict[str, Any], 
        input_var: str = "input"
    ) -> ChatPromptTemplate:
        """
        Create a template for JSON-formatted output.
        
        Args:
            schema: JSON schema describing the expected output structure
            input_var: Variable name for the input
            
        Returns:
            ChatPromptTemplate configured for JSON output
        """
        import json
        schema_str = json.dumps(schema, indent=2)
        # Escape curly braces in schema by doubling them for template
        schema_str = schema_str.replace("{", "{{").replace("}", "}}")
        return ChatPromptTemplate.from_template(
            cls.JSON_OUTPUT.replace("{json_schema}", schema_str)
        )
    
    @classmethod
    def create_structured_template(
        cls, 
        template_type: str, 
        **kwargs
    ) -> ChatPromptTemplate:
        """
        Create a structured output template.
        
        Args:
            template_type: Type of structured output
            **kwargs: Template variables
            
        Returns:
            ChatPromptTemplate for the specified structure
            
        Example:
            >>> template = StructuredOutputPrompts.create_structured_template(
            ...     template_type='architecture_diagram',
            ...     requirement='E-commerce platform'
            ... )
        """
        templates = {
            'json': cls.JSON_OUTPUT,
            'yaml': cls.YAML_OUTPUT,
            'markdown_table': cls.MARKDOWN_TABLE,
            'architecture_diagram': cls.ARCHITECTURE_DIAGRAM_JSON,
            'api_specification': cls.API_SPECIFICATION,
            'database_schema': cls.DATABASE_SCHEMA,
            'comparison_table': cls.COMPARISON_TABLE,
            'decision_matrix': cls.DECISION_MATRIX,
            'test_cases': cls.TEST_CASES,
            'deployment_config': cls.DEPLOYMENT_CONFIG,
        }
        
        if template_type not in templates:
            available = ', '.join(templates.keys())
            raise ValueError(f"Unknown template: {template_type}. Available: {available}")
        
        return ChatPromptTemplate.from_template(templates[template_type])
    
    @classmethod
    def create_custom_json_template(
        cls,
        description: str,
        schema: Dict[str, Any],
        requirements: Optional[List[str]] = None
    ) -> str:
        """
        Create a custom JSON output template.
        
        Args:
            description: Description of what should be generated
            schema: JSON schema for the output
            requirements: Additional requirements for the output
            
        Returns:
            Formatted template string
        """
        import json
        template = f"{description}\n\n"
        template += "Output Structure:\n"
        template += json.dumps(schema, indent=2)
        template += "\n\n"
        
        if requirements:
            template += "Requirements:\n"
            for req in requirements:
                template += f"- {req}\n"
            template += "\n"
        
        template += "Input:\n{input}\n\n"
        template += "Generate the JSON output:"
        
        return template
    
    @classmethod
    def list_available_templates(cls) -> Dict[str, str]:
        """
        List all available structured output templates.
        
        Returns:
            Dictionary mapping template types to descriptions
        """
        return {
            'json': 'Generic JSON formatted output',
            'yaml': 'Generic YAML formatted output',
            'markdown_table': 'Markdown table format',
            'architecture_diagram': 'System architecture in JSON',
            'api_specification': 'REST API specification in JSON',
            'database_schema': 'Database schema in JSON',
            'comparison_table': 'Feature comparison table',
            'decision_matrix': 'Decision-making matrix',
            'test_cases': 'Test cases in JSON format',
            'deployment_config': 'Deployment configuration in YAML',
        }
