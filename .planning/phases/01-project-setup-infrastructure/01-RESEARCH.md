# Phase 1: Project Setup & Infrastructure - Research

**Researched:** 2026-01-24
**Domain:** Full-stack web application infrastructure (React/FastAPI)
**Confidence:** HIGH

## Summary

Phase 1 establishes a production-ready development environment for a multi-tenant SaaS application with a React frontend and FastAPI backend. The research covered the complete modern stack for 2026: Vite 7+ for blazing-fast React development with TypeScript, the latest Tailwind CSS v4 with its new Vite plugin architecture, Zustand for client state management paired with TanStack Query v5 for server state, and React Hook Form for performant forms. On the backend, FastAPI with async SQLAlchemy 2.0, PostgreSQL with PostGIS for geographic data, Alembic for migrations, and Celery + Redis for background tasks (specifically PDF generation with WeasyPrint).

The deployment architecture leverages modern PaaS solutions: Vercel for the frontend (zero-config React deployments), Railway for backend + PostgreSQL + Redis (integrated environment with auto-provisioned services), and Cloudflare R2 for S3-compatible storage with zero egress fees. CI/CD through GitHub Actions completes the pipeline with automated testing and deployment on git push.

Critical findings include the shift to Tailwind CSS v4's Vite plugin approach (no more tailwind.config.js), the importance of async SQLAlchemy 2.0 patterns for FastAPI performance, GeoAlchemy2 for PostGIS integration, and specific CORS/environment variable configurations needed for the Vercel-Railway integration.

**Primary recommendation:** Use the module-functionality project structure for both frontend and backend (organizing by feature/domain rather than file type), adopt async-first patterns throughout the stack, implement multi-tenant isolation via tenant_id discriminator with PostgreSQL Row-Level Security, and configure separate Railway services for FastAPI, PostgreSQL, and Redis rather than Docker Compose.

## Standard Stack

The established libraries/tools for this full-stack domain:

### Core Frontend

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Vite | 7.3+ | Build tool & dev server | Industry standard for React in 2026, 10x faster than CRA, HMR in milliseconds |
| React | 19.0+ | UI framework | Ecosystem standard, concurrent features, RSC support |
| TypeScript | 5.0+ | Type safety | Catches errors at build time, essential for large apps |
| Tailwind CSS | 4.1+ | Utility-first CSS | v4 redesign with Vite plugin, zero-runtime CSS-in-JS alternative |
| Zustand | 5.0+ | Client state management | 30% YoY growth, minimal boilerplate, 1KB gzipped |
| TanStack Query | 5.90+ | Server state management | De facto standard for data fetching, caching, synchronization |
| React Hook Form | 7.71+ | Form state & validation | Performant (uncontrolled inputs), built-in TS support |

### Core Backend

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | 0.115+ | Web framework | Async-first, automatic OpenAPI docs, Pydantic validation |
| SQLAlchemy | 2.0+ | ORM/database toolkit | v2 async support, industry standard for Python ORMs |
| psycopg | 3.0+ | PostgreSQL adapter | Async support, recommended over psycopg2 for new projects |
| Alembic | 1.14+ | Database migrations | Official SQLAlchemy migration tool, auto-generation support |
| Pydantic | 2.0+ | Data validation | Built into FastAPI, dropped v1 support in Python 3.14+ |
| GeoAlchemy2 | 0.18+ | PostGIS integration | Extends SQLAlchemy with spatial types, official PostGIS library |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Celery | 5.4+ | Distributed task queue | Long-running tasks (PDF generation), requires monitoring |
| Redis | 7.0+ | Message broker & cache | Celery broker, session storage, rate limiting |
| WeasyPrint | 68.0+ | HTML to PDF conversion | Server-side PDF generation, CSS Paged Media support |
| boto3 | 1.35+ | AWS SDK (S3-compatible) | Cloudflare R2 access via S3 API |
| Uvicorn | 0.32+ | ASGI server | FastAPI production server, supports workers |

### Development Tools

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| @tanstack/react-query-devtools | 5.90+ | Query debugging | Development only, visualize cache state |
| fastapi-cli | Latest | CLI tooling | Development server, scaffolding |
| ESLint | 9.0+ | Linting | Code quality, integrate with TypeScript parser |
| Prettier | 3.0+ | Code formatting | Consistent style, integrate with Tailwind plugin |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Zustand | Redux Toolkit | Redux has more DevTools but much more boilerplate |
| TanStack Query | SWR | SWR is simpler but less feature-complete (no mutations API) |
| Celery | ARQ | ARQ is async-native but less mature, smaller ecosystem |
| WeasyPrint | Playwright PDF | Playwright requires headless browser, heavier resource usage |
| Requirements.txt | Poetry | Poetry better for complex deps but adds build complexity |

