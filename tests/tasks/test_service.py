import pytest
from unittest.mock import MagicMock, AsyncMock

from src.tasks.service import TaskService
from src.tasks.models import Task as TaskModel
from src.tasks.schemas import CreateTaskSchema, UpdateTaskSchema, TaskStatus
from src.base.exceptions import NotFoundException, UnAuthorizedException

from tests.conftest import TEST_USER_ID


pytestmark = pytest.mark.asyncio


async def test_get_tasks_no_status(task_service: TaskService, mock_task_repository: MagicMock, mock_task_list: list):
    """Test getting tasks without status filter."""
    page = 2
    per_page = 5
    expected_offset = (page - 1) * per_page
    mock_task_repository.get_tasks.return_value = mock_task_list[:per_page]

    result = await task_service.get_tasks(page=page, elements_per_page=per_page, status=None)

    assert result == mock_task_list[:per_page]
    mock_task_repository.get_tasks.assert_awaited_once_with(
        offset=expected_offset, limit=per_page)
    mock_task_repository.get_tasks_by_status.assert_not_called()


async def test_get_tasks_with_status(task_service: TaskService, mock_task_repository: MagicMock, mock_task_list: list):
    """Test getting tasks with status filter."""
    page = 1
    per_page = 10
    status_filter = TaskStatus.NEW.value
    expected_offset = 0
    expected_tasks = [t for t in mock_task_list if t.status == status_filter]
    mock_task_repository.get_tasks_by_status.return_value = expected_tasks

    result = await task_service.get_tasks(page=page, elements_per_page=per_page, status=status_filter)

    assert result == expected_tasks
    mock_task_repository.get_tasks_by_status.assert_awaited_once_with(
        offset=expected_offset, limit=per_page, status=status_filter
    )
    mock_task_repository.get_tasks.assert_not_called()


async def test_get_user_tasks(task_service: TaskService, mock_task_repository: MagicMock, mock_task_list: list):
    """Test getting tasks for a specific user."""
    user_id = TEST_USER_ID
    page = 1
    per_page = 10
    expected_offset = 0
    expected_tasks = [t for t in mock_task_list if t.user_id == user_id]
    mock_task_repository.get_user_tasks.return_value = expected_tasks

    result = await task_service.get_user_tasks(user_id=user_id, page=page, elements_per_page=per_page)

    assert result == expected_tasks
    mock_task_repository.get_user_tasks.assert_awaited_once_with(
        user_id=user_id, offset=expected_offset, limit=per_page
    )


@pytest.fixture
def mock_task() -> TaskModel:
    """Provides a mock Task instance for tests."""
    return TaskModel(id=999, title="Mock Task", description="Mock Description", status=TaskStatus.NEW)


async def test_create_task(
    task_service: TaskService,
    mock_task_repository: MagicMock,
    mock_task: TaskModel,
):
    """Test creating a task."""
    user_id = TEST_USER_ID
    create_schema = CreateTaskSchema(
        title="New Service Task", description="Desc", status=TaskStatus.NEW)

    async def add_task_side_effect(task: TaskModel):
        if not task.id:
            task.id = 999
        return task

    mock_task_repository.add_task.side_effect = add_task_side_effect

    result = await task_service.create_task(schema=create_schema, user_id=user_id)

    mock_task_repository.add_task.assert_awaited_once()

    call_kwargs = mock_task_repository.add_task.call_args.kwargs
    task_object_passed = call_kwargs.get('task')

    assert task_object_passed is not None
    assert isinstance(task_object_passed, TaskModel)
    assert task_object_passed.title == create_schema.title
    assert task_object_passed.description == create_schema.description
    assert task_object_passed.status == create_schema.status
    assert task_object_passed.id == 999

    assert isinstance(result, TaskModel)
    assert result.title == create_schema.title
    assert result.user_id == user_id
    assert result.id == 999


@pytest.fixture
def update_schema(mock_task: TaskModel) -> UpdateTaskSchema:
    return UpdateTaskSchema(id=mock_task.id, title="Updated Service Title", status=TaskStatus.COMPLETED)


async def test_update_task_success(task_service: TaskService, mock_task_repository: MagicMock, mock_task: TaskModel, update_schema: UpdateTaskSchema):
    """Test successfully updating a task."""
    user_id = mock_task.user_id

    mock_task_repository.get_task.return_value = mock_task

    mock_task_repository.update_task = AsyncMock()

    result = await task_service.update_task(schema=update_schema, user_id=user_id)

    mock_task_repository.get_task.assert_awaited_once_with(update_schema.id)
    mock_task_repository.update_task.assert_awaited_once()

    assert result == mock_task
    assert result.title == update_schema.title
    assert result.status == update_schema.status


async def test_update_task_not_found(task_service: TaskService, mock_task_repository: MagicMock, update_schema: UpdateTaskSchema):
    """Test updating task when task not found."""
    user_id = TEST_USER_ID
    mock_task_repository.get_task.return_value = None

    with pytest.raises(NotFoundException):
        await task_service.update_task(schema=update_schema, user_id=user_id)

    mock_task_repository.get_task.assert_awaited_once_with(update_schema.id)
    mock_task_repository.update_task.assert_not_called()


async def test_update_task_unauthorized(task_service: TaskService, mock_task_repository: MagicMock, mock_task: TaskModel, update_schema: UpdateTaskSchema):
    """Test updating task when user is not authorized."""
    user_id = 999
    assert mock_task.user_id != user_id
    mock_task_repository.get_task.return_value = mock_task

    with pytest.raises(UnAuthorizedException):
        await task_service.update_task(schema=update_schema, user_id=user_id)

    mock_task_repository.get_task.assert_awaited_once_with(update_schema.id)
    mock_task_repository.update_task.assert_not_called()


async def test_delete_task_success(task_service: TaskService, mock_task_repository: MagicMock, mock_task: TaskModel):
    """Test successfully deleting a task."""
    user_id = mock_task.user_id
    task_id_to_delete = mock_task.id

    mock_task_repository.get_task.return_value = mock_task
    mock_task_repository.delete_task = AsyncMock()

    await task_service.delete_task(task_id=task_id_to_delete, user_id=user_id)

    mock_task_repository.get_task.assert_awaited_once_with(task_id_to_delete)
    mock_task_repository.delete_task.assert_awaited_once_with(mock_task)


async def test_delete_task_not_found(task_service: TaskService, mock_task_repository: MagicMock):
    """Test deleting task when task not found."""
    user_id = TEST_USER_ID
    task_id_to_delete = 999
    mock_task_repository.get_task.return_value = None

    with pytest.raises(NotFoundException):
        await task_service.delete_task(task_id=task_id_to_delete, user_id=user_id)

    mock_task_repository.get_task.assert_awaited_once_with(task_id_to_delete)
    mock_task_repository.delete_task.assert_not_called()


async def test_delete_task_unauthorized(task_service: TaskService, mock_task_repository: MagicMock, mock_task: TaskModel):
    """Test deleting task when user is not authorized."""
    user_id = 999
    task_id_to_delete = mock_task.id
    assert mock_task.user_id != user_id
    mock_task_repository.get_task.return_value = mock_task

    with pytest.raises(UnAuthorizedException):
        await task_service.delete_task(task_id=task_id_to_delete, user_id=user_id)

    mock_task_repository.get_task.assert_awaited_once_with(task_id_to_delete)
    mock_task_repository.delete_task.assert_not_called()
