"""
Factory functions for creating test data.
"""
import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant
from app.models.user import User
from app.models.template import Template
from app.models.template_section import TemplateSection
from app.models.template_field import TemplateField
from app.models.template_info_field import TemplateInfoField
from app.models.template_signature_field import TemplateSignatureField
from app.models.project import Project
from app.models.report import Report
from app.models.report_info_value import ReportInfoValue
from app.models.report_checklist_response import ReportChecklistResponse
from app.core.security import hash_password


async def create_tenant(db: AsyncSession, **overrides) -> Tenant:
    """Create a test tenant."""
    slug = f"test-{uuid.uuid4().hex[:8]}"
    defaults = {
        "name": "Test Company",
        "slug": slug,
        "is_active": True,
    }
    defaults.update(overrides)
    tenant = Tenant(**defaults)
    db.add(tenant)
    await db.flush()
    return tenant


async def create_user(
    db: AsyncSession,
    tenant_id: Optional[uuid.UUID] = None,
    role: str = "technician",
    **overrides,
) -> User:
    """Create a test user."""
    defaults = {
        "email": f"user-{uuid.uuid4().hex[:8]}@test.com",
        "full_name": "Test User",
        "password_hash": hash_password("Test1234!"),
        "role": role,
        "tenant_id": tenant_id,
        "is_active": True,
    }
    defaults.update(overrides)
    user = User(**defaults)
    db.add(user)
    await db.flush()
    return user


async def create_template(db: AsyncSession, tenant_id: uuid.UUID, **overrides) -> Template:
    """Create a test template with 1 section and 2 fields."""
    defaults = {
        "tenant_id": tenant_id,
        "name": "Test Template",
        "code": f"TST-{uuid.uuid4().hex[:3].upper()}",
        "category": "Commissioning",
        "version": 1,
        "is_active": True,
    }
    defaults.update(overrides)
    template = Template(**defaults)
    db.add(template)
    await db.flush()

    # Add a section with 2 fields
    section = TemplateSection(
        template_id=template.id,
        name="Test Section",
        order=1,
    )
    db.add(section)
    await db.flush()

    field1 = TemplateField(
        section_id=section.id,
        label="Check Item 1",
        field_type="dropdown",
        options="Sim,Nao,N/A",
        order=1,
        photo_config={"required": False, "min_count": 0, "max_count": 5},
        comment_config={"enabled": True, "required": False},
    )
    field2 = TemplateField(
        section_id=section.id,
        label="Check Item 2",
        field_type="text",
        order=2,
        photo_config={"required": False, "min_count": 0, "max_count": 3},
        comment_config={"enabled": True, "required": False},
    )
    db.add_all([field1, field2])
    await db.flush()

    return template


async def create_project(db: AsyncSession, tenant_id: uuid.UUID, **overrides) -> Project:
    """Create a test project."""
    defaults = {
        "tenant_id": tenant_id,
        "name": "Test Project",
        "description": "A test project",
        "client_name": "Test Client",
        "is_active": True,
    }
    defaults.update(overrides)
    project = Project(**defaults)
    db.add(project)
    await db.flush()
    return project


async def create_report(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    template: Template,
    project: Project,
    user: User,
    **overrides,
) -> Report:
    """Create a test report with template snapshot."""
    snapshot = {
        "id": str(template.id),
        "name": template.name,
        "code": template.code,
        "category": template.category,
        "version": template.version,
        "title": None,
        "reference_standards": None,
        "planning_requirements": None,
        "info_fields": [],
        "sections": [
            {
                "id": str(uuid.uuid4()),
                "name": "Test Section",
                "order": 1,
                "fields": [
                    {
                        "id": str(uuid.uuid4()),
                        "label": "Check Item 1",
                        "field_type": "dropdown",
                        "options": "Sim,Nao,N/A",
                        "order": 1,
                        "photo_config": {"required": False, "min_count": 0, "max_count": 5},
                        "comment_config": {"enabled": True, "required": False},
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "label": "Check Item 2",
                        "field_type": "text",
                        "order": 2,
                        "photo_config": {"required": False, "min_count": 0, "max_count": 3},
                        "comment_config": {"enabled": True, "required": False},
                    },
                ],
            }
        ],
        "signature_fields": [],
    }

    defaults = {
        "tenant_id": tenant_id,
        "template_id": template.id,
        "project_id": project.id,
        "user_id": user.id,
        "title": "Test Report",
        "status": "draft",
        "template_snapshot": snapshot,
    }
    defaults.update(overrides)
    report = Report(**defaults)
    db.add(report)
    await db.flush()
    return report
