"""
Calibration certificate Pydantic schemas.
"""
import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class CertificateCreate(BaseModel):
    """Schema for creating a calibration certificate."""
    equipment_name: str = Field(..., min_length=1, max_length=255)
    certificate_number: str = Field(..., min_length=1, max_length=100)
    manufacturer: Optional[str] = Field(None, max_length=255)
    model: Optional[str] = Field(None, max_length=255)
    serial_number: Optional[str] = Field(None, max_length=255)
    laboratory: Optional[str] = Field(None, max_length=255)
    calibration_date: date
    expiry_date: date
    status: str = Field(default="valid", pattern="^(valid|expiring|expired)$")


class CertificateUpdate(BaseModel):
    """Schema for updating a calibration certificate."""
    equipment_name: Optional[str] = Field(None, min_length=1, max_length=255)
    certificate_number: Optional[str] = Field(None, min_length=1, max_length=100)
    manufacturer: Optional[str] = Field(None, max_length=255)
    model: Optional[str] = Field(None, max_length=255)
    serial_number: Optional[str] = Field(None, max_length=255)
    laboratory: Optional[str] = Field(None, max_length=255)
    calibration_date: Optional[date] = None
    expiry_date: Optional[date] = None
    status: Optional[str] = Field(None, pattern="^(valid|expiring|expired)$")


class CertificateResponse(BaseModel):
    """Schema for certificate response."""
    id: uuid.UUID
    tenant_id: uuid.UUID
    equipment_name: str
    certificate_number: str
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    laboratory: Optional[str] = None
    calibration_date: date
    expiry_date: date
    file_key: Optional[str] = None
    status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CertificateListResponse(BaseModel):
    """Schema for paginated certificate list."""
    certificates: list[CertificateResponse]
    total: int


class ReportCertificateLink(BaseModel):
    """Schema for linking certificates to a report."""
    certificate_ids: list[uuid.UUID]
