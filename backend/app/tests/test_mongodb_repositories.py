"""
MongoDB Repository Integration Tests

Comprehensive tests for all repository methods including:
- User repository operations
- Project repository operations
- Design repository operations
- Feedback repository operations
"""

import pytest
import asyncio
from datetime import datetime
from typing import Generator
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config.mongodb_config import get_mongodb_config
from app.repositories.user_repository import UserRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.design_repository import DesignRepository
from app.repositories.feedback_repository import FeedbackRepository
from app.schemas.mongodb_schemas import (
    UserCreate,
    UserUpdate,
    ProjectCreate,
    ProjectUpdate,
    DesignCreate,
    DesignUpdate,
    FeedbackCreate,
    FeedbackUpdate,
    C4Element,
    C4Relationship
)
from app.exceptions.mongodb_exceptions import (
    DocumentNotFoundError,
    DuplicateKeyError,
    InvalidObjectIdError
)


# Test database configuration
TEST_DB_NAME = "test_system_architect_generator"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_database() -> AsyncIOMotorDatabase:
    """
    Create a test database connection.
    
    Yields:
        Test database instance
    """
    config = get_mongodb_config()
    client = AsyncIOMotorClient(config.get_connection_uri())
    database = client[TEST_DB_NAME]
    
    yield database
    
    # Cleanup: Drop the test database
    await client.drop_database(TEST_DB_NAME)
    client.close()


@pytest.fixture
async def user_repository(test_database: AsyncIOMotorDatabase) -> UserRepository:
    """Create UserRepository instance for testing."""
    repo = UserRepository(test_database)
    yield repo
    # Cleanup: Clear the collection
    await repo.collection.delete_many({})


@pytest.fixture
async def project_repository(test_database: AsyncIOMotorDatabase) -> ProjectRepository:
    """Create ProjectRepository instance for testing."""
    repo = ProjectRepository(test_database)
    yield repo
    # Cleanup: Clear the collection
    await repo.collection.delete_many({})


@pytest.fixture
async def design_repository(test_database: AsyncIOMotorDatabase) -> DesignRepository:
    """Create DesignRepository instance for testing."""
    repo = DesignRepository(test_database)
    yield repo
    # Cleanup: Clear the collection
    await repo.collection.delete_many({})


@pytest.fixture
async def feedback_repository(test_database: AsyncIOMotorDatabase) -> FeedbackRepository:
    """Create FeedbackRepository instance for testing."""
    repo = FeedbackRepository(test_database)
    yield repo
    # Cleanup: Clear the collection
    await repo.collection.delete_many({})


# ==================== User Repository Tests ====================

class TestUserRepository:
    """Tests for UserRepository."""
    
    @pytest.mark.asyncio
    async def test_create_user(self, user_repository: UserRepository):
        """Test creating a new user."""
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="Password123"
        )
        
        user_id = await user_repository.create_user(user_data, "hashed_password_123")
        
        assert user_id is not None
        user = await user_repository.find_by_id(user_id)
        assert user is not None
        assert user["username"] == "testuser"
        assert user["email"] == "test@example.com"
        assert user["hashed_password"] == "hashed_password_123"
    
    @pytest.mark.asyncio
    async def test_find_by_email(self, user_repository: UserRepository):
        """Test finding user by email."""
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="Password123"
        )
        await user_repository.create_user(user_data, "hashed_password")
        
        user = await user_repository.find_by_email("test@example.com")
        assert user is not None
        assert user["username"] == "testuser"
    
    @pytest.mark.asyncio
    async def test_find_by_username(self, user_repository: UserRepository):
        """Test finding user by username."""
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="Password123"
        )
        await user_repository.create_user(user_data, "hashed_password")
        
        user = await user_repository.find_by_username("testuser")
        assert user is not None
        assert user["email"] == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_update_user(self, user_repository: UserRepository):
        """Test updating user information."""
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="Password123"
        )
        user_id = await user_repository.create_user(user_data, "hashed_password")
        
        update_data = UserUpdate(full_name="Test User")
        success = await user_repository.update_user(user_id, update_data)
        
        assert success is True
        user = await user_repository.find_by_id(user_id)
        assert user["full_name"] == "Test User"
    
    @pytest.mark.asyncio
    async def test_duplicate_email(self, user_repository: UserRepository):
        """Test that duplicate email raises error."""
        user_data = UserCreate(
            username="testuser1",
            email="test@example.com",
            password="Password123"
        )
        await user_repository.create_user(user_data, "hashed_password")
        
        # Try to create another user with same email
        user_data2 = UserCreate(
            username="testuser2",
            email="test@example.com",
            password="Password123"
        )
        
        with pytest.raises(DuplicateKeyError):
            await user_repository.create_user(user_data2, "hashed_password")
    
    @pytest.mark.asyncio
    async def test_email_exists(self, user_repository: UserRepository):
        """Test checking if email exists."""
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="Password123"
        )
        await user_repository.create_user(user_data, "hashed_password")
        
        exists = await user_repository.email_exists("test@example.com")
        assert exists is True
        
        not_exists = await user_repository.email_exists("other@example.com")
        assert not_exists is False
    
    @pytest.mark.asyncio
    async def test_deactivate_user(self, user_repository: UserRepository):
        """Test deactivating a user."""
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="Password123"
        )
        user_id = await user_repository.create_user(user_data, "hashed_password")
        
        success = await user_repository.deactivate_user(user_id)
        assert success is True
        
        user = await user_repository.find_by_id(user_id)
        assert user["is_active"] is False


