"""
PDF generation package.

Provides both the legacy PDFService (backward compatible) and the new
ComponentPDFService with pluggable renderers.
"""

from .pdf_service import ComponentPDFService
from .layout_config import LayoutConfig

__all__ = ["ComponentPDFService", "LayoutConfig"]
