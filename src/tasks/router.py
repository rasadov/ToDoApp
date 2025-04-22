from fastapi import APIRouter, Depends

from src.dependencies import get_current_user, get_task_service
from src.tasks.schemas import CreateTaskSchema, UpdateTaskSchema


router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)

@router.get("/{task_id}")
async def get_task(
    task_id: int,
    task_service=Depends(get_task_service),
):
    """Get a task by ID."""
    return await task_service.get_task(task_id)

@router.get("/list")
async def list_tasks(
    page: int = 1,
    elements_per_page: int = 10,
    task_service=Depends(get_task_service),
):
    """Get a list of tasks."""
    return await task_service.get_tasks(
        page=page,
        elements_per_page=elements_per_page
    )

@router.get("/user/{user_id}")
async def list_user_tasks(
    user_id: int,
    page: int = 1,
    elements_per_page: int = 10,
    task_service=Depends(get_task_service),
):
    """Get a list of tasks for a specific user."""
    return await task_service.get_user_tasks(
        user_id=user_id,
        page=page,
        elements_per_page=elements_per_page
    )

@router.post("/create")
async def create_task(
    schema: CreateTaskSchema,
    task_service=Depends(get_task_service),
    user=Depends(get_current_user),
):
    """Create a new task."""
    return await task_service.create_task(
        schema=schema,
        user_id=user.user_id,
    )

@router.put("/update")
async def update_task(
    schema: UpdateTaskSchema,
    task_service=Depends(get_task_service),
    user=Depends(get_current_user),
):
    """Update an existing task."""
    return await task_service.update_task(
        schema=schema,
        user_id=user.user_id,
    )

@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    task_service=Depends(get_task_service),
    user=Depends(get_current_user),
):
    """Delete a task."""
    return await task_service.delete_task(
        task_id=task_id,
        user_id=user.user_id,
    )
