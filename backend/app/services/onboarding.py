"""
Onboarding service - manages tenant onboarding wizard progress.

Provides operations for tracking step completion, cloning demo templates,
and managing the 3-step onboarding lifecycle (Sua Marca, Seu Template, Teste Real).
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.fixtures.demo_template import DEMO_TEMPLATE
from app.models.template import Template
from app.models.template_field import TemplateField
from app.models.template_section import TemplateSection
from app.models.tenant_onboarding import TenantOnboarding


# Ordered step keys matching the wizard flow (3-step onboarding)
STEP_KEYS = ["branding", "template", "first_report"]

STEP_LABELS = {
    "branding": "Sua Marca",
    "template": "Seu Template",
    "first_report": "Teste Real",
}


def _get_step_attr(step_key: str) -> str:
    """Convert step key to model attribute name."""
    return f"step_{step_key}"


class OnboardingService:
    """Handles onboarding wizard lifecycle for tenants."""

    async def get_or_create(self, db: AsyncSession, tenant_id: uuid.UUID) -> TenantOnboarding:
        """Get existing onboarding record or create a new one."""
        result = await db.execute(
            select(TenantOnboarding).where(TenantOnboarding.tenant_id == tenant_id)
        )
        onboarding = result.scalar_one_or_none()
        if onboarding is None:
            onboarding = TenantOnboarding(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
            )
            db.add(onboarding)
            await db.flush()
        return onboarding

    async def get_status(self, db: AsyncSession, tenant_id: uuid.UUID) -> dict:
        """Get onboarding status with step details."""
        onboarding = await self.get_or_create(db, tenant_id)

        steps = []
        for key in STEP_KEYS:
            attr = _get_step_attr(key)
            steps.append({
                "key": key,
                "status": getattr(onboarding, attr),
                "label": STEP_LABELS[key],
            })

        return {
            "id": onboarding.id,
            "tenant_id": onboarding.tenant_id,
            "is_completed": onboarding.is_completed,
            "completed_at": onboarding.completed_at,
            "current_step": onboarding.current_step,
            "steps": steps,
            "metadata_json": onboarding.metadata_json or {},
        }

    async def complete_step(self, db: AsyncSession, tenant_id: uuid.UUID, step_key: str) -> TenantOnboarding:
        """Mark a step as completed and advance current_step."""
        if step_key not in STEP_KEYS:
            raise ValueError(f"Invalid step key: {step_key}")

        onboarding = await self.get_or_create(db, tenant_id)
        attr = _get_step_attr(step_key)
        setattr(onboarding, attr, "completed")

        self._advance_current_step(onboarding)
        self._check_all_completed(onboarding)

        await db.flush()
        return onboarding

    async def skip_step(self, db: AsyncSession, tenant_id: uuid.UUID, step_key: str) -> TenantOnboarding:
        """Mark a step as skipped and advance current_step."""
        if step_key not in STEP_KEYS:
            raise ValueError(f"Invalid step key: {step_key}")

        onboarding = await self.get_or_create(db, tenant_id)
        attr = _get_step_attr(step_key)
        setattr(onboarding, attr, "skipped")

        self._advance_current_step(onboarding)
        self._check_all_completed(onboarding)

        await db.flush()
        return onboarding

    async def clone_demo_template(self, db: AsyncSession, tenant_id: uuid.UUID) -> Template:
        """Clone the demo template fixture into the tenant's templates."""
        onboarding = await self.get_or_create(db, tenant_id)

        # Check if already cloned
        meta = onboarding.metadata_json or {}
        if meta.get("demo_template_id"):
            # Return existing template
            result = await db.execute(
                select(Template).where(Template.id == meta["demo_template_id"])
            )
            existing = result.scalar_one_or_none()
            if existing:
                return existing

        # Create template from fixture
        template = Template(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            name=DEMO_TEMPLATE["name"],
            code=DEMO_TEMPLATE["code"],
            category=DEMO_TEMPLATE["category"],
            title=DEMO_TEMPLATE.get("title"),
            reference_standards=DEMO_TEMPLATE.get("reference_standards"),
            version=1,
            is_active=True,
        )
        db.add(template)
        await db.flush()

        # Create sections and fields
        for section_data in DEMO_TEMPLATE["sections"]:
            section = TemplateSection(
                id=uuid.uuid4(),
                template_id=template.id,
                name=section_data["name"],
                order=section_data["order"],
            )
            db.add(section)
            await db.flush()

            for field_data in section_data["fields"]:
                field = TemplateField(
                    id=uuid.uuid4(),
                    section_id=section.id,
                    label=field_data["label"],
                    field_type=field_data["field_type"],
                    options=field_data.get("options"),
                    order=field_data["order"],
                    photo_config=field_data.get("photo_config"),
                    comment_config=field_data.get("comment_config"),
                )
                db.add(field)

        await db.flush()

        # Store template_id in metadata
        meta["demo_template_id"] = str(template.id)
        onboarding.metadata_json = meta

        await db.flush()
        return template

    def _advance_current_step(self, onboarding: TenantOnboarding) -> None:
        """Set current_step to the index of the first pending step."""
        for i, key in enumerate(STEP_KEYS):
            attr = _get_step_attr(key)
            if getattr(onboarding, attr) == "pending":
                onboarding.current_step = i
                return
        # All steps are non-pending; set to last index + 1
        onboarding.current_step = len(STEP_KEYS)

    def _check_all_completed(self, onboarding: TenantOnboarding) -> None:
        """If all steps are non-pending, mark onboarding as completed."""
        for key in STEP_KEYS:
            attr = _get_step_attr(key)
            if getattr(onboarding, attr) == "pending":
                return
        onboarding.is_completed = True
        onboarding.completed_at = datetime.now(timezone.utc)


# Singleton instance
onboarding_service = OnboardingService()
