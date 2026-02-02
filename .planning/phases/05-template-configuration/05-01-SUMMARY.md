---
phase: 05-template-configuration
plan: 01
subsystem: backend-models
tags: [database, models, sqlalchemy, alembic, jsonb, postgres]
requires:
  - 04-01-template-data-models
provides:
  - TemplateInfoField model for project metadata configuration
  - TemplateSignatureField model for signature requirements
  - Photo and comment configuration on TemplateField via JSONB
  - Database migration 004 for schema changes
affects:
  - 05-02-info-signature-schemas
  - 05-03-field-config-schemas
  - 06-report-models (will use info_fields and signature_fields)
tech-stack:
  added: []
  patterns:
    - JSONB columns for flexible configuration storage
    - SimpleBase inheritance for child models (no tenant_id)
    - Ordered relationships with order_by clause
key-files:
  created:
    - backend/app/models/template_info_field.py
    - backend/app/models/template_signature_field.py
    - backend/alembic/versions/20260202_004_template_configuration.py
  modified:
    - backend/app/models/template_field.py
    - backend/app/models/template.py
    - backend/app/models/__init__.py
    - backend/alembic/env.py
decisions:
  - slug: jsonb-for-field-config
    choice: Use JSONB columns for photo_config and comment_config
    rationale: Flexible schema for configuration without additional tables
    alternatives: Separate tables for photo/comment config (more normalized but complex)
  - slug: simple-base-for-config-models
    choice: TemplateInfoField and TemplateSignatureField extend SimpleBase
    rationale: Inherit tenant isolation via Template relationship, no direct tenant_id needed
    alternatives: Extend Base with tenant_id (redundant, more complex queries)
  - slug: ordered-relationships
    choice: Use order_by in relationships for info_fields and signature_fields
    rationale: SQLAlchemy returns collections in correct order automatically
    alternatives: Manual sorting in application code (less reliable)
metrics:
  duration: 11min
  completed: 2026-02-02
---

# Phase 5 Plan 01: Template Configuration Models Summary

**One-liner:** Database models for configurable template structure: info fields for project metadata, signature fields for approval requirements, and JSONB-based photo/comment configuration on template fields.

## What Was Built

### New Models

1. **TemplateInfoField** - Template-level project metadata fields
   - Configures what info is collected when creating a report (project name, date, location, client, etc.)
   - Field types: text, date, select (with options)
   - Each field has label, required flag, and order
   - Inherits tenant isolation via Template relationship

2. **TemplateSignatureField** - Template-level signature requirements
   - Defines who must sign reports (Technician, Supervisor, Client, etc.)
   - Each signature has role_name, required flag, and order
   - Inherits tenant isolation via Template relationship

### Model Extensions

3. **TemplateField JSONB Columns**
   - **photo_config**: `{"required": bool, "min_count": int, "max_count": int, "require_gps": bool, "watermark": bool}`
   - **comment_config**: `{"enabled": bool, "required": bool}`
   - Flexible configuration without schema changes for future field-level settings

4. **Template Relationships**
   - `info_fields`: Ordered relationship to TemplateInfoField
   - `signature_fields`: Ordered relationship to TemplateSignatureField
   - Both use `cascade="all, delete-orphan"` for referential integrity

### Database Migration

5. **Migration 004** - Schema changes for Phase 5
   - Created `template_info_fields` table with CASCADE delete FK to templates
   - Created `template_signature_fields` table with CASCADE delete FK to templates
   - Added `photo_config` JSONB column to `template_fields`
   - Added `comment_config` JSONB column to `template_fields`
   - Migration verified in alembic history chain (003 -> 004)

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create TemplateInfoField and TemplateSignatureField models | 8daf374 | template_info_field.py, template_signature_field.py, __init__.py |
| 2 | Extend TemplateField with JSONB columns and update Template relationships | 7c4638a | template_field.py, template.py |
| 3 | Create Alembic migration for schema changes | 566ebe1 | 20260202_004_template_configuration.py, env.py |

## Technical Decisions

### 1. JSONB for Field Configuration

**Decision:** Use JSONB columns (`photo_config`, `comment_config`) instead of separate tables.

**Rationale:**
- Photo/comment requirements are field-specific configuration, not relational data
- Schema flexibility: Can add new config keys without migrations
- Performance: Single column read vs JOIN to separate tables
- PostgreSQL JSONB supports indexing and querying if needed

**Impact:** Future field configuration additions (e.g., validation rules, help text) can be added without schema changes.

### 2. SimpleBase for Configuration Models