### Installation

**Frontend:**
```bash
# Create Vite project
npm create vite@latest frontend -- --template react-ts
cd frontend

# Install dependencies
npm install @tanstack/react-query zustand react-hook-form
npm install tailwindcss @tailwindcss/vite
npm install @tanstack/react-query-devtools -D
```

**Backend:**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install "fastapi[standard]" sqlalchemy[asyncio] psycopg[binary] alembic
pip install geoalchemy2 celery redis weasyprint boto3 python-multipart
```

## Architecture Patterns

### Recommended Project Structure

**Frontend (Module-Functionality Pattern):**
```
frontend/
├── src/
│   ├── features/           # Feature-based modules
│   │   ├── auth/          # Authentication feature
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── api.ts     # React Query hooks
│   │   │   └── store.ts   # Zustand slice
│   │   ├── reports/       # Reports feature
│   │   └── templates/     # Templates feature
│   ├── shared/            # Shared utilities
│   │   ├── components/    # Reusable UI components
│   │   ├── hooks/         # Shared hooks
│   │   ├── types/         # TypeScript types
│   │   └── utils/         # Helper functions
│   ├── lib/               # Third-party integrations
│   │   ├── queryClient.ts # React Query config
│   │   └── api.ts         # Axios/fetch wrapper
│   ├── App.tsx
│   └── main.tsx
├── public/
├── vite.config.ts
└── package.json
```

**Backend (Module-Functionality Pattern):**
```
backend/
├── app/
│   ├── main.py            # FastAPI app initialization
│   ├── core/              # Core configuration
│   │   ├── config.py      # Settings (Pydantic BaseSettings)
│   │   ├── security.py    # Auth utilities
│   │   └── database.py    # DB session management
│   ├── models/            # SQLAlchemy models
│   │   ├── base.py        # Base model with common fields
│   │   ├── tenant.py
│   │   ├── user.py
│   │   ├── report.py
│   │   └── report_photo.py
│   ├── schemas/           # Pydantic schemas
│   │   ├── tenant.py
│   │   ├── user.py
│   │   └── report.py
│   ├── api/               # API routes
│   │   ├── deps.py        # Shared dependencies
│   │   └── v1/            # API version 1
│   │       ├── routes/
│   │       │   ├── auth.py
│   │       │   ├── reports.py
│   │       │   └── templates.py
│   │       └── api.py     # Router aggregation
│   ├── services/          # Business logic
│   │   ├── report_service.py
│   │   └── storage_service.py
│   ├── tasks/             # Celery tasks
│   │   └── pdf_generation.py
│   └── db/                # Database utilities
│       └── base.py        # Import all models
├── alembic/               # Migration files
│   ├── versions/
│   └── env.py
├── tests/
├── alembic.ini
├── requirements.txt
└── Dockerfile
```

### Pattern 1: Async SQLAlchemy 2.0 with FastAPI

**What:** Async database sessions with dependency injection
**When to use:** All database operations in FastAPI endpoints
**Example:**
```python
# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

DATABASE_URL = "postgresql+psycopg://user:pass@localhost/db"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

# app/api/v1/routes/reports.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

router = APIRouter()

@router.get("/reports")
async def get_reports(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Report))
    reports = result.scalars().all()
    return reports
```
**Source:** [FastAPI with Async SQLAlchemy](https://testdriven.io/blog/fastapi-sqlmodel/)

### Pattern 2: Multi-Tenant Isolation with Row-Level Security

**What:** Tenant discriminator column + PostgreSQL RLS policies
**When to use:** Multi-tenant SaaS from day one
**Example:**
```python
# app/models/base.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class TenantMixin:
    tenant_id = Column(Integer, nullable=False, index=True)

# app/models/report.py
class Report(Base, TenantMixin):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    # tenant_id inherited from TenantMixin

# PostgreSQL RLS policy (via Alembic migration)
"""
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON reports
    USING (tenant_id = current_setting('app.current_tenant')::int);
"""

