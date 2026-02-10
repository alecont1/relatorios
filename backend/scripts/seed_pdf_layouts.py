#!/usr/bin/env python3
"""
Seed default PDF layouts for the SmartHand system.

Creates three system layouts: Classico, Compacto, Fotografico.

Usage:
    python scripts/seed_pdf_layouts.py
"""

import asyncio
import sys
import uuid
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Windows event loop compatibility
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.models.pdf_layout import PdfLayout

engine = create_async_engine(settings.database_url, echo=False, future=True)
SessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

LAYOUTS = [
    {
        "name": "Classico",
        "slug": "classico",
        "description": "Layout padrao com tabelas claras e fotos em grade 2x3. Ideal para relatorios de inspecao geral.",
        "is_system": True,
        "is_active": True,
        "config_json": {
            "cover_page": {"enabled": False},
            "fonts": {"base_size": 9, "header_size": 14, "section_size": 11},
            "margins": {"top": 10, "right": 10, "bottom": 20, "left": 10},
            "photos": {"columns": 2, "max_per_section": 6, "width_mm": 80, "height_mm": 60},
            "checklist": {"show_all_items": True, "highlight_non_conforming": True},
            "certificates": {"show_table": True},
            "signatures": {"columns": 3, "box_width_mm": 60, "box_height_mm": 30},
        },
    },
    {
        "name": "Compacto",
        "slug": "compacto",
        "description": "Layout condensado com fontes menores e margens reduzidas. Mais itens por pagina.",
        "is_system": True,
        "is_active": True,
        "config_json": {
            "cover_page": {"enabled": False},
            "fonts": {"base_size": 8, "header_size": 12, "section_size": 10},
            "margins": {"top": 8, "right": 8, "bottom": 15, "left": 8},
            "photos": {"columns": 3, "max_per_section": 9, "width_mm": 55, "height_mm": 40},
            "checklist": {"show_all_items": True, "highlight_non_conforming": True},
            "certificates": {"show_table": True},
            "signatures": {"columns": 3, "box_width_mm": 55, "box_height_mm": 25},
        },
    },
    {
        "name": "Fotografico",
        "slug": "fotografico",
        "description": "Layout com fotos grandes em coluna unica. Ideal para relatorios visuais e documentacao detalhada.",
        "is_system": True,
        "is_active": True,
        "config_json": {
            "cover_page": {"enabled": True},
            "fonts": {"base_size": 9, "header_size": 14, "section_size": 11},
            "margins": {"top": 10, "right": 10, "bottom": 20, "left": 10},
            "photos": {"columns": 1, "max_per_section": 20, "width_mm": 170, "height_mm": 120},
            "checklist": {"show_all_items": True, "highlight_non_conforming": True},
            "certificates": {"show_table": True},
            "signatures": {"columns": 3, "box_width_mm": 60, "box_height_mm": 30},
        },
    },
    {
        "name": "Executivo",
        "slug": "executivo",
        "description": "Layout executivo com capa, resumo estatistico e foco em itens nao-conformes. Ideal para gestores.",
        "is_system": True,
        "is_active": True,
        "config_json": {
            "cover_page": {"enabled": True},
            "fonts": {"base_size": 9, "header_size": 14, "section_size": 11},
            "margins": {"top": 10, "right": 10, "bottom": 20, "left": 10},
            "photos": {"columns": 2, "max_per_section": 4, "width_mm": 80, "height_mm": 60},
            "checklist": {"show_all_items": False, "highlight_non_conforming": True},
            "certificates": {"show_table": True},
            "signatures": {"columns": 3, "box_width_mm": 60, "box_height_mm": 30},
        },
    },
    {
        "name": "Detalhado",
        "slug": "detalhado",
        "description": "Layout completo sem truncamentos, com comentarios expandidos e todas as fotos. Para documentacao tecnica.",
        "is_system": True,
        "is_active": True,
        "config_json": {
            "cover_page": {"enabled": False},
            "fonts": {"base_size": 9, "header_size": 14, "section_size": 11},
            "margins": {"top": 10, "right": 10, "bottom": 20, "left": 10},
            "photos": {"columns": 2, "max_per_section": 20, "width_mm": 80, "height_mm": 60},
            "checklist": {"show_all_items": True, "highlight_non_conforming": True},
            "certificates": {"show_table": True},
            "signatures": {"columns": 3, "box_width_mm": 60, "box_height_mm": 30},
        },
    },
]


async def main() -> None:
    """Seed default PDF layouts (skip existing by slug)."""
    print("=" * 50)
    print("  SmartHand - Seed PDF Layouts")
    print("=" * 50)

    async with SessionLocal() as session:
        created = 0
        skipped = 0

        for layout_data in LAYOUTS:
            # Check if layout with this slug already exists (system layouts have tenant_id=NULL)
            result = await session.execute(
                select(PdfLayout).where(
                    PdfLayout.slug == layout_data["slug"],
                    PdfLayout.tenant_id.is_(None),
                )
            )
            existing = result.scalar_one_or_none()
            if existing:
                print(f"  SKIP: '{layout_data['name']}' already exists (id={existing.id})")
                skipped += 1
                continue

            layout = PdfLayout(
                id=uuid.uuid4(),
                name=layout_data["name"],
                slug=layout_data["slug"],
                description=layout_data["description"],
                config_json=layout_data["config_json"],
                is_system=layout_data["is_system"],
                is_active=layout_data["is_active"],
            )
            session.add(layout)
            created += 1
            print(f"  CREATE: '{layout_data['name']}' ({layout_data['slug']})")

        await session.commit()

        print(f"\n  Created: {created}, Skipped: {skipped}")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
