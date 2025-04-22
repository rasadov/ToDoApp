from datetime import datetime

from sqlalchemy import func, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base


class CustomBase(Base):
    """Base class for models"""

    __abstract__ = True
    __repr_fields__: tuple[str, ...] = ("id",)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        attrs = ", ".join(
            f"{field}: {getattr(self, field)}" for field in self.__repr_fields__
        )
        return f"{self.__class__.__name__}({attrs})"


class TimestampMixin(CustomBase):
    """Mixin for timestamp columns"""
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
    )
