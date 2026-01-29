# Project State: SmartHand

**Last Updated:** 2026-01-29

---

## Current Status

**Active Phase:** 2 - Authentication System (IN PROGRESS)
**Active Plan:** 02-02 (completed)
**Last Action:** Completed 02-02-PLAN.md - Auth Endpoints (login, logout, refresh)
**Next Action:** Continue with 02-03 (User Management) or 02-05 (Login UI)

---

## Project Reference

**See:** C:\Users\xande\smarthand-reports\.planning\PROJECT.md (updated 2026-01-24)

**Core Value:** Technicians in the field can fill a checklist on their phone, take geolocated photos with automatic watermarks, and generate a professional PDF report.

**Current Focus:** Phase 2 - Authentication System

**Tech Stack:**
- Frontend: React + Vite + TypeScript + Tailwind CSS + Zustand + React Query + React Hook Form + Axios
- Backend: Python + FastAPI + SQLAlchemy + PostgreSQL (PostGIS) + WeasyPrint
- Infrastructure: Vercel (frontend), Railway (backend + DB), Cloudflare R2 (storage), Redis (jobs)

---

## Phase Progress

| Phase | Name | Status | Progress | Plans |
|-------|------|--------|----------|-------|
| 1 | Project Setup & Infrastructure | Complete | 100% | 5/5 |
| 2 | Authentication System | In Progress | 50% | 3/6 |
| 3 | Multi-Tenant Architecture | Pending | 0% | 0/0 |
| 4 | Template Management | Pending | 0% | 0/0 |
| 5 | Template Configuration | Pending | 0% | 0/0 |
| 6 | Report Core | Pending | 0% | 0/0 |
| 7 | Photo Capture & Processing | Pending | 0% | 0/0 |
| 8 | PDF Generation System | Pending | 0% | 0/0 |
| 9 | Digital Signatures | Pending | 0% | 0/0 |
| 10 | Mobile UX & Polish | Pending | 0% | 0/0 |

**Overall Progress:** 1.5/10 phases (~15%)

**Progress Bar:**
██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 15%

---

## Performance Metrics

**Project Started:** 2026-01-24
**Phases Completed:** 1/10
**Total Requirements:** 48
**Requirements Completed:** 0/48 (0%)

**Velocity:**
- Phase 1 duration: ~30 minutes (5 plans)
- Plans per day: 5 (Phase 1 completed in single session)
- Requirements per day: N/A (Phase 1 is infrastructure, no v1 requirements)

---

## Accumulated Context

### Key Decisions

