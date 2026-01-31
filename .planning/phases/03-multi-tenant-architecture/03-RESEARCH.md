# Phase 3: Multi-Tenant Architecture - Research

**Researched:** 2026-01-31
**Domain:** Multi-tenant SaaS data isolation, branding, and tenant management
**Confidence:** HIGH

## Summary

Multi-tenant architecture implementation for a FastAPI + SQLAlchemy + React stack requires careful attention to three critical domains: tenant data isolation, tenant CRUD operations with RBAC, and dynamic branding. The codebase already has excellent foundations with tenant_id columns on all tables and JWT tokens carrying tenant context.

The standard approach for this stack is application-level tenant filtering (not PostgreSQL RLS for Phase 3) using middleware or dependency injection to automatically scope database queries. Tenant branding is best achieved with CSS variables and dynamic theming in React, while file storage follows a prefix-based organization pattern in Cloudflare R2 (already implemented).

**Primary recommendation:** Build superadmin tenant CRUD endpoints, add a query dependency that auto-filters by tenant_id for non-superadmin users, extend the Tenant model with branding fields, create tenant settings UI with logo upload to R2, and implement CSS variable-based dynamic theming in React.

## Standard Stack

The established libraries/tools for multi-tenant FastAPI + React applications:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | 0.110+ | API framework with dependency injection | Native support for request-scoped dependencies ideal for tenant context |
| SQLAlchemy 2.0 | 2.0+ | ORM with async support | Proven pattern for multi-tenant with tenant_id filtering |
| Zustand | 4.5+ | React state management | Lightweight, perfect for tenant context in React apps |
| CSS Variables | Native | Dynamic theming | Browser-native, no library needed, works seamlessly with Tailwind |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| sqlalchemy-filters | 0.13+ | Query filtering utility | Optional - manual WHERE clauses sufficient for this phase |
| Pillow | 10.0+ | Image processing | For logo validation and thumbnail generation |
| react-colorful | 5.6+ | Color picker component | Tenant brand color configuration UI |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Application-level filtering | PostgreSQL RLS | RLS adds complexity for Phase 3; better for later when query volume increases and risk of filter bugs grows |
| CSS Variables | styled-components | CSS variables are simpler, faster, and work better with Tailwind CSS v4 already in use |
| Single bucket with prefixes | Separate R2 buckets per tenant | Prefix-based approach already implemented in storage service - no change needed |

**Installation:**
```bash
# Backend (already have FastAPI + SQLAlchemy)
pip install Pillow  # For logo validation

# Frontend (already have React + Zustand + Tailwind)
npm install react-colorful  # For color picker
npm install @heroicons/react  # For UI icons
```

## Architecture Patterns

### Recommended Project Structure
```
backend/app/
├── api/v1/routes/
│   ├── tenants.py           # NEW: Superadmin tenant CRUD
│   └── tenant_settings.py   # NEW: Tenant admin branding config
├── core/
│   ├── deps.py              # EXTEND: Add get_tenant_filter dependency
│   └── middleware.py        # OPTIONAL: Tenant context middleware
├── models/
│   └── tenant.py            # EXTEND: Add branding fields
└── services/
    └── storage.py           # ALREADY DONE: Tenant-scoped R2 keys

frontend/src/
├── stores/
│   └── tenantStore.ts       # NEW: Tenant branding state
├── hooks/
│   └── useTheme.ts          # NEW: Apply CSS variables
├── pages/
│   ├── TenantsPage.tsx      # NEW: Superadmin tenant management
│   └── TenantSettingsPage.tsx # NEW: Tenant branding config
└── styles/
    └── theme.css            # NEW: CSS variable definitions
```

### Pattern 1: Automatic Tenant Filtering with FastAPI Dependencies

**What:** Use FastAPI's dependency injection to automatically scope queries to the current user's tenant_id

**When to use:** For all routes except superadmin tenant management

**Example:**
```python
# backend/app/core/deps.py
from typing import Annotated
from fastapi import Depends
from sqlalchemy import Select
from app.core.deps import get_current_user
from app.models.user import User

def get_tenant_filter(
    current_user: Annotated[User, Depends(get_current_user)]
) -> uuid.UUID:
    """
    Return current user's tenant_id for query filtering.

    Usage in routes:
        tenant_id: Annotated[uuid.UUID, Depends(get_tenant_filter)]
        query = select(Template).where(Template.tenant_id == tenant_id)
    """
    return current_user.tenant_id

def require_superadmin(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Dependency for superadmin-only routes."""
    if current_user.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado - apenas superadmin"
        )
    return current_user
```

