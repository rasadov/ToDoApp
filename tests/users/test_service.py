import pytest
from unittest.mock import patch, MagicMock, ANY, AsyncMock
from fastapi import status, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from src.base.exceptions import UnAuthorizedException, BadRequestException, NotFoundException
from src.users.service import UserService
from src.users.schemas import RegisterSchema, LoginSchema, TokenData
from src.users.models import User

pytestmark = pytest.mark.asyncio

new_username = "testuser"

# Sample data
REGISTER_SCHEMA = RegisterSchema(
    first_name="Test", last_name="User", username=new_username, password="password123"
)
LOGIN_SCHEMA = LoginSchema(username=new_username, password="password123")
MOCK_USER = User(
    id=1,
    first_name="Test",
    last_name="User",
    username=new_username,
    password="hashed_password",
)
AUTH_RESPONSE_DATA = {"access_token": "fake_access_token"}
LOGIN_DATA = {"username": "testuser", "password": "password123"}
ACCESS_TOKEN = "fake_access_token"
REFRESH_TOKEN = "fake_refresh_token"
NEW_REFRESH_TOKEN = "new_fake_refresh_token_value"  # Example new token value


class SimpleMockRequest:
    def __init__(self, cookies_dict=None):
        self.cookies = cookies_dict if cookies_dict is not None else {}

# --- Test Register ---


@pytest.fixture
def mock_user() -> User:
    """Provides a mock User instance for tests."""
    return User(id=1, username="testuser", password="hashed_password", first_name="Test", last_name="User")


@patch("src.users.service.utils.hash_password", return_value="hashed_password")
@patch("src.users.service.auth.generate_auth_tokens", return_value=(ACCESS_TOKEN, REFRESH_TOKEN))
async def test_register_success(
    mock_gen_tokens: MagicMock,
    mock_hash_pw: MagicMock,
    user_service: UserService,
    mock_user_repository: MagicMock,
    mock_user: User,  # Inject the mock_user fixture
):
    """Test successful user registration in service."""
    # Configure get_user_by_username
    mock_user_repository.get_user_by_username.return_value = None  # User does not exist

    # Configure create_user mock using side_effect to simulate ID assignment
    async def create_user_side_effect(user_obj_passed_to_method):
        # Simulate the DB assigning an ID to the object passed in
        user_obj_passed_to_method.id = mock_user.id  # Assign the ID (e.g., 1)
        # The real method often returns the same (now refreshed) object
        return user_obj_passed_to_method

    mock_user_repository.create_user.side_effect = create_user_side_effect
    # Do not set return_value if using side_effect for the same mock method
    # mock_user_repository.create_user.return_value = MOCK_USER # Remove/comment out

    # --- Run the service method ---
    response = await user_service.register(REGISTER_SCHEMA)

    # --- Assertions ---
    mock_user_repository.get_user_by_username.assert_awaited_once_with(
        REGISTER_SCHEMA.username)
    mock_hash_pw.assert_called_once_with(REGISTER_SCHEMA.password)

    # Check create_user was called and the object passed to it
    mock_user_repository.create_user.assert_awaited_once()
    call_args = mock_user_repository.create_user.call_args[0][0]
    assert isinstance(call_args, User)
    assert call_args.username == REGISTER_SCHEMA.username
    assert call_args.password == "hashed_password"
    # Verify the side effect assigned the ID *before* generate_auth_tokens was called
    assert call_args.id == mock_user.id

    # This assertion should now pass
    mock_gen_tokens.assert_called_once_with(mock_user.id)

    # Response assertions (remain the same)
    assert isinstance(response, JSONResponse)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.body == b'{"access_token":"fake_access_token"}'
    assert "refresh_token" in response.headers["set-cookie"]


async def test_register_user_already_exists(
    user_service: UserService,
    mock_user_repository: MagicMock,
    mock_user: User  # Inject user data
):
    """Test registration when username already exists."""
    mock_user_repository.get_user_by_username.return_value = mock_user  # Simulate user found

    # Expect BadRequestException instead of UnAuthorizedException
    with pytest.raises(BadRequestException, match="User already exists"):
        await user_service.register(REGISTER_SCHEMA)

    # Assertions after the check
    mock_user_repository.get_user_by_username.assert_awaited_once_with(
        REGISTER_SCHEMA.username)
    mock_user_repository.create_user.assert_not_awaited()

# --- Test Login ---


# Use TestClient type hint
async def test_login_success(client: TestClient, mock_user_service: MagicMock):
    """Test successful user login endpoint."""
    # Configure the mock service method to return data matching AuthResponseSchema
    mock_user_service.login.return_value = AUTH_RESPONSE_DATA  # <-- RETURN DICT/MODEL

    # Call the endpoint
    # TestClient calls are synchronous
    response = client.post("/user/login", json=LOGIN_DATA)

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == AUTH_RESPONSE_DATA
    # You cannot directly assert cookies set by the *service* layer mock here.
    # If the service layer returns a JSONResponse, you'd need a different mocking approach.
    # Assuming service layer returns data and FastAPI builds the response:
    # To test cookies properly, you might need integration tests or adjust service mock.
    # For now, focus on status and JSON body.
    mock_user_service.login.assert_awaited_once()


