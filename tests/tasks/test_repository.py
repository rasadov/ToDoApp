import pytest
from unittest.mock import AsyncMock

from sqlalchemy.sql import Select

from src.tasks.repository import TaskRepository
from src.tasks.models import Task as TaskModel
from src.tasks.schemas import TaskStatus

from tests.conftest import TEST_USER_ID


pytestmark = pytest.mark.asyncio


async def test_repo_get_task_found(task_repository: TaskRepository, mock_session: AsyncMock, mock_task: TaskModel):
    task_id = mock_task.id
    mock_session.execute.return_value.scalars.return_value.first.return_value = mock_task
    result = await task_repository.get_task(mock_task.id)
    assert result == mock_task
    mock_session.execute.assert_awaited_once()
    call_args = mock_session.execute.call_args[0][0]
    assert isinstance(call_args, Select)
    assert f"WHERE tasks.id = {task_id}" in str(
        call_args.compile(compile_kwargs={"literal_binds": True}))


async def test_repo_get_tasks(task_repository: TaskRepository, mock_session: AsyncMock, mock_task_list: list):
    """Test getting all tasks with limit and offset."""
    limit = 5
    offset = 10
    mock_session.execute.return_value.scalars.return_value.all.return_value = mock_task_list
    result = await task_repository.get_tasks(limit=limit, offset=offset)
    assert result == mock_task_list
    mock_session.execute.assert_awaited_once()
    call_args = mock_session.execute.call_args[0][0]
    assert isinstance(call_args, Select)
    assert call_args._limit_clause.value == limit
    assert call_args._offset_clause.value == offset


async def test_repo_get_tasks_by_status(task_repository: TaskRepository, mock_session: AsyncMock, mock_task_list: list):
    """Test getting tasks by status."""
    limit = 20
    offset = 0
    status_filter = TaskStatus.NEW.value
    expected_tasks = [t for t in mock_task_list if t.status == status_filter]
    mock_session.execute.return_value.scalars.return_value.all.return_value = expected_tasks

    result = await task_repository.get_tasks_by_status(limit=limit, offset=offset, status=status_filter)
    assert result == expected_tasks
    mock_session.execute.assert_awaited_once()
    call_args = mock_session.execute.call_args[0][0]
    assert isinstance(call_args, Select)
    assert call_args._limit_clause.value == limit
    assert call_args._offset_clause.value == offset
    assert f"WHERE tasks.status = '{status_filter}'" in str(
        call_args.compile(compile_kwargs={"literal_binds": True}))


# --- Test get_user_tasks ---
async def test_repo_get_user_tasks(task_repository: TaskRepository, mock_session: AsyncMock, mock_task_list: list):
    """Test getting tasks for a specific user."""
    user_id = TEST_USER_ID
    limit = 15
    offset = 5
    expected_tasks = [t for t in mock_task_list if t.user_id == user_id]
    mock_session.execute.return_value.scalars.return_value.all.return_value = expected_tasks

    result = await task_repository.get_user_tasks(user_id=user_id, limit=limit, offset=offset)
    assert result == expected_tasks
    mock_session.execute.assert_awaited_once()
    call_args = mock_session.execute.call_args[0][0]
    assert isinstance(call_args, Select)

    assert call_args._limit_clause.value == limit
    assert call_args._offset_clause.value == offset
    assert f"WHERE tasks.user_id = {user_id}" in str(
        call_args.compile(compile_kwargs={"literal_binds": True}))


async def test_repo_get_task_not_found(task_repository: TaskRepository, mock_session: AsyncMock):
    """Test getting task by ID when not found."""
    task_id = 999
    mock_session.execute.return_value.scalars.return_value.first.return_value = None

    result = await task_repository.get_task(task_id)

    assert result is None
    mock_session.execute.assert_awaited_once()


async def test_repo_add_task(task_repository: TaskRepository, mock_session: AsyncMock):
    """Test adding a task."""
    new_task = TaskModel(
        title="Repo Add", description="Testing add", status="new")
    expected_id = 555

    async def refresh_side_effect(obj):
        obj.id = expected_id
    mock_session.refresh.side_effect = refresh_side_effect

    result = await task_repository.add_task(new_task)

    mock_session.add.assert_called_once_with(new_task)
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(new_task)
    assert result == new_task
    assert result.id == expected_id


async def test_repo_update_task(task_repository: TaskRepository, mock_session: AsyncMock):
    """Test updating a task (commit only)."""
    await task_repository.update_task()
    mock_session.commit.assert_awaited_once()


async def test_repo_delete_task(task_repository: TaskRepository, mock_session: AsyncMock, mock_task: TaskModel):
    """Test deleting a task."""
    task_to_delete = mock_task

    await task_repository.delete_task(task_to_delete)

    mock_session.delete.assert_awaited_once_with(task_to_delete)
    mock_session.commit.assert_awaited_once()