**Source:** [FastAPI Multi Tenancy - Medium](https://sayanc20002.medium.com/fastapi-multi-tenancy-bf7c387d07b0), [Multitenancy with FastAPI - MergeBoard](https://mergeboard.com/blog/6-multitenancy-fastapi-sqlalchemy-postgresql/)

### Pattern 2: Tenant Model Extensions for Branding

**What:** Extend the Tenant model with branding and contact fields

**When to use:** Phase 3 implementation

**Example:**
```python
# backend/app/models/tenant.py
class Tenant(Base):
    __tablename__ = "tenants"

    # Existing fields
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # NEW: Branding fields (TNNT-03, TNNT-04)
    logo_primary_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    logo_secondary_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    brand_color_primary: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)  # #RRGGBB
    brand_color_secondary: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    brand_color_accent: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)

    # NEW: Contact fields (TNNT-05)
    contact_address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
```

**Source:** Codebase analysis + [Multi-Tenant Architecture with FastAPI - Medium](https://medium.com/@koushiksathish3/multi-tenant-architecture-with-fastapi-design-patterns-and-pitfalls-aa3f9e75bf8c)

### Pattern 3: Dynamic CSS Variables for Tenant Branding

**What:** Load tenant branding from API and apply as CSS variables to enable dynamic theming

**When to use:** After tenant authentication, apply theme to entire React app

**Example:**
```typescript
// frontend/src/hooks/useTheme.ts
import { useEffect } from 'react'
import { useTenantStore } from '@/stores/tenantStore'

export function useTheme() {
  const { branding } = useTenantStore()

  useEffect(() => {
    if (!branding) return

    const root = document.documentElement

    // Apply tenant brand colors as CSS variables
    if (branding.colorPrimary) {
      root.style.setProperty('--color-primary', branding.colorPrimary)
    }
    if (branding.colorSecondary) {
      root.style.setProperty('--color-secondary', branding.colorSecondary)
    }
    if (branding.colorAccent) {
      root.style.setProperty('--color-accent', branding.colorAccent)
    }
  }, [branding])
}

// Usage in App.tsx
function App() {
  useTheme()  // Apply theme globally
  return <Router>...</Router>
}
```

**Source:** [Dynamic Theming in React Using Context API](https://dev.to/yorgie7/dynamic-theming-in-react-using-context-api-multi-brand-56l1), [Dynamic Branding With React and CSS Variables](https://dev.to/osninja_io/dynamic-branding-with-react-and-scss-css-variables-5524)

### Pattern 4: Logo Upload with R2 Presigned URLs

**What:** Reuse existing storage service pattern for logo uploads with tenant-specific keys

**When to use:** Tenant settings form logo upload

**Example:**
```python
# backend/app/api/v1/routes/tenant_settings.py
from app.services.storage import get_storage_service

@router.post("/logo/upload-url")
async def generate_logo_upload_url(
    logo_type: Literal["primary", "secondary"],
    filename: str,
    current_user: Annotated[User, Depends(require_role("admin", "superadmin"))],
):
    """Generate presigned URL for logo upload."""
    storage = get_storage_service()

    # Generate tenant-scoped key: {tenant_id}/branding/{type}-logo.{ext}
    ext = filename.rsplit(".", 1)[-1] if "." in filename else "png"
    object_key = f"{current_user.tenant_id}/branding/{logo_type}-logo.{ext}"

    url = storage._client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": storage._bucket,
            "Key": object_key,
            "ContentType": f"image/{ext}",
        },
        ExpiresIn=3600,
    )

    return {"upload_url": url, "object_key": object_key}
```

**Source:** Existing codebase pattern (backend/app/services/storage.py) + [Cloudflare R2 Documentation](https://developers.cloudflare.com/r2/)

### Anti-Patterns to Avoid

- **Forgetting tenant_id in queries:** Every query for tenant-scoped data MUST include WHERE tenant_id = X. Missing this creates data leakage. Use dependency injection to enforce.
- **Hardcoding tenant context in components:** Don't pass tenant_id as props everywhere. Use global state (Zustand) or React Context for tenant branding.
- **Storing branding in localStorage:** Branding can change server-side. Always fetch from API after login and cache in memory only.
- **Complex RLS for Phase 3:** PostgreSQL Row-Level Security adds migration and testing complexity. Application-level filtering is sufficient for current scale.
- **Multiple R2 buckets per tenant:** Unnecessary cost and complexity. Prefix-based organization already implemented and proven.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Color validation | Regex for hex colors | Simple string validation + Pillow for image color extraction | Edge cases: 3-digit hex, named colors, rgb() syntax |
| Logo resizing/thumbnails | Manual PIL operations | Pillow with standard thumbnail() method | Aspect ratio preservation, format conversion |
| Tenant subdomain routing | Custom middleware parsing | Not needed - tenant identified by JWT token in this architecture | Simpler, works with mobile apps |
| Query scoping library | sqlalchemy-filters or custom ORM layer | FastAPI dependency returning tenant_id for manual WHERE clauses | Explicit > Implicit for security-critical filtering |
| Theme switching animation | Custom CSS transitions | Browser-native CSS variable transitions | Smooth, performant, no JavaScript |

**Key insight:** Multi-tenant security depends on explicit filtering being visible in every query. Auto-magic query modification libraries can hide bugs. For Phase 3 scale (dozens of tenants), explicit WHERE clauses with dependency injection strike the right balance between safety and simplicity.

## Common Pitfalls

### Pitfall 1: Cross-Tenant Data Leakage via Missing Filters

**What goes wrong:** A developer writes a query without tenant_id filter, accidentally exposing data across all tenants. This is the #1 multi-tenant security risk.

**Why it happens:** Forgetting to add `.where(Model.tenant_id == tenant_id)` in queries, especially in new routes or one-off admin queries.

**How to avoid:**
1. Use FastAPI dependency `get_tenant_filter()` that returns current user's tenant_id
2. Code review checklist: every SELECT on tenant-scoped tables must filter by tenant_id
3. Integration tests that create data for Tenant A, authenticate as Tenant B user, verify no data returned
4. For superadmin routes that legitimately access all tenants, use explicit `require_superadmin` dependency to make intent clear

**Warning signs:**
- Query returns more rows than expected
- Users report seeing unfamiliar data
- Integration tests fail with "unexpected row count"

**Source:** [Multi-Tenant Leakage - Medium](https://medium.com/@instatunnel/multi-tenant-leakage-when-row-level-security-fails-in-saas-da25f40c788c), [Multi-Tenant Security - Qrvey](https://qrvey.com/blog/multi-tenant-security/)

### Pitfall 2: Admin Can Escalate to Superadmin

**What goes wrong:** Admin users can promote themselves or others to superadmin role, bypassing tenant isolation.

**Why it happens:** Insufficient role validation in user update endpoints.

**How to avoid:**
1. In user update endpoints, check `if current_user.role == "admin" and user_data.role == "superadmin": raise 403`
2. Only superadmins can create or modify superadmin users
3. Never trust role from request payload - always verify against current_user from JWT

**Warning signs:**
- Admins reporting they can't promote users (good - means guard is working)
- Audit log shows non-superadmin creating superadmin users (bad)

**Source:** Codebase already implements this pattern in users.py routes + [Multi-Tenant Architecture Pitfalls](https://medium.com/@koushiksathish3/multi-tenant-architecture-with-fastapi-design-patterns-and-pitfalls-aa3f9e75bf8c)

### Pitfall 3: Logo Upload Without Size/Type Validation

**What goes wrong:** Users upload 50MB PNGs or executable files masquerading as images, causing storage bloat or security issues.

**Why it happens:** Trusting client-side file input and not validating server-side.

**How to avoid:**
1. Validate Content-Type header matches image/* before generating presigned URL
2. Set max file size limit (e.g., 5MB) in presigned URL generation
3. After upload completes, verify file is valid image using Pillow
4. Generate thumbnail (e.g., 200x200) for UI display, store both original and thumbnail
5. On frontend, validate file size and type before uploading

**Warning signs:**
- S3/R2 storage costs unexpectedly high
- Logo images not rendering (invalid format)
- Security scanners flag uploaded files

**Source:** [Cloudflare R2 Best Practices](https://developers.cloudflare.com/r2/), [Multi-Tenant SaaS Security - eSecurityPlanet](https://www.esecurityplanet.com/cloud/multi-tenancy-cloud-security/)

### Pitfall 4: CSS Variable Conflicts with Tailwind

**What goes wrong:** Tenant brand colors don't apply, or only work on some components.

**Why it happens:** Tailwind CSS uses its own color system; CSS variables must be configured in tailwind.config.js to work with Tailwind utilities.

**How to avoid:**
1. Define CSS variables in :root selector
2. Reference variables in Tailwind config using var() syntax
3. Use Tailwind utilities (bg-primary, text-primary) instead of inline styles
4. Test theme switching with different color values

**Example Tailwind config:**
```javascript
// tailwind.config.js
export default {
  theme: {
    extend: {
      colors: {
        primary: 'var(--color-primary)',
        secondary: 'var(--color-secondary)',
        accent: 'var(--color-accent)',
      }
    }
  }
}
```

**Warning signs:**
- Colors work in vanilla CSS but not with Tailwind classes
- Theme switching requires page refresh
- Inconsistent colors across components

**Source:** [Designing Multi-Tenant UI with Tailwind CSS](https://dev.to/jonathz/designing-multi-tenant-ui-with-tailwind-css-5gi7), [Dynamic Themes with Tailwind](https://dev.to/ohitslaurence/creating-dynamic-themes-with-react-tailwindcss-59cl)

### Pitfall 5: Fetching Tenant Data on Every Request

**What goes wrong:** Performance degrades as each API request queries the tenant table to get branding, causing unnecessary database load.

**Why it happens:** Not caching tenant branding data that rarely changes.

**How to avoid:**
1. Include tenant branding in JWT token claims (small data: just colors, no logos)
2. OR: Fetch tenant branding once after login, store in Zustand state
3. Cache tenant data in React Query with long staleTime (e.g., 1 hour)
4. Backend can use in-memory cache (Redis or Python dict) for tenant lookups if needed

**Warning signs:**
- Database query logs show repeated SELECT from tenants table
- API response times increase with user count
- Database CPU usage high for simple queries

**Source:** [FastAPI Multi Tenancy - Medium](https://sayanc20002.medium.com/fastapi-multi-tenancy-bf7c387d07b0), Performance best practices

## Code Examples

Verified patterns from official sources and existing codebase:

### Tenant CRUD Endpoints (Superadmin Only)

```python
# backend/app/api/v1/routes/tenants.py
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_superadmin
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.tenant import TenantCreate, TenantUpdate, TenantResponse

router = APIRouter(prefix="/tenants", tags=["tenants"])

@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant_data: TenantCreate,
    current_user: Annotated[User, Depends(require_superadmin)],
    db: AsyncSession = Depends(get_db),
):
    """Create new tenant (superadmin only)."""
    # Check slug uniqueness
    result = await db.execute(
        select(Tenant).where(Tenant.slug == tenant_data.slug)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug ja existe",
        )

    tenant = Tenant(**tenant_data.model_dump())
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)

    return TenantResponse.model_validate(tenant)

@router.get("/", response_model=list[TenantResponse])
async def list_tenants(
    current_user: Annotated[User, Depends(require_superadmin)],
    db: AsyncSession = Depends(get_db),
):
    """List all tenants (superadmin only)."""
    result = await db.execute(
        select(Tenant).order_by(Tenant.created_at.desc())
    )
    tenants = result.scalars().all()
    return [TenantResponse.model_validate(t) for t in tenants]

@router.patch("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: UUID,
    tenant_data: TenantUpdate,
    current_user: Annotated[User, Depends(require_superadmin)],
    db: AsyncSession = Depends(get_db),
):
    """Update tenant (superadmin only)."""
    result = await db.execute(
        select(Tenant).where(Tenant.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant nao encontrado",
        )

    # Update fields
    for field, value in tenant_data.model_dump(exclude_unset=True).items():
        setattr(tenant, field, value)

    await db.commit()
    await db.refresh(tenant)

    return TenantResponse.model_validate(tenant)
```

**Source:** Existing users.py pattern + [Multi-Tenant FastAPI](https://github.com/Madeeha-Anjum/multi-tenancy-system)

### Tenant Settings Endpoints (Admin/Superadmin)

```python
# backend/app/api/v1/routes/tenant_settings.py
from typing import Annotated, Literal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_role
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.tenant import TenantBrandingUpdate, TenantResponse
from app.services.storage import get_storage_service

router = APIRouter(prefix="/tenant-settings", tags=["tenant-settings"])

@router.get("/branding", response_model=TenantResponse)
async def get_tenant_branding(
    current_user: Annotated[User, Depends(require_role("admin", "superadmin"))],
    db: AsyncSession = Depends(get_db),
):
    """Get current tenant's branding settings."""
    result = await db.execute(
        select(Tenant).where(Tenant.id == current_user.tenant_id)
    )
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant nao encontrado",
        )

    return TenantResponse.model_validate(tenant)

@router.patch("/branding", response_model=TenantResponse)
async def update_tenant_branding(
    branding_data: TenantBrandingUpdate,
    current_user: Annotated[User, Depends(require_role("admin", "superadmin"))],
    db: AsyncSession = Depends(get_db),
):
    """Update tenant branding (colors, contact info)."""
    result = await db.execute(
        select(Tenant).where(Tenant.id == current_user.tenant_id)
    )
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant nao encontrado",
        )

    # Update fields
    for field, value in branding_data.model_dump(exclude_unset=True).items():
        setattr(tenant, field, value)

    await db.commit()
    await db.refresh(tenant)

    return TenantResponse.model_validate(tenant)

@router.post("/logo/upload-url")
async def generate_logo_upload_url(
    logo_type: Literal["primary", "secondary"],
    filename: str,
    current_user: Annotated[User, Depends(require_role("admin", "superadmin"))],
):
    """Generate presigned URL for logo upload."""
    storage = get_storage_service()

    # Validate filename extension
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ["png", "jpg", "jpeg", "svg"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato invalido. Use PNG, JPG ou SVG.",
        )

    object_key = f"{current_user.tenant_id}/branding/{logo_type}-logo.{ext}"

    url = storage._client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": storage._bucket,
            "Key": object_key,
            "ContentType": f"image/{ext}",
        },
        ExpiresIn=3600,
    )

    return {"upload_url": url, "object_key": object_key}
```

**Source:** Existing storage.py pattern + [FastAPI File Upload Best Practices](https://fastapi.tiangolo.com/tutorial/request-files/)

### React Tenant Branding Store

```typescript
// frontend/src/stores/tenantStore.ts
import { create } from 'zustand'

interface TenantBranding {
  name: string
  logoPrimaryUrl: string | null
  logoSecondaryUrl: string | null
  colorPrimary: string | null
  colorSecondary: string | null
  colorAccent: string | null
  contactAddress: string | null
  contactPhone: string | null
  contactEmail: string | null
  contactWebsite: string | null
}

interface TenantState {
  branding: TenantBranding | null
  isLoading: boolean
  setBranding: (branding: TenantBranding) => void
  clearBranding: () => void
}

export const useTenantStore = create<TenantState>((set) => ({
  branding: null,
  isLoading: false,
  setBranding: (branding) => set({ branding, isLoading: false }),
  clearBranding: () => set({ branding: null }),
}))
```

**Source:** Existing appStore.ts pattern + [Zustand Documentation](https://docs.pmnd.rs/zustand/getting-started/introduction)

### React Dynamic Theme Hook

```typescript
// frontend/src/hooks/useTheme.ts
import { useEffect } from 'react'
import { useTenantStore } from '@/stores/tenantStore'

export function useTheme() {
  const { branding } = useTenantStore()

  useEffect(() => {
    if (!branding) return

    const root = document.documentElement

    // Apply tenant brand colors as CSS variables
    if (branding.colorPrimary) {
      root.style.setProperty('--color-primary', branding.colorPrimary)
    }
    if (branding.colorSecondary) {
      root.style.setProperty('--color-secondary', branding.colorSecondary)
    }
    if (branding.colorAccent) {
      root.style.setProperty('--color-accent', branding.colorAccent)
    }

    // Apply default colors if not set
    if (!branding.colorPrimary) {
      root.style.setProperty('--color-primary', '#3B82F6') // Default blue
    }
  }, [branding])
}
```

**Source:** [Dynamic Theming in React](https://dev.to/yorgie7/dynamic-theming-in-react-using-context-api-multi-brand-56l1)

### Tenant Settings Form with Color Picker

```typescript
// frontend/src/pages/TenantSettingsPage.tsx
import { useState } from 'react'
import { HexColorPicker } from 'react-colorful'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/axios'

export function TenantSettingsPage() {
  const queryClient = useQueryClient()
  const [showColorPicker, setShowColorPicker] = useState<string | null>(null)

  const { data: branding } = useQuery({
    queryKey: ['tenant-branding'],
    queryFn: async () => {
      const { data } = await api.get('/tenant-settings/branding')
      return data
    },
  })

  const updateBranding = useMutation({
    mutationFn: async (updates: Partial<typeof branding>) => {
      const { data } = await api.patch('/tenant-settings/branding', updates)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tenant-branding'] })
    },
  })

  const handleColorChange = (field: string, color: string) => {
    updateBranding.mutate({ [field]: color })
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Configurações do Tenant</h1>

      <div className="space-y-6">
        {/* Color configuration */}
        <div>
          <label className="block text-sm font-medium mb-2">
            Cor Primária
          </label>
          <div className="flex items-center gap-4">
            <div
              className="w-12 h-12 rounded border-2 cursor-pointer"
              style={{ backgroundColor: branding?.colorPrimary || '#3B82F6' }}
              onClick={() => setShowColorPicker('primary')}
            />
            <span className="text-sm text-gray-600">
              {branding?.colorPrimary || '#3B82F6'}
            </span>
          </div>
          {showColorPicker === 'primary' && (
            <div className="mt-4">
              <HexColorPicker
                color={branding?.colorPrimary || '#3B82F6'}
                onChange={(color) => handleColorChange('colorPrimary', color)}
              />
              <button
                onClick={() => setShowColorPicker(null)}
                className="mt-2 text-sm text-gray-600"
              >
                Fechar
              </button>
            </div>
          )}
        </div>

        {/* Logo upload */}
        <div>
          <label className="block text-sm font-medium mb-2">
            Logo Primária
          </label>
          {/* Logo upload component - implement presigned URL upload */}
        </div>
      </div>
    </div>
  )
}
```

**Source:** [react-colorful documentation](https://www.npmjs.com/package/react-colorful)

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Subdomain-based tenant detection | JWT token claims with tenant_id | 2022-2023 | Simpler deployment, works with mobile apps, no DNS complexity |
| PostgreSQL Row-Level Security everywhere | Application-level filtering for small scale, RLS for large scale | 2023-2024 | Start simple, migrate to RLS when query complexity grows |
| styled-components for theming | CSS variables with Tailwind | 2024-2025 | Native browser support, better performance, cleaner with Tailwind v4 |
| Separate databases per tenant | Single database with tenant_id column | 2020-2023 | Cost-effective, easier backups, sufficient isolation for most SaaS |
| Admin creates tenants | Superadmin-only tenant creation | Current best practice | Clear security boundary, prevents tenant sprawl |

**Deprecated/outdated:**
- **SQLAlchemy 1.x with sync sessions**: SQLAlchemy 2.0 with async is now standard for FastAPI
- **React class components for theming**: Hooks (useEffect) are cleaner for CSS variable manipulation
- **localStorage for tenant branding**: Security risk if XSS occurs; use memory state or httpOnly cookies

## Open Questions

Things that couldn't be fully resolved:

1. **Tenant deactivation cascade behavior**
   - What we know: is_active flag exists on Tenant model
   - What's unclear: Should deactivating a tenant soft-delete all its data? Block logins? Hide from lists?
   - Recommendation: For Phase 3, just block login (check tenant.is_active in get_current_user). Later phases can add cascade soft-delete.

2. **Logo image processing pipeline**
   - What we know: R2 storage handles uploads, presigned URLs work
   - What's unclear: Should logos be auto-resized server-side? Generate thumbnails? Validate dimensions?
   - Recommendation: Phase 3 minimum - validate file type and size. Phase 7 (Photo Processing) can add Pillow thumbnail generation if needed.

3. **Tenant slug immutability**
   - What we know: Slug is unique identifier, could be used in URLs
   - What's unclear: Should slug be editable after creation? Affects R2 object keys if used in paths.
   - Recommendation: Make slug immutable after creation (update endpoint rejects slug changes) to avoid R2 object key migrations.

4. **Default branding values**
   - What we know: Brand colors are nullable
   - What's unclear: Should there be system-wide defaults? Per-tenant defaults on creation?
   - Recommendation: Define default colors in frontend theme.css (:root variables). Tenant colors override when set.

## Sources

### Primary (HIGH confidence)
- [FastAPI Multi Tenancy - Medium](https://sayanc20002.medium.com/fastapi-multi-tenancy-bf7c387d07b0) - Class-based multi-tenancy implementation
- [Multitenancy with FastAPI, SQLAlchemy and PostgreSQL - MergeBoard](https://mergeboard.com/blog/6-multitenancy-fastapi-sqlalchemy-postgresql/) - Practical guide with code examples
- [Multi-Tenant Architecture with FastAPI - Medium](https://medium.com/@koushiksathish3/multi-tenant-architecture-with-fastapi-design-patterns-and-pitfalls-aa3f9e75bf8c) - Design patterns and pitfalls (April 2025)
- [PostgreSQL Row-Level Security for Multi-Tenant - AWS](https://aws.amazon.com/blogs/database/multi-tenant-data-isolation-with-postgresql-row-level-security/) - Official RLS documentation
- [Dynamic Theming in React Using Context API - DEV](https://dev.to/yorgie7/dynamic-theming-in-react-using-context-api-multi-brand-56l1) - Multi-brand theming pattern
- [Designing Multi-Tenant UI with Tailwind CSS - DEV](https://dev.to/jonathz/designing-multi-tenant-ui-with-tailwind-css-5gi7) - CSS variables with Tailwind
- [Cloudflare R2 Documentation](https://developers.cloudflare.com/r2/) - Official R2 docs
- Existing codebase: backend/app/models/tenant.py, backend/app/services/storage.py, backend/app/api/v1/routes/users.py

### Secondary (MEDIUM confidence)
- [Multi-Tenant Leakage - Medium](https://medium.com/@instatunnel/multi-tenant-leakage-when-row-level-security-fails-in-saas-da25f40c788c) - Recent security analysis (Jan 2026)
- [Multi-Tenant Security - Qrvey](https://qrvey.com/blog/multi-tenant-security/) - Security best practices
- [Architecting Secure Multi-Tenant Data Isolation - Medium](https://medium.com/@justhamade/architecting-secure-multi-tenant-data-isolation-d8f36cb0d25e) - Isolation patterns
- [react-colorful - npm](https://www.npmjs.com/package/react-colorful) - Color picker library
- [Dynamic Branding With React and CSS Variables - DEV](https://dev.to/osninja_io/dynamic-branding-with-react-and-scss-css-variables-5524) - Implementation guide

### Tertiary (LOW confidence - for context only)
- [GitHub: multi-tenancy-system](https://github.com/Madeeha-Anjum/multi-tenancy-system) - Example repo structure
- [sqlalchemy-tenants - GitHub](https://github.com/Telemaco019/sqlalchemy-tenants) - Library (not recommended for this phase)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - FastAPI + SQLAlchemy + React patterns well-established, confirmed by multiple 2025-2026 sources
- Architecture: HIGH - Patterns verified in existing codebase and recent tutorials
- Pitfalls: HIGH - Cross-tenant leakage well-documented, branding pitfalls verified from multiple sources
- Branding implementation: MEDIUM - CSS variable approach is proven, but react-colorful library not yet tested in this codebase
- Logo processing: MEDIUM - Basic validation is clear, but thumbnail generation details can be refined in planning

**Research date:** 2026-01-31
**Valid until:** 2026-03-02 (30 days - multi-tenant patterns are stable, but libraries update frequently)

---

**Ready for Planning:** This research provides sufficient detail to create detailed PLAN.md files for Phase 3 implementation. The planner should focus on:
1. Tenant model migration adding branding fields
2. Superadmin tenant CRUD endpoints
3. Admin tenant settings endpoints with logo upload
4. React tenant branding store and theme hook
5. Tenant settings UI with color picker and logo upload
6. Integration tests for cross-tenant isolation
