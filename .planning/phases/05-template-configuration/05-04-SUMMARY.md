---
phase: 05-template-configuration
plan: 04
subsystem: frontend
tags: [react, typescript, react-hook-form, tanstack-query, tailwind]
requires:
  - 05-02-info-fields-api
  - 05-03-signature-fields-api
provides:
  - TemplateConfigPage for configuring templates
  - AccordionSection reusable component
  - InfoFieldsConfigurator with useFieldArray
  - TypeScript types for all configuration entities
affects:
  - 05-05-frontend-field-configuration
  - user workflow for template management
tech-stack:
  added: []
  patterns:
    - useFieldArray with keyName for dynamic forms
    - React Query for data fetching and mutations
    - Accordion pattern for organized configuration UI
key-files:
  created:
    - frontend/src/features/template/components/AccordionSection.tsx
    - frontend/src/features/template/components/InfoFieldsConfigurator.tsx
    - frontend/src/pages/TemplateConfigPage.tsx
  modified:
    - frontend/src/features/template/api/templateApi.ts
    - frontend/src/features/template/components/TemplateList.tsx
    - frontend/src/features/template/components/index.ts
    - frontend/src/pages/index.ts
    - frontend/src/App.tsx
decisions:
  - slug: useFieldArray-keyName
    choice: Use keyName='key' in useFieldArray to avoid id conflicts
    rationale: Prevents React key warnings when items have existing id fields
    alternatives: Use index as key (causes bugs when reordering)
  - slug: accordion-layout
    choice: Use accordion sections for Info Fields, Checklist, Signatures
    rationale: Organized layout, reduces visual overwhelm, common configuration pattern
    alternatives: Tabs (harder to compare sections), flat layout (too long)
metrics:
  duration: 15min
  completed: 2026-02-02
---

# Phase 5 Plan 04: Frontend Template Configuration UI Summary

**One-liner:** React UI for template configuration with accordion layout, dynamic info fields form using useFieldArray, and API integration.

## What Was Built

### TypeScript Types (templateApi.ts)

Added types for all configuration entities:

1. **InfoField / InfoFieldCreate / InfoFieldUpdate** - Info field CRUD types
2. **SignatureField / SignatureFieldCreate / SignatureFieldUpdate** - Signature field types
3. **PhotoConfig / CommentConfig** - Field configuration types
4. **FieldConfigResponse / FieldConfigUpdate** - API response types

### API Functions (templateApi.ts)

Extended templateApi with:

| Function | Endpoint | Purpose |
|----------|----------|---------|
| getInfoFields | GET /templates/{id}/info-fields | List info fields |
| createInfoField | POST /templates/{id}/info-fields | Create info field |
| updateInfoField | PATCH /templates/{id}/info-fields/{fid} | Update info field |
| deleteInfoField | DELETE /templates/{id}/info-fields/{fid} | Delete info field |
| reorderInfoFields | PUT /templates/{id}/info-fields/reorder | Reorder fields |
| getSignatureFields | GET /templates/{id}/signature-fields | List signature fields |
| createSignatureField | POST /templates/{id}/signature-fields | Create signature field |
| updateSignatureField | PATCH /templates/{id}/signature-fields/{fid} | Update signature field |
| deleteSignatureField | DELETE /templates/{id}/signature-fields/{fid} | Delete signature field |
| reorderSignatureFields | PUT /templates/{id}/signature-fields/reorder | Reorder signatures |
| getFieldConfig | GET /templates/fields/{id}/config | Get field config |
| updateFieldConfig | PATCH /templates/fields/{id}/config | Update field config |

### Components

1. **AccordionSection.tsx** (45 lines)
   - Reusable collapsible section component
   - Props: title, defaultOpen, badge, children
   - Smooth expand/collapse animation
   - Chevron rotation on toggle

2. **InfoFieldsConfigurator.tsx** (200 lines)
   - Dynamic form using react-hook-form useFieldArray
   - Features:
     - Add/edit/delete info fields
     - Field type selector (text, date, select)
     - Options input (enabled for select type)
     - Required checkbox
     - Save changes with API mutations
     - Loading state during save

