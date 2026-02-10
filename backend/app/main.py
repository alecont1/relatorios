from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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
    lifespan=lifespan,
    redirect_slashes=True  # Enable automatic redirect for trailing slashes
)

# Configure rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origins_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.users import router as users_router
from app.api.v1.routes.tenant_settings import router as tenant_settings_router
from app.api.v1.routes.tenants import router as tenants_router
from app.api.v1.routes.templates import router as templates_router
from app.api.v1.routes.template_info_fields import router as template_info_fields_router
from app.api.v1.routes.template_signature_fields import router as template_signature_fields_router
from app.api.v1.routes.template_field_config import router as template_field_config_router
from app.api.v1.routes.reports import router as reports_router
from app.api.v1.routes.photos import router as photos_router
from app.api.v1.routes.signatures import router as signatures_router
from app.api.v1.routes.certificates import router as certificates_router
from app.api.v1.routes.report_certificates import router as report_certificates_router

app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(tenant_settings_router, prefix="/api/v1")
app.include_router(tenants_router, prefix="/api/v1")
app.include_router(templates_router, prefix="/api/v1")
app.include_router(template_info_fields_router, prefix="/api/v1")
app.include_router(template_signature_fields_router, prefix="/api/v1")
app.include_router(template_field_config_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(photos_router, prefix="/api/v1")
app.include_router(signatures_router, prefix="/api/v1")
app.include_router(certificates_router, prefix="/api/v1")
app.include_router(report_certificates_router, prefix="/api/v1")

# Mount static files for local photo storage (development)
uploads_path = Path("uploads")
uploads_path.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")
