"""
Tests for Design Engine Service and Chains

Tests the specialized chains and Design Engine service.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from app.services.design_engine_service import DesignEngineService
from app.chains.initial_generation_chain import InitialGenerationChain
from app.chains.tech_suggestion_chain import TechSuggestionChain
from app.chains.decomposition_chain import DecompositionChain
from app.chains.api_suggestion_chain import APISuggestionChain
from app.chains.refactor_chain import RefactorChain


@pytest.fixture
def mock_kb_service():
    """Mock knowledge base service."""
    mock = Mock()
    mock.get_context = AsyncMock(return_value=Mock(
        relevant_documents=[],
        query_used="test query"
    ))
    return mock


@pytest.fixture
def design_engine(mock_kb_service):
    """Design engine service instance."""
    return DesignEngineService(
        kb_service=mock_kb_service,
        use_rag=False,  # Disable RAG for faster tests
        temperature=0.7
    )


class TestDesignEngineService:
    """Tests for DesignEngineService."""
    
    def test_initialization(self, design_engine):
        """Test that design engine initializes correctly."""
        assert design_engine is not None
        assert design_engine.initial_generation_chain is not None
        assert design_engine.tech_suggestion_chain is not None
        assert design_engine.decomposition_chain is not None
        assert design_engine.api_suggestion_chain is not None
        assert design_engine.refactor_chain is not None
    
    def test_get_chain_info(self, design_engine):
        """Test getting chain information."""
        info = design_engine.get_chain_info()
        
        assert "engine_version" in info
        assert "rag_enabled" in info
        assert "chains" in info
        assert "initial_generation" in info["chains"]
        assert "tech_suggestion" in info["chains"]
        assert "decomposition" in info["chains"]
        assert "api_suggestion" in info["chains"]
        assert "refactor" in info["chains"]
    
    @pytest.mark.asyncio
    async def test_generate_initial_design_mock(self, design_engine):
        """Test initial design generation with mocked LLM."""
        mock_result = {
            "system_context": {
                "name": "E-Commerce Platform",
                "description": "Online shopping system",
                "external_actors": [
                    {"name": "Customer", "type": "user", "description": "Shops online"}
                ],
                "key_features": ["Shopping", "Payments"]
            },
            "containers": [
                {
                    "id": "web_app",
                    "name": "Web Application",
                    "type": "web_application",
                    "description": "Customer-facing web app",
                    "technology_suggestions": ["React", "Next.js"],
                    "interactions": []
                }
            ],
            "design_rationale": {
                "architecture_pattern": "Microservices",
                "key_decisions": ["Scalability"],
                "trade_offs": ["Complexity"]
            }
        }
        
        # Mock the chain's ainvoke method
        with patch.object(
            design_engine.initial_generation_chain,
            'ainvoke',
            return_value=mock_result
        ):
            result = await design_engine.generate_initial_design(
                "Build an e-commerce platform"
            )
            
            assert result is not None
            assert "system_context" in result
            assert "containers" in result
            assert result["system_context"]["name"] == "E-Commerce Platform"
    
    @pytest.mark.asyncio
    async def test_suggest_technology_mock(self, design_engine):
        """Test technology suggestion with mocked LLM."""
        mock_result = {
            "primary_recommendation": {
                "technology": "PostgreSQL",
                "version": "15",
                "rationale": "Reliable relational database",
                "pros": ["ACID compliance", "Mature"],
                "cons": ["Horizontal scaling complexity"],
                "use_cases": ["Transactional data"]
            },
            "alternative_options": [],
            "implementation_guidance": {
                "setup_steps": ["Install", "Configure"],
                "dependencies": ["libpq"],
                "configuration_tips": ["Set max_connections"],
                "best_practices": ["Use connection pooling"]
            },
            "integration_considerations": {
                "compatibility": ["Works with Node.js"],
                "potential_issues": ["Connection limits"],
                "monitoring_recommendations": ["Monitor connections"]
            }
        }
        
        with patch.object(
            design_engine.tech_suggestion_chain,
            'ainvoke',
            return_value=mock_result
        ):
            result = await design_engine.suggest_technology(
                element_name="User Database",
                element_type="database",
                element_description="Stores user data"
            )
            
            assert result is not None
            assert "primary_recommendation" in result
            assert result["primary_recommendation"]["technology"] == "PostgreSQL"


class TestInitialGenerationChain:
    """Tests for InitialGenerationChain."""
    
    def test_chain_initialization(self, mock_kb_service):
        """Test chain initializes correctly."""
        chain = InitialGenerationChain(
            kb_service=mock_kb_service,
            use_rag=False
        )
        
        assert chain is not None
        assert chain.llm is not None
        assert chain.output_parser is not None
    
    def test_create_prompt(self, mock_kb_service):
        """Test prompt creation."""
        chain = InitialGenerationChain(
            kb_service=mock_kb_service,
            use_rag=False
        )
        
        prompt = chain._create_prompt()
        assert prompt is not None


class TestTechSuggestionChain:
    """Tests for TechSuggestionChain."""
    
    def test_chain_initialization(self, mock_kb_service):
        """Test chain initializes correctly."""
        chain = TechSuggestionChain(
            kb_service=mock_kb_service,
            use_rag=False
        )
        
        assert chain is not None
        assert chain.llm is not None
    
    def test_create_prompt(self, mock_kb_service):
        """Test prompt creation."""
        chain = TechSuggestionChain(
            kb_service=mock_kb_service,
            use_rag=False
        )
        
        prompt = chain._create_prompt()
        assert prompt is not None


class TestDecompositionChain:
    """Tests for DecompositionChain."""
    
    def test_chain_initialization(self, mock_kb_service):
        """Test chain initializes correctly."""
        chain = DecompositionChain(
            kb_service=mock_kb_service,
            use_rag=False
        )
        
        assert chain is not None
        assert chain.llm is not None
    
    def test_create_prompt(self, mock_kb_service):
        """Test prompt creation."""
        chain = DecompositionChain(
            kb_service=mock_kb_service,
            use_rag=False
        )
        
        prompt = chain._create_prompt()
        assert prompt is not None


class TestAPISuggestionChain:
    """Tests for APISuggestionChain."""
    
    def test_chain_initialization(self, mock_kb_service):
        """Test chain initializes correctly."""
        chain = APISuggestionChain(
            kb_service=mock_kb_service,
            use_rag=False
        )
        
        assert chain is not None
        assert chain.llm is not None
    
    def test_create_prompt(self, mock_kb_service):
        """Test prompt creation."""
        chain = APISuggestionChain(
            kb_service=mock_kb_service,
            use_rag=False
        )
        
        prompt = chain._create_prompt()
        assert prompt is not None


class TestRefactorChain:
    """Tests for RefactorChain."""
    
    def test_chain_initialization(self, mock_kb_service):
        """Test chain initializes correctly."""
        chain = RefactorChain(
            kb_service=mock_kb_service,
            use_rag=False
        )
        
        assert chain is not None
        assert chain.llm is not None
    
    def test_create_prompt(self, mock_kb_service):
        """Test prompt creation."""
        chain = RefactorChain(
            kb_service=mock_kb_service,
            use_rag=False
        )
        
        prompt = chain._create_prompt()
        assert prompt is not None
    
    @pytest.mark.asyncio
    async def test_refactor_element_mock(self, mock_kb_service):
        """Test refactoring with mocked LLM."""
        chain = RefactorChain(
            kb_service=mock_kb_service,
            use_rag=False
        )
        
        mock_result = {
            "refactored_element": {
                "name": "Updated Service",
                "type": "microservice",
                "description": "Enhanced service",
                "changes_summary": "Added caching",
                "updated_design": {"cache": "Redis"}
            },
            "rationale": {
                "why_changed": "Improve performance",
                "benefits": ["Faster"],
                "trade_offs": ["Complexity"],
                "risks": ["Cache invalidation"]
            },
            "migration_strategy": {
                "approach": "Gradual rollout",
                "steps": ["Deploy cache", "Update code"],
                "considerations": ["Monitor performance"],
                "rollback_plan": "Disable cache"
            },
            "impact_analysis": {
                "affected_components": ["API"],
                "breaking_changes": [],
                "compatibility_notes": ["Backward compatible"],
                "testing_recommendations": ["Load test"]
            },
            "alternatives_considered": [],
            "implementation_guidance": {
                "priority": "high",
                "estimated_effort": "2 weeks",
                "prerequisites": ["Redis setup"],
                "next_steps": ["Configure Redis"]
            }
        }
        
        with patch.object(chain, 'ainvoke', return_value=mock_result):
            result = await chain.refactor_element(
                element_name="User Service",
                element_type="microservice",
                element_description="User management",
                current_design={"auth": "JWT"},
                refactor_request="Add caching for better performance"
            )
            
            assert result is not None
            assert "refactored_element" in result


class TestChainIntegration:
    """Integration tests for chains."""
    
    @pytest.mark.asyncio
    async def test_chain_building(self, mock_kb_service):
        """Test that chains build correctly."""
        chains = [
            InitialGenerationChain(kb_service=mock_kb_service, use_rag=False),
            TechSuggestionChain(kb_service=mock_kb_service, use_rag=False),
            DecompositionChain(kb_service=mock_kb_service, use_rag=False),
            APISuggestionChain(kb_service=mock_kb_service, use_rag=False),
            RefactorChain(kb_service=mock_kb_service, use_rag=False),
        ]
        
        for chain in chains:
            built_chain = chain._build_chain()
            assert built_chain is not None


# Run with: pytest app/tests/test_design_engine.py -v
