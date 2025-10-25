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
    db_mock = AsyncMock()
    db_mock.close = AsyncMock()
    return db_mock


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
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
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
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "created_by_ai": True,
        "ai_model": "gemini-pro"
    }


# ==================== Project API Tests ====================

class TestProjectAPI:
    """Tests for Project API endpoints."""
    
    @patch('app.api.projects.get_database')
    @patch('app.repositories.project_repository.ProjectRepository.create_project')
    @patch('app.repositories.project_repository.ProjectRepository.find_by_id')
    def test_create_project(self, mock_find, mock_create, mock_db, client, auth_headers, mock_project):
        """Test creating a new project."""
        mock_create.return_value = "project_123"
        mock_find.return_value = mock_project
        
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
    
    @patch('app.api.projects.get_database')
    @patch('app.repositories.project_repository.ProjectRepository.find_by_id')
    @patch('app.repositories.design_repository.DesignRepository.find_by_project')
    def test_get_project(self, mock_find_designs, mock_find_project, mock_db, client, auth_headers, mock_project):
        """Test getting a project by ID."""
        mock_find_project.return_value = mock_project
        mock_find_designs.return_value = []
        
        response = client.get(
            "/api/projects/project_123",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "project_123"
        assert data["name"] == "Test Project"
    
    @patch('app.api.projects.get_database')
    @patch('app.repositories.project_repository.ProjectRepository.find_by_id')
    def test_get_project_not_found(self, mock_find, mock_db, client, auth_headers):
        """Test getting a non-existent project."""
        mock_find.return_value = None
        
        response = client.get(
            "/api/projects/nonexistent",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    @patch('app.api.projects.get_database')
    @patch('app.repositories.project_repository.ProjectRepository.find_by_user')
    @patch('app.repositories.project_repository.ProjectRepository.count_by_user')
    def test_list_projects(self, mock_count, mock_find, mock_db, client, auth_headers, mock_project):
        """Test listing projects."""
        mock_find.return_value = [mock_project]
        mock_count.return_value = 1
        
        response = client.get(
            "/api/projects",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["projects"]) == 1
        assert data["projects"][0]["id"] == "project_123"
    
    @patch('app.api.projects.get_database')
    @patch('app.repositories.project_repository.ProjectRepository.find_by_id')
    @patch('app.repositories.project_repository.ProjectRepository.update_project')
    def test_update_project(self, mock_update, mock_find, mock_db, client, auth_headers, mock_project):
        """Test updating a project."""
        updated_project = mock_project.copy()
        updated_project["name"] = "Updated Project"
        
        mock_find.side_effect = [mock_project, updated_project]
        mock_update.return_value = True
        
        response = client.put(
            "/api/projects/project_123",
            json={"name": "Updated Project"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Project"
    
    @patch('app.api.projects.get_database')
    @patch('app.repositories.project_repository.ProjectRepository.find_by_id')
    @patch('app.repositories.project_repository.ProjectRepository.update_project')
    def test_delete_project_soft(self, mock_update, mock_find, mock_db, client, auth_headers, mock_project):
        """Test soft deleting a project."""
        mock_find.return_value = mock_project
        mock_update.return_value = True
        
        response = client.delete(
            "/api/projects/project_123",
            headers=auth_headers
        )
        
        assert response.status_code == 204
    
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
    
    @patch('app.api.design.get_database')
    @patch('app.repositories.design_repository.DesignRepository.find_by_id')
    def test_get_design_tree(self, mock_find, mock_db, client, auth_headers, mock_design):
        """Test getting design tree."""
        mock_find.return_value = mock_design
        
        response = client.get(
            "/api/designs/design_123",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["design_id"] == "design_123"
        assert data["title"] == "System Architecture"
        assert len(data["elements"]) == 1
    
    @patch('app.api.design.get_database')
    @patch('app.repositories.design_repository.DesignRepository.find_by_id')
    def test_get_design_not_found(self, mock_find, mock_db, client, auth_headers):
        """Test getting a non-existent design."""
        mock_find.return_value = None
        
        response = client.get(
            "/api/designs/nonexistent",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    @patch('app.api.design.get_database')
    @patch('app.repositories.design_repository.DesignRepository.find_by_id')
    @patch('app.services.design_engine_service.DesignEngineService.generate_initial_design')
    def test_ai_action_initial_generation(self, mock_generate, mock_find, mock_db, client, auth_headers, mock_design):
        """Test AI action for initial generation."""
        mock_find.return_value = mock_design
        mock_generate.return_value = {
            "system_context": {"name": "Test System"},
            "containers": []
        }
        
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
    
    @patch('app.api.design.get_database')
    @patch('app.repositories.design_repository.DesignRepository.find_by_id')
    @patch('app.services.design_engine_service.DesignEngineService.suggest_technology')
    def test_ai_action_tech_suggestion(self, mock_suggest, mock_find, mock_db, client, auth_headers, mock_design):
        """Test AI action for technology suggestion."""
        mock_find.return_value = mock_design
        mock_suggest.return_value = {
            "primary_recommendation": {
                "technology": "FastAPI",
                "rationale": "Best for Python APIs"
            }
        }
        
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
    
    @patch('app.api.design.get_database')
    @patch('app.repositories.design_repository.DesignRepository.find_by_id')
    @patch('app.repositories.design_repository.DesignRepository.update_design')
    def test_update_element(self, mock_update, mock_find, mock_db, client, auth_headers, mock_design):
        """Test updating a design element."""
        mock_find.return_value = mock_design
        mock_update.return_value = True
        
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
    
    @patch('app.api.design.get_database')
    @patch('app.repositories.design_repository.DesignRepository.find_by_id')
    def test_update_element_not_found(self, mock_find, mock_db, client, auth_headers, mock_design):
        """Test updating a non-existent element."""
        mock_find.return_value = mock_design
        
        response = client.put(
            "/api/designs/design_123/element/nonexistent",
            json={"name": "Updated"},
            headers=auth_headers
        )
        
        assert response.status_code == 404


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
        assert "model" in data
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
    
    def test_valid_auth_token(self, client, auth_headers):
        """Test that valid token allows access."""
        # This will fail on DB access but should pass auth
        response = client.get(
            "/api/projects",
            headers=auth_headers
        )
        # Should not be 401 or 403 (auth errors)
        assert response.status_code != 401
        assert response.status_code != 403


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