# ==================== Project Repository Tests ====================

class TestProjectRepository:
    """Tests for ProjectRepository."""
    
    @pytest.mark.asyncio
    async def test_create_project(self, project_repository: ProjectRepository):
        """Test creating a new project."""
        project_data = ProjectCreate(
            name="Test Project",
            description="A test project",
            tags=["test", "demo"]
        )
        
        project_id = await project_repository.create_project("user123", project_data)
        
        assert project_id is not None
        project = await project_repository.find_by_id(project_id)
        assert project is not None
        assert project["name"] == "Test Project"
        assert project["user_id"] == "user123"
        assert project["design_count"] == 0
    
    @pytest.mark.asyncio
    async def test_find_by_user(self, project_repository: ProjectRepository):
        """Test finding projects by user."""
        # Create multiple projects
        for i in range(3):
            project_data = ProjectCreate(
                name=f"Project {i}",
                description=f"Project {i} description"
            )
            await project_repository.create_project("user123", project_data)
        
        projects = await project_repository.find_by_user("user123")
        assert len(projects) == 3
    
    @pytest.mark.asyncio
    async def test_update_project(self, project_repository: ProjectRepository):
        """Test updating project information."""
        project_data = ProjectCreate(
            name="Original Name",
            description="Original description"
        )
        project_id = await project_repository.create_project("user123", project_data)
        
        update_data = ProjectUpdate(
            name="Updated Name",
            description="Updated description"
        )
        success = await project_repository.update_project(project_id, update_data)
        
        assert success is True
        project = await project_repository.find_by_id(project_id)
        assert project["name"] == "Updated Name"
        assert project["description"] == "Updated description"
    
    @pytest.mark.asyncio
    async def test_increment_design_count(self, project_repository: ProjectRepository):
        """Test incrementing design count."""
        project_data = ProjectCreate(name="Test Project")
        project_id = await project_repository.create_project("user123", project_data)
        
        await project_repository.increment_design_count(project_id)
        
        project = await project_repository.find_by_id(project_id)
        assert project["design_count"] == 1
    
    @pytest.mark.asyncio
    async def test_archive_project(self, project_repository: ProjectRepository):
        """Test archiving a project."""
        project_data = ProjectCreate(name="Test Project")
        project_id = await project_repository.create_project("user123", project_data)
        
        success = await project_repository.archive_project(project_id)
        assert success is True
        
        project = await project_repository.find_by_id(project_id)
        assert project["status"] == "archived"
    
    @pytest.mark.asyncio
    async def test_search_projects(self, project_repository: ProjectRepository):
        """Test searching projects."""
        project_data1 = ProjectCreate(name="Backend API", description="API service")
        project_data2 = ProjectCreate(name="Frontend App", description="React application")
        
        await project_repository.create_project("user123", project_data1)
        await project_repository.create_project("user123", project_data2)
        
        results = await project_repository.search_projects("user123", "API")
        assert len(results) == 1
        assert results[0]["name"] == "Backend API"


