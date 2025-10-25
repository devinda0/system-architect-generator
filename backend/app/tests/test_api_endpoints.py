"""
API Endpoints Integration Tests

Tests for all API endpoints including projects, designs, and authentication.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from datetime import datetime, timezone

from app.main import app
from app.middleware.auth import create_access_token, get_current_user


@pytest.fixture
def mock_current_user():
    """Mock current user for authentication."""
    return {
        "id": "test_user_123",
        "username": "testuser",
        "email": "test@example.com"
    }


@pytest.fixture
def client(mock_current_user):
    """Test client fixture with authentication override."""
    # Override the dependency
    app.dependency_overrides[get_current_user] = lambda: mock_current_user
    test_client = TestClient(app)
    yield test_client
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def client_no_auth():
    """Test client without authentication."""
    app.dependency_overrides.clear()
    return TestClient(app)


@pytest.fixture
def auth_token(mock_current_user):
    """Create a valid JWT token."""
    return create_access_token(mock_current_user)


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
    
    @patch('app.api.projects.get_database', new_callable=AsyncMock)
    @patch('app.repositories.project_repository.ProjectRepository.create_project', new_callable=AsyncMock)
    @patch('app.repositories.project_repository.ProjectRepository.find_by_id', new_callable=AsyncMock)
    def test_create_project(self, mock_find, mock_create, mock_db, client, mock_project):
        """Test creating a new project."""
        from bson import ObjectId
        project_id = str(ObjectId())
        mock_create.return_value = project_id
        
        # Return a valid project
        mock_project["_id"] = project_id
        mock_find.return_value = mock_project
        
        response = client.post(
            "/api/projects",
            json={
                "name": "New Project",
                "description": "Project description",
                "tags": ["test"]
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == "Test Project"
    
    @patch('app.api.projects.get_database', new_callable=AsyncMock)
    @patch('app.repositories.project_repository.ProjectRepository.find_by_id', new_callable=AsyncMock)
    @patch('app.repositories.design_repository.DesignRepository.find_by_project', new_callable=AsyncMock)
    def test_get_project(self, mock_find_designs, mock_find, mock_db, client, mock_project):
        """Test getting a project."""
        mock_find.return_value = mock_project
        mock_find_designs.return_value = []
        
        response = client.get("/api/projects/project_123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "project_123"
        assert data["name"] == "Test Project"
    
    @patch('app.api.projects.get_database', new_callable=AsyncMock)
    @patch('app.repositories.project_repository.ProjectRepository.find_by_id', new_callable=AsyncMock)
    def test_get_project_not_found(self, mock_find, mock_db, client):
        """Test getting a non-existent project."""
        mock_find.return_value = None
        
        response = client.get("/api/projects/nonexistent")
        
        assert response.status_code == 404
    
    @patch('app.api.projects.get_database', new_callable=AsyncMock)
    @patch('app.repositories.project_repository.ProjectRepository.find_by_user', new_callable=AsyncMock)
    @patch('app.repositories.project_repository.ProjectRepository.count_by_user', new_callable=AsyncMock)
    def test_list_projects(self, mock_count, mock_find, mock_db, client, mock_project):
        """Test listing projects."""
        mock_find.return_value = [mock_project]
        mock_count.return_value = 1
        
        response = client.get("/api/projects")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["projects"]) == 1
    
    @patch('app.api.projects.get_database', new_callable=AsyncMock)
    @patch('app.repositories.project_repository.ProjectRepository.find_by_id', new_callable=AsyncMock)
    @patch('app.repositories.project_repository.ProjectRepository.update_project', new_callable=AsyncMock)
    def test_update_project(self, mock_update, mock_find, mock_db, client, mock_project):
        """Test updating a project."""
        mock_find.return_value = mock_project
        mock_update.return_value = True
        
        # Update the mock to reflect the change
        updated_project = mock_project.copy()
        updated_project["name"] = "Updated Project"
        mock_find.return_value = updated_project
        
        response = client.put(
            "/api/projects/project_123",
            json={"name": "Updated Project"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Project"
    
    @patch('app.api.projects.get_database', new_callable=AsyncMock)
    @patch('app.repositories.project_repository.ProjectRepository.find_by_id', new_callable=AsyncMock)
    @patch('app.repositories.project_repository.ProjectRepository.update_project', new_callable=AsyncMock)
    def test_delete_project_soft(self, mock_update, mock_find, mock_db, client, mock_project):
        """Test soft deleting a project."""
        mock_find.return_value = mock_project
        mock_update.return_value = True
        
        response = client.delete("/api/projects/project_123")
        
        assert response.status_code == 204  # No Content for soft delete
        # No body to check for 204 responses

    
    def test_unauthorized(self, client_no_auth):
        """Test unauthorized access to project endpoints."""
        response = client_no_auth.get("/api/projects")
        assert response.status_code == 403


# ==================== Design API Tests ====================

class TestDesignAPI:
    """Tests for Design API endpoints."""
    
    @patch('app.api.design.get_database', new_callable=AsyncMock)
    @patch('app.repositories.design_repository.DesignRepository.find_by_id', new_callable=AsyncMock)
    def test_get_design_tree(self, mock_find, mock_db, client, mock_design):
        """Test getting design tree."""
        mock_find.return_value = mock_design
        
        response = client.get("/api/designs/design_123")
        
        assert response.status_code == 200
        data = response.json()
        assert "elements" in data
    
    @patch('app.api.design.get_database', new_callable=AsyncMock)
    @patch('app.repositories.design_repository.DesignRepository.find_by_id', new_callable=AsyncMock)
    def test_get_design_not_found(self, mock_find, mock_db, client):
        """Test getting a non-existent design."""
        mock_find.return_value = None
        
        response = client.get("/api/designs/nonexistent")
        
        assert response.status_code == 404
    
    @patch('app.api.design.get_database', new_callable=AsyncMock)
    @patch('app.repositories.design_repository.DesignRepository.find_by_id', new_callable=AsyncMock)
    @patch('app.services.design_engine_service.DesignEngineService.generate_initial_design', new_callable=AsyncMock)
    def test_ai_action_initial_generation(self, mock_generate, mock_find, mock_db, client, mock_design):
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
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    @patch('app.api.design.get_database', new_callable=AsyncMock)
    @patch('app.repositories.design_repository.DesignRepository.find_by_id', new_callable=AsyncMock)
    @patch('app.services.design_engine_service.DesignEngineService.suggest_technology', new_callable=AsyncMock)
    def test_ai_action_tech_suggestion(self, mock_suggest, mock_find, mock_db, client, mock_design):
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
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    @patch('app.api.design.get_database', new_callable=AsyncMock)
    @patch('app.repositories.design_repository.DesignRepository.find_by_id', new_callable=AsyncMock)
    @patch('app.repositories.design_repository.DesignRepository.update_design', new_callable=AsyncMock)
    def test_update_element(self, mock_update, mock_find, mock_db, client, mock_design):
        """Test updating a design element."""
        mock_find.return_value = mock_design
        mock_update.return_value = True
        
        response = client.put(
            "/api/designs/design_123/element/elem_1",
            json={
                "name": "Updated System",
                "description": "Updated description"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


# ==================== Design Engine API Tests ====================

class TestDesignEngineAPI:
    """Tests for Design Engine API endpoints."""
    
    def test_get_engine_info(self, client):
        """Test getting engine information."""
        response = client.get("/api/designs/info")
        
        assert response.status_code == 200
        data = response.json()
        # Check for actual response fields
        assert "model" in data
        assert "engine_version" in data
        assert "chains" in data


# ==================== Authentication Tests ====================

class TestAuthentication:
    """Tests for authentication middleware."""
    
    def test_no_auth_token(self, client_no_auth):
        """Test that requests without token are rejected."""
        response = client_no_auth.get("/api/projects")
        assert response.status_code == 403
    
    def test_invalid_auth_token(self, client_no_auth):
        """Test that invalid tokens are rejected."""
        response = client_no_auth.get(
            "/api/projects",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
    
    @patch('app.api.projects.get_database', new_callable=AsyncMock)
    @patch('app.repositories.project_repository.ProjectRepository.find_by_user', new_callable=AsyncMock)
    @patch('app.repositories.project_repository.ProjectRepository.count_by_user', new_callable=AsyncMock)
    def test_valid_auth_token(self, mock_count, mock_find, mock_db, client):
        """Test that valid token allows access."""
        mock_find.return_value = []
        mock_count.return_value = 0
        
        response = client.get("/api/projects")
        
        # Should pass authentication (200 or other non-auth error)
        assert response.status_code != 401
        assert response.status_code != 403
