"""
PDF generation service using fpdf2.
"""
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, Optional
import urllib.request

from fpdf import FPDF

from app.models.report import Report
from app.models.tenant import Tenant


class ReportPDF(FPDF):
    """Custom PDF class for reports."""

    def __init__(self, tenant: dict, template: dict):
        super().__init__()
        self.tenant = tenant
        self.template = template
        self.primary_color = self._hex_to_rgb(tenant.get("primary_color", "#2563eb"))

    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def header(self):
        """Page header with logos and title."""
        # Left logo
        if self.tenant.get("logo_primary_url"):
            try:
                self._add_image_from_url(self.tenant["logo_primary_url"], 10, 8, 40)
            except:
                pass

        # Title in center
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*self.primary_color)
        self.set_xy(60, 10)
        self.cell(90, 8, self.template.get("name", "Relatório"), align="C")

        # Right logo
        if self.tenant.get("logo_secondary_url"):
            try:
                self._add_image_from_url(self.tenant["logo_secondary_url"], 160, 8, 40)
            except:
                pass

        # Subtitle
        self.set_font("Helvetica", "", 10)
        self.set_text_color(100, 100, 100)
        self.set_xy(60, 18)
        self.cell(90, 6, f"Código: {self.template.get('code', '')} | Versão: {self.template.get('version', '1')}", align="C")

        # Line
        self.set_draw_color(*self.primary_color)
        self.set_line_width(0.5)
        self.line(10, 28, 200, 28)

        self.ln(25)

    def footer(self):
        """Page footer."""
        self.set_y(-15)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(128, 128, 128)

        # Tenant info
        footer_text = self.tenant.get("name", "")
        if self.tenant.get("phone"):
            footer_text += f" | {self.tenant['phone']}"
        if self.tenant.get("email"):
            footer_text += f" | {self.tenant['email']}"

        self.cell(0, 5, footer_text, align="C")
        self.ln(4)
        self.cell(0, 5, f"Página {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title: str):
        """Add a section title."""
        self.set_fill_color(240, 244, 255)
        self.set_draw_color(*self.primary_color)
        self.set_text_color(*self.primary_color)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, f"  {title}", border="L", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def _add_image_from_url(self, url: str, x: float, y: float, w: float):
        """Add image from URL."""
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                img_data = response.read()
                img_io = BytesIO(img_data)
                self.image(img_io, x, y, w)
        except:
            pass


class PDFService:
    """Service for generating PDF reports."""

    def generate_report_pdf(
        self,
        report: Report,
        tenant: Tenant,
    ) -> bytes:
        """
        Generate a PDF for a report.

        Args:
            report: The report with all related data loaded
            tenant: The tenant for branding

        Returns:
            PDF file as bytes
        """
        snapshot = report.template_snapshot

        # Build context
        tenant_info = {
            "name": tenant.name,
            "logo_primary_url": tenant.logo_primary_url,
            "logo_secondary_url": tenant.logo_secondary_url,
            "primary_color": tenant.primary_color or "#2563eb",
            "phone": tenant.phone,
            "email": tenant.email,
        }

        template_info = {
            "name": snapshot.get("name", "Relatório"),
            "code": snapshot.get("code", ""),
            "version": snapshot.get("version", "1"),
        }

        # Create PDF
        pdf = ReportPDF(tenant_info, template_info)
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=20)

        # Report title and date
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 8, report.title, new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, f"Data: {report.created_at.strftime('%d/%m/%Y')} | Status: {report.status}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        # Info fields section
        if report.info_values:
            pdf.section_title("Informações do Projeto")
            self._add_info_table(pdf, report.info_values)

        # Checklist sections
        sections = self._group_responses_by_section(report, snapshot)
        for section in sections:
            pdf.section_title(section["name"])
            self._add_checklist_table(pdf, section["fields"])

            # Photos for this section
            section_photos = self._get_section_photos(section)
            if section_photos:
                self._add_photos(pdf, section_photos)

            pdf.ln(3)

        # Generate PDF bytes
        return bytes(pdf.output())

    def _add_info_table(self, pdf: ReportPDF, info_values):
        """Add info fields table."""
        pdf.set_font("Helvetica", "", 9)

        for iv in info_values:
            # Label
            pdf.set_fill_color(249, 250, 251)
            pdf.set_text_color(55, 65, 81)
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(60, 7, iv.field_label, border=1, fill=True)

            # Value
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 7, iv.value or "-", border=1, new_x="LMARGIN", new_y="NEXT")

        pdf.ln(3)

    def _add_checklist_table(self, pdf: ReportPDF, fields: list):
        """Add checklist table."""
        # Header
        pdf.set_fill_color(*pdf.primary_color)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(95, 7, "Item de Verificação", border=1, fill=True)
        pdf.cell(30, 7, "Resultado", border=1, fill=True, align="C")
        pdf.cell(0, 7, "Observações", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

        # Rows
        pdf.set_font("Helvetica", "", 9)
        for i, field in enumerate(fields):
            # Alternate row colors
            if i % 2 == 0:
                pdf.set_fill_color(249, 250, 251)
            else:
                pdf.set_fill_color(255, 255, 255)

            response = field.get("response", {})
            response_value = response.get("response_value", "-") or "-"
            comment = response.get("comment", "") or ""

            # Label
            pdf.set_text_color(0, 0, 0)
            label = field.get("label", "")
            if len(label) > 50:
                label = label[:47] + "..."
            pdf.cell(95, 7, label, border=1, fill=True)

            # Response with color
            if response_value in ("Sim", "OK", "Conforme"):
                pdf.set_text_color(5, 150, 105)
            elif response_value in ("Nao", "NOK", "Não Conforme"):
                pdf.set_text_color(220, 38, 38)
            elif response_value == "N/A":
                pdf.set_text_color(107, 114, 128)
            else:
                pdf.set_text_color(0, 0, 0)

            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(30, 7, response_value, border=1, fill=True, align="C")

            # Comment
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(100, 100, 100)
            if len(comment) > 35:
                comment = comment[:32] + "..."
            pdf.cell(0, 7, comment, border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

            pdf.set_font("Helvetica", "", 9)

    def _add_photos(self, pdf: ReportPDF, photos: list):
        """Add photos grid."""
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 6, "Registro Fotográfico:", new_x="LMARGIN", new_y="NEXT")

        x_start = 10
        y_start = pdf.get_y()
        photo_width = 60
        photo_height = 45
        photos_per_row = 3
        margin = 3

        for i, photo_data in enumerate(photos[:9]):  # Limit to 9 photos
            col = i % photos_per_row
            row = i // photos_per_row

            x = x_start + col * (photo_width + margin)
            y = y_start + row * (photo_height + 12)

            # Check if we need a new page
            if y + photo_height + 12 > pdf.h - 25:
                pdf.add_page()
                y_start = pdf.get_y()
                y = y_start + row * (photo_height + 12)

            # Add photo
            photo_url = photo_data.get("url", "")
            if photo_url:
                try:
                    pdf._add_image_from_url(photo_url, x, y, photo_width)
                except:
                    pass

            # Caption
            pdf.set_xy(x, y + photo_height)
            pdf.set_font("Helvetica", "", 7)
            pdf.set_text_color(100, 100, 100)

            caption = photo_data.get("field", "")[:20]
            if photo_data.get("captured_at"):
                captured = photo_data["captured_at"][:16].replace("T", " ")
                caption += f"\n{captured}"

            pdf.multi_cell(photo_width, 3, caption, align="C")

        # Move cursor after photos
        last_row = (len(photos[:9]) - 1) // photos_per_row
        pdf.set_y(y_start + (last_row + 1) * (photo_height + 15))

    def _group_responses_by_section(self, report: Report, snapshot: dict) -> list:
        """Group checklist responses by section."""
        responses_by_field = {
            (r.section_name, r.field_label): r
            for r in report.checklist_responses
        }

        sections = []
        for section_data in snapshot.get("sections", []):
            fields = []
            for field_data in section_data.get("fields", []):
                response = responses_by_field.get(
                    (section_data["name"], field_data["label"])
                )
                fields.append({
                    "label": field_data.get("label"),
                    "response": {
                        "response_value": response.response_value if response else None,
                        "comment": response.comment if response else None,
                        "photos": response.photos if response else [],
                    } if response else {},
                })

            sections.append({
                "name": section_data.get("name"),
                "fields": fields,
            })

        return sections

    def _get_section_photos(self, section: dict) -> list:
        """Get all photos from a section."""
        photos = []
        for field in section.get("fields", []):
            response = field.get("response", {})
            for photo in response.get("photos", []) or []:
                photos.append({
                    **photo,
                    "field": field.get("label", ""),
                })
        return photos


# Singleton instance
pdf_service = PDFService()