# ==================== Design Repository Tests ====================

class TestDesignRepository:
    """Tests for DesignRepository."""
    
    @pytest.mark.asyncio
    async def test_create_design(self, design_repository: DesignRepository):
        """Test creating a new design."""
        elements = [
            C4Element(
                id="elem1",
                type="system",
                name="System A",
                description="A system"
            )
        ]
        relationships = [
            C4Relationship(
                id="rel1",
                source_id="elem1",
                target_id="elem2",
                description="Connects to"
            )
        ]
        
        design_data = DesignCreate(
            project_id="project123",
            title="Test Design",
            description="A test design",
            diagram_type="system_context",
            version=1,
            elements=elements,
            relationships=relationships
        )
        
        design_id = await design_repository.create_design(
            "user123",
            design_data,
            created_by_ai=True,
            ai_model="gemini-pro"
        )
        
        assert design_id is not None
        design = await design_repository.find_by_id(design_id)
        assert design is not None
        assert design["title"] == "Test Design"
        assert design["created_by_ai"] is True
        assert design["ai_model"] == "gemini-pro"
        assert len(design["elements"]) == 1
    
    @pytest.mark.asyncio
    async def test_find_by_project(self, design_repository: DesignRepository):
        """Test finding designs by project."""
        # Create multiple designs
        for i in range(3):
            design_data = DesignCreate(
                project_id="project123",
                title=f"Design {i}",
                diagram_type="system_context",
                version=i + 1
            )
            await design_repository.create_design("user123", design_data)
        
        designs = await design_repository.find_by_project("project123")
        assert len(designs) == 3
    
    @pytest.mark.asyncio
    async def test_find_latest_version(self, design_repository: DesignRepository):
        """Test finding latest version of a design."""
        # Create multiple versions
        for i in range(1, 4):
            design_data = DesignCreate(
                project_id="project123",
                title="Design",
                diagram_type="system_context",
                version=i
            )
            await design_repository.create_design("user123", design_data)
        
        latest = await design_repository.find_latest_version("project123")
        assert latest is not None
        assert latest["version"] == 3
    
    @pytest.mark.asyncio
    async def test_get_ai_generated_designs(self, design_repository: DesignRepository):
        """Test getting AI-generated designs."""
        # Create AI and manual designs
        design_data1 = DesignCreate(
            project_id="project123",
            title="AI Design",
            diagram_type="system_context"
        )
        await design_repository.create_design("user123", design_data1, created_by_ai=True)
        
        design_data2 = DesignCreate(
            project_id="project124",
            title="Manual Design",
            diagram_type="container"
        )
        await design_repository.create_design("user123", design_data2, created_by_ai=False)
        
        ai_designs = await design_repository.get_ai_generated_designs("user123")
        assert len(ai_designs) == 1
        assert ai_designs[0]["title"] == "AI Design"
    
    @pytest.mark.asyncio
    async def test_count_by_project(self, design_repository: DesignRepository):
        """Test counting designs for a project."""
        for i in range(5):
            design_data = DesignCreate(
                project_id="project123",
                title=f"Design {i}",
                diagram_type="system_context"
            )
            await design_repository.create_design("user123", design_data)
        
        count = await design_repository.count_by_project("project123")
        assert count == 5


# ==================== Feedback Repository Tests ====================

