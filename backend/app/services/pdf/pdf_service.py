"""
PDF generation orchestrator.

Reads layout config and delegates to individual renderers.
"""

import logging
from typing import Any

from fpdf import FPDF

from app.models.report import Report
from app.models.tenant import Tenant
from app.core.config import settings

logger = logging.getLogger(__name__)

from .layout_config import LayoutConfig
from .cover_renderer import CoverRenderer
from .header_renderer import HeaderRenderer
from .footer_renderer import FooterRenderer
from .info_table_renderer import InfoTableRenderer
from .checklist_renderer import ChecklistRenderer
from .photo_renderer import PhotoRenderer
from .certificate_renderer import CertificateRenderer
from .signature_renderer import SignatureRenderer


class ComponentReportPDF(FPDF):
    """Custom PDF class that delegates header/footer to renderers."""

    def __init__(self, header_renderer: HeaderRenderer, footer_renderer: FooterRenderer,
                 template_info: dict):
        super().__init__()
        self._header_renderer = header_renderer
        self._footer_renderer = footer_renderer
        self._template_info = template_info
        self._is_cover_page = False

    def header(self):
        if self._is_cover_page and self.page_no() == 1:
            return
        self._header_renderer.render(self._template_info)

    def footer(self):
        if self._is_cover_page and self.page_no() == 1:
            return
        self._footer_renderer.render()


class ComponentPDFService:
    """PDF generation service using componentized renderers."""

    @staticmethod
    def _validate_snapshot(snapshot: Any) -> dict:
        """Validate template snapshot structure before rendering."""
        if not isinstance(snapshot, dict):
            logger.warning("Template snapshot is not a dict, using empty snapshot")
            return {"name": "Relatorio", "code": "", "version": "1",
                    "sections": [], "info_fields": [], "signature_fields": []}

        validated = {
            "name": snapshot.get("name", "Relatorio"),
            "code": snapshot.get("code", ""),
            "version": snapshot.get("version", "1"),
            "info_fields": snapshot.get("info_fields") or [],
            "signature_fields": snapshot.get("signature_fields") or [],
            "sections": [],
        }
        for section in (snapshot.get("sections") or []):
            if not isinstance(section, dict):
                continue
            validated_section = {
                "name": section.get("name", ""),
                "order": section.get("order", 0),
                "fields": [],
            }
            for field in (section.get("fields") or []):
                if not isinstance(field, dict):
                    continue
                validated_section["fields"].append({
                    "id": field.get("id", ""),
                    "label": field.get("label", ""),
                    "field_type": field.get("field_type", "text"),
                    "options": field.get("options"),
                    "order": field.get("order", 0),
                    "photo_config": field.get("photo_config") or {},
                    "comment_config": field.get("comment_config") or {},
                })
            validated["sections"].append(validated_section)
        return validated

    def generate_report_pdf(
        self,
        report: Report,
        tenant: Tenant,
        certificates: list | None = None,
        layout_config: dict | None = None,
    ) -> bytes:
        """Generate a PDF using componentized renderers."""
        snapshot = self._validate_snapshot(report.template_snapshot)
        config = LayoutConfig.from_dict(layout_config)

        # Route to specialized renderer if style is set
        if config.style == "gensep":
            from .gensep_renderer import GensepPDFRenderer
            renderer = GensepPDFRenderer(report, tenant, certificates, config)
            return renderer.generate()

        # Build logo URLs
        logo_primary_url = self._resolve_logo_url(tenant.logo_primary_key)
        logo_secondary_url = self._resolve_logo_url(tenant.logo_secondary_key)

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

        # Create a temporary FPDF for header/footer renderers (they need the pdf ref)
        # We'll set the actual pdf ref after creating ComponentReportPDF
        header_renderer = HeaderRenderer.__new__(HeaderRenderer)
        footer_renderer = FooterRenderer.__new__(FooterRenderer)

        pdf = ComponentReportPDF(header_renderer, footer_renderer, template_info)

        # Now properly init renderers with the real pdf
        header_renderer.__init__(pdf, config, tenant_info)
        footer_renderer.__init__(pdf, config, tenant_info)

        pdf.alias_nb_pages()

        # Create other renderers
        cover = CoverRenderer(pdf, config, tenant_info)
        info_table = InfoTableRenderer(pdf, config, tenant_info)
        checklist = ChecklistRenderer(pdf, config, tenant_info)
        photo = PhotoRenderer(pdf, config, tenant_info)
        cert_renderer = CertificateRenderer(pdf, config, tenant_info)
        sig_renderer = SignatureRenderer(pdf, config, tenant_info)

        # Cover page
        cover.render(report, template_info, snapshot)

        # Content pages
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=25)

        # Report title and date
        pdf.set_font("Helvetica", "B", config.fonts.header_size - 2)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 8, report.title, new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "", config.fonts.base_size)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, f"Data: {report.created_at.strftime('%d/%m/%Y')} | Status: {report.status}",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        # Section title helper
        primary = header_renderer.get_primary_color()
        secondary = header_renderer.get_secondary_color()

        def section_title(title: str):
            if secondary:
                pdf.set_fill_color(
                    min(255, secondary[0] + 180),
                    min(255, secondary[1] + 180),
                    min(255, secondary[2] + 180),
                )
            else:
                pdf.set_fill_color(240, 244, 255)
            pdf.set_draw_color(*primary)
            pdf.set_text_color(*primary)
            pdf.set_font("Helvetica", "B", config.fonts.section_size)
            pdf.cell(0, 8, f"  {title}", border="L", fill=True, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)

        # Info fields
        if report.info_values:
            try:
                section_title("Informacoes do Projeto")
                info_table.render(report.info_values)
            except Exception as e:
                logger.error("Failed to render info table: %s", e)
                pdf.ln(5)

        # Checklist sections
        sections = self._group_responses_by_section(report, snapshot)
        for section in sections:
            try:
                section_title(section["name"])
                checklist.render(section["fields"])

                section_photos = self._get_section_photos(section)
                if section_photos:
                    photo.render(section_photos)
                pdf.ln(3)
            except Exception as e:
                logger.error("Failed to render section '%s': %s", section.get("name"), e)
                pdf.ln(5)

        # Certificates
        if certificates:
            try:
                section_title("Certificados de Calibracao")
                cert_renderer.render(certificates)
            except Exception as e:
                logger.error("Failed to render certificates table: %s", e)
                pdf.ln(5)

        # Signatures
        if report.signatures:
            try:
                section_title("Assinaturas")
                sig_renderer.render(report.signatures)
            except Exception as e:
                logger.error("Failed to render signatures: %s", e)
                pdf.ln(5)

        return bytes(pdf.output())

    def _resolve_logo_url(self, key: str | None) -> str | None:
        if not key:
            return None
        if key.startswith(("http://", "https://")):
            return key
        if settings.r2_public_url:
            return f"{settings.r2_public_url}/{key}"
        return f"uploads/{key}"

    def _group_responses_by_section(self, report: Report, snapshot: dict) -> list:
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
        photos = []
        for field in section.get("fields", []):
            response = field.get("response", {})
            for photo in response.get("photos", []) or []:
                photos.append({
                    **photo,
                    "field": field.get("label", ""),
                })
        return photos
