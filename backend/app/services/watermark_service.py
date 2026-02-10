"""
Watermark service using Pillow for server-side photo watermarking.
"""
from io import BytesIO
from typing import Any, Optional

from PIL import Image, ImageDraw, ImageFont


class WatermarkService:
    """Apply configurable watermarks to images."""

    # Default config when tenant has no watermark_config set
    DEFAULT_CONFIG = {
        "logo": True,
        "gps": True,
        "datetime": True,
        "company_name": True,
        "report_number": False,
        "technician_name": True,
    }

    def apply_watermark(
        self,
        image_bytes: bytes,
        config: Optional[dict],
        context: dict,
    ) -> bytes:
        """
        Apply watermark to an image.

        Args:
            image_bytes: Raw image bytes
            config: Watermark configuration from tenant (or None for defaults)
            context: Contextual data for watermark fields:
                - company_name: str
                - technician_name: str
                - report_number: str
                - datetime: str (formatted datetime)
                - gps: str (lat, lon)
                - address: str
                - logo_bytes: bytes (optional logo image)

        Returns:
            Watermarked image as JPEG bytes
        """
        cfg = {**self.DEFAULT_CONFIG, **(config or {})}

        # Open image
        img = Image.open(BytesIO(image_bytes))
        if img.mode != "RGB":
            img = img.convert("RGB")

        width, height = img.size

        # Calculate strip dimensions
        strip_height = max(80, int(height * 0.12))

        # Create semi-transparent overlay
        overlay = Image.new("RGBA", (width, strip_height), (0, 0, 0, 160))
        draw = ImageDraw.Draw(overlay)

        # Try to load a font, fall back to default
        try:
            font_large = ImageFont.truetype("arial.ttf", max(14, strip_height // 5))
            font_small = ImageFont.truetype("arial.ttf", max(11, strip_height // 7))
            font_bold = ImageFont.truetype("arialbd.ttf", max(14, strip_height // 5))
        except (OSError, IOError):
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
            font_bold = font_large

        # Build text lines
        left_lines = []
        right_lines = []

        if cfg.get("company_name") and context.get("company_name"):
            left_lines.append(("bold", context["company_name"], (255, 255, 255)))

        if cfg.get("technician_name") and context.get("technician_name"):
            left_lines.append(("normal", context["technician_name"], (255, 220, 50)))

        if cfg.get("report_number") and context.get("report_number"):
            left_lines.append(("normal", f"Ref: {context['report_number']}", (200, 200, 200)))

        if cfg.get("datetime") and context.get("datetime"):
            right_lines.append(("bold", context["datetime"], (255, 255, 255)))

        if cfg.get("gps") and context.get("gps"):
            gps_text = context["gps"]
            if context.get("address"):
                gps_text = context["address"]
            right_lines.append(("normal", gps_text, (200, 200, 200)))

        # Draw left-aligned text
        padding = 10
        logo_offset = padding

        # Draw logo if configured
        if cfg.get("logo") and context.get("logo_bytes"):
            try:
                logo = Image.open(BytesIO(context["logo_bytes"]))
                logo_h = strip_height - 20
                logo_w = int(logo.width * (logo_h / logo.height))
                logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
                if logo.mode == "RGBA":
                    overlay.paste(logo, (padding, 10), logo)
                else:
                    overlay.paste(logo, (padding, 10))
                logo_offset = padding + logo_w + 10
            except Exception:
                pass

        y_offset = 8
        for style, text, color in left_lines:
            font = font_bold if style == "bold" else font_small
            draw.text((logo_offset, y_offset), text, fill=color, font=font)
            y_offset += font_large.size + 4 if style == "bold" else font_small.size + 2

        # Draw right-aligned text
        y_offset = 8
        for style, text, color in right_lines:
            font = font_bold if style == "bold" else font_small
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            draw.text((width - text_width - padding, y_offset), text, fill=color, font=font)
            y_offset += font_large.size + 4 if style == "bold" else font_small.size + 2

        # Composite overlay onto image
        img_rgba = img.convert("RGBA")
        # Create a full-size overlay
        full_overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        full_overlay.paste(overlay, (0, height - strip_height))

        result = Image.alpha_composite(img_rgba, full_overlay)
        result = result.convert("RGB")

        # Output as JPEG
        output = BytesIO()
        result.save(output, format="JPEG", quality=92)
        output.seek(0)
        return output.read()


# Singleton instance
watermark_service = WatermarkService()
