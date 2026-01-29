"""
Authentication schemas for login request/response.
"""

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Login request with email and password."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Token response returned on successful login."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Decoded token payload data."""
    sub: str | None = None
    tenant_id: str | None = None
    role: str | None = None
    type: str | None = None
