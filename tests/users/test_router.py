import pytest
from fastapi import status, Request
from unittest.mock import MagicMock, AsyncMock, patch

from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse

from src.base.exceptions import UnAuthorizedException, BadRequestException

# Use the client fixture defined in conftest.py
pytestmark = pytest.mark.asyncio

# Sample data for schemas
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
    # Configure the mock service method to return data matching AuthResponseSchema
    mock_user_service.login.return_value = AUTH_RESPONSE_DATA  # <-- Supposedly corrected

    # Call the endpoint
    # TestClient calls are sync
    response = client.post("/user/login", json=LOGIN_DATA)

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == AUTH_RESPONSE_DATA
    mock_user_service.login.assert_awaited_once()


async def test_login_invalid_credentials(client: TestClient, mock_user_service: MagicMock):
    """Test login endpoint with invalid credentials."""
    # Configure the mock service method to RAISE the error the handler expects
    error_message = "Invalid password"
    # Use the specific exception type your handler catches, if applicable
    mock_user_service.login.side_effect = UnAuthorizedException
    # Or: mock_user_service.login.side_effect = InvalidCredentialsError(error_message)

    # Call the endpoint - the exception handler should catch the ValueError
    response = client.post("/user/login", json=LOGIN_DATA)

    # Assertions based on what the EXCEPTION HANDLER returns
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    # assert response.json() == {"detail": "Invalid username or password"}
    mock_user_service.login.assert_awaited_once()


async def test_register_success(client: TestClient, mock_user_service: MagicMock):
    """Test successful user registration endpoint."""
    # Configure mock to return an actual JSONResponse with status 201
    mock_user_service.register.return_value = JSONResponse(
        content=AUTH_RESPONSE_DATA,
        status_code=status.HTTP_201_CREATED
    )

    # Call the endpoint
    response = client.post("/user/register", json=REGISTER_DATA)

    # Assertions
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == AUTH_RESPONSE_DATA
    mock_user_service.register.assert_awaited_once()


async def test_register_user_exists(client: TestClient, mock_user_service: MagicMock):
    """Test registration endpoint when user already exists."""
    mock_user_service.register.side_effect = BadRequestException

    mock_user_service.register.return_value = BadRequestException

    response = client.post("/user/register", json=REGISTER_DATA)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    mock_user_service.register.assert_awaited_once()


async def test_refresh_success(client: TestClient, mock_user_service: MagicMock):
    """Test successful token refresh endpoint via dependency injection."""

    # Configure the mock service instance's refresh method.
    # Let's configure it to return the expected data dict.
    # We need to make the mock method awaitable, so use AsyncMock or configure return directly.
    mock_user_service.refresh = AsyncMock(return_value=AUTH_RESPONSE_DATA)

    cookies = {"refresh_token": OLD_REFRESH_TOKEN}
    # Use the TestClient to make the HTTP request
    # This call should hit the mock
    response = client.post("/user/refresh", cookies=cookies)

    # ---- Assertions on the HTTP Response ----
    # FastAPI should create a 200 OK response by default from the dict
    assert response.status_code == status.HTTP_200_OK
    # The JSON body should match the data returned by the mock
    assert response.json() == AUTH_RESPONSE_DATA

    # ---- Assertions on the Mock ----
    # Verify the mock service instance's refresh method was called
    mock_user_service.refresh.assert_awaited_once()
    # Check the arguments passed to the mock method
    request_arg = mock_user_service.refresh.await_args[0][0]
    assert isinstance(request_arg, Request)
    assert request_arg.cookies.get("refresh_token") == OLD_REFRESH_TOKEN


async def test_refresh_no_token(client: TestClient, mock_user_service: MagicMock):
    """Test token refresh without refresh token cookie."""
    mock_user_service.refresh.side_effect = UnAuthorizedException
    # Assuming this translates to 401 or 400
    mock_user_service.refresh.return_value = MagicMock(
        status_code=status.HTTP_401_UNAUTHORIZED,
        body=b'{"detail": "Refresh token not found"}',
        headers={"content-type": "application/json"},
        cookies={}
    )
    mock_user_service.refresh.return_value.json.return_value = {
        "detail": "Refresh token not found"}

    response = client.post("/user/refresh")  # No cookie sent

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_logout_success(client: TestClient, mock_user_service: MagicMock):
    """Test successful logout."""
    mock_user_service.logout.return_value = MagicMock(
        status_code=status.HTTP_200_OK,
        body=b'{"message": "Logged out"}',
        headers={'content-type': 'application/json',
                 # Simulate cookie deletion
                 'set-cookie': 'refresh_token=; Max-Age=0; Path=/; SameSite=None; HttpOnly; Secure'},
        cookies={}
    )
    mock_user_service.logout.return_value.json.return_value = {
        "message": "Logged out"}

    response = client.post("/user/logout")

    assert response.status_code == status.HTTP_200_OK
    assert "refresh_token=" in response.headers.get("set-cookie", "")
    assert "Max-Age=0" in response.headers.get("set-cookie", "")