3. **TemplateConfigPage.tsx** (160 lines)
   - Main configuration page
   - Fetches template, info fields, signature fields
   - Three accordion sections:
     - Info Fields (with InfoFieldsConfigurator)
     - Checklist Sections (read-only preview)
     - Signature Fields (read-only preview for now)
   - Back navigation to template list

### Routing Updates

- Added route: `/templates/:templateId/configure`
- Protected for admin/superadmin roles
- Added Settings button to TemplateList for navigation

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create types and API functions | 7127847 | templateApi.ts |
| 2 | Create AccordionSection and InfoFieldsConfigurator | 7127847 | AccordionSection.tsx, InfoFieldsConfigurator.tsx |
| 3 | Create TemplateConfigPage and routing | 7127847 | TemplateConfigPage.tsx, App.tsx, TemplateList.tsx |

## Technical Decisions

### 1. useFieldArray with keyName

**Decision:** Use `keyName: 'key'` in useFieldArray configuration.

**Rationale:**
- InfoField objects have their own `id` field from the API
- Default useFieldArray uses `id` for React keys
- Using `keyName: 'key'` avoids conflicts and React warnings
- Fields array items get unique `key` property for React keys

**Code Pattern:**
```typescript
const { fields, append, remove } = useFieldArray({
  control,
  name: 'fields',
  keyName: 'key',  // Use 'key' instead of default 'id'
})

// In JSX:
{fields.map((field, index) => (
  <div key={field.key}>...</div>  // Use field.key, not index
))}
```

### 2. Accordion Layout

**Decision:** Use accordion sections for template configuration UI.

**Rationale:**
- Logical grouping of related settings
- Reduces visual overwhelm on complex templates
- Common pattern for configuration interfaces
- Allows focus on one section at a time
- Badge shows count for quick reference

## Verification Results

All success criteria met:

✅ TemplateConfigPage accessible at /templates/:id/configure for admin/superadmin
✅ Accordion sections for Info Fields, Checklist, Signatures
✅ InfoFieldsConfigurator uses useFieldArray with field.key as React key
✅ Add/edit/delete info fields work with API persistence
✅ Field type "select" shows options input
✅ Loading states displayed during save
✅ TypeScript compiles without errors
✅ Settings button added to template list

## Next Steps

**Immediate (Plan 05-05):**
- Add SignatureFieldsConfigurator component
- Add field configuration UI for photo/comment settings
- Complete signature field CRUD in frontend

**Future Plans:**
- 05-06: Integration verification
- 06: Report Core (will use template configuration)

## Files Changed

### Created (3 files)

**frontend/src/features/template/components/AccordionSection.tsx** (45 lines)
- Reusable accordion with smooth animations
- Badge support for showing counts
- Chevron rotation indicator

**frontend/src/features/template/components/InfoFieldsConfigurator.tsx** (200 lines)
- Dynamic form with useFieldArray
- CRUD operations with React Query mutations
- Field type conditional options input

**frontend/src/pages/TemplateConfigPage.tsx** (160 lines)
- Configuration page with three accordion sections
- Data fetching with React Query
- Back navigation to template list

### Modified (5 files)

**frontend/src/features/template/api/templateApi.ts**
- Added 15+ TypeScript interfaces for configuration entities
- Added 12 API functions for info/signature/config CRUD

**frontend/src/features/template/components/TemplateList.tsx**
- Added Settings button with navigate to configure page
- Imported Settings icon from lucide-react

**frontend/src/features/template/components/index.ts**
- Exported AccordionSection and InfoFieldsConfigurator

**frontend/src/pages/index.ts**
- Exported TemplateConfigPage

**frontend/src/App.tsx**
- Imported TemplateConfigPage
- Added /templates/:templateId/configure route

## User Flow

1. User navigates to /templates
2. Clicks Settings icon on a template row
3. Navigates to /templates/{id}/configure
4. Sees three accordion sections
5. Expands "Campos de Informacao" (default open)
6. Adds/edits/deletes info fields
7. Clicks "Salvar Alteracoes" to persist
8. Clicks "Voltar" to return to list

---

**Phase:** 5 - Template Configuration
**Plan:** 04
**Status:** ✅ Complete
**Duration:** 15 minutes
**Commit:** 7127847
