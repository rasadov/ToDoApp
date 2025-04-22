from dataclasses import dataclass

from src.tasks.repository import TaskRepository

@dataclass
class TaskService:
    task_repository: TaskRepository