from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for application startup and shutdown.

    Handles:
    - Database initialization
    - Resource cleanup
    """
    # Startup: initialize database connections, etc.
    # (placeholder for future implementation)
    yield
    # Shutdown: cleanup resources
    # (placeholder for future implementation)


# Rate limiting configuration
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI application
app = FastAPI(
    title="SmartHand API",
    version=settings.app_version,
    lifespan=lifespan
)

# Configure rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.auth import router as auth_router

app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
