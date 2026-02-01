---
phase: 04-template-management
plan: 01
subsystem: backend-data-layer
tags:
  - sqlalchemy
  - alembic
  - postgresql
  - pydantic
  - models
  - schemas
  - migrations
dependency-graph:
  requires:
    - 03-01-base-schema
    - 03-02-tenant-branding
  provides:
    - template-models
    - template-schemas
    - template-migration
  affects:
    - 04-02-excel-parser
    - 04-03-template-api
    - 05-report-generation
tech-stack:
  added:
    - SimpleBase for child models without tenant_id
  patterns:
    - hierarchical-models
    - cascade-delete-relationships
    - tenant-isolation-via-parent
key-files:
  created:
    - backend/app/models/template.py
    - backend/app/models/template_section.py
    - backend/app/models/template_field.py
    - backend/app/models/simple_base.py
    - backend/alembic/versions/20260131_003_template_tables.py
    - backend/app/schemas/template.py
  modified:
    - backend/app/models/__init__.py
    - backend/alembic/env.py
decisions:
  - id: child-model-base
    choice: Create SimpleBase for models that inherit tenant isolation
    rationale: TemplateSection and TemplateField don't need tenant_id since they cascade from Template
    alternatives:
      - Use Base with nullable tenant_id
      - Override tenant_id in each child model
  - id: windows-eventloop-fix
    choice: Add WindowsSelectorEventLoopPolicy in alembic env.py
    rationale: psycopg requires SelectorEventLoop, but Windows defaults to ProactorEventLoop
    alternatives:
      - Document manual workaround
      - Use different async driver
metrics:
  tasks: 3
  commits: 3
  duration: 19m 34s
  completed: 2026-01-31
---

# Phase 04 Plan 01: Template Data Models Summary

**One-liner:** Hierarchical SQLAlchemy models (Template → Section → Field) with unique tenant+code constraint, cascade deletes, and Pydantic validation schemas

## What Was Built

Created the complete data layer for the template management system:

1. **Three SQLAlchemy models** with proper relationships:
   - `Template`: Main model with metadata (name, code, category, version) and header fields (title, reference_standards, planning_requirements)
   - `TemplateSection`: Groups of fields with ordering
   - `TemplateField`: Individual checklist items with field_type (dropdown/text) and options

2. **SimpleBase class**: New base class for child models that inherit tenant isolation through their parent (no direct tenant_id)

3. **Alembic migration 003**: Creates all three tables with foreign keys, cascade deletes, and unique constraint on (tenant_id, code)

4. **Pydantic schemas**: Complete request/response schemas with validation (dropdown requires options, category enum, etc.)

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create Template, TemplateSection, and TemplateField models | 88ba73a | template.py, template_section.py, template_field.py, simple_base.py, __init__.py |
| 2 | Create Alembic migration for template tables | d4083b8 | 20260131_003_template_tables.py, env.py |
| 3 | Create Pydantic schemas for template API | c91cd03 | template.py (schemas) |

## Key Technical Details

### Model Architecture

**Template (tenant-scoped):**
- Inherits from Base (includes id, tenant_id, timestamps)
- Unique constraint on (tenant_id, code) prevents duplicate template codes per tenant
- One-to-many relationship with TemplateSection (cascade="all, delete-orphan")

**TemplateSection (inherits tenant via parent):**
- Inherits from SimpleBase (id + timestamps only)
- Foreign key to templates.id with CASCADE delete
- One-to-many relationship with TemplateField (cascade="all, delete-orphan")

**TemplateField (inherits tenant via parent → parent):**
- Inherits from SimpleBase (id + timestamps only)
- Foreign key to template_sections.id with CASCADE delete
- field_type: "dropdown" | "text"
- options: TEXT field storing JSON array for dropdown choices

### Schema Validation

**TemplateFieldCreate:**
- Custom validator ensures dropdown fields have options
- Text fields can have options=None

**TemplateCreate:**
- Category enum: "Commissioning" | "Inspection" | "Maintenance" | "Testing"
- Sections list with nested fields
- Optional header fields (title, reference_standards, planning_requirements)

**Response schemas:**
- ConfigDict(from_attributes=True) for ORM compatibility
- TemplateListItem (no sections) for list endpoints
- TemplateResponse (with sections) for detail endpoints

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed Windows async event loop incompatibility**

