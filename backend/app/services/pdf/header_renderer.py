"""Header renderer."""

from .base_renderer import BaseRenderer


class HeaderRenderer(BaseRenderer):
    """Renders page headers."""

    def render(self, template_info: dict):
        """Called by ReportPDF.header() on each new page."""
        pdf = self.pdf
        primary = self.get_primary_color()
        font_size = self.config.fonts.header_size

        # Left logo
        if self.tenant.get("logo_primary_url"):
            try:
                self.add_image_from_url(self.tenant["logo_primary_url"], 10, 8, 40)
            except Exception:
                pass

        # Title in center
        pdf.set_font("Helvetica", "B", font_size)
        pdf.set_text_color(*primary)
        pdf.set_xy(60, 10)
        pdf.cell(90, 8, template_info.get("name", "Relatorio"), align="C")

        # Right logo
        if self.tenant.get("logo_secondary_url"):
            try:
                self.add_image_from_url(self.tenant["logo_secondary_url"], 160, 8, 40)
            except Exception:
                pass

        # Subtitle
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.set_xy(60, 20)
        subtitle = f"Codigo: {template_info.get('code', '')} | Versao: {template_info.get('version', '1')}"
        revision_number = getattr(pdf, 'revision_number', 0) or 0
        if revision_number > 0:
            subtitle += f" | Rev. {revision_number}"
        pdf.cell(90, 6, subtitle, align="C")

        # Line
        pdf.set_draw_color(*primary)
        pdf.set_line_width(0.5)
        pdf.line(10, 30, 200, 30)
        pdf.ln(30)
