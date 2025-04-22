from typing import Optional

from pydantic import BaseModel


class TokenData(BaseModel):
    user_id: int
    action: str


class BaseUserSchema(BaseModel):
    first_name: str
    last_name: str
    username: str


class LoginSchema(BaseModel):
    username: str
    password: str


class RegisterSchema(BaseUserSchema):
    password: str

    class Config:
        orm_mode = True


class UserResponseSchema(BaseUserSchema):
    id: int

    class Config:
        orm_mode = True


class AuthResponseSchema(BaseModel):
    access_token: str


class UpdateUserSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None


class UpdatePasswordSchema(BaseModel):
    old_password: str
    new_password: str
