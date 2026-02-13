"""
Base renderer with shared PDF utilities.
"""

import logging
import time
from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path
from typing import Any
import urllib.request
import urllib.error

from fpdf import FPDF

logger = logging.getLogger(__name__)

from app.core.config import settings
from .layout_config import LayoutConfig


class BaseRenderer(ABC):
    """Abstract base class for PDF renderers."""

    def __init__(self, pdf: FPDF, config: LayoutConfig, tenant_info: dict):
        self.pdf = pdf
        self.config = config
        self.tenant = tenant_info

    @staticmethod
    def hex_to_rgb(hex_color: str) -> tuple:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip("#")
        if len(hex_color) != 6:
            return (37, 99, 235)
        try:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except ValueError:
            return (37, 99, 235)

    def get_primary_color(self) -> tuple:
        return self.hex_to_rgb(self.tenant.get("primary_color", "#2563eb"))

    def get_secondary_color(self) -> tuple | None:
        sc = self.tenant.get("secondary_color", "")
        return self.hex_to_rgb(sc) if sc else None

    def get_accent_color(self) -> tuple | None:
        ac = self.tenant.get("accent_color", "")
        return self.hex_to_rgb(ac) if ac else None

    def safe_cell(self, w: float, h: float, text: str, border=0, fill=False,
                  align="", new_x="RIGHT", new_y="TOP", font_size=None):
        """
        Render text in a cell, using multi_cell with wrapping if text overflows.
        Returns the actual height used.
        """
        pdf = self.pdf
        if font_size:
            pdf.set_font_size(font_size)

        text = text or ""
        text_width = pdf.get_string_width(text)
        available_width = w - 2

        if text_width <= available_width or not text.strip():
            pdf.cell(w, h, text, border=border, fill=fill, align=align,
                     new_x=new_x, new_y=new_y)
            return h
        else:
            x_before = pdf.get_x()
            y_before = pdf.get_y()
            line_height = h * 0.7 if h > 5 else 3.5
            pdf.multi_cell(w, line_height, text, border=border, fill=fill,
                          align=align, new_x="RIGHT", new_y="TOP",
                          max_line_height=line_height)
            actual_height = pdf.get_y() - y_before
            if actual_height < h:
                actual_height = h
            if new_x == "RIGHT":
                pdf.set_xy(x_before + w, y_before)
            return actual_height

    def add_image_from_url(self, url: str, x: float, y: float, w: float,
                           max_retries: int = 3):
        """Add image from URL or local path with retry logic."""
        try:
            if url.startswith(("http://", "https://")):
                img_data = None
                last_err = None
                for attempt in range(max_retries):
                    try:
                        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                        with urllib.request.urlopen(req, timeout=15) as response:
                            img_data = response.read()
                        break
                    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
                        last_err = e
                        if attempt < max_retries - 1:
                            time.sleep(0.5 * (2 ** attempt))
                if img_data:
                    self.pdf.image(BytesIO(img_data), x, y, w)
                elif last_err:
                    logger.warning("Failed to download image after %d retries: %s - %s",
                                   max_retries, url, last_err)
            else:
                local_path = Path(url)
                if local_path.exists():
                    self.pdf.image(str(local_path), x, y, w)
        except Exception as e:
            logger.warning("Failed to add image to PDF: %s - %s", url, e)

    def resolve_image_url(self, key_or_url: str) -> str:
        """Resolve an R2 object key or URL to a fetchable URL."""
        if not key_or_url:
            return ""
        if key_or_url.startswith(("http://", "https://")):
            return key_or_url
        if key_or_url.startswith("/uploads/"):
            return key_or_url[1:]
        if settings.r2_public_url:
            return f"{settings.r2_public_url}/{key_or_url}"
        return f"uploads/{key_or_url}"
