from fastapi import Depends, Request

from src.base.exceptions import UnAuthorizedException
from src.db import get_session
from src.tasks import TaskRepository, TaskService
from src.users import UserRepository, UserService, TokenData, get_payload_from_token


def get_current_user(
        request: Request
) -> TokenData:
    access_token = request.headers.get("Authorization")

    if not access_token:
        raise UnAuthorizedException

    try:
        user_id = get_payload_from_token(
            access_token,
        ).get("user_id")
        if user_id is None:
            raise UnAuthorizedException
        token_data = TokenData(user_id=user_id, action="auth")
    except Exception:
        raise UnAuthorizedException
    return token_data


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
