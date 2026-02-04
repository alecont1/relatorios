"""
Authentication endpoints: login, logout, refresh, and user info.
"""

from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.models.user import User
from app.schemas.user import UserResponse, UserWithToken


router = APIRouter(prefix="/auth", tags=["auth"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/login", response_model=UserWithToken)
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user with email and password.

    Returns access token in response body.
    Sets refresh token in httpOnly cookie.

    Rate limited to 5 requests per minute per IP.
    """
    # Find user by email (form_data.username is the email)
    result = await db.execute(
        select(User).where(User.email == form_data.username)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email nao encontrado",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inativo",
        )

    # Verify password in thread pool (CPU-intensive Argon2)
    is_valid = await run_in_threadpool(
        verify_password, form_data.password, user.password_hash
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha incorreta",
        )

    # Create tokens with user claims
    # tenant_id can be None for superadmin users
    token_data = {
        "sub": str(user.id),
        "tenant_id": str(user.tenant_id) if user.tenant_id else None,
        "role": user.role,
    }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    # Set refresh token in httpOnly cookie
    # samesite="none" required for cross-origin requests (Vercel frontend -> Railway backend)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # HTTPS only in production
        samesite="none",  # Required for cross-origin
        max_age=7 * 24 * 60 * 60,  # 7 days in seconds
        path="/api/v1/auth",  # Only sent to auth endpoints
    )

    return UserWithToken(
        user=UserResponse.model_validate(user),
        access_token=access_token,
    )


@router.post("/refresh", response_model=UserWithToken)
async def refresh_tokens(
    request: Request,
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Get new access token using refresh token from cookie.

    Also rotates the refresh token (issues new one, old becomes invalid).
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token ausente",
        )

    payload = decode_token(refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalido ou expirado",
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido",
        )

    # Get user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario nao encontrado ou inativo",
        )

    # Create new tokens (rotation)
    # tenant_id can be None for superadmin users
    token_data = {
        "sub": str(user.id),
        "tenant_id": str(user.tenant_id) if user.tenant_id else None,
        "role": user.role,
    }
    new_access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)

    # Set new refresh token cookie
    # samesite="none" required for cross-origin requests (Vercel frontend -> Railway backend)
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="none",  # Required for cross-origin
        max_age=7 * 24 * 60 * 60,
        path="/api/v1/auth",
    )

    return UserWithToken(
        user=UserResponse.model_validate(user),
        access_token=new_access_token,
    )


@router.post("/logout")
async def logout(
    response: Response,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Logout current user by clearing refresh token cookie.

    Note: Access token remains valid until expiry (15 min).
    For immediate invalidation, implement token blacklist (future).
    """
    response.delete_cookie(
        key="refresh_token",
        path="/api/v1/auth",
        httponly=True,
        secure=True,
        samesite="none",  # Required for cross-origin
    )

    return {"message": "Logout realizado com sucesso"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Get current authenticated user's information."""
    return UserResponse.model_validate(current_user)
