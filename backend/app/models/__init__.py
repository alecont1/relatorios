"""
SQLAlchemy models for SmartHand application.

Base classes:
- Base: Common columns (id, created_at, updated_at) - NO tenant_id
- TenantBase: Extends Base with tenant_id for multi-tenant models
- SimpleBase: Alias for Base, used by child models

Models with tenant_id (extend TenantBase):
- Tenant (special case - no tenant_id, it IS the tenant)
- User, Template, Project, Report

Models without tenant_id (extend Base/SimpleBase):
- TemplateSection, TemplateField, etc. (inherit isolation via parent)
"""

from app.models.base import Base, TenantBase
from app.models.simple_base import SimpleBase
from app.models.tenant import Tenant
from app.models.tenant_plan import TenantPlan
from app.models.tenant_config import TenantConfig
from app.models.tenant_audit_log import TenantAuditLog
from app.models.tenant_onboarding import TenantOnboarding
from app.models.user import User
# Import child models BEFORE parent models to ensure forward refs resolve
from app.models.template_section import TemplateSection
from app.models.template_field import TemplateField
from app.models.template_info_field import TemplateInfoField
from app.models.template_signature_field import TemplateSignatureField
from app.models.template import Template
from app.models.project import Project
# Import report child models before Report
from app.models.report_info_value import ReportInfoValue
from app.models.report_checklist_response import ReportChecklistResponse
from app.models.report_signature import ReportSignature
from app.models.calibration_certificate import CalibrationCertificate
from app.models.pdf_layout import PdfLayout
from app.models.report_certificate import ReportCertificate
from app.models.report import Report
from app.models.report_photo import ReportPhoto

__all__ = [
    "Base",
    "TenantBase",
    "SimpleBase",
    "Tenant",
    "TenantPlan",
    "TenantConfig",
    "TenantAuditLog",
    "TenantOnboarding",
    "User",
    "Template",
    "TemplateSection",
    "TemplateField",
    "TemplateInfoField",
    "TemplateSignatureField",
    "Project",
    "Report",
    "ReportInfoValue",
    "ReportChecklistResponse",
    "ReportSignature",
    "ReportPhoto",
    "CalibrationCertificate",
    "PdfLayout",
    "ReportCertificate",
]