class TestFeedbackRepository:
    """Tests for FeedbackRepository."""
    
    @pytest.mark.asyncio
    async def test_create_feedback(self, feedback_repository: FeedbackRepository):
        """Test creating new feedback."""
        feedback_data = FeedbackCreate(
            design_id="design123",
            rating=5,
            comment="Great design!",
            feedback_type="general"
        )
        
        feedback_id = await feedback_repository.create_feedback("user123", feedback_data)
        
        assert feedback_id is not None
        feedback = await feedback_repository.find_by_id(feedback_id)
        assert feedback is not None
        assert feedback["rating"] == 5
        assert feedback["comment"] == "Great design!"
        assert feedback["status"] == "new"
    
    @pytest.mark.asyncio
    async def test_find_by_design(self, feedback_repository: FeedbackRepository):
        """Test finding feedback by design."""
        # Create multiple feedback items
        for i in range(3):
            feedback_data = FeedbackCreate(
                design_id="design123",
                rating=i + 1,
                comment=f"Comment {i}"
            )
            await feedback_repository.create_feedback("user123", feedback_data)
        
        feedback_list = await feedback_repository.find_by_design("design123")
        assert len(feedback_list) == 3
    
    @pytest.mark.asyncio
    async def test_get_average_rating(self, feedback_repository: FeedbackRepository):
        """Test calculating average rating."""
        # Create feedback with different ratings
        ratings = [5, 4, 3, 5, 4]
        for rating in ratings:
            feedback_data = FeedbackCreate(
                design_id="design123",
                rating=rating
            )
            await feedback_repository.create_feedback("user123", feedback_data)
        
        avg_rating = await feedback_repository.get_average_rating_for_design("design123")
        assert avg_rating is not None
        assert avg_rating == pytest.approx(4.2, 0.1)
    
    @pytest.mark.asyncio
    async def test_get_rating_distribution(self, feedback_repository: FeedbackRepository):
        """Test getting rating distribution."""
        # Create feedback with various ratings
        ratings = [5, 5, 4, 4, 3, 2, 1]
        for rating in ratings:
            feedback_data = FeedbackCreate(
                design_id="design123",
                rating=rating
            )
            await feedback_repository.create_feedback("user123", feedback_data)
        
        distribution = await feedback_repository.get_rating_distribution("design123")
        assert distribution[5] == 2
        assert distribution[4] == 2
        assert distribution[3] == 1
        assert distribution[2] == 1
        assert distribution[1] == 1
    
    @pytest.mark.asyncio
    async def test_mark_as_reviewed(self, feedback_repository: FeedbackRepository):
        """Test marking feedback as reviewed."""
        feedback_data = FeedbackCreate(
            design_id="design123",
            rating=4,
            comment="Good"
        )
        feedback_id = await feedback_repository.create_feedback("user123", feedback_data)
        
        success = await feedback_repository.mark_as_reviewed(feedback_id)
        assert success is True
        
        feedback = await feedback_repository.find_by_id(feedback_id)
        assert feedback["status"] == "reviewed"
    
    @pytest.mark.asyncio
    async def test_get_feedback_by_status(self, feedback_repository: FeedbackRepository):
        """Test getting feedback by status."""
        # Create feedback
        feedback_data = FeedbackCreate(
            design_id="design123",
            rating=5
        )
        feedback_id = await feedback_repository.create_feedback("user123", feedback_data)
        await feedback_repository.mark_as_reviewed(feedback_id)
        
        reviewed = await feedback_repository.get_feedback_by_status("reviewed")
        assert len(reviewed) == 1
        assert reviewed[0]["status"] == "reviewed"


# ==================== Base Repository Tests ====================

class TestBaseRepository:
    """Tests for base repository functionality."""
    
    @pytest.mark.asyncio
    async def test_invalid_object_id(self, user_repository: UserRepository):
        """Test that invalid ObjectId raises error."""
        with pytest.raises(InvalidObjectIdError):
            await user_repository.find_by_id("invalid_id")
    
    @pytest.mark.asyncio
    async def test_delete_by_id(self, user_repository: UserRepository):
        """Test deleting document by ID."""
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="Password123"
        )
        user_id = await user_repository.create_user(user_data, "hashed_password")
        
        success = await user_repository.delete_by_id(user_id)
        assert success is True
        
        user = await user_repository.find_by_id(user_id)
        assert user is None
    
    @pytest.mark.asyncio
    async def test_count(self, project_repository: ProjectRepository):
        """Test counting documents."""
        # Create some projects
        for i in range(5):
            project_data = ProjectCreate(name=f"Project {i}")
            await project_repository.create_project("user123", project_data)
        
        count = await project_repository.count({"user_id": "user123"})
        assert count == 5
    
    @pytest.mark.asyncio
    async def test_exists(self, user_repository: UserRepository):
        """Test checking document existence."""
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="Password123"
        )
        await user_repository.create_user(user_data, "hashed_password")
        
        exists = await user_repository.exists({"email": "test@example.com"})
        assert exists is True
        
        not_exists = await user_repository.exists({"email": "other@example.com"})
        assert not_exists is False
