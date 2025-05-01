from sqlalchemy import select

from src.base.repository import Repository
from src.users.models import User


class UserRepository(Repository[User]):
    """User repository"""

    async def get_user_by(self, condition):
        """Gets a user by condition."""
        result = await self.session.execute(select(User).where(condition))

        return result.scalars().first()

    async def get_user_by_id(self, user_id: int) -> User:
        """Gets a user by id."""
        return await self.get_user_by(User.id == user_id)

    async def get_user_by_username(self, username: str) -> User:
        """Gets a user by username."""
        return await self.get_user_by(User.username == username)

    async def create_user(self, user: User) -> User:
        """Creates a user in the database."""
        self.add(user)
        await self.commit()
        await self.refresh(user)
        return user

    async def update_user(self) -> None:
        """Updates a user in the database."""
        await self.commit()

    async def delete_user(self, user: User) -> None:
        """Deletes a user from the database."""
        await self.delete(user)
        await self.commit()
