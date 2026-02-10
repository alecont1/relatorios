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
from app.core.config import settings


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
            except Exception:
                pass

        # Title in center
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*self.primary_color)
        self.set_xy(60, 10)
        self.cell(90, 8, self.template.get("name", "Relatorio"), align="C")

        # Right logo
        if self.tenant.get("logo_secondary_url"):
            try:
                self._add_image_from_url(self.tenant["logo_secondary_url"], 160, 8, 40)
            except Exception:
                pass

        # Subtitle
        self.set_font("Helvetica", "", 10)
        self.set_text_color(100, 100, 100)
        self.set_xy(60, 20)
        self.cell(90, 6, f"Codigo: {self.template.get('code', '')} | Versao: {self.template.get('version', '1')}", align="C")

        # Line - increased spacing from 28 to 35pt
        self.set_draw_color(*self.primary_color)
        self.set_line_width(0.5)
        self.line(10, 30, 200, 30)

        # Padding below line
        self.ln(30)

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
        self.cell(0, 5, f"Pagina {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title: str):
        """Add a section title."""
        self.set_fill_color(240, 244, 255)
        self.set_draw_color(*self.primary_color)
        self.set_text_color(*self.primary_color)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, f"  {title}", border="L", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def _add_image_from_url(self, url: str, x: float, y: float, w: float):
        """Add image from URL or local path."""
        try:
            if url.startswith(("http://", "https://")):
                with urllib.request.urlopen(url, timeout=5) as response:
                    img_data = response.read()
                    img_io = BytesIO(img_data)
                    self.image(img_io, x, y, w)
            else:
                # Local file path
                local_path = Path(url)
                if local_path.exists():
                    self.image(str(local_path), x, y, w)
        except Exception:
            pass

    def _resolve_image_url(self, key_or_url: str) -> str:
        """Resolve an R2 object key or URL to a fetchable URL."""
        if not key_or_url:
            return ""
        if key_or_url.startswith(("http://", "https://")):
            return key_or_url
        if key_or_url.startswith("/uploads/"):
            return key_or_url[1:]  # Remove leading slash for local path
        # Assume it's an R2 object key
        if settings.r2_public_url:
            return f"{settings.r2_public_url}/{key_or_url}"
        # Fallback to local uploads
        return f"uploads/{key_or_url}"


class PDFService:
    """Service for generating PDF reports."""

    def generate_report_pdf(
        self,
        report: Report,
        tenant: Tenant,
        certificates: list | None = None,
    ) -> bytes:
        """
        Generate a PDF for a report.

        Args:
            report: The report with all related data loaded
            tenant: The tenant for branding
            certificates: Optional list of CalibrationCertificate objects

        Returns:
            PDF file as bytes
        """
        snapshot = report.template_snapshot

        # Build logo URLs properly
        logo_primary_url = self._resolve_logo_url(tenant.logo_primary_key)
        logo_secondary_url = self._resolve_logo_url(tenant.logo_secondary_key)

        # Build context
        tenant_info = {
            "name": tenant.name,
            "logo_primary_url": logo_primary_url,
            "logo_secondary_url": logo_secondary_url,
            "primary_color": tenant.brand_color_primary or "#2563eb",
            "phone": tenant.contact_phone,
            "email": tenant.contact_email,
        }

        template_info = {
            "name": snapshot.get("name", "Relatorio"),
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
            pdf.section_title("Informacoes do Projeto")
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

        # Certificates section (before signatures)
        if certificates:
            pdf.section_title("Certificados de Calibracao")
            self._add_certificates_table(pdf, certificates)

        # Signatures section
        if report.signatures:
            pdf.section_title("Assinaturas")
            self._add_signatures(pdf, report.signatures)

        # Generate PDF bytes
        return bytes(pdf.output())

    def _resolve_logo_url(self, key: str | None) -> str | None:
        """Resolve logo key to a full URL."""
        if not key:
            return None
        if key.startswith(("http://", "https://")):
            return key
        if settings.r2_public_url:
            return f"{settings.r2_public_url}/{key}"
        return f"uploads/{key}"

    def _add_info_table(self, pdf: ReportPDF, info_values):
        """Add info fields table with alternating row colors."""
        pdf.set_font("Helvetica", "", 9)

        for i, iv in enumerate(info_values):
            # Alternating row colors
            if i % 2 == 0:
                pdf.set_fill_color(249, 250, 251)
            else:
                pdf.set_fill_color(243, 244, 246)

            # Label
            pdf.set_text_color(55, 65, 81)
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(60, 7, iv.field_label, border=1, fill=True)

            # Value
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 7, iv.value or "-", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

        pdf.ln(3)

    def _add_checklist_table(self, pdf: ReportPDF, fields: list):
        """Add checklist table with multi_cell for long labels."""
        # Header
        pdf.set_fill_color(*pdf.primary_color)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(95, 7, "Item de Verificacao", border=1, fill=True)
        pdf.cell(30, 7, "Resultado", border=1, fill=True, align="C")
        pdf.cell(0, 7, "Observacoes", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

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

            # Calculate row height based on label length
            label = field.get("label", "")
            # Use multi_cell approach for long labels
            if len(label) > 55:
                # Estimate line count
                line_count = (len(label) // 50) + 1
                row_height = max(7, line_count * 5)
            else:
                row_height = 7

            y_before = pdf.get_y()
            x_before = pdf.get_x()

            # Label with multi_cell for long text
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "", 9)
            if len(label) > 55:
                pdf.multi_cell(95, 5, label, border=1, fill=True, new_x="RIGHT", new_y="TOP", max_line_height=5)
                actual_height = pdf.get_y() - y_before
                pdf.set_xy(x_before + 95, y_before)
            else:
                pdf.cell(95, row_height, label, border=1, fill=True)
                actual_height = row_height

            # Response with color
            if response_value in ("Sim", "OK", "Conforme"):
                pdf.set_text_color(5, 150, 105)
            elif response_value in ("Nao", "NOK", "Nao Conforme"):
                pdf.set_text_color(220, 38, 38)
            elif response_value == "N/A":
                pdf.set_text_color(107, 114, 128)
            else:
                pdf.set_text_color(0, 0, 0)

            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(30, actual_height, response_value, border=1, fill=True, align="C")

            # Comment
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(100, 100, 100)
            if len(comment) > 40:
                comment = comment[:37] + "..."
            pdf.cell(0, actual_height, comment, border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

            pdf.set_font("Helvetica", "", 9)

    def _add_photos(self, pdf: ReportPDF, photos: list):
        """Add photos in 2x3 grid with larger photos."""
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 6, "Registro Fotografico:", new_x="LMARGIN", new_y="NEXT")

        x_start = 10
        y_start = pdf.get_y()
        photo_width = 80  # Increased from 60pt
        photo_height = 60  # Increased from 45pt
        photos_per_row = 2  # Changed to 2x3 layout
        margin = 15

        for i, photo_data in enumerate(photos[:6]):  # Limit to 6 photos (2x3)
            col = i % photos_per_row
            row = i // photos_per_row

            x = x_start + col * (photo_width + margin)
            y = y_start + row * (photo_height + 15)

            # Check if we need a new page
            if y + photo_height + 15 > pdf.h - 25:
                pdf.add_page()
                y_start = pdf.get_y()
                y = y_start

            # Add photo
            photo_url = photo_data.get("url", "")
            if photo_url:
                try:
                    resolved_url = pdf._resolve_image_url(photo_url)
                    pdf._add_image_from_url(resolved_url, x, y, photo_width)
                except Exception:
                    pass

            # Caption
            pdf.set_xy(x, y + photo_height)
            pdf.set_font("Helvetica", "", 7)
            pdf.set_text_color(100, 100, 100)

            caption = photo_data.get("field", "")[:30]
            if photo_data.get("captured_at"):
                captured = photo_data["captured_at"][:16].replace("T", " ")
                caption += f"\n{captured}"

            pdf.multi_cell(photo_width, 3, caption, align="C")

        # Move cursor after photos
        if photos[:6]:
            last_row = (len(photos[:6]) - 1) // photos_per_row
            pdf.set_y(y_start + (last_row + 1) * (photo_height + 18))

    def _add_certificates_table(self, pdf: ReportPDF, certificates: list):
        """Add certificates table section."""
        # Header
        pdf.set_fill_color(*pdf.primary_color)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 8)
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
            pdf.set_font("Helvetica", "", 8)

            equipment = cert.equipment_name[:25] if len(cert.equipment_name) > 25 else cert.equipment_name
            cert_num = cert.certificate_number[:18] if len(cert.certificate_number) > 18 else cert.certificate_number
            lab = (cert.laboratory or "-")[:22]
            cal_date = cert.calibration_date.strftime("%d/%m/%Y")
            exp_date = cert.expiry_date.strftime("%d/%m/%Y")

            pdf.cell(50, 6, equipment, border=1, fill=True)
            pdf.cell(35, 6, cert_num, border=1, fill=True)
            pdf.cell(45, 6, lab, border=1, fill=True)
            pdf.cell(25, 6, cal_date, border=1, fill=True, align="C")
            pdf.cell(25, 6, exp_date, border=1, fill=True, align="C")

            # Status with color
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

            pdf.set_font("Helvetica", "B", 8)
            pdf.cell(0, 6, status_text, border=1, fill=True, align="C", new_x="LMARGIN", new_y="NEXT")

        pdf.ln(3)

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

    def _add_signatures(self, pdf: ReportPDF, signatures) -> None:
        """Add signatures grid."""
        pdf.ln(2)

        x_start = 10
        y_start = pdf.get_y()
        sig_width = 60
        sig_height = 30
        sigs_per_row = 3
        margin = 5

        for i, sig in enumerate(signatures):
            col = i % sigs_per_row
            row = i // sigs_per_row

            x = x_start + col * (sig_width + margin)
            y = y_start + row * (sig_height + 25)

            # Check if we need a new page
            if y + sig_height + 25 > pdf.h - 25:
                pdf.add_page()
                y_start = pdf.get_y()
                y = y_start

            # Signature box
            pdf.set_draw_color(200, 200, 200)
            pdf.rect(x, y, sig_width, sig_height)

            # Try to add signature image
            if hasattr(sig, 'file_key') and sig.file_key:
                try:
                    # Resolve URL properly (local or R2)
                    sig_url = pdf._resolve_image_url(sig.file_key)
                    pdf._add_image_from_url(sig_url, x + 2, y + 2, sig_width - 4)
                except Exception:
                    pass

            # Role name
            pdf.set_xy(x, y + sig_height + 1)
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(sig_width, 4, sig.role_name[:20], align="C")

            # Signer name
            if sig.signer_name:
                pdf.set_xy(x, y + sig_height + 5)
                pdf.set_font("Helvetica", "", 7)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(sig_width, 4, sig.signer_name[:25], align="C")

            # Date
            pdf.set_xy(x, y + sig_height + 9)
            pdf.set_font("Helvetica", "", 7)
            pdf.set_text_color(100, 100, 100)
            signed_date = sig.signed_at.strftime("%d/%m/%Y %H:%M") if sig.signed_at else ""
            pdf.cell(sig_width, 4, signed_date, align="C")

        # Move cursor after signatures
        if signatures:
            last_row = (len(signatures) - 1) // sigs_per_row
            pdf.set_y(y_start + (last_row + 1) * (sig_height + 28))


# Singleton instance
pdf_service = PDFService()
