"""
SQLAlchemy models for SmartHand application.

All models inherit from Base and include:
- id: UUID primary key
- tenant_id: Multi-tenant support (except Tenant model itself)
- created_at: Timestamp of creation
- updated_at: Timestamp of last update
"""

from app.models.base import Base
from app.models.simple_base import SimpleBase
from app.models.tenant import Tenant
from app.models.user import User
from app.models.template import Template
from app.models.template_section import TemplateSection
from app.models.template_field import TemplateField
from app.models.project import Project
from app.models.report import Report
from app.models.report_photo import ReportPhoto

__all__ = [
    "Base",
    "SimpleBase",
    "Tenant",
    "User",
    "Template",
    "TemplateSection",
    "TemplateField",
    "Project",
    "Report",
    "ReportPhoto",
]
