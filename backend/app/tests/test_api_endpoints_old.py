"""
API Endpoints Integration Tests

Tests for all API endpoints including projects, designs, and authentication.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timezone

from app.main import app
from app.middleware.auth import create_access_token


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


@pytest.fixture
def mock_current_user():
    """Mock current user for authentication."""
    return {
        "id": "test_user_123",
        "username": "testuser",
        "email": "test@example.com"
    }


@pytest.fixture
def auth_token(mock_current_user):
    """Create a valid JWT token."""
    return create_access_token(mock_current_user)


@pytest.fixture
def auth_headers(auth_token):
    """Create authorization headers."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def mock_db():
    """Mock database instance."""
    return AsyncMock()


@pytest.fixture
def mock_project():
    """Mock project data."""
    return {
        "_id": "project_123",
        "user_id": "test_user_123",
        "name": "Test Project",
        "description": "Test project description",
        "tags": ["test", "backend"],
        "status": "active",
        "metadata": {"key": "value"},
        "design_count": 2,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }


@pytest.fixture
def mock_design():
    """Mock design data."""
    return {
        "_id": "design_123",
        "user_id": "test_user_123",
        "project_id": "project_123",
        "title": "System Architecture",
        "description": "Test design",
        "diagram_type": "system_context",
        "version": 1,
        "elements": [
            {
                "id": "elem_1",
                "type": "system",
                "name": "Test System",
                "description": "Main system",
                "technology": "Python",
                "tags": [],
                "properties": {}
            }
        ],
        "relationships": [],
        "metadata": {},
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "created_by_ai": True,
        "ai_model": "gemini-pro"
    }

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timezone

from app.main import app
from app.middleware.auth import create_access_token


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_current_user():
    """Mock current user for authentication."""
    return {
        "id": "test_user_123",
        "username": "testuser",
        "email": "test@example.com",
        "role": "user"
    }


@pytest.fixture
def auth_token(mock_current_user):
    """Create authentication token for testing."""
    token_data = {
        "sub": mock_current_user["id"],
        "username": mock_current_user["username"],
        "email": mock_current_user["email"]
    }
    return create_access_token(token_data)


