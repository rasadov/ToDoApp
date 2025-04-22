from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.base.models import CustomBase
if TYPE_CHECKING:
    from src.tasks.models import Task


class User(CustomBase):
    """User model"""

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)

    tasks: Mapped[list[Task]] = relationship(
        "Task",
        back_populates="user",
        cascade="all, delete-orphan",
    )