# app/api/deps.py
async def set_tenant_context(
    tenant_id: int,
    db: AsyncSession = Depends(get_db)
):
    await db.execute(text(f"SET app.current_tenant = {tenant_id}"))
    return tenant_id
```
**Source:** [Multi-Tenancy on PostgreSQL](https://dev.to/shiviyer/how-to-build-multi-tenancy-in-postgresql-for-developing-saas-applications-4b6)

### Pattern 3: PostGIS Geographic Data with GeoAlchemy2

**What:** Store photo locations as PostGIS POINT geometry
**When to use:** Geographic data (photo coordinates)
**Example:**
```python
# app/models/report_photo.py
from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, String

class ReportPhoto(Base, TenantMixin):
    __tablename__ = "report_photos"
    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey("reports.id"))
    storage_key = Column(String)  # R2 object key
    location = Column(Geometry('POINT', srid=4326))  # WGS84 lat/lng

# Alembic migration to enable PostGIS
"""
def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.create_table(
        'report_photos',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('location', Geometry('POINT', srid=4326))
    )
"""
```
**Source:** [GeoAlchemy2 Documentation](https://geoalchemy-2.readthedocs.io/)

### Pattern 4: React Query + Zustand Separation

**What:** Server state in React Query, client state in Zustand
**When to use:** All data fetching (Query) vs UI state (Zustand)
**Example:**
```typescript
// src/features/reports/api.ts
import { useQuery, useMutation } from '@tanstack/react-query';

export const useReports = () => {
  return useQuery({
    queryKey: ['reports'],
    queryFn: async () => {
      const res = await fetch('/api/v1/reports');
      return res.json();
    },
  });
};

// src/features/reports/store.ts
import { create } from 'zustand';

interface ReportUIState {
  selectedReportId: number | null;
  isFilterOpen: boolean;
  setSelectedReport: (id: number | null) => void;
  toggleFilter: () => void;
}

export const useReportStore = create<ReportUIState>((set) => ({
  selectedReportId: null,
  isFilterOpen: false,
  setSelectedReport: (id) => set({ selectedReportId: id }),
  toggleFilter: () => set((state) => ({ isFilterOpen: !state.isFilterOpen })),
}));

// Usage: useQuery for server data, useStore for UI state
const reports = useReports();
const { selectedReportId, setSelectedReport } = useReportStore();
```
**Source:** [Zustand + React Query: A New Approach](https://medium.com/@freeyeon96/zustand-react-query-new-state-management-7aad6090af56)

### Pattern 5: Celery Task for PDF Generation

**What:** Offload WeasyPrint PDF generation to background worker
**When to use:** Any task > 5 seconds (PDF generation, bulk exports)
**Example:**
```python
# app/tasks/pdf_generation.py
from celery import Celery
from weasyprint import HTML
from app.services.storage_service import upload_to_r2

celery_app = Celery('tasks', broker='redis://localhost:6379/0')

@celery_app.task
def generate_report_pdf(report_id: int):
    # Fetch report data
    html_content = render_report_template(report_id)

    # Generate PDF
    pdf_bytes = HTML(string=html_content).write_pdf()

    # Upload to R2
    key = f"reports/{report_id}/report.pdf"
    upload_to_r2(key, pdf_bytes)

    return {"status": "complete", "key": key}

# app/api/v1/routes/reports.py
@router.post("/reports/{id}/generate-pdf")
async def trigger_pdf_generation(id: int):
    task = generate_report_pdf.delay(id)
    return {"task_id": task.id, "status": "processing"}
```
**Source:** [Asynchronous Tasks with FastAPI and Celery](https://testdriven.io/blog/fastapi-and-celery/)

### Pattern 6: Cloudflare R2 with boto3

**What:** S3-compatible storage with zero egress fees
**When to use:** Photo uploads, PDF storage
**Example:**
```python
# app/services/storage_service.py
import boto3
from app.core.config import settings

s3_client = boto3.client(
    's3',
    endpoint_url=f'https://{settings.CLOUDFLARE_ACCOUNT_ID}.r2.cloudflarestorage.com',
    aws_access_key_id=settings.R2_ACCESS_KEY_ID,
    aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
    region_name='auto',  # Required by SDK but not used
)

def upload_photo(file_bytes: bytes, key: str) -> str:
    s3_client.put_object(
        Bucket=settings.R2_BUCKET_NAME,
        Key=key,
        Body=file_bytes,
        ContentType='image/jpeg',
    )
    return key

