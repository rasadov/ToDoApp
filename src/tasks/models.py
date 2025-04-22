from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from src.base.models import TimestampMixin
if TYPE_CHECKING:
    from src.users.models import User

class Task(TimestampMixin):
    """Task model"""
    __tablename__ = "tasks"

    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    user: User = relationship("User", backref="tasks")