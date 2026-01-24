from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


# Create FastAPI application
app = FastAPI(
    title="SmartHand API",
    version=settings.app_version,
    lifespan=lifespan
)

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

app.include_router(health_router, prefix="/api/v1")
