---
phase: 05-template-configuration
plan: 05
subsystem: frontend
tags: [react, typescript, react-hook-form, tanstack-query, modal]
requires:
  - 05-04-frontend-template-config-ui
provides:
  - SignatureFieldsConfigurator for managing signature requirements
  - FieldConfigModal for photo/comment configuration
  - ChecklistSectionsView with clickable fields
  - Complete template configuration UI
affects:
  - 06-report-core (will use configured templates)
  - 07-photo-capture (will use photo_config settings)
  - 09-digital-signatures (will use signature_fields)
tech-stack:
  added: []
  patterns:
    - Modal overlay pattern with backdrop click to close
    - Quick role suggestions for common signature roles
    - Visual indicators for configured fields (camera/comment icons)
key-files:
  created:
    - frontend/src/features/template/components/SignatureFieldsConfigurator.tsx
    - frontend/src/features/template/components/FieldConfigModal.tsx
    - frontend/src/features/template/components/ChecklistSectionsView.tsx
  modified:
    - frontend/src/features/template/components/index.ts
    - frontend/src/pages/TemplateConfigPage.tsx
decisions:
  - slug: quick-role-suggestions
    choice: Provide common role buttons for quick signature field creation
    rationale: Speeds up common workflows, reduces typing errors
    alternatives: Only manual input (slower, more error-prone)
  - slug: field-visual-indicators
    choice: Show camera/comment icons on configured fields
    rationale: Quick visual feedback on field configuration status
    alternatives: Require opening modal to see config (hidden state)
metrics:
  duration: 12min
  completed: 2026-02-02
---

# Phase 5 Plan 05: Frontend Field Configuration UI Summary

**One-liner:** Complete frontend template configuration with signature fields management, checklist field configuration modal, and visual indicators.

## What Was Built

### Components

1. **SignatureFieldsConfigurator.tsx** (200 lines)
   - Dynamic form using useFieldArray for signature fields
   - Quick add buttons for common roles (Tecnico Executor, Responsavel Tecnico, Cliente, etc.)
   - Each row: role_name input, required checkbox, delete button
   - Save changes with API mutations
   - Unused common roles shown as quick add buttons

2. **FieldConfigModal.tsx** (250 lines)
   - Modal overlay for configuring checklist field settings
   - Photo settings section:
     - required checkbox
     - min_count / max_count number inputs
     - require_gps checkbox
     - watermark checkbox
   - Comment settings section:
     - enabled checkbox
     - required checkbox
   - Form validation (min_count <= max_count)
   - Uses react-hook-form for form management
   - Closes on backdrop click or cancel button

3. **ChecklistSectionsView.tsx** (100 lines)
   - Displays template sections with their fields
   - Clickable fields open FieldConfigModal
   - Visual indicators:
     - Camera icon for configured photo requirements
     - Message icon for enabled comments
     - Settings icon on hover
   - Shows section name and field count

### Updated Components

4. **TemplateConfigPage.tsx** (updated)
   - State for selectedField and isFieldModalOpen
   - handleFieldClick opens modal with selected field
   - handleFieldSave refreshes template data
   - Integrated SignatureFieldsConfigurator
   - Integrated ChecklistSectionsView
   - Renders FieldConfigModal conditionally
   - Badge shows "X secoes, Y campos" for checklist

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | API functions already added in 05-04 | - | templateApi.ts |
| 2 | Create SignatureFieldsConfigurator | 0461118 | SignatureFieldsConfigurator.tsx |
| 3 | Create FieldConfigModal and ChecklistSectionsView | 0461118 | FieldConfigModal.tsx, ChecklistSectionsView.tsx, TemplateConfigPage.tsx |

## Technical Decisions

### 1. Quick Role Suggestions

**Decision:** Show buttons for common signature roles that haven't been added yet.

**Rationale:**
- Most templates need similar signature roles
- Quick add reduces typing and errors
- Dynamic list shows only unused roles

**Code Pattern:**
```typescript
const COMMON_ROLES = ['Tecnico Executor', 'Responsavel Tecnico', 'Cliente', ...]
const usedRoles = fields.map(f => f.role_name)
const availableRoles = COMMON_ROLES.filter(r => !usedRoles.includes(r))
```

### 2. Visual Field Indicators

**Decision:** Show camera and comment icons on configured fields in ChecklistSectionsView.

**Rationale:**
- Quick visual feedback without opening modal
- User can see at-a-glance which fields have configuration
- Camera icon shows count if min_count > 0

**Icon Logic:**
```typescript
const hasPhotoConfig = (field) =>
  field.photo_config && (field.photo_config.required || field.photo_config.min_count > 0)

const hasCommentConfig = (field) =>
  field.comment_config?.enabled
```

## Verification Results

All success criteria met:

✅ SignatureFieldsConfigurator allows add/edit/delete signature fields
✅ Signature field role_name and required flag editable
✅ ChecklistSectionsView displays sections with fields
✅ Clicking field opens FieldConfigModal
✅ FieldConfigModal shows photo settings (required, min/max, GPS, watermark)
✅ FieldConfigModal shows comment settings (enabled, required)
✅ Validation prevents min_count > max_count
✅ Changes persist to backend via API calls
✅ Loading states handled appropriately
✅ TypeScript compiles without errors

## Next Steps

**Immediate (Plan 05-06):**
- Integration verification with human testing
- Verify full flow works end-to-end

**Future Phases:**
- Phase 6: Report Core (will use template configuration)
- Phase 7: Photo Capture (will enforce photo_config rules)
- Phase 9: Digital Signatures (will use signature_fields)

## Files Changed

### Created (3 files)

**frontend/src/features/template/components/SignatureFieldsConfigurator.tsx** (200 lines)
- useFieldArray for dynamic signature fields
- COMMON_ROLES constant for quick add buttons
- React Query mutations for CRUD

**frontend/src/features/template/components/FieldConfigModal.tsx** (250 lines)
- Modal overlay with photo/comment settings
- Form validation with react-hook-form
- Default values from existing field config

**frontend/src/features/template/components/ChecklistSectionsView.tsx** (100 lines)
- Section/field display with visual indicators
- onClick handler for field configuration
- Camera/comment icons for configured fields

### Modified (2 files)

**frontend/src/features/template/components/index.ts**
- Exported SignatureFieldsConfigurator
- Exported FieldConfigModal
- Exported ChecklistSectionsView

**frontend/src/pages/TemplateConfigPage.tsx**
- Added state for selected field and modal
- Integrated SignatureFieldsConfigurator
- Integrated ChecklistSectionsView with onFieldClick
- Renders FieldConfigModal conditionally

## User Flow

1. Navigate to /templates
2. Click Settings icon on template row
3. Open "Campos de Assinatura" accordion
4. Click quick add buttons or manual "Adicionar Assinatura"
5. Edit role names and required checkboxes
6. Click "Salvar Alteracoes"
7. Open "Secoes do Checklist" accordion
8. Click on any checklist field
9. Configure photo requirements (required, min/max, GPS, watermark)
10. Configure comment settings (enabled, required)
11. Click "Salvar" in modal

---

**Phase:** 5 - Template Configuration
**Plan:** 05
**Status:** ✅ Complete
**Duration:** 12 minutes
**Commit:** 0461118
