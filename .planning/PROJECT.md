# SmartHand - Plataforma de Relatórios de Campo

## What This Is

A multi-tenant SaaS platform for generating professional field reports in real-time, used by engineers and technicians during data center commissioning projects. Replaces Excel-based workflows with mobile-friendly checklists, geolocated photo capture with watermarks, and automatic PDF generation.

## Core Value

Technicians in the field can fill a checklist on their phone, take geolocated photos with automatic watermarks, and generate a professional PDF report — replacing the manual Excel process entirely.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Multi-tenant architecture with tenant isolation from day one
- [ ] JWT authentication with role-based access (superadmin, admin, manager, user)
- [ ] Admin panel for template CRUD (visual template builder)
- [ ] Dynamic template system with configurable sections, fields, and photo requirements
- [ ] Mobile-first checklist form rendering (Ok/Not Ok/N.A., text, number, select, date fields)
- [ ] Photo capture with automatic GPS coordinates and timestamps (non-editable metadata)
- [ ] Reverse geocoding for photo addresses
- [ ] Photo watermarking (logo, timestamp, address overlay)
- [ ] Image compression before upload to Cloudflare R2
- [ ] PDF generation with professional layout (WeasyPrint + Jinja2 HTML templates)
- [ ] PDF includes header info, bilingual checklist responses, photo grid with metadata, signatures
- [ ] Report lifecycle management (draft, in_progress, completed, archived)
- [ ] Tenant branding (logo, colors) applied to PDFs and watermarks
- [ ] Signature capture for report approval (multiple roles per template)
- [ ] Report listing with status filtering and PDF download

### Out of Scope

- Offline sync / PWA mode — complexity too high for v1, defer to v2
- Real-time collaboration — single user fills each report
- OAuth/SSO — email/password sufficient for v1
- Mobile native app — web-first, responsive design covers mobile use
- Video capture — photos only for v1
- AI-powered field suggestions — not needed for structured checklists
- Drag-and-drop template builder — form-based editor sufficient for v1
- Excel import for templates — manual creation first

## Context

- **Domain:** Data center commissioning (Microsoft DCD projects primarily)
- **Primary template:** "Equipment Energized Report" with 40 checklist items across sections (Prerequisites, Energy Restoration, Final Approvals)
- **Users work on mobile/tablet in the field** — UI must be touch-friendly with large tap targets
- **Photos are legal evidence** — GPS and timestamp metadata must be non-editable, watermarks ensure provenance
- **Bilingual support** — Portuguese primary, English secondary (questions have both languages)
- **Template structure:** Header with references/standards → Info fields (project metadata) → Sections with checklist fields → Signatures
- **PDF must match existing professional format** — header with logos, reference codes, bilingual checklist, photo grid, signature area
- **Existing landing page** at smarthand-landing/ (separate project, not part of this codebase)

## Constraints

- **Tech Stack (Frontend):** React + Vite + TypeScript + Tailwind CSS + Zustand + React Query + React Hook Form
- **Tech Stack (Backend):** Python + FastAPI + SQLAlchemy + PostgreSQL (with PostGIS) + WeasyPrint
- **Deployment:** Frontend on Vercel, Backend on Railway, DB on Railway PostgreSQL
- **Storage:** Cloudflare R2 (S3-compatible) for photos and PDFs
- **Background Jobs:** Celery + Redis for PDF generation
- **Mobile-first:** All form interfaces must work on phones and tablets
- **Photo metadata integrity:** GPS coordinates and timestamps cannot be modified by users after capture

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Multi-tenant from day one | Avoid costly refactor later; tenant isolation in DB and API layer | — Pending |
| WeasyPrint for PDF generation | Python-native, CSS-based styling, good for complex layouts with images | — Pending |
| Cloudflare R2 for storage | S3-compatible API, zero egress fees (photos are frequently downloaded) | — Pending |
| Railway for backend + DB | Simple Python deploys, managed PostgreSQL with PostGIS support | — Pending |
| Form-based template builder (not drag-and-drop) | Simpler to implement, sufficient for structured checklists | — Pending |
| Canvas-based photo watermarking | Client-side processing, no server round-trip needed for watermark | — Pending |
| Bilingual fields in template schema | Portuguese + English on same template, both rendered in PDF | — Pending |

---
*Last updated: 2026-01-24 after initialization*
