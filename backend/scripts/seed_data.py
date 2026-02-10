#!/usr/bin/env python3
"""
Comprehensive seed data script for the SmartHand multi-tenant report system.

Creates tenants, users, templates (with sections/fields/info/signatures),
projects, reports (with responses and info values), calibration certificates,
and links certificates to completed reports.

Usage:
    python scripts/seed_data.py           # Seed data (skip if data exists)
    python scripts/seed_data.py --clean   # Wipe all data and re-seed
"""

import argparse
import asyncio
import json
import sys
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Windows event loop compatibility
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.security import hash_password
from app.models import (
    Base,
    CalibrationCertificate,
    Project,
    Report,
    ReportCertificate,
    ReportChecklistResponse,
    ReportInfoValue,
    ReportSignature,
    Template,
    TemplateField,
    TemplateInfoField,
    TemplateSection,
    TemplateSignatureField,
    Tenant,
    User,
)

# ---------------------------------------------------------------------------
# Engine / Session factory (standalone, not reusing app's to avoid side effects)
# ---------------------------------------------------------------------------
engine = create_async_engine(settings.database_url, echo=False, future=True)
SessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# ---------------------------------------------------------------------------
# Helper: build template_snapshot JSONB from in-memory data
# ---------------------------------------------------------------------------
def build_template_snapshot(
    *,
    template_name: str,
    template_code: str,
    template_category: str,
    info_fields: list[dict[str, Any]],
    sections: list[dict[str, Any]],
    signature_fields: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build the JSONB snapshot that Report.template_snapshot expects.

    The snapshot mirrors the template structure so that historical reports
    remain consistent even if the template is later modified.
    """
    return {
        "name": template_name,
        "code": template_code,
        "category": template_category,
        "info_fields": info_fields,
        "sections": sections,
        "signature_fields": signature_fields,
    }


# ---------------------------------------------------------------------------
# Clean
# ---------------------------------------------------------------------------
TABLES_DELETE_ORDER = [
    "report_certificates",
    "report_signatures",
    "report_checklist_responses",
    "report_info_values",
    "report_photos",
    "reports",
    "calibration_certificates",
    "template_fields",
    "template_sections",
    "template_info_fields",
    "template_signature_fields",
    "templates",
    "projects",
    "users",
    "tenants",
]


async def clean_database(session: AsyncSession) -> None:
    """Delete ALL data from every table in reverse FK order."""
    print("\n--- Cleaning database ---")
    for table in TABLES_DELETE_ORDER:
        await session.execute(text(f'DELETE FROM "{table}"'))
        print(f"  Cleared table: {table}")
    await session.commit()
    print("--- Database cleaned ---\n")


# ---------------------------------------------------------------------------
# Seed: Tenants
# ---------------------------------------------------------------------------
async def seed_tenants(session: AsyncSession) -> dict[str, Tenant]:
    """Create the two demo tenants and return them keyed by slug."""
    print("Seeding tenants...")

    alpha = Tenant(
        id=uuid.uuid4(),
        name="Alpha Engenharia",
        slug="alpha-engenharia",
        is_active=True,
        brand_color_primary="#1E40AF",
        brand_color_secondary="#3B82F6",
        brand_color_accent="#F59E0B",
        contact_address="Rua Augusta, 1500, Sao Paulo, SP",
        contact_phone="(11) 3000-1234",
        contact_email="contato@alphaeng.com.br",
        contact_website="https://www.alphaeng.com.br",
        watermark_text="ALPHA ENGENHARIA",
        watermark_config={
            "logo": True,
            "gps": True,
            "datetime": True,
            "company_name": True,
            "report_number": False,
            "technician_name": True,
        },
    )

    beta = Tenant(
        id=uuid.uuid4(),
        name="Beta Servicos Tecnicos",
        slug="beta-servicos",
        is_active=True,
        brand_color_primary="#059669",
        brand_color_secondary="#10B981",
        brand_color_accent="#F97316",
        contact_address="Av. Paulista, 2000, Sao Paulo, SP",
        contact_phone="(11) 4000-5678",
        contact_email="contato@betaservicos.com.br",
        contact_website="https://www.betaservicos.com.br",
        watermark_text="BETA SERVICOS",
        watermark_config={
            "logo": True,
            "gps": True,
            "datetime": True,
            "company_name": True,
            "report_number": True,
            "technician_name": True,
        },
    )

    session.add_all([alpha, beta])
    await session.flush()

    tenants = {"alpha-engenharia": alpha, "beta-servicos": beta}
    print(f"  Created {len(tenants)} tenants: {', '.join(t.name for t in tenants.values())}")
    return tenants


# ---------------------------------------------------------------------------
# Seed: Users
# ---------------------------------------------------------------------------
async def seed_users(
    session: AsyncSession, tenants: dict[str, Tenant]
) -> dict[str, User]:
    """Create demo users and return them keyed by email."""
    print("Seeding users...")

    alpha_id = tenants["alpha-engenharia"].id
    beta_id = tenants["beta-servicos"].id

    users_data: list[dict[str, Any]] = [
        {
            "full_name": "Super Admin",
            "email": "admin@smarthand.com",
            "password": "Admin123!",
            "role": "superadmin",
            "tenant_id": None,
        },
        {
            "full_name": "Alpha Admin",
            "email": "admin@alphaeng.com.br",
            "password": "Alpha123!",
            "role": "tenant_admin",
            "tenant_id": alpha_id,
        },
        {
            "full_name": "Alpha Gerente",
            "email": "gerente@alphaeng.com.br",
            "password": "Alpha123!",
            "role": "project_manager",
            "tenant_id": alpha_id,
        },
        {
            "full_name": "Alpha Tecnico 1",
            "email": "tecnico1@alphaeng.com.br",
            "password": "Alpha123!",
            "role": "technician",
            "tenant_id": alpha_id,
        },
        {
            "full_name": "Beta Admin",
            "email": "admin@betaservicos.com.br",
            "password": "Beta123!",
            "role": "tenant_admin",
            "tenant_id": beta_id,
        },
        {
            "full_name": "Beta Tecnico 1",
            "email": "tecnico1@betaservicos.com.br",
            "password": "Beta123!",
            "role": "technician",
            "tenant_id": beta_id,
        },
        {
            "full_name": "Beta Visualizador",
            "email": "viewer@betaservicos.com.br",
            "password": "Beta123!",
            "role": "viewer",
            "tenant_id": beta_id,
        },
    ]

    users: dict[str, User] = {}
    for ud in users_data:
        user = User(
            id=uuid.uuid4(),
            full_name=ud["full_name"],
            email=ud["email"],
            password_hash=hash_password(ud["password"]),
            role=ud["role"],
            tenant_id=ud["tenant_id"],
            is_active=True,
        )
        session.add(user)
        users[ud["email"]] = user

    await session.flush()
    print(f"  Created {len(users)} users")
    for u in users.values():
        tenant_label = "GLOBAL" if u.tenant_id is None else str(u.tenant_id)[:8]
        print(f"    {u.email:40s}  role={u.role:20s}  tenant={tenant_label}")
    return users


# ---------------------------------------------------------------------------
# Seed: Templates (with sections, fields, info fields, signature fields)
# ---------------------------------------------------------------------------

# Dropdown option constants
SIM_NAO_NA = json.dumps(["Sim", "Nao", "N/A"])
OK_ALERTA_CRITICO = json.dumps(["OK", "Alerta", "Critico"])


def _make_dropdown_fields(
    section_id: uuid.UUID,
    labels: list[str],
    options: str,
) -> list[TemplateField]:
    """Create a list of dropdown TemplateFields for a section."""
    return [
        TemplateField(
            id=uuid.uuid4(),
            section_id=section_id,
            label=label,
            field_type="dropdown",
            options=options,
            order=idx + 1,
            photo_config={"required": False, "min_count": 0, "max_count": 3, "require_gps": False, "watermark": True},
            comment_config={"enabled": True, "required": False},
        )
        for idx, label in enumerate(labels)
    ]


async def seed_templates(
    session: AsyncSession, tenants: dict[str, Tenant]
) -> dict[str, dict[str, Any]]:
    """Create templates with all child objects.

    Returns a nested dict keyed by template code containing:
        template, info_fields, sections (list of dicts with section + fields),
        signature_fields, and snapshot.
    """
    print("Seeding templates...")

    alpha_id = tenants["alpha-engenharia"].id
    beta_id = tenants["beta-servicos"].id

    result: dict[str, dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # ALPHA: Commissioning Eletrico (CE-001)
    # ------------------------------------------------------------------
    ce_template = Template(
        id=uuid.uuid4(),
        tenant_id=alpha_id,
        name="Commissioning Eletrico",
        code="CE-001",
        category="Commissioning",
        version=1,
        title="Relatorio de Commissioning Eletrico",
        is_active=True,
    )
    session.add(ce_template)

    # Info fields
    ce_info_fields_data = [
        {"label": "Local da Obra", "field_type": "text", "required": True, "order": 1},
        {"label": "Data da Inspecao", "field_type": "date", "required": True, "order": 2},
        {"label": "Responsavel", "field_type": "text", "required": False, "order": 3},
    ]
    ce_info_objs: list[TemplateInfoField] = []
    for ifd in ce_info_fields_data:
        obj = TemplateInfoField(
            id=uuid.uuid4(),
            template_id=ce_template.id,
            label=ifd["label"],
            field_type=ifd["field_type"],
            required=ifd["required"],
            order=ifd["order"],
        )
        session.add(obj)
        ce_info_objs.append(obj)

    # Section 1: Instalacoes Eletricas
    ce_sec1 = TemplateSection(
        id=uuid.uuid4(),
        template_id=ce_template.id,
        name="Instalacoes Eletricas",
        order=1,
    )
    session.add(ce_sec1)
    ce_sec1_labels = [
        "Quadro de distribuicao em bom estado",
        "Disjuntores devidamente identificados",
        "Aterramento conforme norma",
        "Cabos dimensionados corretamente",
        "Protecao contra surtos instalada",
    ]
    ce_sec1_fields = _make_dropdown_fields(ce_sec1.id, ce_sec1_labels, SIM_NAO_NA)
    session.add_all(ce_sec1_fields)

    # Section 2: Iluminacao
    ce_sec2 = TemplateSection(
        id=uuid.uuid4(),
        template_id=ce_template.id,
        name="Iluminacao",
        order=2,
    )
    session.add(ce_sec2)
    ce_sec2_labels = [
        "Luminarias funcionando",
        "Nivel de iluminamento adequado",
        "Iluminacao de emergencia operante",
    ]
    ce_sec2_fields = _make_dropdown_fields(ce_sec2.id, ce_sec2_labels, SIM_NAO_NA)
    session.add_all(ce_sec2_fields)

    # Signature fields
    ce_sig_data = [
        {"role_name": "Tecnico Responsavel", "required": True, "order": 1},
        {"role_name": "Engenheiro Supervisor", "required": False, "order": 2},
    ]
    ce_sig_objs: list[TemplateSignatureField] = []
    for sd in ce_sig_data:
        obj = TemplateSignatureField(
            id=uuid.uuid4(),
            template_id=ce_template.id,
            role_name=sd["role_name"],
            required=sd["required"],
            order=sd["order"],
        )
        session.add(obj)
        ce_sig_objs.append(obj)

    # Build snapshot
    ce_snapshot = build_template_snapshot(
        template_name=ce_template.name,
        template_code=ce_template.code,
        template_category=ce_template.category,
        info_fields=[
            {"id": str(o.id), "label": o.label, "field_type": o.field_type, "required": o.required, "order": o.order}
            for o in ce_info_objs
        ],
        sections=[
            {
                "id": str(ce_sec1.id),
                "name": ce_sec1.name,
                "order": ce_sec1.order,
                "fields": [
                    {"id": str(f.id), "label": f.label, "field_type": f.field_type, "options": f.options, "order": f.order}
                    for f in ce_sec1_fields
                ],
            },
            {
                "id": str(ce_sec2.id),
                "name": ce_sec2.name,
                "order": ce_sec2.order,
                "fields": [
                    {"id": str(f.id), "label": f.label, "field_type": f.field_type, "options": f.options, "order": f.order}
                    for f in ce_sec2_fields
                ],
            },
        ],
        signature_fields=[
            {"id": str(o.id), "role_name": o.role_name, "required": o.required, "order": o.order}
            for o in ce_sig_objs
        ],
    )

    result["CE-001"] = {
        "template": ce_template,
        "info_fields": ce_info_objs,
        "sections": [
            {"section": ce_sec1, "fields": ce_sec1_fields},
            {"section": ce_sec2, "fields": ce_sec2_fields},
        ],
        "signature_fields": ce_sig_objs,
        "snapshot": ce_snapshot,
    }

    # ------------------------------------------------------------------
    # ALPHA: Inspecao Mecanica (IM-001)
    # ------------------------------------------------------------------
    im_template = Template(
        id=uuid.uuid4(),
        tenant_id=alpha_id,
        name="Inspecao Mecanica",
        code="IM-001",
        category="Inspection",
        version=1,
        title="Relatorio de Inspecao Mecanica",
        is_active=True,
    )
    session.add(im_template)

    im_info_fields_data = [
        {"label": "Equipamento", "field_type": "text", "required": True, "order": 1},
        {"label": "Tag", "field_type": "text", "required": False, "order": 2},
        {"label": "Data", "field_type": "date", "required": True, "order": 3},
    ]
    im_info_objs: list[TemplateInfoField] = []
    for ifd in im_info_fields_data:
        obj = TemplateInfoField(
            id=uuid.uuid4(),
            template_id=im_template.id,
            label=ifd["label"],
            field_type=ifd["field_type"],
            required=ifd["required"],
            order=ifd["order"],
        )
        session.add(obj)
        im_info_objs.append(obj)

    im_sec1 = TemplateSection(
        id=uuid.uuid4(),
        template_id=im_template.id,
        name="Condicao Geral",
        order=1,
    )
    session.add(im_sec1)
    im_sec1_labels = [
        "Estrutura sem deformacao",
        "Pintura em bom estado",
        "Fixacao adequada",
        "Vibracoes dentro do aceitavel",
    ]
    im_sec1_fields = _make_dropdown_fields(im_sec1.id, im_sec1_labels, SIM_NAO_NA)
    session.add_all(im_sec1_fields)

    im_sig_data = [
        {"role_name": "Inspetor", "required": True, "order": 1},
    ]
    im_sig_objs: list[TemplateSignatureField] = []
    for sd in im_sig_data:
        obj = TemplateSignatureField(
            id=uuid.uuid4(),
            template_id=im_template.id,
            role_name=sd["role_name"],
            required=sd["required"],
            order=sd["order"],
        )
        session.add(obj)
        im_sig_objs.append(obj)

    im_snapshot = build_template_snapshot(
        template_name=im_template.name,
        template_code=im_template.code,
        template_category=im_template.category,
        info_fields=[
            {"id": str(o.id), "label": o.label, "field_type": o.field_type, "required": o.required, "order": o.order}
            for o in im_info_objs
        ],
        sections=[
            {
                "id": str(im_sec1.id),
                "name": im_sec1.name,
                "order": im_sec1.order,
                "fields": [
                    {"id": str(f.id), "label": f.label, "field_type": f.field_type, "options": f.options, "order": f.order}
                    for f in im_sec1_fields
                ],
            },
        ],
        signature_fields=[
            {"id": str(o.id), "role_name": o.role_name, "required": o.required, "order": o.order}
            for o in im_sig_objs
        ],
    )

    result["IM-001"] = {
        "template": im_template,
        "info_fields": im_info_objs,
        "sections": [{"section": im_sec1, "fields": im_sec1_fields}],
        "signature_fields": im_sig_objs,
        "snapshot": im_snapshot,
    }

    # ------------------------------------------------------------------
    # BETA: Laudo Termografico (LT-001)
    # ------------------------------------------------------------------
    lt_template = Template(
        id=uuid.uuid4(),
        tenant_id=beta_id,
        name="Laudo Termografico",
        code="LT-001",
        category="Thermography",
        version=1,
        title="Laudo de Inspecao Termografica",
        is_active=True,
    )
    session.add(lt_template)

    lt_info_fields_data = [
        {"label": "Cliente", "field_type": "text", "required": True, "order": 1},
        {"label": "Subestacao", "field_type": "text", "required": True, "order": 2},
        {"label": "Data", "field_type": "date", "required": True, "order": 3},
        {"label": "Condicao Climatica", "field_type": "text", "required": False, "order": 4},
    ]
    lt_info_objs: list[TemplateInfoField] = []
    for ifd in lt_info_fields_data:
        obj = TemplateInfoField(
            id=uuid.uuid4(),
            template_id=lt_template.id,
            label=ifd["label"],
            field_type=ifd["field_type"],
            required=ifd["required"],
            order=ifd["order"],
        )
        session.add(obj)
        lt_info_objs.append(obj)

    lt_sec1 = TemplateSection(
        id=uuid.uuid4(),
        template_id=lt_template.id,
        name="Paineis Eletricos",
        order=1,
    )
    session.add(lt_sec1)
    lt_sec1_labels = [
        "Conexoes sem aquecimento anormal",
        "Barramentos em condicao normal",
        "Disjuntores sem anomalia termica",
        "Cabos sem sobreaquecimento",
    ]
    lt_sec1_fields = _make_dropdown_fields(lt_sec1.id, lt_sec1_labels, SIM_NAO_NA)
    session.add_all(lt_sec1_fields)

    lt_sig_data = [
        {"role_name": "Termografista", "required": True, "order": 1},
        {"role_name": "Supervisor Tecnico", "required": False, "order": 2},
    ]
    lt_sig_objs: list[TemplateSignatureField] = []
    for sd in lt_sig_data:
        obj = TemplateSignatureField(
            id=uuid.uuid4(),
            template_id=lt_template.id,
            role_name=sd["role_name"],
            required=sd["required"],
            order=sd["order"],
        )
        session.add(obj)
        lt_sig_objs.append(obj)

    lt_snapshot = build_template_snapshot(
        template_name=lt_template.name,
        template_code=lt_template.code,
        template_category=lt_template.category,
        info_fields=[
            {"id": str(o.id), "label": o.label, "field_type": o.field_type, "required": o.required, "order": o.order}
            for o in lt_info_objs
        ],
        sections=[
            {
                "id": str(lt_sec1.id),
                "name": lt_sec1.name,
                "order": lt_sec1.order,
                "fields": [
                    {"id": str(f.id), "label": f.label, "field_type": f.field_type, "options": f.options, "order": f.order}
                    for f in lt_sec1_fields
                ],
            },
        ],
        signature_fields=[
            {"id": str(o.id), "role_name": o.role_name, "required": o.required, "order": o.order}
            for o in lt_sig_objs
        ],
    )

    result["LT-001"] = {
        "template": lt_template,
        "info_fields": lt_info_objs,
        "sections": [{"section": lt_sec1, "fields": lt_sec1_fields}],
        "signature_fields": lt_sig_objs,
        "snapshot": lt_snapshot,
    }

    # ------------------------------------------------------------------
    # BETA: Analise de Vibracoes (AV-001)
    # ------------------------------------------------------------------
    av_template = Template(
        id=uuid.uuid4(),
        tenant_id=beta_id,
        name="Analise de Vibracoes",
        code="AV-001",
        category="Vibration",
        version=1,
        title="Relatorio de Analise de Vibracoes",
        is_active=True,
    )
    session.add(av_template)

    av_info_fields_data = [
        {"label": "Equipamento", "field_type": "text", "required": True, "order": 1},
        {"label": "Ponto de Medicao", "field_type": "text", "required": True, "order": 2},
        {"label": "Data", "field_type": "date", "required": True, "order": 3},
    ]
    av_info_objs: list[TemplateInfoField] = []
    for ifd in av_info_fields_data:
        obj = TemplateInfoField(
            id=uuid.uuid4(),
            template_id=av_template.id,
            label=ifd["label"],
            field_type=ifd["field_type"],
            required=ifd["required"],
            order=ifd["order"],
        )
        session.add(obj)
        av_info_objs.append(obj)

    av_sec1 = TemplateSection(
        id=uuid.uuid4(),
        template_id=av_template.id,
        name="Medicoes",
        order=1,
    )
    session.add(av_sec1)
    av_sec1_labels = [
        "Nivel de vibracao global",
        "Frequencia dominante aceitavel",
        "Balanceamento adequado",
    ]
    av_sec1_fields = _make_dropdown_fields(av_sec1.id, av_sec1_labels, OK_ALERTA_CRITICO)
    session.add_all(av_sec1_fields)

    av_sig_data = [
        {"role_name": "Analista de Vibracoes", "required": True, "order": 1},
    ]
    av_sig_objs: list[TemplateSignatureField] = []
    for sd in av_sig_data:
        obj = TemplateSignatureField(
            id=uuid.uuid4(),
            template_id=av_template.id,
            role_name=sd["role_name"],
            required=sd["required"],
            order=sd["order"],
        )
        session.add(obj)
        av_sig_objs.append(obj)

    av_snapshot = build_template_snapshot(
        template_name=av_template.name,
        template_code=av_template.code,
        template_category=av_template.category,
        info_fields=[
            {"id": str(o.id), "label": o.label, "field_type": o.field_type, "required": o.required, "order": o.order}
            for o in av_info_objs
        ],
        sections=[
            {
                "id": str(av_sec1.id),
                "name": av_sec1.name,
                "order": av_sec1.order,
                "fields": [
                    {"id": str(f.id), "label": f.label, "field_type": f.field_type, "options": f.options, "order": f.order}
                    for f in av_sec1_fields
                ],
            },
        ],
        signature_fields=[
            {"id": str(o.id), "role_name": o.role_name, "required": o.required, "order": o.order}
            for o in av_sig_objs
        ],
    )

    result["AV-001"] = {
        "template": av_template,
        "info_fields": av_info_objs,
        "sections": [{"section": av_sec1, "fields": av_sec1_fields}],
        "signature_fields": av_sig_objs,
        "snapshot": av_snapshot,
    }

    await session.flush()
    print(f"  Created 4 templates: {', '.join(result.keys())}")
    return result


# ---------------------------------------------------------------------------
# Seed: Projects
# ---------------------------------------------------------------------------
async def seed_projects(
    session: AsyncSession, tenants: dict[str, Tenant]
) -> dict[str, Project]:
    """Create one project per tenant, keyed by tenant slug."""
    print("Seeding projects...")

    alpha_id = tenants["alpha-engenharia"].id
    beta_id = tenants["beta-servicos"].id

    alpha_project = Project(
        id=uuid.uuid4(),
        tenant_id=alpha_id,
        name="Projeto Industria ABC",
        client_name="Industria ABC Ltda",
        description="Commissioning da nova planta industrial",
        is_active=True,
    )
    beta_project = Project(
        id=uuid.uuid4(),
        tenant_id=beta_id,
        name="Contrato Energia XYZ",
        client_name="Energia XYZ S.A.",
        description="Manutencao preditiva trimestral",
        is_active=True,
    )
    session.add_all([alpha_project, beta_project])
    await session.flush()

    projects = {
        "alpha-engenharia": alpha_project,
        "beta-servicos": beta_project,
    }
    print(f"  Created {len(projects)} projects")
    for slug, p in projects.items():
        print(f"    [{slug}] {p.name} (client: {p.client_name})")
    return projects


# ---------------------------------------------------------------------------
# Seed: Reports  (with info values and checklist responses)
# ---------------------------------------------------------------------------
def _create_checklist_responses(
    report_id: uuid.UUID,
    template_data: dict[str, Any],
    *,
    fill: str = "none",
) -> list[ReportChecklistResponse]:
    """Generate ReportChecklistResponse rows from template data.

    Args:
        fill: "none" - no responses, "partial" - half filled, "all" - all filled.
    """
    responses: list[ReportChecklistResponse] = []
    total_fields = 0
    for sec_data in template_data["sections"]:
        sec = sec_data["section"]
        for field in sec_data["fields"]:
            total_fields += 1
            value = None
            if fill == "all":
                opts = json.loads(field.options) if field.options else ["Sim"]
                value = opts[0]  # Pick the first option (positive answer)
            elif fill == "partial" and total_fields % 2 == 0:
                opts = json.loads(field.options) if field.options else ["Sim"]
                value = opts[0]

            resp = ReportChecklistResponse(
                id=uuid.uuid4(),
                report_id=report_id,
                section_id=sec.id,
                field_id=field.id,
                section_name=sec.name,
                section_order=sec.order,
                field_label=field.label,
                field_order=field.order,
                field_type=field.field_type,
                field_options=field.options,
                response_value=value,
                comment=None,
                photos=[],
            )
            responses.append(resp)
    return responses


def _create_info_values(
    report_id: uuid.UUID,
    template_data: dict[str, Any],
    *,
    fill: bool = False,
    overrides: dict[str, str] | None = None,
) -> list[ReportInfoValue]:
    """Generate ReportInfoValue rows from template info fields."""
    overrides = overrides or {}
    values: list[ReportInfoValue] = []
    for info_obj in template_data["info_fields"]:
        val = overrides.get(info_obj.label)
        if val is None and fill:
            if info_obj.field_type == "date":
                val = "2025-02-01"
            else:
                val = f"Valor de {info_obj.label}"
        riv = ReportInfoValue(
            id=uuid.uuid4(),
            report_id=report_id,
            info_field_id=info_obj.id,
            field_label=info_obj.label,
            field_type=info_obj.field_type,
            value=val,
        )
        values.append(riv)
    return values


async def seed_reports(
    session: AsyncSession,
    tenants: dict[str, Tenant],
    templates: dict[str, dict[str, Any]],
    projects: dict[str, Project],
    users: dict[str, User],
) -> dict[str, Report]:
    """Create reports in various statuses and return them keyed by a label."""
    print("Seeding reports...")

    alpha_id = tenants["alpha-engenharia"].id
    beta_id = tenants["beta-servicos"].id
    alpha_project_id = projects["alpha-engenharia"].id
    beta_project_id = projects["beta-servicos"].id
    alpha_tech = users["tecnico1@alphaeng.com.br"]
    beta_tech = users["tecnico1@betaservicos.com.br"]

    now = datetime.now(timezone.utc)
    reports: dict[str, Report] = {}

    # ------------------------------------------------------------------
    # Alpha Report 1: Draft (CE-001)
    # ------------------------------------------------------------------
    ce_data = templates["CE-001"]
    r1 = Report(
        id=uuid.uuid4(),
        tenant_id=alpha_id,
        title="Commissioning Eletrico - Galpao A",
        status="draft",
        template_id=ce_data["template"].id,
        project_id=alpha_project_id,
        user_id=alpha_tech.id,
        template_snapshot=ce_data["snapshot"],
        location="-23.5505,-46.6333",
        started_at=None,
        completed_at=None,
    )
    session.add(r1)
    # Info values -- not filled for draft
    r1_info = _create_info_values(r1.id, ce_data, fill=False)
    session.add_all(r1_info)
    # Checklist responses -- empty for draft
    r1_responses = _create_checklist_responses(r1.id, ce_data, fill="none")
    session.add_all(r1_responses)
    reports["alpha-draft-ce"] = r1

    # ------------------------------------------------------------------
    # Alpha Report 2: In-progress (IM-001), partial responses
    # ------------------------------------------------------------------
    im_data = templates["IM-001"]
    r2 = Report(
        id=uuid.uuid4(),
        tenant_id=alpha_id,
        title="Inspecao Mecanica - Bomba P-101",
        status="in_progress",
        template_id=im_data["template"].id,
        project_id=alpha_project_id,
        user_id=alpha_tech.id,
        template_snapshot=im_data["snapshot"],
        location="-23.5489,-46.6388",
        started_at=now,
        completed_at=None,
    )
    session.add(r2)
    r2_info = _create_info_values(
        r2.id,
        im_data,
        fill=True,
        overrides={
            "Equipamento": "Bomba Centrifuga P-101",
            "Tag": "P-101",
            "Data": "2025-02-05",
        },
    )
    session.add_all(r2_info)
    r2_responses = _create_checklist_responses(r2.id, im_data, fill="partial")
    session.add_all(r2_responses)
    reports["alpha-inprogress-im"] = r2

    # ------------------------------------------------------------------
    # Alpha Report 3: Completed (CE-001), all filled
    # ------------------------------------------------------------------
    r3 = Report(
        id=uuid.uuid4(),
        tenant_id=alpha_id,
        title="Commissioning Eletrico - Subestacao B",
        status="completed",
        template_id=ce_data["template"].id,
        project_id=alpha_project_id,
        user_id=alpha_tech.id,
        template_snapshot=ce_data["snapshot"],
        location="-23.5510,-46.6340",
        started_at=now,
        completed_at=now,
    )
    session.add(r3)
    r3_info = _create_info_values(
        r3.id,
        ce_data,
        fill=True,
        overrides={
            "Local da Obra": "Subestacao B - Industria ABC",
            "Data da Inspecao": "2025-02-01",
            "Responsavel": "Alpha Tecnico 1",
        },
    )
    session.add_all(r3_info)
    r3_responses = _create_checklist_responses(r3.id, ce_data, fill="all")
    session.add_all(r3_responses)

    # Add signature for completed report
    r3_sig = ReportSignature(
        id=uuid.uuid4(),
        report_id=r3.id,
        signature_field_id=ce_data["signature_fields"][0].id,
        role_name="Tecnico Responsavel",
        signer_name="Alpha Tecnico 1",
        file_key=f"signatures/{r3.id}/tecnico.png",
        signed_at=now,
    )
    session.add(r3_sig)
    reports["alpha-completed-ce"] = r3

    # ------------------------------------------------------------------
    # Beta Report 1: Draft (LT-001)
    # ------------------------------------------------------------------
    lt_data = templates["LT-001"]
    r4 = Report(
        id=uuid.uuid4(),
        tenant_id=beta_id,
        title="Laudo Termografico - SE Principal",
        status="draft",
        template_id=lt_data["template"].id,
        project_id=beta_project_id,
        user_id=beta_tech.id,
        template_snapshot=lt_data["snapshot"],
        location="-23.5615,-46.6560",
        started_at=None,
        completed_at=None,
    )
    session.add(r4)
    r4_info = _create_info_values(r4.id, lt_data, fill=False)
    session.add_all(r4_info)
    r4_responses = _create_checklist_responses(r4.id, lt_data, fill="none")
    session.add_all(r4_responses)
    reports["beta-draft-lt"] = r4

    # ------------------------------------------------------------------
    # Beta Report 2: Completed (AV-001), all filled
    # ------------------------------------------------------------------
    av_data = templates["AV-001"]
    r5 = Report(
        id=uuid.uuid4(),
        tenant_id=beta_id,
        title="Analise de Vibracoes - Motor M-201",
        status="completed",
        template_id=av_data["template"].id,
        project_id=beta_project_id,
        user_id=beta_tech.id,
        template_snapshot=av_data["snapshot"],
        location="-23.5620,-46.6570",
        started_at=now,
        completed_at=now,
    )
    session.add(r5)
    r5_info = _create_info_values(
        r5.id,
        av_data,
        fill=True,
        overrides={
            "Equipamento": "Motor Eletrico M-201",
            "Ponto de Medicao": "Mancal LA - Horizontal",
            "Data": "2025-02-03",
        },
    )
    session.add_all(r5_info)
    r5_responses = _create_checklist_responses(r5.id, av_data, fill="all")
    session.add_all(r5_responses)

    r5_sig = ReportSignature(
        id=uuid.uuid4(),
        report_id=r5.id,
        signature_field_id=av_data["signature_fields"][0].id,
        role_name="Analista de Vibracoes",
        signer_name="Beta Tecnico 1",
        file_key=f"signatures/{r5.id}/analista.png",
        signed_at=now,
    )
    session.add(r5_sig)
    reports["beta-completed-av"] = r5

    await session.flush()
    print(f"  Created {len(reports)} reports:")
    for label, r in reports.items():
        print(f"    [{label}] {r.title}  status={r.status}")
    return reports


# ---------------------------------------------------------------------------
# Seed: Calibration Certificates
# ---------------------------------------------------------------------------
async def seed_certificates(
    session: AsyncSession, tenants: dict[str, Tenant]
) -> dict[str, CalibrationCertificate]:
    """Create calibration certificates and return them keyed by certificate_number."""
    print("Seeding calibration certificates...")

    alpha_id = tenants["alpha-engenharia"].id
    beta_id = tenants["beta-servicos"].id

    certs_data: list[dict[str, Any]] = [
        # Alpha certificates
        {
            "tenant_id": alpha_id,
            "equipment_name": "Multimetro Digital",
            "certificate_number": "CAL-2024-001",
            "manufacturer": "Fluke",
            "model": "87V",
            "serial_number": "SN-12345678",
            "laboratory": "Lab ABC Calibracoes",
            "calibration_date": date(2024, 6, 15),
            "expiry_date": date(2025, 6, 15),
            "status": "valid",
        },
        {
            "tenant_id": alpha_id,
            "equipment_name": "Megometro",
            "certificate_number": "CAL-2024-002",
            "manufacturer": "Megabras",
            "model": "MI-2552",
            "serial_number": "SN-87654321",
            "laboratory": "Instituto de Metrologia",
            "calibration_date": date(2024, 8, 20),
            "expiry_date": date(2025, 8, 20),
            "status": "valid",
        },
        {
            "tenant_id": alpha_id,
            "equipment_name": "Terrometro",
            "certificate_number": "CAL-2024-003",
            "manufacturer": "Minipa",
            "model": "MTR-1522",
            "serial_number": "SN-11223344",
            "laboratory": "Calibra Brasil",
            "calibration_date": date(2024, 3, 10),
            "expiry_date": date(2025, 3, 10),
            "status": "expiring",
        },
        {
            "tenant_id": alpha_id,
            "equipment_name": "Alicate Amperimetro",
            "certificate_number": "CAL-2023-045",
            "manufacturer": "Fluke",
            "model": "376 FC",
            "serial_number": "SN-99887766",
            "laboratory": "MetroCal",
            "calibration_date": date(2023, 12, 15),
            "expiry_date": date(2024, 12, 15),
            "status": "expired",
        },
        # Beta certificates
        {
            "tenant_id": beta_id,
            "equipment_name": "Camera Termografica",
            "certificate_number": "CAL-2024-010",
            "manufacturer": "FLIR",
            "model": "T640",
            "serial_number": "SN-TH001122",
            "laboratory": "INMETRO Calibracoes",
            "calibration_date": date(2024, 10, 1),
            "expiry_date": date(2025, 10, 1),
            "status": "valid",
        },
        {
            "tenant_id": beta_id,
            "equipment_name": "Analisador de Vibracoes",
            "certificate_number": "CAL-2024-011",
            "manufacturer": "SKF",
            "model": "CMXA 75",
            "serial_number": "SN-VB334455",
            "laboratory": "Lab Vibracao",
            "calibration_date": date(2024, 9, 15),
            "expiry_date": date(2025, 9, 15),
            "status": "valid",
        },
        {
            "tenant_id": beta_id,
            "equipment_name": "Termometro Infravermelho",
            "certificate_number": "CAL-2024-012",
            "manufacturer": "Fluke",
            "model": "62 MAX+",
            "serial_number": "SN-IR556677",
            "laboratory": "Lab ABC Calibracoes",
            "calibration_date": date(2024, 4, 1),
            "expiry_date": date(2025, 4, 1),
            "status": "expiring",
        },
    ]

    certs: dict[str, CalibrationCertificate] = {}
    for cd in certs_data:
        cert = CalibrationCertificate(
            id=uuid.uuid4(),
            tenant_id=cd["tenant_id"],
            equipment_name=cd["equipment_name"],
            certificate_number=cd["certificate_number"],
            manufacturer=cd["manufacturer"],
            model=cd["model"],
            serial_number=cd["serial_number"],
            laboratory=cd["laboratory"],
            calibration_date=cd["calibration_date"],
            expiry_date=cd["expiry_date"],
            status=cd["status"],
            is_active=True,
        )
        session.add(cert)
        certs[cd["certificate_number"]] = cert

    await session.flush()
    print(f"  Created {len(certs)} calibration certificates:")
    for num, c in certs.items():
        print(f"    [{num}] {c.equipment_name} ({c.model}) - {c.status}")
    return certs


# ---------------------------------------------------------------------------
# Link: Certificates to completed reports
# ---------------------------------------------------------------------------
async def link_certificates(
    session: AsyncSession,
    reports: dict[str, Report],
    certificates: dict[str, CalibrationCertificate],
) -> int:
    """Link calibration certificates to completed reports.

    - Alpha completed CE report -> Multimetro Digital + Megometro
    - Beta completed AV report -> Analisador de Vibracoes
    """
    print("Linking certificates to completed reports...")

    links: list[tuple[str, str, str]] = [
        # (report_key, certificate_number, description)
        ("alpha-completed-ce", "CAL-2024-001", "Multimetro Digital"),
        ("alpha-completed-ce", "CAL-2024-002", "Megometro"),
        ("beta-completed-av", "CAL-2024-011", "Analisador de Vibracoes"),
    ]

    count = 0
    for report_key, cert_num, desc in links:
        report = reports.get(report_key)
        cert = certificates.get(cert_num)
        if report and cert:
            rc = ReportCertificate(
                id=uuid.uuid4(),
                report_id=report.id,
                certificate_id=cert.id,
            )
            session.add(rc)
            count += 1
            print(f"  Linked [{cert_num}] {desc} -> {report.title}")

    await session.flush()
    print(f"  Created {count} report-certificate links")
    return count


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
async def main() -> None:
    """Run the full seed process."""
    parser = argparse.ArgumentParser(
        description="Seed data for SmartHand multi-tenant report system"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete all existing data before seeding",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  SmartHand - Seed Data Script")
    print("=" * 60)
    print(f"  Database: {settings.database_url[:50]}...")
    print(f"  Clean mode: {args.clean}")
    print("=" * 60)

    async with SessionLocal() as session:
        try:
            # Clean if requested
            if args.clean:
                await clean_database(session)

            # Seed in dependency order
            tenants = await seed_tenants(session)
            users = await seed_users(session, tenants)
            templates = await seed_templates(session, tenants)
            projects = await seed_projects(session, tenants)
            reports = await seed_reports(session, tenants, templates, projects, users)
            certificates = await seed_certificates(session, tenants)
            link_count = await link_certificates(session, reports, certificates)

            # Commit everything
            await session.commit()

            # Print summary
            print("\n" + "=" * 60)
            print("  SEED COMPLETE - Summary")
            print("=" * 60)
            print(f"  Tenants:                  {len(tenants)}")
            print(f"  Users:                    {len(users)}")
            print(f"  Templates:                {len(templates)}")

            total_sections = sum(
                len(t["sections"]) for t in templates.values()
            )
            total_fields = sum(
                sum(len(s["fields"]) for s in t["sections"])
                for t in templates.values()
            )
            total_info_fields = sum(
                len(t["info_fields"]) for t in templates.values()
            )
            total_sig_fields = sum(
                len(t["signature_fields"]) for t in templates.values()
            )
            print(f"  Template Sections:        {total_sections}")
            print(f"  Template Fields:          {total_fields}")
            print(f"  Template Info Fields:     {total_info_fields}")
            print(f"  Template Signature Fields:{total_sig_fields}")
            print(f"  Projects:                 {len(projects)}")
            print(f"  Reports:                  {len(reports)}")
            print(f"  Calibration Certificates: {len(certificates)}")
            print(f"  Report-Certificate Links: {link_count}")
            print("=" * 60)

            # Print login credentials
            print("\n  Login Credentials:")
            print("  " + "-" * 56)
            print(f"  {'Email':40s} {'Password':15s} {'Role'}")
            print("  " + "-" * 56)
            credentials = [
                ("admin@smarthand.com", "Admin123!", "superadmin"),
                ("admin@alphaeng.com.br", "Alpha123!", "tenant_admin"),
                ("gerente@alphaeng.com.br", "Alpha123!", "project_manager"),
                ("tecnico1@alphaeng.com.br", "Alpha123!", "technician"),
                ("admin@betaservicos.com.br", "Beta123!", "tenant_admin"),
                ("tecnico1@betaservicos.com.br", "Beta123!", "technician"),
                ("viewer@betaservicos.com.br", "Beta123!", "viewer"),
            ]
            for email, pwd, role in credentials:
                print(f"  {email:40s} {pwd:15s} {role}")
            print("  " + "-" * 56)
            print()

        except Exception as exc:
            await session.rollback()
            print(f"\nERROR: Seed failed - {exc}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