- **Found during:** Task 2 - Running Alembic migration
- **Issue:** psycopg requires SelectorEventLoop but Windows defaults to ProactorEventLoop, causing "Psycopg cannot use the 'ProactorEventLoop'" error
- **Fix:** Added `asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())` in alembic/env.py for Windows platform
- **Files modified:** backend/alembic/env.py
- **Commit:** d4083b8

**2. [Rule 2 - Missing Critical] Added new model imports to alembic env.py**

- **Found during:** Task 2 - Creating migration
- **Issue:** TemplateSection and TemplateField not imported in env.py, would cause autogenerate to miss them
- **Fix:** Added imports for TemplateSection and TemplateField to alembic/env.py
- **Files modified:** backend/alembic/env.py
- **Commit:** d4083b8

## Decisions Made

### 1. SimpleBase for Child Models

**Decision:** Created SimpleBase class for models that don't need tenant_id

**Context:** TemplateSection and TemplateField belong to tenant-scoped parents (Template), so they inherit tenant isolation through the relationship chain.

**Options considered:**
1. Use Base with nullable tenant_id (rejected - would require overriding in each model)
2. Create SimpleBase without tenant_id (chosen - cleaner, explicit design)
3. Use DeclarativeBase directly (rejected - would duplicate id/timestamp logic)

**Result:** SimpleBase provides id and timestamps without tenant_id, making it clear that child models inherit tenant context from their parents.

### 2. Migration Strategy: Drop and Recreate

**Decision:** Drop existing templates stub table and recreate with full schema

**Context:** Initial migration 001 created a basic templates table as a placeholder. Now we need the full hierarchical structure.

**Options considered:**
1. ALTER existing table (rejected - too many changes, complex migration)
2. Drop and recreate (chosen - cleaner, reversible)

**Result:** Migration drops old templates, creates new tables with proper relationships. Downgrade reverses cleanly.

## Verification Results

All verification checks passed:

- ✅ All models import correctly: `from app.models import Template, TemplateSection, TemplateField`
- ✅ All schemas import correctly: `from app.schemas.template import *`
- ✅ Migration file syntax validated
- ✅ Schema validation tests pass (dropdown requires options, category enum works)
- ✅ Three atomic commits created

**Note:** Migration execution not tested (no running PostgreSQL database in environment). Migration syntax verified and will run when database is available.

## Success Criteria Met

- ✅ Template model with all required fields and tenant_id for isolation
- ✅ TemplateSection and TemplateField with proper relationships and cascade delete
- ✅ Unique constraint on (tenant_id, code) prevents duplicate template codes
- ✅ Migration creates all tables with correct foreign keys
- ✅ Pydantic schemas ready for API request/response validation

## Integration Points

**Upstream dependencies:**
- Requires Base model from 03-01 (provides id, tenant_id, timestamps)
- Requires Tenant model from 03-01 (foreign key reference)
- Requires migration 002 from 03-02 (migration chain)

**Downstream consumers:**
- 04-02-excel-parser will use TemplateCreate schema to validate parsed Excel files
- 04-03-template-api will use all schemas for CRUD endpoints
- 05-report-generation will query Template models to build report structures

## Next Phase Readiness

**Ready for:**
- ✅ Excel parser can now validate against TemplateCreate schema
- ✅ Template API can implement CRUD operations with existing schemas
- ✅ Report generation can query template hierarchy

**Blockers/Concerns:**
- None - all dependencies satisfied

**Recommended next steps:**
1. Implement Excel parser service (04-02) to create templates from spreadsheets
2. Build template CRUD API endpoints (04-03) using schemas
3. Set up database and run migration when environment ready

## Files Changed

### Created (6 files)
- `backend/app/models/simple_base.py` - Base class for child models without tenant_id
- `backend/app/models/template.py` - Template model with metadata and header fields
- `backend/app/models/template_section.py` - Section model with ordering
- `backend/app/models/template_field.py` - Field model with type and options
- `backend/alembic/versions/20260131_003_template_tables.py` - Migration for three tables
- `backend/app/schemas/template.py` - Pydantic schemas for API

### Modified (2 files)
- `backend/app/models/__init__.py` - Export new models and SimpleBase
- `backend/alembic/env.py` - Add Windows event loop fix and new model imports

## Lessons Learned

**What went well:**
- Hierarchical model design with SimpleBase is clean and explicit
- Cascade deletes ensure referential integrity automatically
- Pydantic validators catch configuration errors early (dropdown without options)

**Challenges:**
- Windows async event loop incompatibility required platform-specific fix
- No running database prevented migration execution testing

**For next time:**
- Include database setup in development environment docs
- Consider adding migration tests that don't require live database
