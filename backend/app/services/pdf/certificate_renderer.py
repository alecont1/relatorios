"""Certificate table renderer."""

from .base_renderer import BaseRenderer


class CertificateRenderer(BaseRenderer):
    """Renders the calibration certificates table."""

    def render(self, certificates: list):
        """Add certificates table with text wrapping."""
        if not certificates:
            return
        if not self.config.certificates.show_table:
            return

        pdf = self.pdf
        primary = self.get_primary_color()
        font_size = self.config.fonts.base_size - 1

        # Header
        pdf.set_fill_color(*primary)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", font_size)
        pdf.cell(50, 7, "Equipamento", border=1, fill=True)
        pdf.cell(35, 7, "Certificado", border=1, fill=True)
        pdf.cell(45, 7, "Laboratorio", border=1, fill=True)
        pdf.cell(25, 7, "Calibracao", border=1, fill=True, align="C")
        pdf.cell(25, 7, "Validade", border=1, fill=True, align="C")
        pdf.cell(0, 7, "Status", border=1, fill=True, align="C", new_x="LMARGIN", new_y="NEXT")

        # Rows
        for i, cert in enumerate(certificates):
            if i % 2 == 0:
                pdf.set_fill_color(249, 250, 251)
            else:
                pdf.set_fill_color(255, 255, 255)

            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "", font_size)

            equipment = cert.equipment_name or ""
            cert_num = cert.certificate_number or ""
            lab = cert.laboratory or "-"
            cal_date = cert.calibration_date.strftime("%d/%m/%Y")
            exp_date = cert.expiry_date.strftime("%d/%m/%Y")

            row_h = 6
            for text, width in [(equipment, 50), (cert_num, 35), (lab, 45)]:
                text_w = pdf.get_string_width(text)
                if text_w > width - 2:
                    lines = (len(text) // int(width / 2)) + 1
                    row_h = max(row_h, lines * 4)

            self.safe_cell(50, row_h, equipment, border=1, fill=True)
            self.safe_cell(35, row_h, cert_num, border=1, fill=True)
            self.safe_cell(45, row_h, lab, border=1, fill=True)
            pdf.cell(25, row_h, cal_date, border=1, fill=True, align="C")
            pdf.cell(25, row_h, exp_date, border=1, fill=True, align="C")

            status = cert.status
            if status == "valid":
                pdf.set_text_color(5, 150, 105)
                status_text = "Valido"
            elif status == "expiring":
                pdf.set_text_color(217, 119, 6)
                status_text = "Vencendo"
            else:
                pdf.set_text_color(220, 38, 38)
                status_text = "Vencido"

            pdf.set_font("Helvetica", "B", font_size)
            pdf.cell(0, row_h, status_text, border=1, fill=True, align="C", new_x="LMARGIN", new_y="NEXT")

        pdf.ln(3)
