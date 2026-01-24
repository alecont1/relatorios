from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/")
async def health_check():
    """
    Health check endpoint.

    Returns application status, version, and name.
    Used by load balancers and monitoring systems.
    """
    return {
        "status": "ok",
        "version": settings.app_version,
        "app": settings.app_name
    }


@router.get("/health")
async def health():
    """
    Alternative health check endpoint.

    Returns same information as root endpoint.
    Provided for compatibility with different load balancers.
    """
    return {
        "status": "ok",
        "version": settings.app_version,
        "app": settings.app_name
    }
