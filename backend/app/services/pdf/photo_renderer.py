"""Photo grid renderer."""

from .base_renderer import BaseRenderer


class PhotoRenderer(BaseRenderer):
    """Renders photo grids."""

    def render(self, photos: list):
        """Add photos in configurable grid layout."""
        if not photos:
            return

        pdf = self.pdf
        pc = self.config.photos

        pdf.ln(2)
        pdf.set_font("Helvetica", "B", self.config.fonts.base_size)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 6, "Registro Fotografico:", new_x="LMARGIN", new_y="NEXT")

        x_start = self.config.margins.left
        y_start = pdf.get_y()
        photo_width = pc.width_mm
        photo_height = pc.height_mm
        photos_per_row = pc.columns
        max_photos = pc.max_per_section
        margin = max(5, (190 - photos_per_row * photo_width) // max(1, photos_per_row - 1)) if photos_per_row > 1 else 0

        for i, photo_data in enumerate(photos[:max_photos]):
            col = i % photos_per_row
            row = i // photos_per_row

            x = x_start + col * (photo_width + margin)
            y = y_start + row * (photo_height + 15)

            if y + photo_height + 15 > pdf.h - 25:
                pdf.add_page()
                y_start = pdf.get_y()
                y = y_start

            photo_url = photo_data.get("url", "")
            if photo_url:
                try:
                    resolved_url = self.resolve_image_url(photo_url)
                    self.add_image_from_url(resolved_url, x, y, photo_width)
                except Exception:
                    pass

            # Caption - no truncation
            pdf.set_xy(x, y + photo_height)
            pdf.set_font("Helvetica", "", 7)
            pdf.set_text_color(100, 100, 100)
            caption = photo_data.get("field", "")
            if photo_data.get("captured_at"):
                captured = photo_data["captured_at"][:16].replace("T", " ")
                caption += f"\n{captured}"
            pdf.multi_cell(photo_width, 3, caption, align="C")

        if photos[:max_photos]:
            last_row = (len(photos[:max_photos]) - 1) // photos_per_row
            pdf.set_y(y_start + (last_row + 1) * (photo_height + 18))
