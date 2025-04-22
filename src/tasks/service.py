from typing import Sequence
from dataclasses import dataclass

from src.tasks.repository import TaskRepository
from src.tasks.models import Task
from src.tasks.schemas import CreateTaskSchema, UpdateTaskSchema

@dataclass
class TaskService:
    task_repository: TaskRepository

    async def get_tasks(
            self,
            page: int = 1,
            elements_per_page: int = 10,
    ):
        """Gets a list of tasks."""
        tasks = await self.task_repository.get_tasks(
            offset=(page - 1) * elements_per_page,
            limit=elements_per_page
        )
        return tasks

    async def get_user_tasks(
            self,
            user_id: int,
            page: int = 1,
            elements_per_page: int = 10,
        ) -> Sequence[Task]:
        """Gets a list of tasks."""
        tasks = await self.task_repository.get_user_tasks(
            user_id=user_id,
            offset=(page - 1) * elements_per_page,
            limit=elements_per_page
        )
        return tasks

    async def create_task(
        self,
        schema: CreateTaskSchema,
        user_id: int,
    ) -> Task:
        """Creates a task."""
        task = await self.task_repository.add_task(task=Task(**schema.model_dump()))
        task.user_id = user_id
        return task

    async def update_task(
        self,
        schema: UpdateTaskSchema,
    ) -> Task:
        """Updates a task."""
        task = await self.task_repository.get_task(schema.id)
        if not task:
            raise ValueError("Task not found")
        task.update(**schema.model_dump())
        await self.task_repository.update_task()
        return task

    async def delete_task(
        self,
        task_id: int,
        user_id: int,
    ) -> None:
        """Deletes a task."""
        task = await self.task_repository.get_task(task_id)
        if not task:
            raise ValueError("Task not found")
        if task.user_id != user_id:
            raise ValueError("You do not have permission to delete this task")
        await self.task_repository.delete_task(task)