| Date | Decision | Rationale | Impact |
|------|----------|-----------|--------|
| 2026-01-24 | Multi-tenant from day one | Avoid costly refactor later | Database schema includes tenant_id on all tables |
| 2026-01-24 | WeasyPrint for PDF generation | Python-native, CSS-based styling | Backend must run on Linux (Railway) |
| 2026-01-24 | Cloudflare R2 for storage | Zero egress fees for photo downloads | S3-compatible client library needed |
| 2026-01-24 | Canvas-based watermarking | Client-side processing, no server load | Frontend handles image manipulation |
| 2026-01-24 | Comprehensive roadmap depth | Complex SaaS with 48 requirements | 10 phases with 5-10 plans each expected |
| 2026-01-24 | Tailwind CSS v4 with Vite plugin | No config file needed, cleaner setup | Use @import "tailwindcss" in CSS |
| 2026-01-24 | React 18 over React 19 | Broader ecosystem compatibility | Better library support currently |
| 2026-01-24 | React Query mobile defaults | staleTime 5min, refetchOnWindowFocus false | Optimized for mobile PWA behavior |
| 2026-01-24 | Path alias @/* for imports | Cleaner imports across frontend | Configured in vite.config.ts and tsconfig |
| 2026-01-24 | Boto3 S3-compatible API for R2 | Mature library over custom HTTP | StorageService uses boto3 client |
| 2026-01-24 | Tenant-scoped object keys | Storage isolation at key level | Format: {tenant_id}/photos/{uuid}.{ext} |
| 2026-01-24 | Presigned URLs for uploads | Client-side upload without proxying | 1-hour expiry for security |
| 2026-01-24 | Singleton storage service | Shared boto3 client instance | get_storage_service() factory pattern |
| 2026-01-24 | Use declared_attr for conditional tenant_id | Clean inheritance without separate base classes | Tenant model excluded from multi-tenant pattern |
| 2026-01-24 | Text columns for location (Phase 1) | Defer PostGIS geometry to later phase | Faster Phase 1, migration path preserved |
| 2026-01-24 | Manual initial migration | Ensure PostGIS extension created first | Explicit control over migration order |
| 2026-01-24 | Vercel SPA fallback route | React Router works on refresh | All routes fallback to /index.html |
| 2026-01-24 | Railway health check at /api/v1/health | Auto-restart on service failure | 30s timeout, ON_FAILURE restart policy |
| 2026-01-24 | GitHub Actions parallel jobs | Faster CI feedback | Frontend and backend tests run independently |
| 2026-01-24 | SQLite for CI backend tests | Avoid PostgreSQL service in CI | sqlite+aiosqlite:///test.db for unit tests |
| 2026-01-24 | Monorepo working-directory in CI | Correct context for npm/pip commands | frontend/ and backend/ roots specified |
| 2026-01-29 | Access token in memory only | Security - not persisted to localStorage | Recovered via refresh endpoint on page reload |
| 2026-01-29 | User info persisted to localStorage | Fast rehydration without API call | Zustand partialize middleware |
| 2026-01-29 | Lazy import for auth store in axios | Avoid circular dependency | Dynamic import in interceptors |
| 2026-01-29 | OAuth2PasswordRequestForm format | FastAPI compatibility | Login sends username/password as form data |
| 2026-01-29 | Token refresh queue mechanism | Handle concurrent requests during refresh | Queue failed requests, retry with new token |
| 2026-01-29 | JWT tokens include type claim | Differentiate access vs refresh tokens | Payload includes type: "access" or "refresh" |
| 2026-01-29 | 15-min access / 7-day refresh expiry | Balance security vs user convenience | Configurable via env settings |
| 2026-01-29 | jwt_secret_key required (no default) | Force secure configuration | Must be set in environment |
| 2026-01-29 | Error messages in Portuguese | Brazilian user base | "Token invalido ou expirado", etc. |
| 2026-01-29 | Rate limiting on login (5/min/IP) | Prevent brute force attacks | SlowAPI decorator on login endpoint |
| 2026-01-29 | httpOnly cookie for refresh token | XSS protection | Cookie path restricted to /api/v1/auth |
| 2026-01-29 | Refresh token rotation | Limit stolen token damage | New refresh token issued on each use |
| 2026-01-29 | Password verify in threadpool | Non-blocking Argon2 | run_in_threadpool for CPU-intensive ops |

### Active TODOs

(None yet - project not started)

### Current Blockers

- External services setup required before Phase 2 - see 01-USER-SETUP.md
  - Vercel project must be created and linked to repository
  - Railway project must be created with PostgreSQL and Redis services
  - Cloudflare R2 bucket must be created with API credentials
  - Environment variables must be configured on each platform

---

## Recent Activity

- **2026-01-24:** Project initialized with PROJECT.md
- **2026-01-24:** Requirements defined (48 v1 requirements across 8 categories)
- **2026-01-24:** Roadmap created (10 phases, comprehensive depth)
- **2026-01-24:** Completed 01-01-PLAN.md - Frontend initialization with React + Vite + TypeScript + Tailwind CSS v4
- **2026-01-24:** Completed 01-02-PLAN.md - Backend initialization with FastAPI + SQLAlchemy
- **2026-01-24:** Completed 01-03-PLAN.md - Database Schema & Migrations with Alembic + 6 core tables
- **2026-01-24:** Completed 01-04-PLAN.md - R2 Storage Service with boto3 + presigned URLs
- **2026-01-24:** Completed 01-05-PLAN.md - Deployment Configuration & CI/CD
- **2026-01-24:** **Phase 1 Complete** - All infrastructure setup finished (5 plans in ~30 minutes)
- **2026-01-29:** Completed 02-01-PLAN.md - Backend Security Core (JWT + Argon2 + FastAPI deps)
- **2026-01-29:** Completed 02-02-PLAN.md - Auth Endpoints (login, logout, refresh with rate limiting)
- **2026-01-29:** Completed 02-04-PLAN.md - Frontend Auth Infrastructure (Axios + Zustand auth store + ProtectedRoute)

---

## Session Continuity

**If starting new session:**
1. Read this STATE.md to understand current position
2. Read ROADMAP.md for phase structure
3. If mid-phase, read current phase plan from .planning/plans/
4. Check PROJECT.md for core value and constraints

**Current session context:**
- Phase 1 complete (5/5 plans finished)
- Phase 2 in progress: 3/6 plans completed (02-01, 02-02, 02-04)
- Remaining: 02-03 (User Management), 02-05 (Login UI), 02-06 (TBD)
- Next: Continue with 02-03 or 02-05
- User action required: Complete 01-USER-SETUP.md before deploying

**Last session:** 2026-01-29
**Stopped at:** Completed 02-02-PLAN.md
**Resume file:** None

---

*State initialized: 2026-01-24*
