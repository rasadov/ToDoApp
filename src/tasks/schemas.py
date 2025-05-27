from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TaskStatus(str, Enum):
    """Task status enum"""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

    def __str__(self) -> str:
        return self.value


class BaseTaskSchema(BaseModel):
    title: str
    description: str
    status: TaskStatus = TaskStatus.NEW


class CreateTaskSchema(BaseTaskSchema):
    pass


class UpdateTaskSchema(BaseModel):
    id: int
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None


class TaskResponseSchema(BaseTaskSchema):
    id: int
    updated_at: str
    created_at: str
    user_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
