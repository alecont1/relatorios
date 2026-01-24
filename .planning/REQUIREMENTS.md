# Requirements: SmartHand

**Defined:** 2026-01-24
**Core Value:** Technicians in the field can fill a checklist on their phone, take geolocated photos with automatic watermarks, and generate a professional PDF report.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Authentication

- [ ] **AUTH-01**: User can login with email and password
- [ ] **AUTH-02**: User session persists via JWT token with automatic refresh
- [ ] **AUTH-03**: User can logout from any page
- [ ] **AUTH-04**: Role-based access control enforced (superadmin, admin, manager, user)
- [ ] **AUTH-05**: Admin can create user accounts for their tenant (no self-registration)

### Tenants

- [ ] **TNNT-01**: Superadmin can create, edit, and deactivate tenants
- [ ] **TNNT-02**: All data queries are isolated by tenant (no cross-tenant access)
- [ ] **TNNT-03**: Tenant can upload primary and secondary logo images
- [ ] **TNNT-04**: Tenant can configure brand colors (primary, secondary, accent)
- [ ] **TNNT-05**: Tenant has contact info fields (address, phone, email, website)

### Templates

- [ ] **TMPL-01**: Admin can create templates with name, code, category, and version
- [ ] **TMPL-02**: Admin can edit existing templates
- [ ] **TMPL-03**: Admin can activate/deactivate templates
- [ ] **TMPL-04**: Templates support global scope (SmartHand) and per-tenant scope
- [ ] **TMPL-05**: Template header has title, reference standards, and planning requirements text
- [ ] **TMPL-06**: Template has configurable info fields (text, date, select types) for project metadata
- [ ] **TMPL-07**: Template has ordered sections containing checklist fields
- [ ] **TMPL-08**: Checklist fields support types: Ok/Not Ok/N.A., text, number, select, date
- [ ] **TMPL-09**: Checklist fields have configurable photo settings (required, min/max, GPS, watermark)
- [ ] **TMPL-10**: Checklist fields have configurable comment settings (enabled, required)
- [ ] **TMPL-11**: Template has configurable signature fields with role names and required flag

### Reports

- [ ] **REPT-01**: User can select a template and create a new report
- [ ] **REPT-02**: User fills info fields (project metadata) as the first step
- [ ] **REPT-03**: User answers checklist questions rendered dynamically from template
- [ ] **REPT-04**: Report auto-saves as draft during filling (no data loss)
- [ ] **REPT-05**: User can resume a previously saved draft report
- [ ] **REPT-06**: Report transitions through lifecycle: draft → in_progress → completed → archived
- [ ] **REPT-07**: User can list their reports with filters (status, date, template)
- [ ] **REPT-08**: Template snapshot is saved with report for historical consistency

### Photos

- [ ] **PHOT-01**: User can capture photo from device camera within a checklist field
- [ ] **PHOT-02**: GPS coordinates are captured automatically and cannot be edited
- [ ] **PHOT-03**: Capture timestamp is recorded automatically and cannot be edited
- [ ] **PHOT-04**: Reverse geocoding converts GPS coordinates to human-readable address
- [ ] **PHOT-05**: Photo watermark overlay includes tenant logo, timestamp, and address
- [ ] **PHOT-06**: Images are compressed client-side before upload (max 1920px, 85% quality)
- [ ] **PHOT-07**: Photos are uploaded to Cloudflare R2 storage
- [ ] **PHOT-08**: Multiple photos per checklist field with configurable maximum
- [ ] **PHOT-09**: Photo metadata (GPS, timestamp) cannot be modified after capture

### PDF Generation

- [ ] **PDF-01**: PDF is generated server-side with WeasyPrint from HTML/CSS templates
- [ ] **PDF-02**: PDF header includes tenant logos, project info, and reference standards
- [ ] **PDF-03**: PDF renders bilingual checklist questions (Portuguese + English) with responses
- [ ] **PDF-04**: PDF includes photo grid with metadata captions (timestamp, address)
- [ ] **PDF-05**: PDF includes captured digital signatures in footer area
- [ ] **PDF-06**: Tenant branding (logos, colors) applied throughout PDF
- [ ] **PDF-07**: User can generate and download PDF from completed reports

### Signatures

- [ ] **SIGN-01**: User can draw digital signature on touchscreen canvas
- [ ] **SIGN-02**: Template defines multiple signature roles (e.g., Técnico Executor, Responsável Técnico)
- [ ] **SIGN-03**: Captured signatures are rendered in PDF footer with role labels

