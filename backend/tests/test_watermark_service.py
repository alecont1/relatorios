"""
Unit tests for the WatermarkService.

These tests exercise the Pillow-based watermark overlay without any
HTTP layer or database access.
"""
from io import BytesIO

import pytest
from PIL import Image

from app.services.watermark_service import WatermarkService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_image(width: int = 400, height: int = 400, color: str = "red") -> bytes:
    """Create a minimal RGB JPEG image and return raw bytes."""
    img = Image.new("RGB", (width, height), color=color)
    buf = BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf.read()


def _make_logo(width: int = 80, height: int = 80) -> bytes:
    """Create a small RGBA logo image as PNG bytes."""
    img = Image.new("RGBA", (width, height), color=(0, 0, 255, 200))
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


def _full_context(**overrides) -> dict:
    """Build a full watermark context dict with sensible defaults."""
    defaults = {
        "company_name": "SmartHand Test Co.",
        "technician_name": "Joao Silva",
        "report_number": "RPT-001",
        "datetime": "2025-06-15 14:30",
        "gps": "-23.5505, -46.6333",
        "address": "Av Paulista 1000, Sao Paulo",
    }
    defaults.update(overrides)
    return defaults


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

svc = WatermarkService()


def test_apply_watermark_default_config():
    """With None config, default config is applied; output is valid JPEG bytes."""
    image_bytes = _make_image()
    result = svc.apply_watermark(image_bytes, config=None, context=_full_context())
    assert isinstance(result, bytes)
    assert len(result) > 0
    # Verify we can open the result as an image
    img = Image.open(BytesIO(result))
    assert img.format == "JPEG"


def test_apply_watermark_custom_config():
    """Custom config with only company_name enabled produces valid output."""
    cfg = {
        "logo": False,
        "gps": False,
        "datetime": False,
        "company_name": True,
        "report_number": False,
        "technician_name": False,
    }
    result = svc.apply_watermark(
        _make_image(), config=cfg, context=_full_context()
    )
    assert isinstance(result, bytes)
    img = Image.open(BytesIO(result))
    assert img.format == "JPEG"


def test_apply_watermark_no_config():
    """Passing config=None uses defaults and does not raise."""
    result = svc.apply_watermark(
        _make_image(), config=None, context=_full_context()
    )
    assert len(result) > 100  # non-trivial output


def test_apply_watermark_empty_context():
    """Minimal (empty) context does not crash the service."""
    result = svc.apply_watermark(
        _make_image(), config=None, context={}
    )
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_apply_watermark_with_gps():
    """When GPS is enabled and provided, the watermark is applied."""
    cfg = {"gps": True, "datetime": False, "company_name": False,
           "technician_name": False, "report_number": False, "logo": False}
    ctx = {"gps": "-23.55, -46.63"}
    result = svc.apply_watermark(_make_image(), config=cfg, context=ctx)
    assert isinstance(result, bytes)
    # We can't easily assert the text is visible without OCR,
    # but we verify no exceptions and valid output.
    img = Image.open(BytesIO(result))
    assert img.mode == "RGB"


def test_apply_watermark_output_is_jpeg():
    """Output image is always JPEG regardless of input format."""
    # Create a PNG input
    png_buf = BytesIO()
    Image.new("RGB", (200, 200), "green").save(png_buf, format="PNG")
    png_bytes = png_buf.getvalue()

    result = svc.apply_watermark(png_bytes, config=None, context=_full_context())
    img = Image.open(BytesIO(result))
    assert img.format == "JPEG"


def test_apply_watermark_preserves_dimensions():
    """Output image preserves the same width and height as the input."""
    w, h = 640, 480
    result = svc.apply_watermark(
        _make_image(w, h), config=None, context=_full_context()
    )
    img = Image.open(BytesIO(result))
    assert img.size == (w, h)


def test_apply_watermark_with_logo():
    """Logo bytes in context are composited without errors."""
    logo = _make_logo()
    ctx = _full_context(logo_bytes=logo)
    cfg = {"logo": True, "company_name": True, "technician_name": False,
           "gps": False, "datetime": False, "report_number": False}
    result = svc.apply_watermark(_make_image(600, 400), config=cfg, context=ctx)
    assert isinstance(result, bytes)
    img = Image.open(BytesIO(result))
    assert img.size == (600, 400)
