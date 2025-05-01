import pytest
from typing import Generator, Any
from unittest.mock import AsyncMock, MagicMock

from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import app as actual_app
from src.tasks import TaskRepository, TaskService, Task as TaskModel
from src.users import User as UserModel
from src.users.service import UserService
from src.users.repository import UserRepository
from src.dependencies import get_user_service, get_task_service, get_current_user


TEST_USER_ID = 1


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="function")
def client(
    mock_user_service: UserService,
    mock_task_service: TaskService,
    mock_current_user_data: Any,
) -> Generator[TestClient, None, None]:
    """Provides a FastAPI TestClient with mocked dependencies."""
    # Apply overrides
    actual_app.dependency_overrides[get_user_service] = lambda: mock_user_service
    actual_app.dependency_overrides[get_task_service] = lambda: mock_task_service
    actual_app.dependency_overrides[get_current_user] = lambda: mock_current_user_data

    # Create client
    with TestClient(app=actual_app, base_url="http://test") as test_client:
        yield test_client

    # Clean up overrides
    actual_app.dependency_overrides = {}


@pytest.fixture
def mock_user_repository() -> MagicMock:
    """Fixture for a mocked UserRepository."""
    mock = MagicMock(spec=UserRepository)
    mock.get_user_by_username = AsyncMock()
    mock.create_user = AsyncMock()

    return mock


@pytest.fixture
def user_service(mock_user_repository: UserRepository) -> UserService:
    """Fixture for UserService instance with mocked repository."""
    return UserService(user_repository=mock_user_repository)


@pytest.fixture
def mock_user_service() -> MagicMock:
    """Fixture for a mocked UserService used in user router tests."""
    mock = MagicMock(spec=UserService)
    mock.login = AsyncMock()
    mock.register = AsyncMock()
    mock.refresh = AsyncMock()
    mock.logout = AsyncMock()
    return mock


@pytest.fixture
def mock_user_db() -> UserModel:
    """Provides a reusable mock User object for repository tests."""
    # Define the mock data within a fixture for better isolation
    return UserModel(id=1, username="dbuser", password="dbpassword", first_name="DB", last_name="User")


@pytest.fixture
def mock_session() -> AsyncMock:
    """Fixture for a mocked SQLAlchemy AsyncSession with explicit chain."""
    session = AsyncMock(spec=AsyncSession)
    mock_execute_result = AsyncMock()
    session.execute.return_value = mock_execute_result
    mock_scalars_result = MagicMock()
    mock_execute_result.scalars = MagicMock(return_value=mock_scalars_result)
    mock_scalars_result.first = MagicMock()  # Configure return_value in tests
    mock_scalars_result.all = MagicMock()   # Configure return_value in tests
    session.commit = AsyncMock()
    session.add = MagicMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    return session


@pytest.fixture
def user_repository(mock_session: AsyncSession) -> UserRepository:
    """Fixture for UserRepository instance with mocked session."""
    return UserRepository(session=mock_session)


@pytest.fixture
def mock_request() -> MagicMock:
    """Fixture for a mocked FastAPI Request object."""
    request = MagicMock(spec=Request)
    request.cookies = {}
    return request


@pytest.fixture(autouse=True)
def override_settings(monkeypatch):
    """Override settings for testing."""
    monkeypatch.setattr("src.config.Settings.SECRET_KEY", "test_secret")
    monkeypatch.setattr("src.config.Settings.ALGORITHM", "HS256")
    monkeypatch.setattr("src.config.Settings.ACCESS_TOKEN_EXPIRE_MINUTES", 15)
    monkeypatch.setattr(
        "src.config.Settings.REFRESH_TOKEN_EXPIRE_MINUTES", 1440)


@pytest.fixture(scope="function")
def mock_current_user_data() -> Any:
    """Provides mock data for the current user dependency."""
    # Adjust the structure based on what get_current_user actually returns
    # Assuming it returns an object/dict with user_id
    class MockCurrentUser:
        user_id: int = TEST_USER_ID
    return MockCurrentUser()
    # Or if it's just a dict: return {"user_id": TEST_USER_ID}

# --- Mocks for Task Service/Repo ---


@pytest.fixture
def mock_task_repository() -> MagicMock:
    """Fixture for a mocked TaskRepository."""
    mock = MagicMock(spec=TaskRepository)
    mock.get_task = AsyncMock()
    mock.get_tasks = AsyncMock()
    mock.get_tasks_by_status = AsyncMock()
    mock.get_user_tasks = AsyncMock()
    mock.add_task = AsyncMock()
    mock.update_task = AsyncMock()
    mock.delete_task = AsyncMock()
    return mock


@pytest.fixture
def task_service(mock_task_repository: TaskRepository) -> TaskService:
    """Fixture for TaskService instance with mocked repository."""
    return TaskService(task_repository=mock_task_repository)


@pytest.fixture
def mock_task_service() -> MagicMock:
    """Fixture for a mocked TaskService used in router tests."""
    mock = MagicMock(spec=TaskService)
    mock.get_task = AsyncMock()
    mock.get_tasks = AsyncMock()
    mock.get_user_tasks = AsyncMock()
    mock.create_task = AsyncMock()
    mock.update_task = AsyncMock()
    mock.delete_task = AsyncMock()
    return mock

# --- Reusable Mock Session (from user tests) ---


@pytest.fixture
def task_repository(mock_session: AsyncSession) -> TaskRepository:
    """Fixture for TaskRepository instance with mocked session."""
    # Assuming Repository base class takes session in __init__
    return TaskRepository(session=mock_session)


# --- Mock User/Task Model data ---
@pytest.fixture
def mock_user() -> UserModel:
    """Provides a mock User instance for tests."""
    return UserModel(id=TEST_USER_ID, username="testuser", password="hashed_password", first_name="Test", last_name="User")


@pytest.fixture
def mock_task(mock_user: UserModel) -> TaskModel:
    """Provides a mock Task instance linked to the mock user."""
    # Adjust fields based on your Task model definition
    return TaskModel(
        id=101,
        title="Test Task 1",
        description="Description for task 1",
        status="new",
        user_id=mock_user.id,
        # created_at, updated_at might be handled by TimestampMixin/DB default
    )


@pytest.fixture
def mock_task_list(mock_user: UserModel) -> list[TaskModel]:
    """Provides a list of mock Task instances."""
    return [
        TaskModel(id=101, title="Task 1", description="Desc 1",
                  status="new", user_id=mock_user.id),
        TaskModel(id=102, title="Task 2", description="Desc 2",
                  status="in_progress", user_id=mock_user.id),
        TaskModel(id=103, title="Task 3", description="Desc 3",
                  status="new", user_id=999),
    ]