@pytest.fixture
def auth_headers(auth_token):
    """Create authorization headers."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def mock_project():
    """Mock project data."""
    return {
        "_id": "project_123",
        "user_id": "test_user_123",
        "name": "Test Project",
        "description": "Test project description",
        "tags": ["test", "backend"],
        "status": "active",
        "metadata": {"key": "value"},
        "design_count": 2,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }


@pytest.fixture
def mock_design():
    """Mock design data."""
    return {
        "_id": "design_123",
        "user_id": "test_user_123",
        "project_id": "project_123",
        "title": "System Architecture",
        "description": "Test design",
        "diagram_type": "system_context",
        "version": 1,
        "elements": [
            {
                "id": "elem_1",
                "type": "system",
                "name": "Test System",
                "description": "Main system",
                "technology": "Python",
                "tags": [],
                "properties": {}
            }
        ],
        "relationships": [],
        "metadata": {},
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "created_by_ai": True,
        "ai_model": "gemini-pro"
    }


# ==================== Project API Tests ====================

class TestProjectAPI:
    """Tests for Project API endpoints."""
    
    def test_create_project(self, client, auth_headers, mock_project):
        """Test creating a new project."""
        from app.api.projects import get_project_repository
        from app.repositories.project_repository import ProjectRepository
        
        mock_repo = AsyncMock(spec=ProjectRepository)
        mock_repo.create_project.return_value = "project_123"
        mock_repo.find_by_id.return_value = mock_project
        
        app.dependency_overrides[get_project_repository] = lambda: mock_repo
        
        try:
            response = client.post(
                "/api/projects",
                json={
                    "name": "Test Project",
                    "description": "Test description",
                    "tags": ["test"],
                    "metadata": {}
                },
                headers=auth_headers
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["name"] == "Test Project"
            assert data["id"] == "project_123"
        finally:
            app.dependency_overrides.clear()
    
    def test_get_project(self, client, auth_headers, mock_project):
        """Test getting a project by ID."""
        from app.api.projects import get_project_repository, get_design_repository
        from app.repositories.project_repository import ProjectRepository
        from app.repositories.design_repository import DesignRepository
        
        mock_project_repo = AsyncMock(spec=ProjectRepository)
        mock_project_repo.find_by_id.return_value = mock_project
        
        mock_design_repo = AsyncMock(spec=DesignRepository)
        mock_design_repo.find_by_project.return_value = []
        
        app.dependency_overrides[get_project_repository] = lambda: mock_project_repo
        app.dependency_overrides[get_design_repository] = lambda: mock_design_repo
        
        try:
            response = client.get(
                "/api/projects/project_123",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "project_123"
            assert data["name"] == "Test Project"
        finally:
            app.dependency_overrides.clear()
    
    def test_get_project_not_found(self, client, auth_headers):
        """Test getting a non-existent project."""
        from app.api.projects import get_project_repository, get_design_repository
        from app.repositories.project_repository import ProjectRepository
        from app.repositories.design_repository import DesignRepository
        
        mock_project_repo = AsyncMock(spec=ProjectRepository)
        mock_project_repo.find_by_id.return_value = None
        
        mock_design_repo = AsyncMock(spec=DesignRepository)
        
        app.dependency_overrides[get_project_repository] = lambda: mock_project_repo
        app.dependency_overrides[get_design_repository] = lambda: mock_design_repo
        
        try:
            response = client.get(
                "/api/projects/nonexistent",
                headers=auth_headers
            )
            
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()
    
    def test_list_projects(self, client, auth_headers, mock_project):
        """Test listing projects."""
        from app.api.projects import get_project_repository
        from app.repositories.project_repository import ProjectRepository
        
        mock_repo = AsyncMock(spec=ProjectRepository)
        mock_repo.find_by_user.return_value = [mock_project]
        mock_repo.count_by_user.return_value = 1
        
        app.dependency_overrides[get_project_repository] = lambda: mock_repo
        
        try:
            response = client.get(
                "/api/projects",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1
            assert len(data["projects"]) == 1
            assert data["projects"][0]["id"] == "project_123"
        finally:
            app.dependency_overrides.clear()
    
    def test_update_project(self, client, auth_headers, mock_project):
        """Test updating a project."""
        from app.api.projects import get_project_repository
        from app.repositories.project_repository import ProjectRepository
        
        mock_repo = AsyncMock(spec=ProjectRepository)
        updated_project = mock_project.copy()
        updated_project["name"] = "Updated Project"
        
        mock_repo.find_by_id.side_effect = [mock_project, updated_project]
        mock_repo.update_project.return_value = True
        
        app.dependency_overrides[get_project_repository] = lambda: mock_repo
        
        try:
            response = client.put(
                "/api/projects/project_123",
                json={"name": "Updated Project"},
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Updated Project"
        finally:
            app.dependency_overrides.clear()
    
    def test_delete_project_soft(self, client, auth_headers, mock_project):
        """Test soft deleting a project."""
        from app.api.projects import get_project_repository
        from app.repositories.project_repository import ProjectRepository
        
        mock_repo = AsyncMock(spec=ProjectRepository)
        mock_repo.find_by_id.return_value = mock_project
        mock_repo.update_project.return_value = True
        
        app.dependency_overrides[get_project_repository] = lambda: mock_repo
        
        try:
            response = client.delete(
                "/api/projects/project_123",
                headers=auth_headers
            )
            
            assert response.status_code == 204
        finally:
            app.dependency_overrides.clear()
    
    def test_create_project_unauthorized(self, client):
        """Test creating a project without authentication."""
        response = client.post(
            "/api/projects",
            json={"name": "Test Project"}
        )
        
        assert response.status_code == 403


# ==================== Design API Tests ====================

class TestDesignAPI:
    """Tests for Design API endpoints."""
    
    def test_get_design_tree(self, client, auth_headers, mock_design):
        """Test getting design tree."""
        from app.api.design import get_design_repository
        from app.repositories.design_repository import DesignRepository

        # Create mock repository
        mock_repo = AsyncMock(spec=DesignRepository)
        mock_repo.find_by_id.return_value = mock_design

        # Override dependency
        app.dependency_overrides[get_design_repository] = lambda: mock_repo

        try:
            response = client.get(
                "/api/designs/design_123",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["design_id"] == "design_123"
            assert data["title"] == "System Architecture"
            assert len(data["elements"]) == 1
        finally:
            app.dependency_overrides.clear()
    
    def test_get_design_not_found(self, client, auth_headers):
        """Test getting a non-existent design."""
        from app.api.design import get_design_repository
        from app.repositories.design_repository import DesignRepository

        # Create mock repository
        mock_repo = AsyncMock(spec=DesignRepository)
        mock_repo.find_by_id.return_value = None

        # Override dependency
        app.dependency_overrides[get_design_repository] = lambda: mock_repo

        try:
            response = client.get(
                "/api/designs/nonexistent",
                headers=auth_headers
            )
            
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()
    
    def test_ai_action_initial_generation(self, client, auth_headers, mock_design):
        """Test AI action for initial generation."""
        from app.api.design import get_design_repository, get_design_engine
        from app.repositories.design_repository import DesignRepository
        from app.services.design_engine_service import DesignEngineService

        # Create mock repository
        mock_repo = AsyncMock(spec=DesignRepository)
        mock_repo.find_by_id.return_value = mock_design

        # Create mock engine
        mock_engine = AsyncMock(spec=DesignEngineService)
        mock_engine.generate_initial_design.return_value = {
            "system_context": {"name": "Test System"},
            "containers": []
        }

        # Override dependencies
        app.dependency_overrides[get_design_repository] = lambda: mock_repo
        app.dependency_overrides[get_design_engine] = lambda: mock_engine

        try:
            response = client.post(
                "/api/designs/design_123/ai-action",
                json={
                    "action_type": "initial_generation",
                    "requirements": "Build a web application"
                },
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["action_type"] == "initial_generation"
        finally:
            app.dependency_overrides.clear()
    
    def test_ai_action_tech_suggestion(self, client, auth_headers, mock_design):
        """Test AI action for technology suggestion."""
        from app.api.design import get_design_repository, get_design_engine
        from app.repositories.design_repository import DesignRepository
        from app.services.design_engine_service import DesignEngineService

        # Create mock repository
        mock_repo = AsyncMock(spec=DesignRepository)
        mock_repo.find_by_id.return_value = mock_design

        # Create mock engine
        mock_engine = AsyncMock(spec=DesignEngineService)
        mock_engine.suggest_technology.return_value = {
            "primary_recommendation": {
                "technology": "FastAPI",
                "rationale": "Best for Python APIs"
            }
        }

        # Override dependencies
        app.dependency_overrides[get_design_repository] = lambda: mock_repo
        app.dependency_overrides[get_design_engine] = lambda: mock_engine

        try:
            response = client.post(
                "/api/designs/design_123/ai-action",
                json={
                    "action_type": "tech_suggestion",
                    "element_name": "API Service",
                    "element_type": "container",
                    "element_description": "RESTful API"
                },
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "primary_recommendation" in data["result"]
        finally:
            app.dependency_overrides.clear()
    
    def test_update_element(self, client, auth_headers, mock_design):
        """Test updating a design element."""
        from app.api.design import get_design_repository
        from app.repositories.design_repository import DesignRepository

        # Create mock repository
        mock_repo = AsyncMock(spec=DesignRepository)
        mock_repo.find_by_id.return_value = mock_design
        mock_repo.update_design.return_value = True

        # Override dependency
        app.dependency_overrides[get_design_repository] = lambda: mock_repo

        try:
            response = client.put(
                "/api/designs/design_123/element/elem_1",
                json={
                    "name": "Updated System",
                    "description": "Updated description"
                },
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["element_id"] == "elem_1"
        finally:
            app.dependency_overrides.clear()
    
    def test_update_element_not_found(self, client, auth_headers, mock_design):
        """Test updating a non-existent element."""
        from app.api.design import get_design_repository
        from app.repositories.design_repository import DesignRepository

        # Create mock repository
        mock_repo = AsyncMock(spec=DesignRepository)
        mock_repo.find_by_id.return_value = mock_design

        # Override dependency
        app.dependency_overrides[get_design_repository] = lambda: mock_repo

        try:
            response = client.put(
                "/api/designs/design_123/element/nonexistent",
                json={"name": "Updated"},
                headers=auth_headers
            )
            
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()


# ==================== Design Engine Tests ====================

class TestDesignEngineAPI:
    """Tests for Design Engine endpoints."""
    
    @patch('app.services.design_engine_service.DesignEngineService.generate_initial_design')
    def test_generate_initial_design(self, mock_generate, client):
        """Test initial design generation endpoint."""
        mock_generate.return_value = {
            "system_context": {
                "name": "E-commerce System",
                "description": "Online shopping platform"
            },
            "containers": [
                {"name": "Web App", "type": "container"}
            ]
        }
        
        response = client.post(
            "/api/designs/generate-initial",
            json={"requirements": "Build an e-commerce platform"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "system_context" in data
        assert "containers" in data
    
    @patch('app.services.design_engine_service.DesignEngineService.suggest_technology')
    def test_suggest_technology(self, mock_suggest, client):
        """Test technology suggestion endpoint."""
        mock_suggest.return_value = {
            "primary_recommendation": {
                "technology": "PostgreSQL",
                "rationale": "Reliable relational database"
            },
            "alternatives": []
        }
        
        response = client.post(
            "/api/designs/suggest-technology",
            json={
                "element_name": "Database",
                "element_type": "container",
                "element_description": "Main data store"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "primary_recommendation" in data
    
    def test_get_engine_info(self, client):
        """Test getting engine information."""
        response = client.get("/api/designs/info")
        
        assert response.status_code == 200
        data = response.json()
        assert "engine_version" in data
        assert "chains" in data


# ==================== Authentication Tests ====================

class TestAuthentication:
    """Tests for authentication middleware."""
    
    def test_no_auth_token(self, client):
        """Test endpoints without authentication token."""
        response = client.get("/api/projects")
        assert response.status_code == 403
    
    def test_invalid_auth_token(self, client):
        """Test endpoints with invalid authentication token."""
        response = client.get(
            "/api/projects",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
    
    def test_valid_auth_token(self, client, auth_headers, mock_project):
        """Test that valid token allows access."""
        from app.api.projects import get_project_repository
        from app.repositories.project_repository import ProjectRepository
        
        # Mock repository to avoid DB connection
        mock_repo = AsyncMock(spec=ProjectRepository)
        mock_repo.find_by_user.return_value = [mock_project]
        mock_repo.count_by_user.return_value = 1
        
        app.dependency_overrides[get_project_repository] = lambda: mock_repo
        
        try:
            response = client.get(
                "/api/projects",
                headers=auth_headers
            )
            # Should not be 401 or 403 (auth errors)
            assert response.status_code != 401
            assert response.status_code != 403
            assert response.status_code == 200
        finally:
            app.dependency_overrides.clear()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
