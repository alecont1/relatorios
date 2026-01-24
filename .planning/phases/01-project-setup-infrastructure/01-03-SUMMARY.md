---
phase: 01-setup-infrastructure
plan: 03
subsystem: database
tags: [alembic, sqlalchemy, postgresql, postgis, migrations, async]

# Dependency graph
requires:
  - phase: 01-02
    provides: Backend scaffold with config and database setup
provides:
  - Alembic migrations configured for async SQLAlchemy
  - Complete database schema with 6 core tables
  - PostGIS extension enabled
  - SQLAlchemy models with proper relationships
affects: [02-authentication, 03-multi-tenant, 04-template-management, 06-report-core, 07-photo-capture]

# Tech tracking
tech-stack:
  added: [alembic]
  patterns: [async-migrations, multi-tenant-base-model, conditional-columns-with-declared-attr]

key-files:
  created:
    - backend/alembic.ini
    - backend/alembic/env.py
    - backend/alembic/versions/20260124_001_initial_schema.py
    - backend/app/models/tenant.py
    - backend/app/models/user.py
    - backend/app/models/template.py
    - backend/app/models/project.py
    - backend/app/models/report.py
    - backend/app/models/report_photo.py
  modified:
    - backend/app/models/__init__.py
    - backend/app/models/base.py

key-decisions:
  - "Use declared_attr to conditionally exclude tenant_id from Tenant model"
  - "Use Text columns for location in Phase 1 (PostGIS geometry columns deferred)"
  - "Manual migration creation to ensure PostGIS extension is created first"

patterns-established:
  - "Base model with conditional tenant_id using @declared_attr"
  - "Async Alembic configuration with async_engine_from_config and NullPool"
  - "Date-prefixed migration filenames for chronological sorting"

# Metrics
duration: 10min
completed: 2026-01-24
---

# Phase 1 Plan 3: Database Schema & Migrations Summary

**Alembic configured for async SQLAlchemy with PostGIS extension and 6 core tables ready for migration**

## Performance

- **Duration:** 10 min
- **Started:** 2026-01-24T15:39:13Z
- **Completed:** 2026-01-24T15:49:10Z
- **Tasks:** 2
- **Files modified:** 12

## Accomplishments
- Alembic initialized and configured for async SQLAlchemy 2.0
- All 6 SQLAlchemy models defined with proper columns, indexes, and foreign keys
- Initial migration creates PostGIS extension before tables
- Multi-tenant architecture with conditional tenant_id column
- Text-based location fields for Phase 1 (PostGIS geometry deferred)

## Task Commits

Each task was committed atomically:

1. **Task 1: Configure Alembic for async SQLAlchemy** - `4b243fb` (chore)
2. **Task 2: Define SQLAlchemy models and create initial migration** - `36cf950` (feat)

## Files Created/Modified

### Created
- `backend/alembic.ini` - Alembic configuration with date-prefixed migration template
- `backend/alembic/env.py` - Async migration environment with model imports
- `backend/alembic/versions/20260124_001_initial_schema.py` - Initial migration with PostGIS + 6 tables
- `backend/app/models/tenant.py` - Tenant model (no tenant_id)
- `backend/app/models/user.py` - User model with email, password_hash, role
- `backend/app/models/template.py` - Template model with schema_json
- `backend/app/models/project.py` - Project model with client_name
- `backend/app/models/report.py` - Report model with status, data_json, location
- `backend/app/models/report_photo.py` - ReportPhoto model with file metadata

### Modified
- `backend/app/models/__init__.py` - Import and export all models
- `backend/app/models/base.py` - Added @declared_attr for conditional tenant_id

## Decisions Made

**1. Use declared_attr to conditionally exclude tenant_id from Tenant model**
- **Rationale:** Tenant is the root entity and doesn't belong to itself. Using @declared_attr allows Base to conditionally add tenant_id to all models except Tenant.
- **Impact:** Clean inheritance model, no need for separate base classes.

**2. Use Text columns for location in Phase 1 instead of PostGIS geometry**
- **Rationale:** Simplifies Phase 1 implementation - store lat,lon as text. PostGIS geometry columns can be added in future phase with migration.
- **Impact:** Faster Phase 1 delivery, migration path preserved for Phase 2+.

**3. Manual migration creation instead of autogenerate**
- **Rationale:** Need to ensure `CREATE EXTENSION postgis` runs before any geometry columns (even though we're not using them yet). Manual control over migration order.
- **Impact:** Initial migration is explicit and well-documented.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Database schema ready for migration execution
- All models properly configured for async SQLAlchemy
- Autogenerate will work for future schema changes
- Ready for authentication system implementation (Phase 2)

**Blocker:** Need to set DATABASE_URL environment variable before running migrations.

---
*Phase: 01-setup-infrastructure*
*Completed: 2026-01-24*
