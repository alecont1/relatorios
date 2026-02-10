"""
Pydantic schemas for SuperAdmin tenant management.

Covers TenantPlan CRUD, TenantConfig responses, tenant provisioning,
suspension, and audit log responses.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# --- Structured limit/feature schemas ---

class TenantLimits(BaseModel):
    """Resource limits for a tenant."""
    max_users: int = Field(..., ge=1, description="Maximum number of users")
    max_storage_gb: float = Field(..., ge=0.1, description="Maximum storage in GB")
    max_reports_month: int = Field(..., ge=1, description="Maximum reports per month")


class TenantFeatures(BaseModel):
    """Feature flags for a tenant."""
    gps_required: bool = Field(default=True, description="Require GPS on photos")
    certificate_required: bool = Field(default=False, description="Require calibration certificates")
    export_excel: bool = Field(default=True, description="Allow Excel export")
    watermark: bool = Field(default=True, description="Enable photo watermark")
    custom_pdf: bool = Field(default=False, description="Allow custom PDF templates")


# --- TenantPlan schemas ---

class TenantPlanCreate(BaseModel):
    """Schema for creating a new plan."""
    name: str = Field(..., min_length=1, max_length=100, description="Plan name")
    description: Optional[str] = Field(None, description="Plan description")
    limits: TenantLimits
    features: TenantFeatures
    price_display: Optional[str] = Field(None, max_length=50, description="Display price")
    is_active: bool = Field(default=True, description="Whether plan is active")


class TenantPlanUpdate(BaseModel):
    """Schema for updating a plan. All fields optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    limits: Optional[TenantLimits] = None
    features: Optional[TenantFeatures] = None
    price_display: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class TenantPlanResponse(BaseModel):
    """Schema for plan response."""
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    limits: TenantLimits
    features: TenantFeatures
    price_display: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- TenantConfig schemas ---

class TenantConfigResponse(BaseModel):
    """Schema for tenant config response."""
    id: uuid.UUID
    tenant_id: uuid.UUID
    status: str
    contract_type: Optional[str] = None
    limits_json: dict
    features_json: dict
    suspended_at: Optional[datetime] = None
    suspended_reason: Optional[str] = None
    trial_ends_at: Optional[datetime] = None
    plan_id: Optional[uuid.UUID] = None
    plan: Optional[TenantPlanResponse] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TenantConfigUpdate(BaseModel):
    """Schema for updating tenant config (limits, features, contract_type)."""
    limits_json: Optional[dict] = Field(None, description="Resource limits override")
    features_json: Optional[dict] = Field(None, description="Feature flags override")
    contract_type: Optional[str] = Field(None, max_length=50, description="Contract type")


# --- Action request schemas ---

class SuspendTenantRequest(BaseModel):
    """Schema for suspending a tenant."""
    reason: str = Field(..., min_length=5, description="Reason for suspension")


class AssignPlanRequest(BaseModel):
    """Schema for assigning a plan to a tenant."""
    plan_id: uuid.UUID = Field(..., description="Plan ID to assign")


# --- Tenant provisioning schemas ---

class TenantCreateWithConfig(BaseModel):
    """Schema for creating a new tenant with full configuration."""
    name: str = Field(..., min_length=1, max_length=255, description="Tenant organization name")
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$", description="Unique slug")
    plan_id: uuid.UUID = Field(..., description="Plan to assign")
    admin_email: EmailStr = Field(..., description="Initial admin email")
    admin_password: str = Field(..., min_length=8, description="Initial admin password")
    admin_full_name: str = Field(..., min_length=1, description="Initial admin full name")
    contract_type: Optional[str] = Field(None, max_length=50, description="Contract type")
    trial_days: int = Field(default=14, ge=0, description="Trial period in days")


# --- Usage and combined response schemas ---

class TenantUsageResponse(BaseModel):
    """Schema for tenant resource usage."""
    users_count: int
    storage_used_gb: float
    reports_this_month: int


class TenantWithConfigResponse(BaseModel):
    """Schema for tenant with config and usage stats."""
    id: uuid.UUID
    name: str
    slug: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    config: Optional[TenantConfigResponse] = None
    usage: Optional[TenantUsageResponse] = None

    class Config:
        from_attributes = True


# --- Audit log schemas ---

class TenantAuditLogResponse(BaseModel):
    """Schema for audit log response."""
    id: uuid.UUID
    tenant_id: uuid.UUID
    admin_user_id: uuid.UUID
    action: str
    old_values: Optional[dict] = None
    new_values: Optional[dict] = None
    reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
