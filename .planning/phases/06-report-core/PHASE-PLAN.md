# Phase 6: Report Core

**Goal:** Users can create, fill, save, and manage reports through their complete lifecycle.

**Requirements:** REPT-01 through REPT-08

---

## Phase Overview

This phase implements the core report functionality - the heart of SmartHand. Users will be able to:
1. Create reports from templates
2. Fill in info fields and checklist responses
3. Auto-save progress as drafts
4. Resume work on drafts
5. Complete and manage reports

---

## Data Architecture

### Current State
- `reports` table exists with basic fields (title, status, data_json, location)
- Foreign keys to templates, projects, users
- No structured storage for checklist responses or info field values

### Target State
- Extended Report model with template_snapshot (JSONB)
- ReportInfoValue model for storing info field values
- ReportChecklistResponse model for checklist answers
- Status enum: draft, in_progress, completed, archived

---

## Plan Breakdown

### Plan 06-01: Report Data Models & Migration
**Focus:** Backend database schema

**Tasks:**
1. Extend Report model with:
   - `template_snapshot` (JSONB) - frozen copy of template at creation time
   - `started_at` (timestamp) - when filling started
   - `completed_at` (timestamp) - when marked complete
   - Remove `data_json` (replaced by structured models)

2. Create ReportInfoValue model:
   - `report_id` (FK to reports)
   - `info_field_id` (FK to template_info_fields)
   - `field_label` (denormalized for snapshot)
   - `value` (text)

3. Create ReportChecklistResponse model:
   - `report_id` (FK to reports)
   - `section_id` (FK to template_sections)
   - `field_id` (FK to template_fields)
   - `section_name` (denormalized)
   - `field_label` (denormalized)
   - `field_type` (denormalized)
   - `response_value` (text - the actual answer)
   - `comment` (text - optional comment)
   - `photos` (JSONB - array of photo references)

4. Create Alembic migration

**Output:** Models + migration + Pydantic schemas

---

### Plan 06-02: Report API Endpoints
**Focus:** Backend CRUD operations

**Tasks:**
1. Create report router with endpoints:
   - `POST /reports/` - Create report from template
   - `GET /reports/` - List reports with filters (status, date, template)
   - `GET /reports/{id}` - Get report details with all responses
   - `PATCH /reports/{id}` - Update report (save draft)
   - `POST /reports/{id}/complete` - Mark report as completed
   - `POST /reports/{id}/archive` - Archive report

2. Create report service with business logic:
   - `create_report(template_id, user_id)` - creates report + snapshots template
   - `save_draft(report_id, info_values, responses)` - saves progress
   - `complete_report(report_id)` - validates and completes

3. Implement tenant isolation

**Output:** Full CRUD API for reports

---

### Plan 06-03: Frontend Report Creation
**Focus:** Create report flow

**Tasks:**
1. Create ReportsPage with list view
2. Create NewReportModal:
   - Template selector (dropdown of active templates)
   - Project selector (optional)
   - Create button
3. Create ReportCard component for list items
4. Add route `/reports` and `/reports/:id`
5. Add navigation to sidebar

**Output:** Users can see report list and create new reports

---

### Plan 06-04: Frontend Report Filling UI
**Focus:** Fill report with checklist

**Tasks:**
1. Create ReportFillPage:
   - Header with report title and status
   - Progress indicator (sections completed)
   - Save button (manual save)
   - Complete button

2. Create InfoFieldsForm:
   - Renders info fields from template snapshot
   - Controlled inputs bound to form state

3. Create ChecklistForm:
   - Accordion sections matching template
   - Field components based on field_type:
     - TextFieldInput
     - DropdownFieldInput
     - CheckboxFieldInput
   - Comment toggle for each field
   - Photo attachment indicator (Phase 7)

**Output:** Users can fill all report fields

---

### Plan 06-05: Auto-save & Draft Resume
**Focus:** Prevent data loss

**Tasks:**
1. Implement auto-save:
   - Debounced save (2 second delay after last change)
   - Save on blur (field loses focus)
   - Save on navigation away
   - Visual indicator "Saving..." / "Saved"

2. Implement draft resume:
   - Load saved values on page load
   - Pre-populate all fields
   - Show "Last saved: X minutes ago"

3. Handle conflicts:
   - Detect stale data
   - Prompt user if conflict

**Output:** No data loss, seamless resume

---

### Plan 06-06: Human Verification
**Focus:** Test complete flow

**Tasks:**
1. Test end-to-end flow:
   - Create report from template
   - Fill info fields
   - Answer checklist questions
   - Auto-save works
   - Resume draft works
   - Complete report
   - View in list with filters

**Output:** Human approval of Phase 6

---

## Success Criteria Mapping

| Requirement | Plan | Criteria |
|-------------|------|----------|
| REPT-01 | 06-02, 06-03 | Create report from template |
| REPT-02 | 06-04 | Fill info fields first |
| REPT-03 | 06-04 | Dynamic checklist rendering |
| REPT-04 | 06-05 | Auto-save as draft |
| REPT-05 | 06-05 | Resume saved draft |
| REPT-06 | 06-02 | Status lifecycle |
| REPT-07 | 06-02, 06-03 | List with filters |
| REPT-08 | 06-01 | Template snapshot |

---

## Technical Decisions

### Template Snapshot Strategy
Store complete template structure as JSONB in report at creation time:
- Includes all sections, fields, info_fields, signature_fields
- Ensures historical consistency
- Report rendering uses snapshot, not live template

### Response Storage Strategy
Separate tables for structured queries vs JSONB blob:
- ReportInfoValue: allows querying "all reports where project_name = X"
- ReportChecklistResponse: allows analyzing field responses across reports
- Denormalize labels for rendering without joins to snapshot

### Auto-save Strategy
- React Query mutation with debounce
- Optimistic updates for instant feedback
- Background sync with visual indicator
- Conflict detection via updated_at timestamp

---

## Dependencies

**From Phase 5:**
- Template with sections and fields
- Info fields configuration
- Field photo_config and comment_config
- Signature fields (used in Phase 9)

**For Phase 7:**
- ReportChecklistResponse.photos array ready for photo references

---

## Estimated Plans: 6
## Estimated Duration: ~2 hours
