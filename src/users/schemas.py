from typing import Optional

from pydantic import BaseModel, ConfigDict


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

    model_config = ConfigDict(from_attributes=True)


class UserResponseSchema(BaseUserSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)


class AuthResponseSchema(BaseModel):
    access_token: str


class UpdateUserSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None


class UpdatePasswordSchema(BaseModel):
    old_password: str
    new_password: str
