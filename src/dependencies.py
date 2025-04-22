from fastapi import Depends

from src.db import get_session
from src.tasks import TaskRepository, TaskService
from src.users import UserRepository, UserService

async def get_user_repository(
        session=Depends(get_session)
) -> UserRepository:
    """Gets a user repository."""
    return UserRepository(session)

async def get_task_repository(
        session=Depends(get_session)
) -> TaskRepository:
    """Gets a task repository."""
    return TaskRepository(session)

async def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    """Gets a user service."""
    return UserService(user_repository)

async def get_task_service(
    task_repository: TaskRepository = Depends(get_task_repository),
) -> TaskService:
    """Gets a task service."""
    return TaskService(task_repository)
