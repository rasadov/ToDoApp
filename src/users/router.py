from fastapi import APIRouter, Depends, Request

from src.dependencies import get_user_service
from src.users import UserService
from src.users.schemas import LoginSchema, RegisterSchema, AuthResponseSchema

router = APIRouter(
    prefix="/user",
    tags=["user"],
)

@router.post(
    "/login",
    response_model=AuthResponseSchema,
)
async def login(
        schema: LoginSchema,
        user_service: UserService = Depends(get_user_service),
):
    """Login endpoint."""
    return await user_service.login(schema)

@router.post(
    "/register",
    response_model=AuthResponseSchema,
)
async def register(
        schema: RegisterSchema,
        user_service: UserService = Depends(get_user_service),
):
    return await user_service.register(schema)

@router.post("/refresh")
async def refresh(
        request: Request,
        user_service: UserService = Depends(get_user_service),
):
    """Refresh token endpoint."""
    return await user_service.refresh(request)

@router.post("/logout")
async def logout():
    """Logout endpoint."""
    return await UserService.logout()

