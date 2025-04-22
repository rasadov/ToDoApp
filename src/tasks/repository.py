from sqlalchemy import select

from src.base.repository import Repository
from src.tasks.models import Task


class TaskRepository(Repository[Task]):
    """Task repository"""

    async def get_tasks(self, user_id: int):
        """Gets all tasks for a user."""
        result = await self.session.execute(
            select(Task).where(Task.user_id == user_id)
        )

        return result.scalars().all()

    async def add_task(self, task: Task):
        """Adds a task to the database."""
        self.add(task)
        await self.commit()

    async def update_task(self):
        """Updates a task in the database."""
        await self.commit()

    async def delete_task(self, task: Task):
        """Deletes a task from the database."""
        await self.delete(task)
        await self.commit()