def generate_presigned_url(key: str, expires_in: int = 3600) -> str:
    return s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': settings.R2_BUCKET_NAME, 'Key': key},
        ExpiresIn=expires_in,
    )
```
**Source:** [Cloudflare R2 boto3 Documentation](https://developers.cloudflare.com/r2/examples/aws/boto3/)

### Anti-Patterns to Avoid

- **Blocking operations in async endpoints:** Never use synchronous DB calls (like `session.query()`) inside `async def` endpoints—use async SQLAlchemy 2.0 patterns
- **Endpoint-to-endpoint calls:** Don't call one FastAPI endpoint from another; extract shared logic to service layer
- **Missing tenant context:** Don't forget to set tenant_id on every create operation; use middleware or dependency injection
- **Synchronous Celery with async FastAPI:** Don't mix sync Celery tasks with async FastAPI without proper thread handling
- **Hard-coding environment variables:** Never commit `.env` files; use Vercel/Railway dashboard for production secrets
- **Tailwind v3 configuration:** Don't create `tailwind.config.js` with Tailwind v4—use the Vite plugin approach
- **Multiple Docker Compose services to Railway:** Don't try to deploy docker-compose.yml directly; reconstruct as separate Railway services

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Form validation | Custom validation logic | React Hook Form + Zod/Yup | Edge cases: nested fields, async validation, field arrays, error focus management |
| Data caching & sync | Custom fetch wrapper | TanStack Query | Stale-while-revalidate, deduplication, background refetch, optimistic updates, retry logic |
| PDF generation | Custom HTML renderer | WeasyPrint | CSS Paged Media, pagination, headers/footers, print-specific layout |
| Geographic queries | Custom lat/lng math | PostGIS functions | Spatial indexing, distance calculations, polygon containment, projections |
| Database migrations | Manual SQL scripts | Alembic autogenerate | Detects model changes, generates migration code, handles dependencies, rollback support |
| S3 integration | Custom HTTP client | boto3 | Multipart uploads, presigned URLs, retry logic, authentication |
| State management | Context API for everything | Zustand for client, Query for server | Context causes re-renders; Query handles cache invalidation |
| Background jobs | Threading in FastAPI | Celery + Redis | Distributed workers, retry logic, monitoring (Flower), scheduled tasks |

**Key insight:** Infrastructure-level problems (storage, caching, migrations, background jobs) have battle-tested solutions with years of production hardening. Custom implementations miss edge cases that only emerge at scale (connection pooling, retry logic, race conditions).

## Common Pitfalls

### Pitfall 1: Async/Sync Confusion in FastAPI

**What goes wrong:** Using blocking operations (like `requests.get()`, synchronous DB calls, file I/O) inside `async def` endpoints blocks the event loop, preventing FastAPI from handling other requests.

**Why it happens:** Python doesn't enforce async consistency—synchronous code runs in async functions but defeats the purpose. Developers unfamiliar with async patterns mix sync libraries with async endpoints.

**How to avoid:**
- Use async libraries: `httpx` instead of `requests`, async SQLAlchemy 2.0, `aiofiles` for file I/O
- If you must use sync libraries, run them in a thread pool: `await run_in_threadpool(sync_function)`
- Check library docs for async support before adding dependencies

**Warning signs:**
- Slow response times under load despite low CPU usage
- Single requests block all others
- Libraries like `requests`, `psycopg2` (non-async version) in requirements.txt

**Source:** [10 Common FastAPI Mistakes That Hurt Performance](https://medium.com/@connect.hashblock/10-common-fastapi-mistakes-that-hurt-performance-and-how-to-fix-them-72b8553fe8e7)

### Pitfall 2: Vercel-Railway CORS Configuration

**What goes wrong:** CORS errors when frontend (Vercel) calls backend (Railway) in production, even though it works locally. Browser blocks requests with "No 'Access-Control-Allow-Origin' header".

**Why it happens:** Vercel provides preview deployments with different URLs per branch, and Railway generates new URLs per service. The backend CORS configuration must allow the exact origin from the browser's Origin header.

**How to avoid:**
```python
# app/main.py - WRONG
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.vercel.app"],  # Doesn't cover previews
)

