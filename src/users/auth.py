"""
Functions for handling OAuth2 token creation and verification.
"""
from datetime import datetime, timedelta, timezone
from enum import Enum

import jwt

from src.users.schemas import TokenData
from src.config import Settings


class AuthTokenTypes(str, Enum):
    """Enum class with authentication token types"""

    ACCESS = "access_token"
    REFRESH = "refresh_token"


def get_payload_from_token(
        access_token: str,
) -> dict:
    payload = jwt.decode(
        access_token,
        Settings.SECRET_KEY,
        [Settings.ALGORITHM],
    )
    return payload


def _create_auth_token(
        data: dict,
        expire_minutes: int,
) -> str:
    to_encode = data.copy()
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        Settings.SECRET_KEY,
        Settings.ALGORITHM
    )


def create_token(
        user_id: int,
        token_type: AuthTokenTypes,
        expire_minutes: int,
) -> str:
    """Create a token with the specified type and expiration"""
    data = {"action": token_type, "user_id": user_id}
    return _create_auth_token(data, expire_minutes)


def create_access_token(
        user_id: int,
) -> str:
    """Create access token"""
    return create_token(
        user_id,
        AuthTokenTypes.ACCESS,
        Settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )


def create_refresh_token(
        user_id: int,
) -> str:
    """Create a refresh token"""
    return create_token(
        user_id,
        AuthTokenTypes.REFRESH,
        Settings.REFRESH_TOKEN_EXPIRE_MINUTES,
    )


def generate_auth_tokens(
        user_id: int,
) -> tuple[str, str]:
    """Generate access and refresh tokens"""
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)

    return access_token, refresh_token


def decode_token(
        token: str,
        credentials_exception: Exception,
) -> TokenData:
    """Decode token"""
    try:
        payload: dict = jwt.decode(
            token,
            Settings.SECRET_KEY,
            [Settings.ALGORITHM]
        )
        token_data = TokenData(
            user_id=payload.get("user_id"),
            action=payload.get("action"))
        return token_data
    except jwt.PyJWTError:
        raise credentials_exception


def verify_action_token(
        token: str,
        action: str,
        credentials_exception: Exception,
) -> int | None:
    """Verify action token"""
    token_data = decode_token(token, credentials_exception)
    if token_data and token_data.user_id and token_data.action == action:
        return token_data.user_id
    return None
