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

    # Unicode chars outside Latin-1 → ASCII replacements
    _CHAR_MAP = {
        "\u03a9": "Ohm", "\u2126": "Ohm",  # Ω
        "\u03bc": "u",    # μ (micro)
        "\u2103": "C", "\u2109": "F",  # ℃ ℉
        "\u2264": "<=", "\u2265": ">=",
    }

    def normalize_text(self, text):
        """Override to sanitize Unicode chars unsupported by Helvetica."""
        if text:
            for char, repl in self._CHAR_MAP.items():
                text = text.replace(char, repl)
            text = text.encode("latin-1", errors="replace").decode("latin-1")
        return super().normalize_text(text)

    def __init__(self, tenant: dict, template: dict):
        super().__init__()
        self.tenant = tenant
        self.template = template
        self.primary_color = self._hex_to_rgb(tenant.get("primary_color", "#2563eb"))
        self.secondary_color = self._hex_to_rgb(
            tenant.get("secondary_color", "")
        ) if tenant.get("secondary_color") else None
        self.accent_color = self._hex_to_rgb(
            tenant.get("accent_color", "")
        ) if tenant.get("accent_color") else None

    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip("#")
        if len(hex_color) != 6:
            return (37, 99, 235)  # fallback blue
        try:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except ValueError:
            return (37, 99, 235)

    def header(self):
        """Page header with logos and title."""
        # Skip header on cover page (page 1 when cover is enabled)
        if getattr(self, '_is_cover_page', False) and self.page_no() == 1:
            return

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

        # Line
        self.set_draw_color(*self.primary_color)
        self.set_line_width(0.5)
        self.line(10, 30, 200, 30)

        # Padding below line
        self.ln(30)

    def footer(self):
        """Page footer with tenant info, contact details, and page number."""
        # Skip footer on cover page
        if getattr(self, '_is_cover_page', False) and self.page_no() == 1:
            return

        self.set_y(-22)

        # Divider line
        line_color = self.secondary_color or self.primary_color
        self.set_draw_color(*line_color)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())

        self.ln(1)
        self.set_font("Helvetica", "", 7)
        self.set_text_color(128, 128, 128)

        # Line 1: Name | Address
        line1_parts = [self.tenant.get("name", "")]
        if self.tenant.get("address"):
            line1_parts.append(self.tenant["address"])
        self.cell(0, 4, " | ".join(filter(None, line1_parts)), align="C")
        self.ln(3.5)

        # Line 2: Phone | Email | Website
        line2_parts = []
        if self.tenant.get("phone"):
            line2_parts.append(self.tenant["phone"])
        if self.tenant.get("email"):
            line2_parts.append(self.tenant["email"])
        if self.tenant.get("website"):
            line2_parts.append(self.tenant["website"])
        if line2_parts:
            self.cell(0, 4, " | ".join(line2_parts), align="C")
            self.ln(3.5)

        # Line 3: Page number
        self.cell(0, 4, f"Pagina {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title: str):
        """Add a section title with secondary color background."""
        bg_color = self.secondary_color or (240, 244, 255)
        self.set_fill_color(*bg_color if self.secondary_color else bg_color)
        if self.secondary_color:
            # Lighten the secondary color for background
            self.set_fill_color(
                min(255, bg_color[0] + 180),
                min(255, bg_color[1] + 180),
                min(255, bg_color[2] + 180),
            )
        else:
            self.set_fill_color(240, 244, 255)

        self.set_draw_color(*self.primary_color)
        self.set_text_color(*self.primary_color)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, f"  {title}", border="L", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def _safe_cell(self, w: float, h: float, text: str, border=0, fill=False,
                   align="", new_x="RIGHT", new_y="TOP", font_size=None):
        """
        Render text in a cell, using multi_cell with wrapping if text is too long.

        Returns the actual height used.
        """
        if font_size:
            self.set_font_size(font_size)

        text = text or ""
        # Calculate if text fits in the cell width
        text_width = self.get_string_width(text)
        available_width = w - 2  # padding

        if text_width <= available_width or not text.strip():
            # Text fits - use normal cell
            self.cell(w, h, text, border=border, fill=fill, align=align,
                      new_x=new_x, new_y=new_y)
            return h
        else:
            # Text doesn't fit - use multi_cell
            x_before = self.get_x()
            y_before = self.get_y()
            line_height = h * 0.7 if h > 5 else 3.5
            self.multi_cell(w, line_height, text, border=border, fill=fill,
                           align=align, new_x="RIGHT", new_y="TOP",
                           max_line_height=line_height)
            actual_height = self.get_y() - y_before
            if actual_height < h:
                actual_height = h
            # Reset position based on new_x/new_y
            if new_x == "RIGHT":
                self.set_xy(x_before + w, y_before)
            return actual_height

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
        layout_config: dict | None = None,
    ) -> bytes:
        """
        Generate a PDF for a report.

        Args:
            report: The report with all related data loaded
            tenant: The tenant for branding
            certificates: Optional list of CalibrationCertificate objects
            layout_config: Optional layout configuration from PdfLayout.config_json

        Returns:
            PDF file as bytes
        """
        snapshot = report.template_snapshot
        config = layout_config or {}

        # Route to specialized renderer if style is set
        if config.get("style") == "gensep":
            from app.services.pdf.gensep_renderer import GensepPDFRenderer
            from app.services.pdf.layout_config import LayoutConfig
            lc = LayoutConfig.from_dict(config)
            renderer = GensepPDFRenderer(report, tenant, certificates, lc)
            return renderer.generate()

        # Build logo URLs properly
        logo_primary_url = self._resolve_logo_url(tenant.logo_primary_key)
        logo_secondary_url = self._resolve_logo_url(tenant.logo_secondary_key)

        # Build context with all branding fields
        tenant_info = {
            "name": tenant.name,
            "logo_primary_url": logo_primary_url,
            "logo_secondary_url": logo_secondary_url,
            "primary_color": tenant.brand_color_primary or "#2563eb",
            "secondary_color": tenant.brand_color_secondary or "",
            "accent_color": tenant.brand_color_accent or "",
            "phone": tenant.contact_phone,
            "email": tenant.contact_email,
            "address": tenant.contact_address,
            "website": tenant.contact_website,
        }

        template_info = {
            "name": snapshot.get("name", "Relatorio"),
            "code": snapshot.get("code", ""),
            "version": snapshot.get("version", "1"),
        }

        # Create PDF
        pdf = ReportPDF(tenant_info, template_info)
        pdf.alias_nb_pages()

        # Cover page (if enabled in layout config)
        cover_config = config.get("cover_page", {})
        if cover_config.get("enabled", False):
            pdf._is_cover_page = True
            self._add_cover_page(pdf, report, tenant_info, template_info, snapshot)
            pdf._is_cover_page = False

        # Content pages
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=25)

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
                self._add_photos(pdf, section_photos, config)

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

    def _add_cover_page(self, pdf: ReportPDF, report: Report, tenant_info: dict,
                        template_info: dict, snapshot: dict):
        """
        Add a cover page mirroring the PdfCoverPreview.tsx design.

        1. Top color bar
        2. Logo centered
        3. Company name bold uppercase
        4. Divider line
        5. Report title in primary color
        6. Template code + version
        7. Info fields with dotted lines
        8. Signature roles with lines
        9. Bottom color bar
        """
        pdf.add_page()
        pdf.set_auto_page_break(auto=False)

        primary = pdf.primary_color

        # 1. Top color bar
        pdf.set_fill_color(*primary)
        pdf.rect(0, 0, 210, 6, "F")

        # 2. Logo centered
        y_pos = 25
        if tenant_info.get("logo_primary_url"):
            try:
                pdf._add_image_from_url(tenant_info["logo_primary_url"], 75, y_pos, 60)
                y_pos += 30
            except Exception:
                y_pos += 5

        # 3. Company name
        pdf.set_xy(10, y_pos)
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(50, 50, 50)
        company_name = (tenant_info.get("name") or "Empresa").upper()
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

                # Dotted line
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
            # Position near bottom
            sig_y = max(y_pos, 240)
            if sig_y > 265:
                sig_y = 240

            sigs_to_show = sig_fields[:3]
            sig_width = 50
            total_width = len(sigs_to_show) * sig_width + (len(sigs_to_show) - 1) * 10
            start_x = (210 - total_width) / 2

            for i, sig in enumerate(sigs_to_show):
                x = start_x + i * (sig_width + 10)
                # Signature line
                pdf.set_draw_color(100, 100, 100)
                pdf.set_line_width(0.3)
                pdf.line(x, sig_y, x + sig_width, sig_y)
                # Role name
                pdf.set_xy(x, sig_y + 1)
                pdf.set_font("Helvetica", "", 8)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(sig_width, 4, sig.get("role_name", ""), align="C")

        # 9. Bottom color bar
        pdf.set_fill_color(*primary)
        pdf.rect(0, 293, 210, 4, "F")

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
        """Add checklist table with proper text wrapping for all columns."""
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

            # Calculate row height based on all columns
            label = field.get("label", "")
            label_lines = max(1, (len(label) // 50) + 1) if len(label) > 55 else 1
            comment_lines = max(1, (len(comment) // 35) + 1) if len(comment) > 40 else 1
            max_lines = max(label_lines, comment_lines)
            row_height = max(7, max_lines * 5)

            y_before = pdf.get_y()
            x_before = pdf.get_x()

            # Check page break needed
            if y_before + row_height > pdf.h - 25:
                pdf.add_page()
                y_before = pdf.get_y()
                x_before = pdf.get_x()

            # Label with multi_cell for long text
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "", 9)
            if len(label) > 55:
                pdf.multi_cell(95, 5, label, border=1, fill=True, new_x="RIGHT", new_y="TOP", max_line_height=5)
                actual_height = max(pdf.get_y() - y_before, row_height)
                pdf.set_xy(x_before + 95, y_before)
            else:
                pdf.cell(95, row_height, label, border=1, fill=True)
                actual_height = row_height

            # Response with color
            if pdf.accent_color and response_value in ("Sim", "OK", "Conforme"):
                pdf.set_text_color(*pdf.accent_color)
            elif response_value in ("Sim", "OK", "Conforme"):
                pdf.set_text_color(5, 150, 105)
            elif response_value in ("Nao", "NOK", "Nao Conforme"):
                pdf.set_text_color(220, 38, 38)
            elif response_value == "N/A":
                pdf.set_text_color(107, 114, 128)
            else:
                pdf.set_text_color(0, 0, 0)

            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(30, actual_height, response_value, border=1, fill=True, align="C")

            # Comment - full text with wrapping (no truncation)
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(100, 100, 100)
            comment_width = 190 - 95 - 30  # remaining width
            if len(comment) > 40:
                x_comment = pdf.get_x()
                pdf.multi_cell(comment_width, 4, comment, border=1, fill=True,
                              new_x="LMARGIN", new_y="TOP", max_line_height=4)
                comment_height = pdf.get_y() - y_before
                # Ensure we move to the right Y position
                final_height = max(actual_height, comment_height)
                pdf.set_xy(x_before, y_before + final_height)
            else:
                pdf.cell(0, actual_height, comment, border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

            pdf.set_font("Helvetica", "", 9)

    def _add_photos(self, pdf: ReportPDF, photos: list, config: dict = None):
        """Add photos in grid layout."""
        config = config or {}
        photo_config = config.get("photos", {})

        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 6, "Registro Fotografico:", new_x="LMARGIN", new_y="NEXT")

        x_start = 10
        y_start = pdf.get_y()
        photo_width = photo_config.get("width_mm", 80)
        photo_height = photo_config.get("height_mm", 60)
        photos_per_row = photo_config.get("columns", 2)
        max_photos = photo_config.get("max_per_section", 6)
        margin = max(5, (190 - photos_per_row * photo_width) // max(1, photos_per_row - 1)) if photos_per_row > 1 else 0

        for i, photo_data in enumerate(photos[:max_photos]):
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

            # Caption - full text, no truncation
            pdf.set_xy(x, y + photo_height)
            pdf.set_font("Helvetica", "", 7)
            pdf.set_text_color(100, 100, 100)

            caption = photo_data.get("field", "")
            if photo_data.get("captured_at"):
                captured = photo_data["captured_at"][:16].replace("T", " ")
                caption += f"\n{captured}"

            pdf.multi_cell(photo_width, 3, caption, align="C")

        # Move cursor after photos
        if photos[:max_photos]:
            last_row = (len(photos[:max_photos]) - 1) // photos_per_row
            pdf.set_y(y_start + (last_row + 1) * (photo_height + 18))

    def _add_certificates_table(self, pdf: ReportPDF, certificates: list):
        """Add certificates table section with text wrapping."""
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

            equipment = cert.equipment_name or ""
            cert_num = cert.certificate_number or ""
            lab = cert.laboratory or "-"
            cal_date = cert.calibration_date.strftime("%d/%m/%Y")
            exp_date = cert.expiry_date.strftime("%d/%m/%Y")

            # Calculate max row height based on content
            row_h = 6
            for text, width in [(equipment, 50), (cert_num, 35), (lab, 45)]:
                text_w = pdf.get_string_width(text)
                if text_w > width - 2:
                    lines = (len(text) // int(width / 2)) + 1
                    row_h = max(row_h, lines * 4)

            y_before = pdf.get_y()
            x_before = pdf.get_x()

            # Equipment - with wrapping
            pdf._safe_cell(50, row_h, equipment, border=1, fill=True)
            # Certificate number - with wrapping
            pdf._safe_cell(35, row_h, cert_num, border=1, fill=True)
            # Laboratory - with wrapping
            pdf._safe_cell(45, row_h, lab, border=1, fill=True)

            # Dates (fixed width, always fit)
            pdf.cell(25, row_h, cal_date, border=1, fill=True, align="C")
            pdf.cell(25, row_h, exp_date, border=1, fill=True, align="C")

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
            pdf.cell(0, row_h, status_text, border=1, fill=True, align="C", new_x="LMARGIN", new_y="NEXT")

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
        """Add signatures grid with text wrapping for names."""
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

            # Role name - with wrapping via multi_cell
            pdf.set_xy(x, y + sig_height + 1)
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(0, 0, 0)
            role_name = sig.role_name or ""
            pdf.multi_cell(sig_width, 3.5, role_name, align="C")

            # Signer name - with wrapping
            if sig.signer_name:
                pdf.set_xy(x, y + sig_height + 6)
                pdf.set_font("Helvetica", "", 7)
                pdf.set_text_color(100, 100, 100)
                pdf.multi_cell(sig_width, 3, sig.signer_name, align="C")

            # Date
            pdf.set_xy(x, y + sig_height + 11)
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
