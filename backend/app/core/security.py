"""
Security utilities for JWT tokens and password hashing.

This module provides:
- JWT access and refresh token creation/verification
- Password hashing with Argon2 (NIST recommended)
"""

from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.core.config import settings


# Password hasher using Argon2 (recommended by NIST)
password_hash = PasswordHash.recommended()


def create_access_token(data: dict) -> str:
    """
    Create JWT access token with 15-minute expiry.

    Args:
        data: Payload data (typically includes sub, tenant_id, role)

    Returns:
        Encoded JWT access token
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )


def create_refresh_token(data: dict) -> str:
    """
    Create JWT refresh token with 7-day expiry.

    Args:
        data: Payload data (typically includes sub, tenant_id, role)

    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash.

    Note: This is CPU-intensive. Run in threadpool for async routes:
        await run_in_threadpool(verify_password, password, hash)

    Args:
        plain_password: Plain text password to verify
        hashed_password: Stored hash to verify against

    Returns:
        True if password matches, False otherwise
    """
    try:
        return password_hash.verify(plain_password, hashed_password)
    except Exception:
        # Hash format not recognized - return False instead of crashing
        return False


def hash_password(password: str) -> str:
    """
    Hash password using Argon2.

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password string
    """
    return password_hash.hash(password)


def decode_token(token: str) -> dict | None:
    """
    Decode and verify JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded payload dict, or None if invalid/expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except jwt.InvalidTokenError:
        return None
