"""Cover page renderer."""

from .base_renderer import BaseRenderer
from .layout_config import LayoutConfig


class CoverRenderer(BaseRenderer):
    """Renders the cover page of a PDF report."""

    def render(self, report, template_info: dict, snapshot: dict):
        """Add a cover page to the PDF."""
        if not self.config.cover_page.enabled:
            return

        pdf = self.pdf
        primary = self.get_primary_color()

        pdf._is_cover_page = True
        pdf.add_page()
        pdf.set_auto_page_break(auto=False)

        # 1. Top color bar
        pdf.set_fill_color(*primary)
        pdf.rect(0, 0, 210, 6, "F")

        # 2. Logo centered
        y_pos = 25
        if self.tenant.get("logo_primary_url"):
            try:
                self.add_image_from_url(self.tenant["logo_primary_url"], 75, y_pos, 60)
                y_pos += 30
            except Exception:
                y_pos += 5

        # 3. Company name
        pdf.set_xy(10, y_pos)
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(50, 50, 50)
        company_name = (self.tenant.get("name") or "Empresa").upper()
        pdf.cell(190, 10, company_name, align="C", new_x="LMARGIN", new_y="NEXT")
        y_pos = pdf.get_y() + 5

        # 4. Divider line
        pdf.set_draw_color(200, 200, 200)
        pdf.set_line_width(0.3)
        pdf.line(40, y_pos, 170, y_pos)
        y_pos += 10

        # 5. Report title
        pdf.set_xy(20, y_pos)
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_text_color(*primary)
        title = report.title or template_info.get("name", "Relatorio")
        pdf.multi_cell(170, 9, title, align="C")
        y_pos = pdf.get_y() + 3

        # 6. Code + version
        pdf.set_xy(10, y_pos)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(150, 150, 150)
        code_text = f"{template_info.get('code', '')} - v{template_info.get('version', '1')}"
        pdf.cell(190, 6, code_text, align="C", new_x="LMARGIN", new_y="NEXT")
        y_pos = pdf.get_y() + 10

        # 7. Info fields with dotted lines
        info_fields = snapshot.get("info_fields", [])
        if info_fields:
            pdf.set_xy(30, y_pos)
            for field in info_fields[:8]:
                if pdf.get_y() > 220:
                    break
                label = field.get("label", "")
                pdf.set_font("Helvetica", "", 10)
                pdf.set_text_color(100, 100, 100)
                label_width = pdf.get_string_width(label + ": ")
                pdf.cell(label_width + 2, 8, f"{label}:")
                line_start = pdf.get_x() + 2
                line_y = pdf.get_y() + 7
                pdf.set_draw_color(180, 180, 180)
                pdf.set_line_width(0.2)
                x = line_start
                while x < 175:
                    pdf.line(x, line_y, x + 1.5, line_y)
                    x += 3
                pdf.set_xy(30, pdf.get_y() + 10)
            y_pos = pdf.get_y() + 5

        # 8. Signature fields
        sig_fields = snapshot.get("signature_fields", [])
        if sig_fields:
            sig_y = max(y_pos, 240)
            if sig_y > 265:
                sig_y = 240
            sigs_to_show = sig_fields[:3]
            sig_width = 50
            total_width = len(sigs_to_show) * sig_width + (len(sigs_to_show) - 1) * 10
            start_x = (210 - total_width) / 2
            for i, sig in enumerate(sigs_to_show):
                x = start_x + i * (sig_width + 10)
                pdf.set_draw_color(100, 100, 100)
                pdf.set_line_width(0.3)
                pdf.line(x, sig_y, x + sig_width, sig_y)
                pdf.set_xy(x, sig_y + 1)
                pdf.set_font("Helvetica", "", 8)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(sig_width, 4, sig.get("role_name", ""), align="C")

        # 9. Bottom color bar
        pdf.set_fill_color(*primary)
        pdf.rect(0, 293, 210, 4, "F")

        pdf._is_cover_page = False
