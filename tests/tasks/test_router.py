import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from src.tasks.schemas import TaskStatus

from tests.conftest import TEST_USER_ID


CREATE_TASK_DATA = {"title": "New API Task",
                    "description": "Create via API", "status": TaskStatus.NEW}
UPDATE_TASK_DATA = {"id": 101, "title": "Updated Title",
                    "status": TaskStatus.IN_PROGRESS}
UPDATED_TASK_RESPONSE_EXPECTED = {
    "id": 101, "title": "Updated Title", "description": "Description for task 1", "status": "in_progress",
}
TASK_RESPONSE_EXPECTED = {
    "id": 101,
    "title": "Test Task 1",
    "description": "Description for task 1",
    "status": "new",
    "created_at": "2025-04-30T08:57:00+04:00",
    "updated_at": "2025-04-30T08:57:00+04:00",
    "user_id": 1
}
TASK_LIST_RESPONSE_EXPECTED = [TASK_RESPONSE_EXPECTED]

pytestmark = pytest.mark.asyncio


async def test_get_task_success(client: TestClient, mock_task_service: MagicMock):
    """Test successfully getting a task by ID."""
    task_id = 101
    # Return data matching response model
    mock_task_service.get_task.return_value = TASK_RESPONSE_EXPECTED

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == TASK_RESPONSE_EXPECTED
    mock_task_service.get_task.assert_awaited_once_with(task_id)


async def test_get_task_not_found(client: TestClient, mock_task_service: MagicMock):
    task_id = 999
    from src.base.exceptions import NotFoundException
    mock_task_service.get_task.side_effect = NotFoundException(
        "Task not found")

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_task_service.get_task.assert_awaited_once_with(task_id)


async def test_list_tasks_success(client: TestClient, mock_task_service: MagicMock):
    """Test successfully listing tasks."""
    mock_task_service.get_tasks.return_value = TASK_LIST_RESPONSE_EXPECTED

    response = client.get("/tasks/list?page=1&elements_per_page=5")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == TASK_LIST_RESPONSE_EXPECTED
    mock_task_service.get_tasks.assert_awaited_once_with(
        page=1, elements_per_page=5, status=None)


async def test_list_tasks_with_status(client: TestClient, mock_task_service: MagicMock):
    """Test successfully listing tasks with a status filter."""
    mock_task_service.get_tasks.return_value = [TASK_RESPONSE_EXPECTED]
    test_status = TaskStatus.NEW

    response = client.get(f"/tasks/list?status={test_status.value}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [TASK_RESPONSE_EXPECTED]
    mock_task_service.get_tasks.assert_awaited_once_with(
        page=1, elements_per_page=10, status=test_status.value)


async def test_list_user_tasks_success(client: TestClient, mock_task_service: MagicMock):
    """Test listing tasks for a specific user."""
    user_id_to_test = TEST_USER_ID
    mock_task_service.get_user_tasks.return_value = TASK_LIST_RESPONSE_EXPECTED

    response = client.get(f"/tasks/user/{user_id_to_test}?page=2")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == TASK_LIST_RESPONSE_EXPECTED
    mock_task_service.get_user_tasks.assert_awaited_once_with(
        user_id=user_id_to_test, page=2, elements_per_page=10)


async def test_create_task_success(client: TestClient, mock_task_service: MagicMock):
    mock_task_service.create_task.return_value = TASK_RESPONSE_EXPECTED

    response = client.post("/tasks/create", json=CREATE_TASK_DATA)

    assert response.status_code == status.HTTP_200_OK

    mock_task_service.create_task.assert_awaited_once()
    call_kwargs = mock_task_service.create_task.call_args.kwargs
    assert call_kwargs['schema'].model_dump() == CREATE_TASK_DATA
    assert call_kwargs['user_id'] == TEST_USER_ID
    assert response.json() == TASK_RESPONSE_EXPECTED


async def test_update_task_success(client: TestClient, mock_task_service: MagicMock):
    """Test successful task update."""
    mock_task_service.update_task.return_value = UPDATED_TASK_RESPONSE_EXPECTED

    response = client.put("/tasks/update", json=UPDATE_TASK_DATA)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == UPDATED_TASK_RESPONSE_EXPECTED

    mock_task_service.update_task.assert_awaited_once()

    call_kwargs = mock_task_service.update_task.call_args.kwargs
    assert call_kwargs['schema'].model_dump(
        exclude_unset=True) == UPDATE_TASK_DATA
    assert call_kwargs['user_id'] == TEST_USER_ID


async def test_update_task_not_found(client: TestClient, mock_task_service: MagicMock):
    """Test updating a non-existent task."""
    from src.base.exceptions import NotFoundException
    mock_task_service.update_task.side_effect = NotFoundException(
        "Task not found")

    response = client.put("/tasks/update", json=UPDATE_TASK_DATA)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_task_service.update_task.assert_awaited_once()


async def test_update_task_unauthorized(client: TestClient, mock_task_service: MagicMock):
    """Test updating a task belonging to another user."""
    from src.base.exceptions import UnAuthorizedException
    mock_task_service.update_task.side_effect = UnAuthorizedException(
        "Unauthorized")

    response = client.put("/tasks/update", json=UPDATE_TASK_DATA)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    mock_task_service.update_task.assert_awaited_once()


async def test_delete_task_success(client: TestClient, mock_task_service: MagicMock):
    """Test successful task deletion."""
    task_id_to_delete = 101
    mock_task_service.delete_task.return_value = None

    response = client.delete(f"/tasks/{task_id_to_delete}")

    assert response.status_code == status.HTTP_200_OK
    mock_task_service.delete_task.assert_awaited_once_with(
        task_id=task_id_to_delete, user_id=TEST_USER_ID)


async def test_delete_task_not_found(client: TestClient, mock_task_service: MagicMock):
    """Test deleting a non-existent task."""
    task_id_to_delete = 999
    from src.base.exceptions import NotFoundException
    mock_task_service.delete_task.side_effect = NotFoundException(
        "Task not found")

    response = client.delete(f"/tasks/{task_id_to_delete}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_task_service.delete_task.assert_awaited_once_with(
        task_id=task_id_to_delete, user_id=TEST_USER_ID)


async def test_delete_task_unauthorized(client: TestClient, mock_task_service: MagicMock):
    """Test deleting a task belonging to another user."""
    task_id_to_delete = 101
    from src.base.exceptions import UnAuthorizedException
    mock_task_service.delete_task.side_effect = UnAuthorizedException(
        "Unauthorized")

    response = client.delete(f"/tasks/{task_id_to_delete}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    mock_task_service.delete_task.assert_awaited_once_with(
        task_id=task_id_to_delete, user_id=TEST_USER_ID)
