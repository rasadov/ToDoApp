import pytest
from typing import Generator
from unittest.mock import AsyncMock, MagicMock

from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import app as actual_app
from src.users import User
from src.users.service import UserService
from src.users.repository import UserRepository
from src.dependencies import get_user_service


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="function")
def client(mock_user_service: UserService) -> Generator[TestClient, None, None]: # Changed return type hint
    """Provides a FastAPI TestClient with mocked user service."""
    # Override the dependency before creating the client
    actual_app.dependency_overrides[get_user_service] = lambda: mock_user_service

    with TestClient(app=actual_app, base_url="http://test") as test_client:
        yield test_client

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
    """Fixture for a mocked UserService used in router tests."""
    mock = MagicMock(spec=UserService)
    mock.login = AsyncMock()
    mock.register = AsyncMock()

    mock.refresh = AsyncMock()
    mock.logout = AsyncMock()
    return mock

@pytest.fixture
def mock_user_db() -> User:
    """Provides a reusable mock User object for repository tests."""
    # Define the mock data within a fixture for better isolation
    return User(id=1, username="dbuser", password="dbpassword", first_name="DB", last_name="User")

@pytest.fixture
def mock_session() -> AsyncMock:
    """Fixture for a mocked SQLAlchemy AsyncSession with explicit chain."""
    session = AsyncMock(spec=AsyncSession)

    # Mock the object returned by awaiting execute()
    mock_execute_result = AsyncMock()
    session.execute.return_value = mock_execute_result

    # Mock the object returned by synchronously calling scalars()
    mock_scalars_result = MagicMock()
    # Configure scalars AS A SYNCHRONOUS METHOD on the execute result
    mock_execute_result.scalars = MagicMock(return_value=mock_scalars_result)

    # Configure first AS A SYNCHRONOUS METHOD on the scalars result
    # The actual return value will be set per-test
    mock_scalars_result.first = MagicMock()

    # Configure other session methods as needed
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
    monkeypatch.setattr("src.config.Settings.REFRESH_TOKEN_EXPIRE_MINUTES", 1440)
