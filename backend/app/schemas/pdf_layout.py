from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PdfLayoutBase(BaseModel):
    name: str = Field(..., max_length=100)
    slug: str = Field(..., max_length=50)
    description: Optional[str] = None
    config_json: dict = Field(default_factory=dict)
    is_active: bool = True


class PdfLayoutCreate(PdfLayoutBase):
    pass


class PdfLayoutUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    slug: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    config_json: Optional[dict] = None
    is_active: Optional[bool] = None


class PdfLayoutResponse(PdfLayoutBase):
    id: UUID
    tenant_id: Optional[UUID] = None
    is_system: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PdfLayoutListResponse(BaseModel):
    layouts: list[PdfLayoutResponse]
    total: int
