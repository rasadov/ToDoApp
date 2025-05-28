import pytest
from unittest.mock import AsyncMock

from src.users.repository import UserRepository
from src.users.models import User

pytestmark = pytest.mark.asyncio

# Sample data
MOCK_USER_DB = User(id=1, username="dbuser",
                    password="dbpassword", first_name="DB", last_name="User")


async def test_get_user_by_id_found(
    user_repository: UserRepository,
    mock_session: AsyncMock,
    mock_user_db: User
):
    """Test getting user by ID when the user exists."""
    mock_session.execute.return_value.scalars.return_value.first.return_value = mock_user_db

    user = await user_repository.get_user_by_id(1)

    assert user == mock_user_db
    mock_session.execute.assert_awaited_once()


async def test_get_user_by_id_not_found(
    user_repository: UserRepository,
    mock_session: AsyncMock
):
    """Test getting user by ID when the user does not exist."""
    mock_session.execute.return_value.scalars.return_value.first.return_value = None

    user = await user_repository.get_user_by_id(99)

    assert user is None
    mock_session.execute.assert_awaited_once()


async def test_get_user_by_username_found(
    user_repository: UserRepository,
    mock_session: AsyncMock,
    mock_user_db: User
):
    """Test getting user by username when the user exists."""
    mock_session.execute.return_value.scalars.return_value.first.return_value = mock_user_db

    user = await user_repository.get_user_by_username("dbuser")

    assert user == mock_user_db
    mock_session.execute.assert_awaited_once()


async def test_get_user_by_username_not_found(
    user_repository: UserRepository,
    mock_session: AsyncMock
):
    """Test getting user by username when the user does not exist."""
    mock_session.execute.return_value.scalars.return_value.first.return_value = None

    user = await user_repository.get_user_by_username("nouser")

    assert user is None
    mock_session.execute.assert_awaited_once()


async def test_create_user(user_repository: UserRepository, mock_session: AsyncMock):
    """Test creating a user."""
    new_user = User(username="newbie", password="pw",
                    first_name="New", last_name="Bie")

    async def mock_refresh(obj):
        obj.id = 5

    mock_session.refresh.side_effect = mock_refresh

    created_user = await user_repository.create_user(new_user)

    mock_session.add.assert_called_once_with(new_user)
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(new_user)
    assert created_user == new_user
    assert created_user.id == 5  # Check if refresh worked


async def test_update_user(user_repository: UserRepository, mock_session: AsyncMock):
    """Test updating a user (commit only)."""
    await user_repository.update_user()

    mock_session.commit.assert_awaited_once()


async def test_delete_user(user_repository: UserRepository, mock_session: AsyncMock):
    """Test deleting a user."""
    user_to_delete = MOCK_USER_DB
    await user_repository.delete_user(user_to_delete)

    mock_session.delete.assert_awaited_once_with(user_to_delete)
    mock_session.commit.assert_awaited_once()