# CORRECT
from app.core.config import settings

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),  # From env var
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Railway environment variables:
# CORS_ORIGINS=https://myapp.vercel.app,https://*.vercel.app
```

Use Vercel's Railway integration to auto-inject environment variables into preview deployments.

**Warning signs:**
- Works in development (localhost), fails in production
- Error: "CORS policy: No 'Access-Control-Allow-Origin' header"
- Preflight OPTIONS requests return 403

**Source:** [CORS Issue: Vercel Frontend to Railway Backend](https://station.railway.com/questions/cors-issue-post-request-blocked-from-ve-6920650c)

### Pitfall 3: Tailwind CSS v4 Migration Confusion

**What goes wrong:** Following outdated Tailwind v3 guides creates `tailwind.config.js` and uses PostCSS setup, but Tailwind v4 (released 2025) changed to a Vite plugin architecture. Styles don't load or throw build errors.

**Why it happens:** AI assistants and older tutorials reference Tailwind v3 patterns. Developers install `tailwindcss` 4.x but follow v3 setup instructions.

**How to avoid:**
```javascript
// vite.config.ts - v4 CORRECT way
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'  // New plugin

export default defineConfig({
  plugins: [react(), tailwindcss()],
})

// src/index.css - v4 CORRECT way
@import "tailwindcss";  // Single import, no @tailwind directives

// DON'T create tailwind.config.js (v3 pattern)
// DON'T use postcss.config.js
```

Check official Tailwind docs for Vite setup, not blog posts from 2024 or earlier.

**Warning signs:**
- `@tailwind` directives don't work
- Need to create `tailwind.config.js` manually
- PostCSS errors about Tailwind plugin

**Source:** [Installing Tailwind CSS with Vite](https://tailwindcss.com/docs) (Official v4 docs)

### Pitfall 4: Multi-Tenant Data Leakage

**What goes wrong:** Queries return data from all tenants instead of just the current tenant's data. A user from Company A sees Company B's reports.

**Why it happens:** Forgetting to add `.filter(tenant_id=current_tenant)` to every query. Copy-pasting code without checking tenant filtering. Admin queries bypass tenant context.

**How to avoid:**
```python
# WRONG - No tenant filtering
@router.get("/reports")
async def get_reports(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Report))
    return result.scalars().all()  # Returns ALL tenants' data!

# CORRECT - Use dependency injection for tenant context
from app.api.deps import get_current_tenant

@router.get("/reports")
async def get_reports(
    db: AsyncSession = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant),
):
    result = await db.execute(
        select(Report).where(Report.tenant_id == tenant_id)
    )
    return result.scalars().all()

# BEST - Use PostgreSQL Row-Level Security
# Set in middleware: await db.execute(text(f"SET app.current_tenant = {tenant_id}"))
# RLS policy automatically filters all queries
```

Write tests that create multiple tenants and verify data isolation.

**Warning signs:**
- No `.filter(tenant_id=...)` in queries
- Tenant ID comes from request body instead of JWT token
- Admin endpoints bypass tenant checks

**Source:** [Multi-Tenancy on PostgreSQL](https://dev.to/shiviyer/how-to-build-multi-tenancy-in-postgresql-for-developing-saas-applications-4b6)

### Pitfall 5: Alembic Autogenerate Missing PostGIS Extension

**What goes wrong:** Alembic autogenerate creates migration with `Geometry` column but doesn't enable PostGIS extension. Migration fails with "type 'geometry' does not exist".

**Why it happens:** Alembic detects model changes but doesn't detect missing PostgreSQL extensions. PostGIS must be enabled before creating geometry columns.

**How to avoid:**
```python
# alembic/versions/xxxx_enable_postgis.py - Create BEFORE models
def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

def downgrade():
    op.execute("DROP EXTENSION IF EXISTS postgis")

# alembic/versions/yyyy_create_report_photos.py - Then create tables
def upgrade():
    op.create_table(
        'report_photos',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('location', Geometry('POINT', srid=4326)),
    )
```

Always create extension migration first, then run `alembic revision --autogenerate` for models.

**Warning signs:**
- Error: "type 'geometry' does not exist"
- Migration creates `geoalchemy2.Geometry` columns
- PostGIS extension not in any migration

**Source:** [Using Extensions with SQLAlchemy](https://atlasgo.io/guides/orms/sqlalchemy/extensions)

### Pitfall 6: Vite Production Build Path Issues

**What goes wrong:** React app works in development but shows blank page in production. Browser console shows 404 errors for JavaScript/CSS files.

**Why it happens:** Vite uses absolute paths by default (`/assets/...`). When deployed to a subdirectory or behind a reverse proxy, paths break. `base: '/'` assumes root deployment.

**How to avoid:**
```typescript
// vite.config.ts
export default defineConfig({
  base: './',  // Use relative paths for assets
  plugins: [react()],
})

