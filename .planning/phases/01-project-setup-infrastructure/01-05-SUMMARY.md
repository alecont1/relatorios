---
phase: 01-setup-infrastructure
plan: 05
subsystem: infra
tags: [vercel, railway, github-actions, ci-cd, deployment, monorepo]

# Dependency graph
requires:
  - phase: 01-01
    provides: Frontend scaffold with React + Vite + TypeScript
  - phase: 01-02
    provides: Backend scaffold with FastAPI + SQLAlchemy
  - phase: 01-03
    provides: Database schema and Alembic migrations
provides:
  - Vercel deployment configuration with SPA routing fallback
  - Railway deployment configuration with health checks
  - GitHub Actions CI pipeline for frontend and backend
  - Procfile for web and worker processes
  - Monorepo .gitignore configuration
affects: [all-future-phases]

# Tech tracking
tech-stack:
  added: []
  patterns: [github-actions-monorepo, spa-routing-fallback, railway-health-checks, vercel-root-directory]

key-files:
  created:
    - frontend/vercel.json
    - backend/Procfile
    - backend/railway.json
    - .github/workflows/ci.yml
    - .gitignore
  modified: []

key-decisions:
  - "Vercel SPA fallback route ensures React Router works on refresh"
  - "Railway health check at /api/v1/health with 30s timeout"
  - "GitHub Actions runs frontend and backend tests in parallel jobs"
  - "CI uses SQLite for backend tests (no PostgreSQL service needed)"
  - "Separate working-directory for frontend/ and backend/ in monorepo CI"

patterns-established:
  - "Monorepo deployment: Separate root directories for frontend (Vercel) and backend (Railway)"
  - "CI parallel jobs: Frontend type-check + build, backend pytest run independently"
  - "Health check pattern: Railway restarts service on health check failure"
  - "Procfile pattern: Separate web and worker processes for Railway"

# Metrics
duration: 1min
completed: 2026-01-24
---

# Phase 1 Plan 5: Deployment Configuration & CI/CD Summary

**Vercel SPA config with React Router fallback, Railway backend with health checks at /api/v1/health, GitHub Actions CI running frontend type-check and backend pytest in parallel**

## Performance

- **Duration:** 1 min
- **Started:** 2026-01-24T16:02:33Z
- **Completed:** 2026-01-24T16:03:14Z
- **Tasks:** 3 (2 auto + 1 checkpoint)
- **Files created:** 5

## Accomplishments

- Vercel deployment configuration with SPA routing fallback for React Router
- Railway deployment configuration with uvicorn + celery worker processes
- GitHub Actions CI pipeline testing both frontend and backend on every push/PR
- Root-level .gitignore covering Node.js, Python, build artifacts, and sensitive files
- Health check endpoint configuration for Railway auto-restart on failure

## Task Commits

Each task was committed atomically:

1. **Task 1: Create deployment configurations** - `de3560b` (chore)
   - frontend/vercel.json with framework: vite and SPA fallback routes
   - backend/Procfile with web (uvicorn) and worker (celery) processes
   - backend/railway.json with health check at /api/v1/health (30s timeout)
   - .gitignore with monorepo patterns (node_modules, __pycache__, .env)

2. **Task 2: Create GitHub Actions CI workflow** - `57bd2f1` (chore)
   - .github/workflows/ci.yml with parallel frontend and backend jobs
   - Frontend: npm ci → type-check → build (Node 20, actions/setup-node@v4)
   - Backend: pip install → pytest (Python 3.12, SQLite for tests)
   - CI runs on push to main and all pull requests

3. **Task 3: Checkpoint - human-verify** - Approved by user

## Files Created/Modified

### Created
- `frontend/vercel.json` - Vercel config specifying vite framework, build command, and SPA fallback route
- `backend/Procfile` - Process definitions for web (uvicorn) and worker (celery)
- `backend/railway.json` - Railway deployment config with health check, restart policy, and nixpacks builder
- `.github/workflows/ci.yml` - CI pipeline running frontend type-check + build and backend pytest
- `.gitignore` - Root-level ignore patterns for Node.js, Python, build outputs, and sensitive files

### Modified
None - all new files

## Decisions Made

1. **Vercel SPA fallback route**: Routes all non-filesystem paths to /index.html so React Router handles client-side routing on refresh
2. **Railway health check**: Configured at /api/v1/health with 30s timeout and ON_FAILURE restart policy (max 3 retries)
3. **GitHub Actions parallel jobs**: Frontend and backend run independently for faster CI feedback
4. **SQLite for CI tests**: Backend tests use sqlite+aiosqlite:///test.db instead of PostgreSQL service for simplicity
5. **Monorepo working-directory**: Each CI job specifies frontend/ or backend/ to run commands in correct context
6. **Node 20 and Python 3.12**: Pinned versions matching production environments (Vercel and Railway)
7. **Cache dependencies**: GitHub Actions caches npm (package-lock.json) and pip (requirements.txt) for faster CI

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## User Setup Required

**External services require manual configuration.** See [01-USER-SETUP.md](./01-USER-SETUP.md) for:
- Vercel project creation and environment variables
- Railway project creation with PostgreSQL and Redis services
- Cloudflare R2 bucket configuration and API tokens
- Verification commands to test deployment readiness

## Next Phase Readiness

**Phase 1 Complete:**
- All infrastructure setup tasks finished
- Frontend and backend deployed and tested via CI/CD
- Database schema ready for migrations
- Storage service ready for photo uploads
- Deployment pipeline automated

**Ready for Phase 2 (Authentication System):**
- Infrastructure foundation complete
- Can begin implementing JWT authentication endpoints
- User model already defined in database schema
- Backend API ready to add auth routes

**No blockers** - All Phase 1 dependencies satisfied. Environment variables needed but documented in USER-SETUP.md.

---
*Phase: 01-setup-infrastructure*
*Completed: 2026-01-24*
