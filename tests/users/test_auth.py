import pytest
from unittest.mock import patch
from datetime import datetime, timedelta, timezone

import jwt

from src.users.auth import (
    create_access_token,
    create_refresh_token,
    generate_auth_tokens,
    decode_token,
    verify_action_token,
    AuthTokenTypes,
    get_payload_from_token,  # Assuming you might want to test this too
)
from src.users.schemas import TokenData

# Constants using overridden settings from conftest
SECRET_KEY = "test_secret"
ALGORITHM = "HS256"
ACCESS_EXPIRE_MINUTES = 15
REFRESH_EXPIRE_MINUTES = 1440
USER_ID = 123


@pytest.fixture
def mock_datetime_now():
    """Fixture to mock datetime.now to control token expiration."""
    fixed_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    # Patch datetime.now within the module where it's CALLED (src.users.auth)
    with patch("src.users.auth.datetime") as mock_dt:
        mock_dt.now.return_value = fixed_time
        yield fixed_time  # Yield the fixed time for use in tests

# --- Updated Test ---


def test_create_access_token(mock_datetime_now):
    """Test creating an access token."""
    token = create_access_token(USER_ID)

    # Decode WITHOUT verifying expiration for this test
    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
        options={"verify_exp": False}  # <--- ADD THIS OPTION
    )

    expected_exp_dt = mock_datetime_now + \
        timedelta(minutes=ACCESS_EXPIRE_MINUTES)

    assert isinstance(token, str)
    assert payload["user_id"] == USER_ID
    assert payload["action"] == AuthTokenTypes.ACCESS
    # We can still check if the 'exp' claim was calculated correctly
    assert payload["exp"] == pytest.approx(expected_exp_dt.timestamp())

# --- Updated Test ---


def test_create_refresh_token(mock_datetime_now):
    """Test creating a refresh token."""
    token = create_refresh_token(USER_ID)

    # Decode WITHOUT verifying expiration for this test
    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
        options={"verify_exp": False}  # <--- ADD THIS OPTION
    )

    expected_exp_dt = mock_datetime_now + \
        timedelta(minutes=REFRESH_EXPIRE_MINUTES)

    assert isinstance(token, str)
    assert payload["user_id"] == USER_ID
    assert payload["action"] == AuthTokenTypes.REFRESH
    # We can still check if the 'exp' claim was calculated correctly
    assert payload["exp"] == pytest.approx(expected_exp_dt.timestamp())


def test_generate_auth_tokens():
    """Test generating both access and refresh tokens."""
    access_token, refresh_token = generate_auth_tokens(USER_ID)

    assert isinstance(access_token, str)
    assert isinstance(refresh_token, str)

    access_payload = jwt.decode(
        access_token, SECRET_KEY, algorithms=[ALGORITHM])
    refresh_payload = jwt.decode(
        refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

    assert access_payload["user_id"] == USER_ID
    assert access_payload["action"] == AuthTokenTypes.ACCESS
    assert refresh_payload["user_id"] == USER_ID
    assert refresh_payload["action"] == AuthTokenTypes.REFRESH


def test_decode_token_success():
    """Test decoding a valid token."""
    access_token = create_access_token(USER_ID)
    credentials_exception = ValueError("Decode Error")  # Example exception

    token_data = decode_token(access_token, credentials_exception)

    assert isinstance(token_data, TokenData)
    assert token_data.user_id == USER_ID
    assert token_data.action == AuthTokenTypes.ACCESS


def test_decode_token_invalid_signature():
    """Test decoding a token with an invalid signature."""
    access_token = create_access_token(USER_ID)
    invalid_token = access_token[:-5] + "xxxxx"  # Tamper with signature
    credentials_exception = ValueError("Decode Error")

    with pytest.raises(ValueError, match="Decode Error"):
        decode_token(invalid_token, credentials_exception)


@patch("src.users.auth.jwt.decode", side_effect=jwt.ExpiredSignatureError)
def test_decode_token_expired(mock_jwt_decode):
    """Test decoding an expired token."""
    expired_token = "fake_expired_token"  # Content doesn't matter due to mock
    credentials_exception = ValueError("Token Expired")

    with pytest.raises(ValueError, match="Token Expired"):
        decode_token(expired_token, credentials_exception)
    mock_jwt_decode.assert_called_once_with(
        expired_token, SECRET_KEY, [ALGORITHM])


def test_verify_action_token_success():
    """Test verifying a token with the correct action."""
    access_token = create_access_token(USER_ID)
    credentials_exception = ValueError("Verify Error")

    verified_user_id = verify_action_token(
        access_token,
        AuthTokenTypes.ACCESS,  # Expected action
        credentials_exception
    )

    assert verified_user_id == USER_ID


def test_verify_action_token_wrong_action():
    """Test verifying a token with the wrong action."""
    access_token = create_access_token(USER_ID)  # This has ACCESS action
    credentials_exception = ValueError("Verify Error")

    verified_user_id = verify_action_token(
        access_token,
        AuthTokenTypes.REFRESH,  # Expecting REFRESH, but token is ACCESS
        credentials_exception
    )

    assert verified_user_id is None


def test_verify_action_token_invalid_token():
    """Test verifying an invalid token."""
    invalid_token = "this.is.not.a.jwt"
    credentials_exception = ValueError("Verify Error")

    # decode_token will raise the exception
    with pytest.raises(ValueError, match="Verify Error"):
        verify_action_token(
            invalid_token,
            AuthTokenTypes.ACCESS,
            credentials_exception
        )


def test_get_payload_from_token():
    """ Test extracting payload directly"""
    token = create_access_token(USER_ID)
    payload = get_payload_from_token(token)

    assert payload["user_id"] == USER_ID
    assert payload["action"] == AuthTokenTypes.ACCESS
    assert "exp" in payload
