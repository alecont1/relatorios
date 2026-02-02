"""
Pydantic schemas for photo metadata.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class GPSCoordinates(BaseModel):
    """GPS coordinates with accuracy."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy: Optional[float] = Field(None, ge=0, description="Accuracy in meters")


class PhotoMetadata(BaseModel):
    """
    Complete photo metadata stored in JSONB.

    This schema represents a single photo attached to a checklist response.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    url: str = Field(..., description="Full URL to the photo")
    thumbnail_url: Optional[str] = Field(None, description="URL to thumbnail version")
    original_filename: Optional[str] = None
    size_bytes: Optional[int] = Field(None, ge=0)
    width: Optional[int] = Field(None, ge=1)
    height: Optional[int] = Field(None, ge=1)
    captured_at: datetime = Field(default_factory=datetime.utcnow)
    gps: Optional[GPSCoordinates] = None
    address: Optional[str] = Field(None, description="Reverse geocoded address")
    watermarked: bool = False

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PhotoUploadRequest(BaseModel):
    """Request body for photo upload metadata."""
    response_id: str = Field(..., description="ID of the checklist response")
    captured_at: Optional[datetime] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    gps_accuracy: Optional[float] = Field(None, ge=0)
    address: Optional[str] = None


class PhotoUploadResponse(BaseModel):
    """Response after successful photo upload."""
    photo: PhotoMetadata
    message: str = "Photo uploaded successfully"


class PhotoDeleteResponse(BaseModel):
    """Response after photo deletion."""
    deleted: bool = True
    message: str = "Photo deleted successfully"


class PhotoListResponse(BaseModel):
    """Response for listing photos."""
    response_id: str
    field_label: str
    photos: list[PhotoMetadata]
    max_photos: Optional[int] = None
    required: bool = False
