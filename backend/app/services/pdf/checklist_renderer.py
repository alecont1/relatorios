"""Checklist table renderer."""

from .base_renderer import BaseRenderer


class ChecklistRenderer(BaseRenderer):
    """Renders checklist tables for each section."""

    def render(self, fields: list):
        """Add checklist table with proper text wrapping."""
        pdf = self.pdf
        primary = self.get_primary_color()
        accent = self.get_accent_color()
        font_size = self.config.fonts.base_size

        # Header
        pdf.set_fill_color(*primary)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", font_size)
        pdf.cell(95, 7, "Item de Verificacao", border=1, fill=True)
        pdf.cell(30, 7, "Resultado", border=1, fill=True, align="C")
        pdf.cell(0, 7, "Observacoes", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

        # Rows
        pdf.set_font("Helvetica", "", font_size)
        for i, field in enumerate(fields):
            if i % 2 == 0:
                pdf.set_fill_color(249, 250, 251)
            else:
                pdf.set_fill_color(255, 255, 255)

            response = field.get("response", {})
            response_value = response.get("response_value", "-") or "-"
            comment = response.get("comment", "") or ""

            label = field.get("label", "")
            label_lines = max(1, (len(label) // 50) + 1) if len(label) > 55 else 1
            comment_lines = max(1, (len(comment) // 35) + 1) if len(comment) > 40 else 1
            max_lines = max(label_lines, comment_lines)
            row_height = max(7, max_lines * 5)

            y_before = pdf.get_y()
            x_before = pdf.get_x()

            if y_before + row_height > pdf.h - 25:
                pdf.add_page()
                y_before = pdf.get_y()
                x_before = pdf.get_x()

            # Label
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "", font_size)
            if len(label) > 55:
                pdf.multi_cell(95, 5, label, border=1, fill=True, new_x="RIGHT", new_y="TOP", max_line_height=5)
                actual_height = max(pdf.get_y() - y_before, row_height)
                pdf.set_xy(x_before + 95, y_before)
            else:
                pdf.cell(95, row_height, label, border=1, fill=True)
                actual_height = row_height

            # Response color
            if accent and response_value in ("Sim", "OK", "Conforme"):
                pdf.set_text_color(*accent)
            elif response_value in ("Sim", "OK", "Conforme"):
                pdf.set_text_color(5, 150, 105)
            elif response_value in ("Nao", "NOK", "Nao Conforme"):
                pdf.set_text_color(220, 38, 38)
            elif response_value == "N/A":
                pdf.set_text_color(107, 114, 128)
            else:
                pdf.set_text_color(0, 0, 0)

            pdf.set_font("Helvetica", "B", font_size)
            pdf.cell(30, actual_height, response_value, border=1, fill=True, align="C")

            # Comment - full text, no truncation
            pdf.set_font("Helvetica", "I", font_size - 1)
            pdf.set_text_color(100, 100, 100)
            comment_width = 190 - 95 - 30
            if len(comment) > 40:
                x_comment = pdf.get_x()
                pdf.multi_cell(comment_width, 4, comment, border=1, fill=True,
                              new_x="LMARGIN", new_y="TOP", max_line_height=4)
                comment_height = pdf.get_y() - y_before
                final_height = max(actual_height, comment_height)
                pdf.set_xy(x_before, y_before + final_height)
            else:
                pdf.cell(0, actual_height, comment, border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

            pdf.set_font("Helvetica", "", font_size)
