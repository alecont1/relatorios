---
phase: 05-template-configuration
plan: 03
subsystem: backend-api
tags: [api, fastapi, crud, signature-fields, field-config, jsonb]
requires:
  - 05-01-template-configuration-models
  - 05-02-info-fields-api
provides:
  - Signature field CRUD endpoints (create, list, update, delete, reorder)
  - Field config endpoints for photo/comment settings
  - JSONB mutation tracking pattern with flag_modified
affects:
  - 05-05-frontend-field-configuration
  - 06-report-core (will use signatures for report signing)
  - 07-photo-capture (will use photo_config for capture rules)
tech-stack:
  added: []
  patterns:
    - flag_modified for JSONB mutation tracking
    - Multi-level join for tenant isolation (Field -> Section -> Template)
    - Nested route structure /templates/{id}/signature-fields
key-files:
  created:
    - backend/app/schemas/template_signature_field.py
    - backend/app/schemas/template_field_config.py
    - backend/app/api/v1/routes/template_signature_fields.py
    - backend/app/api/v1/routes/template_field_config.py
  modified:
    - backend/app/main.py
decisions:
  - slug: flag-modified-jsonb
    choice: Use flag_modified for JSONB column updates
    rationale: SQLAlchemy doesn't detect in-place dict mutations; flag_modified ensures commit
    alternatives: Create new dict on each update (extra allocations, same effect)
  - slug: multi-join-tenant-check
    choice: Join Field -> Section -> Template to verify tenant ownership
    rationale: Fields don't have direct tenant_id, must traverse relationships
    alternatives: Add tenant_id to TemplateField (denormalization, extra migrations)
metrics:
  duration: 8min
  completed: 2026-02-02
---

# Phase 5 Plan 03: Signature Fields + Field Config API Summary

**One-liner:** Backend CRUD for signature fields plus photo/comment configuration endpoints with JSONB mutation tracking.

## What Was Built

### Signature Field Schemas (template_signature_field.py)

1. **SignatureFieldCreate** - Create validation
   - Required: role_name (1-100 chars)
   - Optional: required (default true)

2. **SignatureFieldUpdate** - Partial update
   - All fields optional for PATCH semantics

3. **SignatureFieldResponse** - API response
   - Includes id, template_id, role_name, required, order, timestamps

4. **SignatureFieldListResponse** - List wrapper
   - Contains signature_fields array and total count

5. **SignatureFieldReorder** - Reorder request
   - Requires non-empty list of UUIDs

### Field Config Schemas (template_field_config.py)

1. **PhotoConfig** - Photo settings for checklist fields
   - required: bool (default false)
   - min_count: int (0-20, default 0)
   - max_count: int (1-20, default 10)
   - require_gps: bool (default false)
   - watermark: bool (default true)
   - Model validator ensures min_count <= max_count

2. **CommentConfig** - Comment settings
   - enabled: bool (default true)
   - required: bool (default false)

3. **FieldConfigUpdate** - Update request
   - photo_config: PhotoConfig | None
   - comment_config: CommentConfig | None

4. **FieldConfigResponse** - Response schema
   - Includes field id, label, field_type, and config objects

### Signature Fields API (template_signature_fields.py)

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| POST | /templates/{id}/signature-fields | Create signature field | admin, superadmin |
| GET | /templates/{id}/signature-fields | List signature fields | all authenticated |
| PATCH | /templates/{id}/signature-fields/{fid} | Update signature field | admin, superadmin |
| DELETE | /templates/{id}/signature-fields/{fid} | Delete signature field | admin, superadmin |
| PUT | /templates/{id}/signature-fields/reorder | Reorder fields | admin, superadmin |

### Field Config API (template_field_config.py)

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| GET | /templates/fields/{id}/config | Get field config | all authenticated |
| PATCH | /templates/fields/{id}/config | Update field config | admin, superadmin |

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create signature field schemas and router | d319d13 | template_signature_field.py, template_signature_fields.py |
| 2 | Create field config schemas and router | d319d13 | template_field_config.py, template_field_config.py, main.py |

