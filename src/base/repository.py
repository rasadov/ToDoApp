from abc import ABC
from dataclasses import dataclass
from typing import TypeVar, Generic

from sqlalchemy.ext.asyncio import AsyncSession


T = TypeVar('T')


@dataclass
class Repository(ABC, Generic[T]):
    session: AsyncSession

    def add(self, item: T) -> None:
        """Adds given item into database session."""
        self.session.add(item)

    async def delete(self, item: T) -> None:
        """Removes the given item from the database session."""
        await self.session.delete(item)

    async def refresh(self, item: T) -> None:
        """Commits changes to the database session."""
        await self.session.refresh(item)

    async def commit(self) -> None:
        """Commits changes to the database session."""
        await self.session.commit()

    async def rollback(self) -> None:
        """Rollbacks changes in the database session."""
        await self.session.rollback()
