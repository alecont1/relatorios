# Roadmap: SmartHand

**Created:** 2026-01-24
**Depth:** Comprehensive
**Phases:** 10
**Requirements:** 48 mapped

---

## Phase 1: Project Setup & Infrastructure

**Goal:** Development environment and deployment pipeline are operational for both frontend and backend.

**Requirements:** (Infrastructure foundation - no explicit requirements, but enables all others)

**Dependencies:** None (foundation phase)

**Success Criteria:**
1. Frontend React+Vite+TypeScript project initialized with Tailwind CSS, Zustand, React Query, and React Hook Form configured
2. Backend FastAPI project initialized with SQLAlchemy, PostgreSQL connection, and PostGIS extension enabled
3. Database schema migrations working with Alembic
4. Cloudflare R2 bucket created and accessible from backend with S3-compatible client
5. Frontend deployed to Vercel with environment variables configured
6. Backend deployed to Railway with PostgreSQL database and Redis instance provisioned
7. CI/CD pipeline runs tests and deploys on git push to main branch

---

## Phase 2: Authentication System

**Goal:** Users can securely log in, maintain sessions, and access features based on their assigned roles.

**Requirements:** AUTH-01, AUTH-02, AUTH-03, AUTH-04, AUTH-05

**Dependencies:** Phase 1 (needs infrastructure)

**Success Criteria:**
1. User can log in with email and password and receive a JWT token
2. User session persists across page refreshes with automatic token refresh
3. User can log out from any page and token is invalidated
4. API endpoints enforce role-based access control (superadmin, admin, manager, user)
5. Admin can create new user accounts for their tenant (no public registration allowed)

---

## Phase 3: Multi-Tenant Architecture

**Goal:** Platform supports multiple isolated tenants with custom branding and data separation.

**Requirements:** TNNT-01, TNNT-02, TNNT-03, TNNT-04, TNNT-05

**Dependencies:** Phase 2 (needs authentication with superadmin role)

**Success Criteria:**
1. Superadmin can create, edit, and deactivate tenant organizations
2. All database queries automatically filter by tenant ID (no cross-tenant data leakage)
3. Tenant admin can upload primary and secondary logo images to R2 storage
4. Tenant admin can configure brand colors (primary, secondary, accent) in settings
5. Tenant profile displays contact information (address, phone, email, website)

---

## Phase 4: Template Management

**Goal:** Admins can create and manage report templates with basic metadata and lifecycle.

**Requirements:** TMPL-01, TMPL-02, TMPL-03, TMPL-04, TMPL-05

**Dependencies:** Phase 3 (needs tenant context)

**Success Criteria:**
1. Admin can create new template with name, code, category, and version number
2. Admin can edit existing template metadata (name, code, category, version)
3. Admin can activate or deactivate templates (inactive templates hidden from users)
4. Templates can be created as global scope (SmartHand) or per-tenant scope
5. Template header includes title, reference standards text, and planning requirements text

---

## Phase 5: Template Configuration

**Goal:** Admins can configure complete template structure with info fields, checklist sections, and field-level settings.

**Requirements:** TMPL-06, TMPL-07, TMPL-08, TMPL-09, TMPL-10, TMPL-11

**Dependencies:** Phase 4 (needs basic template management)

**Success Criteria:**
1. Admin can add configurable info fields (text, date, select types) to template for project metadata
2. Admin can create ordered sections containing checklist fields
3. Checklist fields support all required types: Ok/Not Ok/N.A., text, number, select, date
4. Checklist fields have configurable photo settings (required, min/max count, GPS, watermark)
5. Checklist fields have configurable comment settings (enabled, required)
6. Template includes configurable signature fields with role names and required flag

---

## Phase 6: Report Core

**Goal:** Users can create, fill, save, and manage reports through their complete lifecycle.

**Requirements:** REPT-01, REPT-02, REPT-03, REPT-04, REPT-05, REPT-06, REPT-07, REPT-08

**Dependencies:** Phase 5 (needs complete template structure)