## Technical Decisions

### 1. flag_modified for JSONB Updates

**Decision:** Use `flag_modified(field, 'column_name')` when updating JSONB columns.

**Rationale:**
- SQLAlchemy doesn't detect in-place dictionary mutations
- Without flag_modified, changes to JSONB columns may not persist
- Explicit flagging ensures the column is marked dirty for commit

**Code Pattern:**
```python
from sqlalchemy.orm.attributes import flag_modified

field.photo_config = config_data.photo_config.model_dump()
flag_modified(field, 'photo_config')
```

### 2. Multi-Join Tenant Verification

**Decision:** Join TemplateField -> TemplateSection -> Template to check tenant ownership.

**Rationale:**
- TemplateField has no direct tenant_id (inherits via Section -> Template)
- Single query with joins is more efficient than multiple queries
- Consistent with existing tenant isolation pattern

**Query Pattern:**
```python
select(TemplateField)
    .join(TemplateSection, TemplateField.section_id == TemplateSection.id)
    .join(Template, TemplateSection.template_id == Template.id)
    .where(TemplateField.id == field_id)
    .where(Template.tenant_id == tenant_id)
```

## Verification Results

All success criteria met:

✅ SignatureFieldCreate/Update/Response schemas exist with proper validation
✅ POST/GET/PATCH/DELETE/PUT endpoints for signature fields work (5 routes)
✅ PhotoConfig schema enforces min_count <= max_count
✅ CommentConfig schema has enabled and required flags
✅ GET/PATCH /templates/fields/{id}/config works (2 routes)
✅ flag_modified used for JSONB mutation tracking
✅ All endpoints have tenant isolation via template ownership check
✅ Both routers registered in main.py

## Next Steps

**Immediate (Plan 05-04):**
- Create frontend template configuration UI
- Add accordion for template sections
- Add info fields configurator component

**Future Plans:**
- 05-05: Frontend field configuration UI (photo/comment settings)
- 05-06: Integration verification
- 06: Report Core (will use info_fields and signature_fields)

## Files Changed

### Created (4 files)

**backend/app/schemas/template_signature_field.py** (47 lines)
- SignatureFieldCreate with role_name validation
- SignatureFieldUpdate for partial updates
- SignatureFieldResponse with ORM compatibility
- SignatureFieldListResponse wrapper
- SignatureFieldReorder for reordering

**backend/app/schemas/template_field_config.py** (48 lines)
- PhotoConfig with min/max count validation
- CommentConfig with enabled/required flags
- FieldConfigUpdate for PATCH requests
- FieldConfigResponse with config objects

**backend/app/api/v1/routes/template_signature_fields.py** (236 lines)
- Router with /templates prefix
- verify_template_ownership helper
- 5 CRUD + reorder endpoints
- Auto-ordering for new fields

**backend/app/api/v1/routes/template_field_config.py** (112 lines)
- Router with /templates/fields prefix
- get_field_with_tenant_check helper with multi-join
- GET and PATCH endpoints
- flag_modified for JSONB updates

### Modified (1 file)

**backend/app/main.py**
- Added template_signature_fields_router import
- Added template_field_config_router import
- Added router inclusions with /api/v1 prefix

## API Usage Examples

### Create Signature Field
```bash
POST /api/v1/templates/{template_id}/signature-fields
{
  "role_name": "Tecnico Executor",
  "required": true
}
```

### Update Field Photo Config
```bash
PATCH /api/v1/templates/fields/{field_id}/config
{
  "photo_config": {
    "required": true,
    "min_count": 1,
    "max_count": 5,
    "require_gps": true,
    "watermark": true
  }
}
```

### Update Field Comment Config
```bash
PATCH /api/v1/templates/fields/{field_id}/config
{
  "comment_config": {
    "enabled": true,
    "required": false
  }
}
```

---

**Phase:** 5 - Template Configuration
**Plan:** 03
**Status:** ✅ Complete
**Duration:** 8 minutes
**Commit:** d319d13