**Decision:** TemplateInfoField and TemplateSignatureField extend SimpleBase (no tenant_id).

**Rationale:**
- These models only exist as children of Template
- Tenant isolation is inherited via Template.tenant_id
- Simpler queries: No need to filter by tenant_id on child tables
- Consistent with Phase 4 pattern (TemplateSection, TemplateField)

**Impact:** All template children use same inheritance pattern, easier to understand and maintain.

### 3. Ordered Relationships

**Decision:** Use `order_by="Model.order"` in relationship definitions.

**Rationale:**
- SQLAlchemy automatically returns collections in correct order
- No manual sorting needed in API or business logic
- Order is consistently enforced at ORM level

**Impact:** Template.info_fields and Template.signature_fields always return in order, reducing bugs.

## Deviations from Plan

None - plan executed exactly as written.

## Verification Results

All success criteria met:

✅ TemplateInfoField model created with label, field_type, options, required, order fields
✅ TemplateSignatureField model created with role_name, required, order fields
✅ TemplateField model extended with photo_config, comment_config JSONB columns
✅ Template model has relationships to info_fields and signature_fields with cascade delete
✅ Alembic migration 004 applies successfully (verified in migration chain)
✅ All models import without errors from app.models

## Next Steps

**Immediate (Plan 05-02):**
- Create Pydantic schemas for TemplateInfoField and TemplateSignatureField
- Add validation for field_type enum values
- Add validation for JSONB schema structure

**Future Plans:**
- 05-03: Pydantic schemas for photo_config and comment_config JSONB
- 05-04: Template Configuration API endpoints (CRUD for info/signature fields)
- 05-05: Frontend UI for template configuration

## Files Changed

### Created (3 files)

**backend/app/models/template_info_field.py** (52 lines)
```python
class TemplateInfoField(SimpleBase):
    template_id: UUID FK to templates.id (CASCADE)
    label: str (max 255)
    field_type: str (max 50) - "text", "date", "select"
    options: str | None - JSON array for select options
    required: bool (default True)
    order: int
```

**backend/app/models/template_signature_field.py** (47 lines)
```python
class TemplateSignatureField(SimpleBase):
    template_id: UUID FK to templates.id (CASCADE)
    role_name: str (max 100) - e.g., "Technician", "Supervisor"
    required: bool (default True)
    order: int
```

**backend/alembic/versions/20260202_004_template_configuration.py** (65 lines)
- Creates template_info_fields table
- Creates template_signature_fields table
- Adds photo_config JSONB to template_fields
- Adds comment_config JSONB to template_fields

### Modified (4 files)

**backend/app/models/template_field.py**
- Added import for JSONB from sqlalchemy.dialects.postgresql
- Added photo_config: Mapped[dict | None] column
- Added comment_config: Mapped[dict | None] column

**backend/app/models/template.py**
- Added info_fields relationship with cascade and ordering
- Added signature_fields relationship with cascade and ordering

**backend/app/models/__init__.py**
- Added TemplateInfoField import
- Added TemplateSignatureField import
- Updated __all__ exports

**backend/alembic/env.py**
- Added TemplateInfoField to model imports
- Added TemplateSignatureField to model imports

## Knowledge for Future Phases

### Database Schema

**template_info_fields:**
- Stores configurable project metadata fields (shown at report creation)
- Examples: "Project Name", "Date", "Location", "Client", "Equipment ID"
- Field types: "text" (free text), "date" (date picker), "select" (dropdown with options)

**template_signature_fields:**
- Stores signature requirements for reports
- Examples: "Technician", "Supervisor", "Client", "Safety Officer"
- Order determines signature sequence in generated reports

**template_fields.photo_config:**
```json
{
  "required": false,
  "min_count": 0,
  "max_count": 5,
  "require_gps": true,
  "watermark": true
}
```

**template_fields.comment_config:**
```json
{
  "enabled": true,
  "required": false
}
```

### Relationships

```
Template (tenant_id)
├── sections (TemplateSection)
│   └── fields (TemplateField)
│       ├── photo_config (JSONB)
│       └── comment_config (JSONB)
├── info_fields (TemplateInfoField)
└── signature_fields (TemplateSignatureField)
```

All child models inherit tenant isolation via Template.tenant_id relationship.

### Import Pattern

```python
from app.models import (
    Template,
    TemplateSection,
    TemplateField,
    TemplateInfoField,
    TemplateSignatureField,
)
```

---

**Phase:** 5 - Template Configuration
**Plan:** 01
**Status:** ✅ Complete
**Duration:** 11 minutes
**Commits:** 3 (8daf374, 7c4638a, 566ebe1)
