"""Info table renderer."""

from .base_renderer import BaseRenderer


class InfoTableRenderer(BaseRenderer):
    """Renders the info fields table."""

    def render(self, info_values):
        """Add info fields table with alternating row colors."""
        pdf = self.pdf
        font_size = self.config.fonts.base_size

        pdf.set_font("Helvetica", "", font_size)

        for i, iv in enumerate(info_values):
            if i % 2 == 0:
                pdf.set_fill_color(249, 250, 251)
            else:
                pdf.set_fill_color(243, 244, 246)

            pdf.set_text_color(55, 65, 81)
            pdf.set_font("Helvetica", "B", font_size)
            pdf.cell(60, 7, iv.field_label, border=1, fill=True)

            pdf.set_font("Helvetica", "", font_size)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 7, iv.value or "-", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

        pdf.ln(3)
