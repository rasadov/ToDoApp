from typing import Sequence

from sqlalchemy import select

from src.base.repository import Repository
from src.tasks.models import Task


class TaskRepository(Repository[Task]):
    """Task repository"""

    async def get_task(self, task_id: int) -> Task:
        """Gets a task by ID."""
        result = await self.session.execute(select(Task).where(Task.id == task_id))

        return result.scalars().first()

    async def get_tasks(self, limit: int = 100, offset: int = 0) -> Sequence[Task]:
        """Gets all tasks."""
        result = await self.session.execute(select(Task).limit(limit).offset(offset))

        return result.scalars().all()

    async def get_user_tasks(self, user_id: int, limit: int = 100, offset: int = 0) -> Sequence[Task]:
        """Gets all tasks for a user."""
        result = await self.session.execute(
            select(Task).where(Task.user_id == user_id).limit(limit).offset(offset)
        )

        return result.scalars().all()

    async def add_task(self, task: Task) -> Task:
        """Adds a task to the database."""
        self.add(task)
        await self.commit()
        await self.refresh(task)
        return task

    async def update_task(self) -> None:
        """Updates a task in the database."""
        await self.commit()

    async def delete_task(self, task: Task) -> None:
        """Deletes a task from the database."""
        await self.delete(task)
        await self.commit()