// For subdirectory deployment (e.g., /app/)
export default defineConfig({
  base: '/app/',  // Must match deployment path
})
```

Test production build locally: `npm run build && npx serve dist`

**Warning signs:**
- Dev works (`npm run dev`), production blank
- 404 errors for `/assets/index-*.js`
- Works on root domain, breaks on subdirectory

**Source:** [Vite Building for Production](https://vite.dev/guide/build)

### Pitfall 7: Railway Service Configuration Confusion

**What goes wrong:** Deploying a monorepo to Railway with both frontend and backend—Railway builds the wrong service or builds everything together. Environment variables leak between services.

**Why it happens:** Railway auto-detects project type but gets confused with monorepos. Developers expect Docker Compose behavior (one file deploys everything) but Railway requires separate services.

**How to avoid:**
```
# Project structure
/
├── frontend/          # Separate Railway service
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile (optional)
├── backend/           # Separate Railway service
│   ├── requirements.txt
│   ├── main.py
│   └── Dockerfile
└── README.md

# Railway setup:
1. Create "Backend" service → Connect GitHub → Set root directory: /backend
2. Create "Frontend" service → Connect GitHub → Set root directory: /frontend
3. Create PostgreSQL database → Link to Backend service
4. Create Redis instance → Link to Backend service
5. Set environment variables per service (don't share secrets)
```

Don't try to deploy `docker-compose.yml` directly; Railway doesn't support it.

**Warning signs:**
- Railway tries to build entire repo as one service
- Frontend gets Python dependencies
- "No build command found" errors

**Source:** [Deploy React+FastAPI+PostgreSQL+Celery on Railway](https://station.railway.com/questions/deploy-react-fastapi-postgresql-celery-o-d1e8b667)

### Pitfall 8: Environment Variables Undefined in Vercel

**What goes wrong:** `import.meta.env.VITE_API_URL` is `undefined` in production but works locally. API requests fail silently.

**Why it happens:** Vite only exposes variables prefixed with `VITE_` to the browser bundle. Variables added to Vercel after deployment aren't available until redeployed. `.env` files aren't deployed (correctly excluded from git).

**How to avoid:**
```typescript
// .env.local (local development, NOT in git)
VITE_API_URL=http://localhost:8000

// Vercel Dashboard → Project Settings → Environment Variables:
// VITE_API_URL=https://backend.railway.app
// ⚠️ Must redeploy after adding variables

// src/lib/api.ts - Add fallback for debugging
const API_URL = import.meta.env.VITE_API_URL || 'MISSING_API_URL';

if (API_URL === 'MISSING_API_URL') {
  console.error('VITE_API_URL not configured!');
}
```

After adding variables in Vercel dashboard, trigger redeployment (commit or manual redeploy).

**Warning signs:**
- `import.meta.env.VITE_*` is `undefined` in production
- Network tab shows requests to `undefined/api/...`
- Works locally, fails in preview/production

**Source:** [Setting up Environment Variables in React-Vite app on Vercel](https://medium.com/@ayushag.cse/setting-up-environment-variables-in-react-vite-app-and-hosting-it-on-vercel-1762280fd48e)

## Code Examples

Verified patterns from official sources:

### FastAPI Application Initialization

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```
**Source:** [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)

### React Query Client Setup

```typescript
// src/lib/queryClient.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

// src/main.tsx
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { queryClient } from './lib/queryClient';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  </React.StrictMode>
);
```
**Source:** [TanStack Query Installation](https://tanstack.com/query/v5/docs/framework/react/installation)

### Alembic Configuration for Async SQLAlchemy

```python
# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from app.core.config import settings
from app.db.base import Base  # Import all models

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())
```
**Source:** [FastAPI with Async SQLAlchemy and Alembic](https://testdriven.io/blog/fastapi-sqlmodel/)

### Zustand Store with TypeScript

```typescript
// src/features/reports/store.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface ReportFilter {
  startDate: Date | null;
  endDate: Date | null;
  status: 'draft' | 'published' | 'all';
}

interface ReportUIState {
  selectedReportId: number | null;
  filters: ReportFilter;
  isFilterOpen: boolean;
  setSelectedReport: (id: number | null) => void;
  setFilters: (filters: Partial<ReportFilter>) => void;
  toggleFilter: () => void;
  resetFilters: () => void;
}

const initialFilters: ReportFilter = {
  startDate: null,
  endDate: null,
  status: 'all',
};

export const useReportStore = create<ReportUIState>()(
  devtools(
    persist(
      (set) => ({
        selectedReportId: null,
        filters: initialFilters,
        isFilterOpen: false,
        setSelectedReport: (id) => set({ selectedReportId: id }),
        setFilters: (newFilters) =>
          set((state) => ({ filters: { ...state.filters, ...newFilters } })),
        toggleFilter: () => set((state) => ({ isFilterOpen: !state.isFilterOpen })),
        resetFilters: () => set({ filters: initialFilters }),
      }),
      { name: 'report-storage' }
    )
  )
);
```
**Source:** [Zustand Documentation](https://zustand.docs.pmnd.rs/)

### React Hook Form with TypeScript

```typescript
// src/features/reports/components/ReportForm.tsx
import { useForm } from 'react-hook-form';

interface ReportFormData {
  title: string;
  description: string;
  projectId: number;
}

export const ReportForm = () => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ReportFormData>();

  const onSubmit = async (data: ReportFormData) => {
    await fetch('/api/v1/reports', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input
        {...register('title', { required: 'Title is required' })}
        placeholder="Report Title"
      />
      {errors.title && <span>{errors.title.message}</span>}

      <textarea
        {...register('description', { minLength: 10 })}
        placeholder="Description"
      />
      {errors.description && <span>Description must be at least 10 characters</span>}

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Saving...' : 'Save Report'}
      </button>
    </form>
  );
};
```
**Source:** [React Hook Form TypeScript](https://react-hook-form.com/ts)

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Create React App (CRA) | Vite | 2023-2024 | 10x faster dev server, instant HMR, smaller bundles |
| Tailwind v3 + PostCSS | Tailwind v4 + Vite plugin | 2025 | Simpler setup, no config file, faster builds |
| SQLAlchemy 1.4 sync | SQLAlchemy 2.0 async | 2023 | Non-blocking DB calls, better FastAPI performance |
| Pydantic v1 | Pydantic v2 | 2023 | 5-50x faster validation, breaking API changes |
| React Query v4 | TanStack Query v5 | 2023 | Renamed package, improved TypeScript, new features |
| Zustand v4 | Zustand v5 | 2024 | TypeScript improvements, middleware updates |
| Python 3.8 | Python 3.10+ (FastAPI) | 2025 | FastAPI dropped 3.8, added 3.14 support |
| psycopg2 | psycopg 3 | 2023 | Async support, better performance |
| Redux Toolkit | Zustand/Jotai | 2022-2024 | Less boilerplate, smaller bundle size |
| Context API for everything | Zustand (client) + Query (server) | 2023-2025 | Avoid re-render issues, proper cache invalidation |

**Deprecated/outdated:**
- **Create React App:** React team removed it from docs (2024), recommends frameworks (Next.js) or Vite
- **Pydantic v1:** No longer supported for Python 3.14+, FastAPI will drop support soon
- **Tailwind v3 config files:** tailwind.config.js pattern replaced by Vite plugin in v4
- **SQLAlchemy 1.4 style:** Still works but v2 style recommended (async, better typing)
- **requirements.txt for complex projects:** Many teams switching to Poetry/uv for better dependency resolution

## Open Questions

Things that couldn't be fully resolved:

1. **Celery vs ARQ for FastAPI background tasks**
   - What we know: Celery is mature with monitoring (Flower), ARQ is async-native and simpler
   - What's unclear: Performance comparison for PDF generation workload, production reliability of ARQ
   - Recommendation: Use Celery for Phase 1 (proven solution), evaluate ARQ in later phase if Celery adds complexity

2. **Poetry vs pip for Python dependency management**
   - What we know: Poetry has better dependency resolution and lock files, pip+requirements.txt simpler for deployment
   - What's unclear: Railway support for Poetry (needs `requirements.txt` for auto-detection)
   - Recommendation: Start with requirements.txt for simplicity, migrate to Poetry if dependency conflicts arise (can export: `poetry export -f requirements.txt`)

3. **Monorepo vs separate repos for frontend/backend**
   - What we know: Monorepo simplifies cross-cutting changes, complicates CI/CD (need path filters)
   - What's unclear: GitHub Actions caching efficiency with monorepo, Railway deployment complexity
   - Recommendation: Use monorepo for Phase 1 (simpler local dev), separate repos if CI/CD becomes bottleneck

4. **Optimal Celery worker configuration for Railway**
   - What we know: Railway runs containers, Celery can run multiple workers per container
   - What's unclear: Best worker count for Railway's resource limits, autoscaling strategy
   - Recommendation: Start with 2 workers per Celery service, monitor with Flower, scale horizontally (more services) vs vertically (more workers)

5. **Row-Level Security vs application-level filtering for multi-tenancy**
   - What we know: RLS enforces at database level (safer), application-level filtering more flexible
   - What's unclear: Performance impact of RLS on complex queries, compatibility with async SQLAlchemy
   - Recommendation: Use application-level filtering (`.where(tenant_id=...)`) for Phase 1, add RLS policies in security audit phase

## Sources

### Primary (HIGH confidence)

- [Tailwind CSS v4 Installation with Vite](https://tailwindcss.com/docs) - Official docs, verified v4.1 release
- [FastAPI Tutorial: Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/) - Official project structure guidance
- [Cloudflare R2 boto3 Examples](https://developers.cloudflare.com/r2/examples/aws/boto3/) - Official R2 configuration
- [Railway FastAPI Deployment Guide](https://docs.railway.com/guides/fastapi) - Official Railway docs
- [GeoAlchemy2 Documentation](https://geoalchemy-2.readthedocs.io/) - Official PostGIS integration library
- [TanStack Query Installation](https://tanstack.com/query/v5/docs/framework/react/installation) - Official React Query v5 docs
- [Zustand Documentation](https://zustand.docs.pmnd.rs/) - Official state management docs
- [React Hook Form](https://react-hook-form.com/) - Official form library docs
- [Vite Building for Production](https://vite.dev/guide/build) - Official build configuration

### Secondary (MEDIUM confidence)

- [GitHub Actions in 2026: Complete Guide to Monorepo CI/CD](https://dev.to/pockit_tools/github-actions-in-2026-the-complete-guide-to-monorepo-cicd-and-self-hosted-runners-1jop) - Recent (1 week old), comprehensive
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices) - Community-maintained, widely referenced
- [TestDriven.io: FastAPI with Async SQLAlchemy and Alembic](https://testdriven.io/blog/fastapi-sqlmodel/) - Professional tutorial site
- [Multi-Tenancy on PostgreSQL](https://dev.to/shiviyer/how-to-build-multi-tenancy-in-postgresql-for-developing-saas-applications-4b6) - Detailed architectural guidance
- [Complete Guide to Setting Up React with TypeScript and Vite (2026)](https://oneuptime.com/blog/post/2026-01-08-react-typescript-vite-production-setup/view) - Recent guide (Jan 2026)
- [Vercel Vite Framework Docs](https://vercel.com/docs/frameworks/frontend/vite) - Official Vercel integration
- [Stop Fighting Deployment Hell: MERN on Vercel + Railway](https://medium.com/codetodeploy/stop-fighting-deployment-hell-your-2025-guide-to-mern-on-vercel-railway-840453de0649) - Vercel-Railway integration guide

### Tertiary (LOW confidence - marked for validation)

- Various Medium articles on FastAPI performance (need to verify benchmarks in production)
- Community discussions on Celery vs ARQ (anecdotal, no official benchmarks)
- GitHub issue threads on Tailwind v4 migration (user reports, not official guidance)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries verified via official docs, npm/PyPI latest versions checked (Jan 2026)
- Architecture: HIGH - Patterns sourced from official FastAPI/React Query/SQLAlchemy documentation
- Pitfalls: MEDIUM-HIGH - Common issues verified via multiple sources (official docs + community discussions)
- Deployment: MEDIUM - Vercel/Railway guidance from official docs, but monorepo CI/CD patterns from community sources

**Research date:** 2026-01-24
**Valid until:** 2026-02-24 (30 days - stable ecosystem, but check for new releases before implementation)

**Version notes:**
- Tailwind CSS v4 released recently (2025), breaking change from v3 config
- Vite 8 beta available (Rolldown-powered) but recommend stable Vite 7.x for Phase 1
- TanStack Query v5 current, renamed from React Query v4
- Python 3.14 support added to FastAPI in 2025, 3.8 dropped
- SQLAlchemy 2.0 async patterns now standard (2.0 released 2023)
