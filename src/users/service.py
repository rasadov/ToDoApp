from dataclasses import dataclass

from src.users.repository import UserRepository

@dataclass
class UserService:
    user_repository: UserRepository