### Mobile UX

- [ ] **MOBX-01**: All form interfaces are mobile-first with touch-friendly controls (large tap targets)
- [ ] **MOBX-02**: Loading states and error feedback displayed on all async actions
- [ ] **MOBX-03**: Progress indicator shows checklist completion percentage during filling

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Offline & PWA

- **OFFL-01**: App works offline with local data storage
- **OFFL-02**: Reports sync automatically when connection is restored
- **OFFL-03**: Photos queue for upload when offline

### Template Builder

- **BLDR-01**: Drag-and-drop visual template builder
- **BLDR-02**: Live preview of template as it's being built
- **BLDR-03**: Import template structure from Excel file
- **BLDR-04**: Duplicate existing template as starting point
- **BLDR-05**: Template version history and rollback

### Dashboard & Analytics

- **DASH-01**: Dashboard with report completion metrics
- **DASH-02**: Filter reports by date range, project, user
- **DASH-03**: Export report data to CSV/Excel
- **DASH-04**: Charts showing reports per period/user/template

### Advanced Features

- **ADVN-01**: OAuth/SSO login (Google, Microsoft)
- **ADVN-02**: Email notifications on report completion
- **ADVN-03**: Report commenting/review workflow
- **ADVN-04**: Password reset via email link

## Out of Scope

| Feature | Reason |
|---------|--------|
| Native mobile app | Web-first responsive design covers mobile use cases |
| Video capture | Photos sufficient for commissioning evidence |
| Real-time collaboration | Single user fills each report |
| AI-powered suggestions | Structured checklists don't benefit from AI |
| Self-registration | Security requirement - admin creates accounts |
| Multi-language UI | UI in Portuguese, only checklist questions are bilingual |
| Report editing after completion | Completed reports are immutable evidence |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| AUTH-01 | TBD | Pending |
| AUTH-02 | TBD | Pending |
| AUTH-03 | TBD | Pending |
| AUTH-04 | TBD | Pending |
| AUTH-05 | TBD | Pending |
| TNNT-01 | TBD | Pending |
| TNNT-02 | TBD | Pending |
| TNNT-03 | TBD | Pending |
| TNNT-04 | TBD | Pending |
| TNNT-05 | TBD | Pending |
| TMPL-01 | TBD | Pending |
| TMPL-02 | TBD | Pending |
| TMPL-03 | TBD | Pending |
| TMPL-04 | TBD | Pending |
| TMPL-05 | TBD | Pending |
| TMPL-06 | TBD | Pending |
| TMPL-07 | TBD | Pending |
| TMPL-08 | TBD | Pending |
| TMPL-09 | TBD | Pending |
| TMPL-10 | TBD | Pending |
| TMPL-11 | TBD | Pending |
| REPT-01 | TBD | Pending |
| REPT-02 | TBD | Pending |
| REPT-03 | TBD | Pending |
| REPT-04 | TBD | Pending |
| REPT-05 | TBD | Pending |
| REPT-06 | TBD | Pending |
| REPT-07 | TBD | Pending |
| REPT-08 | TBD | Pending |
| PHOT-01 | TBD | Pending |
| PHOT-02 | TBD | Pending |
| PHOT-03 | TBD | Pending |
| PHOT-04 | TBD | Pending |
| PHOT-05 | TBD | Pending |
| PHOT-06 | TBD | Pending |
| PHOT-07 | TBD | Pending |
| PHOT-08 | TBD | Pending |
| PHOT-09 | TBD | Pending |
| PDF-01 | TBD | Pending |
| PDF-02 | TBD | Pending |
| PDF-03 | TBD | Pending |
| PDF-04 | TBD | Pending |
| PDF-05 | TBD | Pending |
| PDF-06 | TBD | Pending |
| PDF-07 | TBD | Pending |
| SIGN-01 | TBD | Pending |
| SIGN-02 | TBD | Pending |
| SIGN-03 | TBD | Pending |
| MOBX-01 | TBD | Pending |
| MOBX-02 | TBD | Pending |
| MOBX-03 | TBD | Pending |

**Coverage:**
- v1 requirements: 48 total
- Mapped to phases: 0
- Unmapped: 48

---
*Requirements defined: 2026-01-24*
*Last updated: 2026-01-24 after initial definition*
