import pytest
from fastapi import status, Request
from unittest.mock import MagicMock, AsyncMock

from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse

from src.base.exceptions import UnAuthorizedException, BadRequestException

pytestmark = pytest.mark.asyncio

LOGIN_DATA = {"username": "testuser", "password": "password123"}
REGISTER_DATA = {
    "first_name": "Test",
    "last_name": "User",
    "username": "testuser",
    "password": "password123",
}
OLD_REFRESH_TOKEN = "old_fake_refresh_token"
AUTH_RESPONSE_DATA = {"access_token": "fake_access_token"}


async def test_login_success(client: TestClient, mock_user_service: MagicMock):
    """Test successful user login endpoint."""
    mock_user_service.login.return_value = AUTH_RESPONSE_DATA

    response = client.post("/user/login", json=LOGIN_DATA)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == AUTH_RESPONSE_DATA
    mock_user_service.login.assert_awaited_once()


async def test_login_invalid_credentials(client: TestClient, mock_user_service: MagicMock):
    """Test login endpoint with invalid credentials."""
    mock_user_service.login.side_effect = UnAuthorizedException

    response = client.post("/user/login", json=LOGIN_DATA)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    mock_user_service.login.assert_awaited_once()


async def test_register_success(client: TestClient, mock_user_service: MagicMock):
    """Test successful user registration endpoint."""
    mock_user_service.register.return_value = JSONResponse(
        content=AUTH_RESPONSE_DATA,
        status_code=status.HTTP_201_CREATED
    )

    response = client.post("/user/register", json=REGISTER_DATA)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == AUTH_RESPONSE_DATA
    mock_user_service.register.assert_awaited_once()


async def test_register_user_exists(client: TestClient, mock_user_service: MagicMock):
    """Test registration endpoint when the user already exists."""
    mock_user_service.register.side_effect = BadRequestException

    mock_user_service.register.return_value = BadRequestException

    response = client.post("/user/register", json=REGISTER_DATA)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    mock_user_service.register.assert_awaited_once()


async def test_refresh_success(client: TestClient, mock_user_service: MagicMock):
    """Test a successful token refresh endpoint via dependency injection."""

    mock_user_service.refresh = AsyncMock(return_value=AUTH_RESPONSE_DATA)

    client.cookies.set("refresh_token", OLD_REFRESH_TOKEN)

    response = client.post("/user/refresh")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == AUTH_RESPONSE_DATA

    mock_user_service.refresh.assert_awaited_once()
    request_arg = mock_user_service.refresh.await_args[0][0]

    assert isinstance(request_arg, Request)
    assert request_arg.cookies.get("refresh_token") == OLD_REFRESH_TOKEN


async def test_refresh_no_token(client: TestClient, mock_user_service: MagicMock):
    """Test token refresh without refresh token cookie."""
    mock_user_service.refresh.side_effect = UnAuthorizedException

    mock_user_service.refresh.return_value = MagicMock(
        status_code=status.HTTP_401_UNAUTHORIZED,
        body=b'{"detail": "Refresh token not found"}',
        headers={"content-type": "application/json"},
        cookies={}
    )
    mock_user_service.refresh.return_value.json.return_value = {
        "detail": "Refresh token not found"}

    response = client.post("/user/refresh")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_logout_success(client: TestClient, mock_user_service: MagicMock):
    """Test successful logout."""
    mock_user_service.logout.return_value = MagicMock(
        status_code=status.HTTP_200_OK,
        body=b'{"message": "Logged out"}',
        headers={'content-type': 'application/json',
                 'set-cookie': 'refresh_token=; Max-Age=0; Path=/; SameSite=None; HttpOnly; Secure'},
        cookies={}
    )
    mock_user_service.logout.return_value.json.return_value = {
        "message": "Logged out"}

    response = client.post("/user/logout")

    assert response.status_code == status.HTTP_200_OK
    assert "refresh_token=" in response.headers.get("set-cookie", "")
    assert "Max-Age=0" in response.headers.get("set-cookie", "")
