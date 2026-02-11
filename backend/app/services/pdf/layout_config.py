"""
Pydantic model for PDF layout configuration (config_json).

Provides defaults for all fields so old layouts don't break.
"""

from pydantic import BaseModel, Field


class CoverPageConfig(BaseModel):
    enabled: bool = False


class FontsConfig(BaseModel):
    base_size: int = 9
    header_size: int = 14
    section_size: int = 11


class MarginsConfig(BaseModel):
    top: int = 10
    right: int = 10
    bottom: int = 20
    left: int = 10


class PhotosConfig(BaseModel):
    columns: int = 2
    max_per_section: int = 6
    width_mm: int = 80
    height_mm: int = 60


class ChecklistConfig(BaseModel):
    show_all_items: bool = True
    highlight_non_conforming: bool = True


class CertificatesConfig(BaseModel):
    show_table: bool = True


class SignaturesConfig(BaseModel):
    columns: int = 3
    box_width_mm: int = 60
    box_height_mm: int = 30


class LayoutConfig(BaseModel):
    """
    Complete layout configuration with sensible defaults.

    All fields have defaults, so partial config_json from the database
    will be filled in automatically.
    """
    style: str = "default"  # "default" | "gensep" | custom renderer styles
    cover_page: CoverPageConfig = Field(default_factory=CoverPageConfig)
    fonts: FontsConfig = Field(default_factory=FontsConfig)
    margins: MarginsConfig = Field(default_factory=MarginsConfig)
    photos: PhotosConfig = Field(default_factory=PhotosConfig)
    checklist: ChecklistConfig = Field(default_factory=ChecklistConfig)
    certificates: CertificatesConfig = Field(default_factory=CertificatesConfig)
    signatures: SignaturesConfig = Field(default_factory=SignaturesConfig)

    @classmethod
    def from_dict(cls, data: dict | None) -> "LayoutConfig":
        """Create LayoutConfig from dict, filling in defaults for missing fields."""
        if not data:
            return cls()
        return cls(**data)
