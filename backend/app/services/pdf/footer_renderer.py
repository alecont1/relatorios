"""Footer renderer."""

from .base_renderer import BaseRenderer


class FooterRenderer(BaseRenderer):
    """Renders page footers."""

    def render(self):
        """Called by ReportPDF.footer() on each page."""
        pdf = self.pdf

        pdf.set_y(-22)

        # Divider line
        secondary = self.get_secondary_color()
        line_color = secondary or self.get_primary_color()
        pdf.set_draw_color(*line_color)
        pdf.set_line_width(0.3)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(1)

        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(128, 128, 128)

        # Line 1: Name | Address
        line1_parts = [self.tenant.get("name", "")]
        if self.tenant.get("address"):
            line1_parts.append(self.tenant["address"])
        pdf.cell(0, 4, " | ".join(filter(None, line1_parts)), align="C")
        pdf.ln(3.5)

        # Line 2: Phone | Email | Website
        line2_parts = []
        if self.tenant.get("phone"):
            line2_parts.append(self.tenant["phone"])
        if self.tenant.get("email"):
            line2_parts.append(self.tenant["email"])
        if self.tenant.get("website"):
            line2_parts.append(self.tenant["website"])
        if line2_parts:
            pdf.cell(0, 4, " | ".join(line2_parts), align="C")
            pdf.ln(3.5)

        # Line 3: Page number
        pdf.cell(0, 4, f"Pagina {pdf.page_no()}/{{nb}}", align="C")
