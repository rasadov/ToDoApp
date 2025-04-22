from dataclasses import dataclass

from fastapi import Request
from fastapi.responses import JSONResponse

from src.users.repository import UserRepository
from src.users.schemas import LoginSchema, RegisterSchema, TokenData
from src.users.models import User
from src.users import auth, utils

@dataclass
class UserService:
    user_repository: UserRepository

    async def register(
            self,
            schema: RegisterSchema,
    ):
        if self.user_repository.get_user_by_username(schema.username):
            raise ValueError("User already exists")

        user = User(
            first_name=schema.first_name,
            last_name=schema.last_name,
            username=schema.username,
            password=utils.hash_password(schema.password),
        )

        await self.user_repository.create_user(user)

        access_token, refresh_token = auth.generate_auth_tokens(
            user.id,
        )

        response = JSONResponse(
            content={
                "access_token": access_token,
            },
            status_code=201,
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="None",
            secure=True,
        )

        return response

    async def login(
            self,
            schema: LoginSchema,
    ):
        user = await self.user_repository.get_user_by_username(schema.username)

        if not user:
            raise ValueError("User not found")

        if not utils.verify_password(schema.password, user.password):
            raise ValueError("Invalid password")

        access_token, refresh_token = auth.generate_auth_tokens(
            user.id,
        )

        response = JSONResponse(
            content={
                "access_token": access_token,
            },
            status_code=200,
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="None",
            secure=True,
        )

        return response

    @staticmethod
    async def refresh(
            request: Request,
    ):
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise ValueError("Refresh token not found")

        token_data = auth.decode_token(
            refresh_token,
            auth.credentials_exception,
        )

        if not token_data:
            raise ValueError("Invalid refresh token")

        if token_data.action != "auth":
            raise ValueError("Invalid action for refresh token")

        access_token, refresh_token = auth.generate_auth_tokens(token_data.user_id)

        response = JSONResponse(
            content={
                "access_token": access_token,
            },
            status_code=200,
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="None",
            secure=True,
        )

        return response

    @staticmethod
    async def logout():
        response = JSONResponse(
            content={
                "message": "Logged out",
            },
            status_code=200,
        )
        response.delete_cookie(
            key="refresh_token",
        )

        return response