async def test_login_user_not_found(
    user_service: UserService, mock_user_repository: MagicMock
):
    """Test login when user is not found."""
    mock_user_repository.get_user_by_username.return_value = None

    with pytest.raises(NotFoundException, match="User not found"):
        await user_service.login(LOGIN_SCHEMA)

    mock_user_repository.get_user_by_username.assert_awaited_once_with(
        LOGIN_SCHEMA.username)


@patch("src.users.service.utils.verify_password", return_value=False)
async def test_login_invalid_password(
    mock_verify_pw: MagicMock,
    user_service: UserService,
    mock_user_repository: MagicMock,
):
    """Test login with invalid password."""
    mock_user_repository.get_user_by_username.return_value = MOCK_USER

    with pytest.raises(UnAuthorizedException, match="Incorrect username or password"):
        await user_service.login(LOGIN_SCHEMA)

    mock_user_repository.get_user_by_username.assert_awaited_once_with(
        LOGIN_SCHEMA.username)
    mock_verify_pw.assert_called_once_with(
        LOGIN_SCHEMA.password, MOCK_USER.password)


# --- Test Refresh ---

# Assuming "auth" is the action type
MOCK_TOKEN_DATA_AUTH = TokenData(user_id=MOCK_USER.id, action="auth")
MOCK_TOKEN_DATA_WRONG_ACTION = TokenData(
    user_id=MOCK_USER.id, action="password_reset")  # Example wrong action


@patch("src.users.service.auth.decode_token", return_value=MOCK_TOKEN_DATA_AUTH)
@patch("src.users.service.auth.generate_auth_tokens", return_value=("new_" + ACCESS_TOKEN, "new_" + REFRESH_TOKEN))
async def test_refresh_success(
    mock_gen_tokens: MagicMock,
    mock_decode: MagicMock,
    # Remove mock_request fixture if using SimpleMockRequest
):
    """Test successful token refresh static method directly."""
    # Create a simple mock request object
    simple_mock_request = SimpleMockRequest(
        cookies_dict={"refresh_token": REFRESH_TOKEN})

    # Call the static method DIRECTLY
    try:
        response = await UserService.refresh(simple_mock_request)
    except RecursionError as e:
        pytest.fail(
            f"RecursionError occurred during UserService.refresh call: {e}")

    # ---- Assertions on the Response from the Service ----
    assert isinstance(response, JSONResponse)
    assert response.status_code == status.HTTP_200_OK
    # Decode body to check content
    import json
    expected_content = {"access_token": "new_" + ACCESS_TOKEN}
    assert json.loads(response.body.decode()) == expected_content
    # Check Set-Cookie header
    assert f"refresh_token=new_{REFRESH_TOKEN}" in response.headers.get(
        "set-cookie", "")

    mock_decode.assert_called_once_with(REFRESH_TOKEN, ANY)
    mock_gen_tokens.assert_called_once_with(MOCK_USER.id)


async def test_refresh_no_token_cookie(mock_request: MagicMock):
    """Test refresh when refresh token cookie is missing."""
    mock_request.cookies = {}  # No cookie

    with pytest.raises(UnAuthorizedException, match="Refresh token not found"):
        await UserService.refresh(mock_request)


@patch("src.users.service.auth.decode_token", return_value=None)
async def test_refresh_invalid_token(
    mock_decode: MagicMock,
    mock_request: MagicMock,
):
    """Test refresh with an invalid or expired token."""
    mock_request.cookies = {"refresh_token": "invalid_or_expired_token"}

    # The exception from decode_token should propagate
    with pytest.raises(UnAuthorizedException, match="Invalid refresh token"):
        await UserService.refresh(mock_request)

    mock_decode.assert_called_once_with("invalid_or_expired_token", ANY)


@patch("src.users.service.auth.decode_token", return_value=None)
async def test_refresh_invalid_token_data(
    mock_decode: MagicMock,
    mock_request: MagicMock,
):
    """Test refresh when token decodes but data is invalid (e.g., None)."""
    mock_request.cookies = {"refresh_token": REFRESH_TOKEN}

    with pytest.raises(UnAuthorizedException, match="Invalid refresh token"):
        await UserService.refresh(mock_request)

    mock_decode.assert_called_once_with(REFRESH_TOKEN, ANY)


@patch("src.users.service.auth.decode_token", return_value=MOCK_TOKEN_DATA_WRONG_ACTION)
async def test_refresh_wrong_action(
    mock_decode: MagicMock,
    mock_request: MagicMock,
):
    """Test refresh with a token meant for a different action."""
    mock_request.cookies = {"refresh_token": REFRESH_TOKEN}

    with pytest.raises(UnAuthorizedException, match="Invalid token action"):
        await UserService.refresh(mock_request)

    mock_decode.assert_called_once_with(REFRESH_TOKEN, ANY)


# --- Test Logout ---

async def test_logout():
    """Test logout service method."""
    response = await UserService.logout()

    assert isinstance(response, JSONResponse)
    assert response.status_code == status.HTTP_200_OK
    assert response.body == b'{"message":"Logged out"}'
    # Check cookie deletion header
    assert "refresh_token=" in response.headers.get("set-cookie", "")
    assert "Max-Age=0" in response.headers.get("set-cookie", "")