**Success Criteria:**
1. User can select an active template and create a new report instance
2. User fills info fields (project metadata) as the first step when creating report
3. User sees dynamically rendered checklist questions from template and can answer them
4. Report auto-saves as draft during filling without user action (no data loss on browser close)
5. User can resume a previously saved draft report from list view
6. Report transitions through lifecycle states: draft → in_progress → completed → archived
7. User can list their reports with filters by status, date range, and template type
8. Template snapshot is saved with report for historical consistency (template changes don't affect existing reports)

---

## Phase 7: Photo Capture & Processing

**Goal:** Users can capture photos with automatic metadata, watermarks, and secure storage.

**Requirements:** PHOT-01, PHOT-02, PHOT-03, PHOT-04, PHOT-05, PHOT-06, PHOT-07, PHOT-08, PHOT-09

**Dependencies:** Phase 6 (needs report filling workflow)

**Success Criteria:**
1. User can capture photo from device camera within a checklist field context
2. GPS coordinates are captured automatically from device and displayed as non-editable
3. Capture timestamp is recorded automatically and displayed as non-editable
4. Reverse geocoding converts GPS coordinates to human-readable address displayed on photo
5. Photo watermark overlay includes tenant logo, timestamp, and address burned into image
6. Images are compressed client-side before upload (max 1920px width, 85% JPEG quality)
7. Photos are uploaded to Cloudflare R2 storage with unique filenames and associated with checklist field
8. Multiple photos can be added per checklist field respecting configured maximum count
9. Photo metadata (GPS coordinates, timestamp) cannot be modified after initial capture

---

## Phase 8: PDF Generation System

**Goal:** Users can generate professional branded PDF reports with all data, photos, and signatures.

**Requirements:** PDF-01, PDF-02, PDF-03, PDF-04, PDF-05, PDF-06, PDF-07

**Dependencies:** Phase 7 (needs photos), Phase 9 (needs signatures for complete PDF)

**Success Criteria:**
1. PDF is generated server-side using WeasyPrint from Jinja2 HTML/CSS templates
2. PDF header includes tenant primary and secondary logos, project info fields, and reference standards
3. PDF renders bilingual checklist questions (Portuguese + English) with user responses
4. PDF includes photo grid with captions showing timestamp and geocoded address
5. PDF includes captured digital signatures in footer area with role labels
6. Tenant branding (logos, colors) applied consistently throughout PDF layout
7. User can generate and download PDF file from completed report detail page

---

## Phase 9: Digital Signatures

**Goal:** Users can capture digital signatures on touchscreen devices for report approval.

**Requirements:** SIGN-01, SIGN-02, SIGN-03

**Dependencies:** Phase 6 (needs report workflow)

**Success Criteria:**
1. User can draw digital signature on HTML canvas with touch or mouse input
2. Template defines multiple signature roles (e.g., Técnico Executor, Responsável Técnico) with required flags
3. Captured signatures are saved as PNG images and rendered in PDF footer with role labels

---

## Phase 10: Mobile UX & Polish

**Goal:** All interfaces are optimized for mobile touch interaction with clear feedback and progress tracking.

**Requirements:** MOBX-01, MOBX-02, MOBX-03

**Dependencies:** All previous phases (polish applied across all features)

**Success Criteria:**
1. All form interfaces use mobile-first design with touch-friendly controls (minimum 44px tap targets)
2. Loading states and error feedback messages displayed clearly on all async actions (API calls, uploads)
3. Progress indicator shows checklist completion percentage during report filling

---

## Progress

| Phase | Name | Status | Requirements |
|-------|------|--------|--------------|
| 1 | Project Setup & Infrastructure | Pending | Foundation (0 explicit) |
| 2 | Authentication System | Pending | 5 |
| 3 | Multi-Tenant Architecture | Pending | 5 |
| 4 | Template Management | Pending | 5 |
| 5 | Template Configuration | Pending | 6 |
| 6 | Report Core | Pending | 8 |
| 7 | Photo Capture & Processing | Pending | 9 |
| 8 | PDF Generation System | Pending | 7 |
| 9 | Digital Signatures | Pending | 3 |
| 10 | Mobile UX & Polish | Pending | 3 |

**Total:** 48 requirements mapped across 10 phases

---

*Roadmap created: 2026-01-24*
