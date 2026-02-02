---
phase: 05-template-configuration
plan: 02
subsystem: backend-api
tags: [api, fastapi, crud, info-fields]
requires:
  - 05-01-template-configuration-models
provides:
  - Info field CRUD endpoints (create, list, update, delete, reorder)
  - Pydantic schemas for info field validation
  - Tenant isolation via template ownership verification
affects:
  - 05-04-frontend-template-configuration
  - 06-report-core (will use info fields for report metadata)
tech-stack:
  added: []
  patterns:
    - Template ownership verification helper function
    - JSON string parsing for options in responses
    - Auto-increment order for new fields
key-files:
  created:
    - backend/app/schemas/template_info_field.py
    - backend/app/api/v1/routes/template_info_fields.py
  modified:
    - backend/app/main.py
decisions:
  - slug: nested-route-pattern
    choice: Use /templates/{id}/info-fields nested routes
    rationale: Clearly establishes parent-child relationship, consistent with REST best practices
    alternatives: Flat routes like /info-fields with query params (less intuitive)
  - slug: reorder-replace-all
    choice: Reorder endpoint replaces all orders based on provided array
    rationale: Simple, atomic operation - client provides complete desired order
    alternatives: Move-up/move-down endpoints (more network calls, race conditions)
metrics:
  duration: resumed
  completed: 2026-02-02
---

# Phase 5 Plan 02: Info Fields API Summary

**One-liner:** Backend CRUD endpoints for template info fields with auto-ordering, validation, and tenant isolation.

## What Was Built

### Pydantic Schemas (template_info_field.py)

1. **InfoFieldCreate** - Create validation
   - Required: label (1-255 chars), field_type ("text", "date", "select")
   - Optional: options (required if field_type="select"), required (default true)
   - Custom validator ensures options consistency with field_type

2. **InfoFieldUpdate** - Partial update validation
   - All fields optional for PATCH semantics
   - Same field_type constraints apply

3. **InfoFieldResponse** - API response schema
   - Includes all fields plus id, template_id, order, timestamps
   - Uses from_attributes for ORM compatibility

4. **InfoFieldListResponse** - List response wrapper
   - Contains info_fields array and total count

5. **InfoFieldReorder** - Reorder request validation
   - Requires non-empty list of UUIDs

### API Endpoints (template_info_fields.py)

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| POST | /templates/{id}/info-fields | Create info field | admin, superadmin |
| GET | /templates/{id}/info-fields | List info fields | all authenticated |
| PATCH | /templates/{id}/info-fields/{fid} | Update info field | admin, superadmin |
| DELETE | /templates/{id}/info-fields/{fid} | Delete info field | admin, superadmin |
| PUT | /templates/{id}/info-fields/reorder | Reorder fields | admin, superadmin |

### Key Implementation Details

- **Tenant Isolation**: `verify_template_ownership()` helper validates template belongs to user's tenant
- **Auto-ordering**: New fields get `max(order) + 1` automatically
- **JSON Parsing**: Options stored as JSON string, parsed to list in responses
- **Order Updates**: Reorder validates all IDs belong to template before updating

## Tasks Completed

| Task | Name | Files |
|------|------|-------|
| 1 | Create Pydantic schemas | template_info_field.py |
| 2 | Create CRUD endpoints | template_info_fields.py |
| 3 | Register router | main.py |

## Technical Decisions

### 1. Nested Route Pattern

**Decision:** Use `/templates/{template_id}/info-fields` nested structure.

**Rationale:**
- Clear parent-child relationship in URL
- Template ID validated before any field operation
- Consistent with REST resource hierarchy

### 2. Reorder as Replace-All

**Decision:** Reorder endpoint takes complete ordered list, replaces all order values.

**Rationale:**
- Single atomic operation vs multiple move-up/move-down calls
- Client maintains full control over final order
- No race conditions from concurrent order changes

## Verification Results

All success criteria met:

✅ InfoFieldCreate schema validates field_type (text, date, select) and options
✅ InfoFieldResponse includes all fields including order
✅ POST /templates/{id}/info-fields creates field with auto-incremented order
✅ GET /templates/{id}/info-fields returns ordered list
✅ PATCH /templates/{id}/info-fields/{id} updates field properties
✅ DELETE /templates/{id}/info-fields/{id} removes field
✅ PUT /templates/{id}/info-fields/reorder updates order values
✅ All endpoints enforce admin/superadmin role and tenant isolation
✅ Router registered in main.py (5 routes)
✅ Schemas and router import without errors

## Next Steps

**Immediate (Plan 05-03):**
- Create Pydantic schemas for signature fields
- Add CRUD endpoints for signature fields
- Add field config update endpoints (photo_config, comment_config)

**Future Plans:**
- 05-04: Frontend template configuration UI
- 05-05: Frontend field configuration UI
- 05-06: Integration verification

## Files Changed

### Created (2 files)

**backend/app/schemas/template_info_field.py** (60 lines)
- InfoFieldCreate with field_type validation
- InfoFieldUpdate for partial updates
- InfoFieldResponse with ORM compatibility
- InfoFieldListResponse wrapper
- InfoFieldReorder for reordering

**backend/app/api/v1/routes/template_info_fields.py** (311 lines)
- Router with /templates prefix
- verify_template_ownership helper
- 5 CRUD + reorder endpoints
- JSON parsing for options

### Modified (1 file)

**backend/app/main.py**
- Added template_info_fields_router import
- Added router inclusion with /api/v1 prefix

## API Usage Examples

### Create Info Field
```bash
POST /api/v1/templates/{template_id}/info-fields
{
  "label": "Nome do Projeto",
  "field_type": "text",
  "required": true
}
```

### Create Select Field
```bash
POST /api/v1/templates/{template_id}/info-fields
{
  "label": "Tipo de Equipamento",
  "field_type": "select",
  "options": ["Transformador", "Disjuntor", "Chave Seccionadora"],
  "required": true
}
```

### Reorder Fields
```bash
PUT /api/v1/templates/{template_id}/info-fields/reorder
{
  "field_ids": [
    "uuid-of-field-2",
    "uuid-of-field-1",
    "uuid-of-field-3"
  ]
}
```

---

**Phase:** 5 - Template Configuration
**Plan:** 02
**Status:** ✅ Complete
**Duration:** Resumed from previous session
