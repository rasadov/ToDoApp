from fastapi import APIRouter, Depends

from src.dependencies import get_current_user, get_task_service
from src.tasks import TaskService
from src.tasks.schemas import CreateTaskSchema, UpdateTaskSchema, TaskResponseSchema
from src.users import TokenData

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)


@router.get("/list", response_model=list[TaskResponseSchema])
async def list_tasks(
    page: int = 1,
    elements_per_page: int = 10,
    status: str = None,
    task_service: TaskService = Depends(get_task_service),
):
    """Get a list of tasks."""
    return await task_service.get_tasks(
        page=page,
        status=status,
        elements_per_page=elements_per_page
    )


@router.get("/user/{user_id}", response_model=list[TaskResponseSchema])
async def list_user_tasks(
    page: int = 1,
    elements_per_page: int = 10,
    current_user: TokenData = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """Get a list of tasks for a specific user."""
    return await task_service.get_user_tasks(
        user_id=current_user.user_id,
        page=page,
        elements_per_page=elements_per_page
    )


@router.get("/{task_id}", response_model=TaskResponseSchema)
async def get_task(
    task_id: int,
    task_service: TaskService = Depends(get_task_service),
):
    """Get a task by ID."""
    return await task_service.get_task(task_id)


@router.post("/create")
async def create_task(
    schema: CreateTaskSchema,
    current_user: TokenData = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """Create a new task."""
    return await task_service.create_task(
        schema=schema,
        user_id=current_user.user_id,
    )


@router.put("/update")
async def update_task(
    schema: UpdateTaskSchema,
    current_user: TokenData = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """Update an existing task."""
    return await task_service.update_task(
        schema=schema,
        user_id=current_user.user_id,
    )


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    current_user: TokenData = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """Delete a task."""
    return await task_service.delete_task(
        task_id=task_id,
        user_id=current_user.user_id,
    )
