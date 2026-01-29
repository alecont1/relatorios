# Phase 2: Authentication System - Research

**Researched:** 2026-01-29
**Domain:** JWT Authentication, RBAC, Session Management (FastAPI + React)
**Confidence:** HIGH

## Summary

Phase 2 implements a complete authentication system for the SmartHand multi-tenant SaaS application. The research covered JWT-based authentication with FastAPI using the modern stack (PyJWT + pwdlib), role-based access control with 4 hierarchical roles (user, manager, admin, superadmin), and React frontend integration using Zustand for auth state with httpOnly cookies for secure token storage.

Key findings include FastAPI's recent migration from python-jose/passlib to PyJWT/pwdlib (Argon2), the superiority of httpOnly cookies over localStorage for JWT storage (XSS mitigation), and the importance of refresh token rotation for session security. The implementation follows the user's CONTEXT.md decisions: email-based login, specific error messages, admin-created accounts, strong password requirements (8+ chars with uppercase, number, special char), and hard delete for users.

The architecture uses FastAPI's dependency injection for route protection (`get_current_user`, `require_role`), SlowAPI for login rate limiting, and React's protected routes pattern with Zustand persist middleware for authentication state. Multi-tenant isolation is enforced by extracting tenant_id from the JWT and filtering all queries accordingly.

**Primary recommendation:** Use PyJWT + pwdlib (Argon2) for backend auth, store access tokens in memory and refresh tokens in httpOnly cookies, implement 15-minute access tokens with 7-day refresh tokens and rotation on each use, and use FastAPI dependencies for RBAC enforcement at the route level.

## Standard Stack

The established libraries/tools for this authentication domain:

### Core Backend

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| PyJWT | 2.9+ | JWT encoding/decoding | FastAPI's official recommendation, actively maintained, lightweight |
| pwdlib | 0.3+ | Password hashing (Argon2) | Modern replacement for passlib, FastAPI-recommended, Python 3.13+ compatible |
| SlowAPI | 0.1.9+ | Rate limiting | Standard FastAPI rate limiter, Redis-backed for distributed deployments |

### Core Frontend

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Zustand | 4.5+ | Auth state management | Already in stack, persist middleware for session persistence |
| React Router | 6.28+ | Protected routes | Already in stack, `<Navigate>` for auth redirects |
| React Hook Form | 7.53+ | Login/user forms | Already in stack, with Zod validation |
| Zod | 3.24+ | Schema validation | Already in stack, password strength rules |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| argon2-cffi | 23.1+ | Argon2 hasher backend | Installed via `pwdlib[argon2]` |
| redis | 5.0+ | Rate limit storage | Already in stack (Celery), use for SlowAPI backend |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| PyJWT | python-jose | python-jose abandoned, security vulnerabilities |
| pwdlib (Argon2) | passlib (bcrypt) | passlib incompatible with Python 3.13+, Argon2 more secure |
| httpOnly cookies | localStorage | localStorage vulnerable to XSS attacks |
| SlowAPI | fastapi-limiter | Both viable, SlowAPI more feature-complete |

### Installation

**Backend:**
```bash
pip install PyJWT "pwdlib[argon2]" slowapi
```

**Frontend:**
No additional packages needed - using existing stack (Zustand, React Router, React Hook Form, Zod).

## Architecture Patterns

### Recommended Project Structure

**Backend additions:**
```
backend/
├── app/
│   ├── core/
│   │   ├── security.py       # JWT + password hashing utilities
│   │   └── deps.py           # Auth dependencies (get_current_user, require_role)
│   ├── api/v1/routes/
│   │   ├── auth.py           # Login, logout, refresh endpoints
│   │   └── users.py          # User CRUD (admin only)
│   └── schemas/
│       ├── auth.py           # Token, login request/response schemas
│       └── user.py           # User create/update/response schemas
```

**Frontend additions:**
```
frontend/src/
├── features/auth/
│   ├── components/
│   │   ├── LoginForm.tsx     # Login form with React Hook Form
│   │   ├── ProtectedRoute.tsx # Route guard component
│   │   └── PasswordInput.tsx  # Password field with visibility toggle
│   ├── hooks/
│   │   └── useAuth.ts        # Auth operations hook
│   ├── api.ts                # React Query mutations for auth
│   └── store.ts              # Zustand auth store
├── lib/
│   └── axios.ts              # Axios instance with interceptors
```

### Pattern 1: JWT Authentication with FastAPI Dependencies

**What:** Dependency injection chain for extracting and validating JWT tokens
**When to use:** Every protected endpoint
**Example:**
```python
# app/core/security.py
from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from app.core.config import settings

password_hash = PasswordHash.recommended()

SECRET_KEY = settings.jwt_secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return password_hash.hash(password)
```

```python
# app/core/deps.py
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import SECRET_KEY, ALGORITHM
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise credentials_exception
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    user = await db.get(User, user_id)
    if user is None:
        raise credentials_exception
    return user

def require_role(*allowed_roles: str):
    """Dependency factory for role-based access control."""
    async def role_checker(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado - permissao insuficiente"
            )
        return current_user
    return role_checker
```
**Source:** [FastAPI OAuth2 JWT Tutorial](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)

### Pattern 2: Zustand Auth Store with Persist

**What:** Client-side auth state with localStorage persistence for session recovery
**When to use:** Managing authentication state across the React app
**Example:**
```typescript
// src/features/auth/store.ts
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'user' | 'manager' | 'admin' | 'superadmin';
  tenant_id: string;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setAuth: (user: User, accessToken: string) => void;
  clearAuth: () => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      isLoading: true,
      setAuth: (user, accessToken) => set({
        user,
        accessToken,
        isAuthenticated: true,
        isLoading: false
      }),
      clearAuth: () => set({
        user: null,
        accessToken: null,
        isAuthenticated: false,
        isLoading: false
      }),
      setLoading: (loading) => set({ isLoading: loading }),
    }),
    {
      name: 'smarthand-auth',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        // Only persist user info, not access token (security)
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
```
**Source:** [Zustand Persist Documentation](https://zustand.docs.pmnd.rs/integrations/persisting-store-data)

### Pattern 3: Protected Route Component

**What:** Route guard that redirects unauthenticated users to login
**When to use:** Wrapping routes that require authentication
**Example:**
```typescript
// src/features/auth/components/ProtectedRoute.tsx
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: ('user' | 'manager' | 'admin' | 'superadmin')[];
}

export function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, user } = useAuthStore();
  const location = useLocation();

  if (isLoading) {
    return <div>Carregando...</div>; // Or a proper loading spinner
  }

  if (!isAuthenticated) {
    // Preserve the attempted URL for redirect after login
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
}
```
**Source:** [React Router Protected Routes](https://ui.dev/react-router-protected-routes-authentication)

### Pattern 4: Axios Interceptors for Token Refresh

**What:** Automatic token refresh on 401 responses
**When to use:** All authenticated API requests
**Example:**
```typescript
// src/lib/axios.ts
import axios from 'axios';
import { useAuthStore } from '@/features/auth/store';

const API_URL = import.meta.env.VITE_API_URL;

export const api = axios.create({
  baseURL: API_URL,
  withCredentials: true, // Send cookies with requests
});

// Request interceptor - add access token
api.interceptors.request.use((config) => {
  const accessToken = useAuthStore.getState().accessToken;
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

// Response interceptor - handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Refresh token is in httpOnly cookie, sent automatically
        const { data } = await axios.post(`${API_URL}/api/v1/auth/refresh`, {}, {
          withCredentials: true,
        });

        useAuthStore.getState().setAuth(data.user, data.access_token);
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        useAuthStore.getState().clearAuth();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);
```
**Source:** [React Query + Axios Authentication](https://codevoweb.com/react-query-context-api-axios-interceptors-jwt-auth/)

### Pattern 5: Role-Based Route Protection

**What:** RBAC enforcement at FastAPI route level using dependencies
**When to use:** Routes restricted to specific roles
**Example:**
```python
# app/api/v1/routes/users.py
from typing import Annotated
from fastapi import APIRouter, Depends
from app.core.deps import get_current_user, require_role
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])

# Only admins and superadmins can create users
@router.post("/")
async def create_user(
    user_data: UserCreate,
    current_user: Annotated[User, Depends(require_role("admin", "superadmin"))],
    db: AsyncSession = Depends(get_db)
):
    # Admin can only create users in their own tenant
    if current_user.role == "admin":
        user_data.tenant_id = current_user.tenant_id
    # Superadmin can specify any tenant
    ...

# Role hierarchy - superadmin sees all, others see their tenant
@router.get("/")
async def list_users(
    current_user: Annotated[User, Depends(require_role("admin", "superadmin"))],
    db: AsyncSession = Depends(get_db)
):
    if current_user.role == "superadmin":
        # Can see all users across all tenants
        result = await db.execute(select(User))
    else:
        # Admin sees only their tenant's users
        result = await db.execute(
            select(User).where(User.tenant_id == current_user.tenant_id)
        )
    return result.scalars().all()
```
**Source:** [FastAPI RBAC Tutorial](https://www.permit.io/blog/fastapi-rbac-full-implementation-tutorial)

### Anti-Patterns to Avoid

- **Storing JWT in localStorage:** Vulnerable to XSS attacks; use httpOnly cookies for refresh tokens, memory for access tokens
- **Long-lived access tokens:** Use short-lived (15 min) access tokens with refresh token rotation
- **Role checks in frontend only:** Always enforce RBAC on backend; frontend is for UX only
- **Hardcoded secrets:** Use environment variables for JWT secret, never commit to git
- **Missing tenant context:** Every query must filter by tenant_id from JWT, not from request body
- **Generic error messages on login:** Per user's decision, use specific messages ("Email nao encontrado" or "Senha incorreta")
- **Blocking sync password hashing:** Use async wrapper or run in thread pool

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Password hashing | Custom hash function | pwdlib (Argon2) | Timing attacks, salt generation, algorithm updates |
| JWT signing | Custom token format | PyJWT | Standard format, expiration handling, signature verification |
| Rate limiting | Custom counter | SlowAPI | Distributed counting, Redis backend, multiple algorithms |
| Password validation | Custom regex | Zod schema | Composable rules, internationalized messages, type inference |
| Token refresh | Custom polling | Axios interceptors | Automatic retry, request queuing, race condition handling |

**Key insight:** Authentication is a security-critical domain where subtle bugs lead to compromised accounts. Battle-tested libraries handle edge cases (timing attacks, token replay, race conditions) that are easy to miss in custom implementations.

## Common Pitfalls

### Pitfall 1: Token Stored in localStorage XSS Vulnerability

**What goes wrong:** Malicious JavaScript (from XSS attack, compromised npm package, or injected script) can read localStorage and steal JWT tokens.

**Why it happens:** localStorage is accessible to any JavaScript on the page. With modern apps pulling in hundreds of npm dependencies, the attack surface is enormous.

**How to avoid:**
- Store refresh tokens in httpOnly cookies (inaccessible to JavaScript)
- Store access tokens in memory only (React state/Zustand)
- On page refresh, use refresh token to get new access token
- Set cookie flags: `HttpOnly`, `Secure`, `SameSite=Strict`

**Warning signs:**
- `localStorage.setItem('token', ...)` in codebase
- Access token in Redux/Zustand persist config
- No httpOnly cookie configuration on backend

### Pitfall 2: Missing Tenant Context in Auth Queries

**What goes wrong:** Admin from Tenant A can see/modify users from Tenant B because queries don't filter by tenant_id.

**Why it happens:** Forgetting to add `.where(tenant_id == current_user.tenant_id)` on user queries. Assuming role check is sufficient.

**How to avoid:**
```python
# WRONG - Missing tenant filter
async def list_users(admin: User):
    return await db.execute(select(User))  # Returns ALL tenants!

# CORRECT - Filter by tenant
async def list_users(admin: User):
    return await db.execute(
        select(User).where(User.tenant_id == admin.tenant_id)
    )

# EXCEPTION - Superadmin can see all
if admin.role == "superadmin":
    return await db.execute(select(User))
```

**Warning signs:**
- User queries without tenant_id filter
- tenant_id coming from request body instead of JWT
- No tests verifying tenant isolation

### Pitfall 3: Refresh Token Reuse Without Rotation

**What goes wrong:** Stolen refresh token can be used indefinitely until it expires. Attacker maintains access for days/weeks.

**Why it happens:** Implementing refresh without rotation - same token reused on each refresh.

**How to avoid:**
- Rotate refresh token on each use (issue new token, invalidate old)
- Store token family/version in database
- Detect reuse: if old token used, invalidate entire family
- Alert user of potential compromise

**Warning signs:**
- Refresh endpoint returns only new access token, not new refresh token
- No refresh token storage in database
- No token version/family tracking

### Pitfall 4: Blocking Event Loop with Password Hashing

**What goes wrong:** Argon2 is intentionally slow (security feature). Synchronous hashing blocks FastAPI's event loop, causing all requests to wait.

**Why it happens:** Calling `password_hash.verify()` directly in async endpoint without thread pool.

**How to avoid:**
```python
from starlette.concurrency import run_in_threadpool

async def authenticate_user(email: str, password: str, db: AsyncSession):
    user = await db.execute(select(User).where(User.email == email))
    user = user.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Email nao encontrado")

    # Run CPU-intensive hash verification in thread pool
    is_valid = await run_in_threadpool(
        password_hash.verify, password, user.password_hash
    )
    if not is_valid:
        raise HTTPException(status_code=401, detail="Senha incorreta")

    return user
```

**Warning signs:**
- Slow login responses under load
- `password_hash.verify()` called directly without await/threadpool
- High latency spikes during authentication

### Pitfall 5: Hard Delete Breaks Foreign Key Constraints

**What goes wrong:** Deleting a user fails because they have reports referencing them. Or delete succeeds but orphans reports with NULL user_id.

**Why it happens:** Per CONTEXT.md decision, users are hard deleted (not soft deleted). But reports have FK to users.

**How to avoid:**
```python
# Option 1: Reassign reports to tenant admin before delete
async def delete_user(user_id: UUID, db: AsyncSession):
    user = await db.get(User, user_id)
    tenant_admin = await get_tenant_admin(user.tenant_id, db)

    # Reassign all reports to tenant admin
    await db.execute(
        update(Report)
        .where(Report.user_id == user_id)
        .values(user_id=tenant_admin.id)
    )

    await db.delete(user)
    await db.commit()

# Option 2: Prevent delete if user has reports
async def delete_user(user_id: UUID, db: AsyncSession):
    report_count = await db.scalar(
        select(func.count()).where(Report.user_id == user_id)
    )
    if report_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Usuario possui {report_count} relatorios. Reatribua antes de excluir."
        )
    ...
```

**Warning signs:**
- FK constraint errors on user delete
- Orphaned records with NULL user_id
- No check for dependent records before delete

## Code Examples

Verified patterns from official sources:

### Login Endpoint with Rate Limiting

```python
# app/api/v1/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.concurrency import run_in_threadpool
from app.core.security import (
    create_access_token, create_refresh_token,
    verify_password, password_hash
)
from app.schemas.auth import Token

router = APIRouter(prefix="/auth", tags=["auth"])
limiter = Limiter(key_func=get_remote_address)

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")  # Rate limit login attempts
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    # Find user by email
    result = await db.execute(
        select(User).where(User.email == form_data.username)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email nao encontrado"
        )

    # Verify password in thread pool (CPU-intensive)
    is_valid = await run_in_threadpool(
        verify_password, form_data.password, user.password_hash
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha incorreta"
        )

    # Create tokens
    token_data = {"sub": str(user.id), "tenant_id": str(user.tenant_id), "role": user.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    # Set refresh token in httpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # HTTPS only
        samesite="strict",
        max_age=7 * 24 * 60 * 60  # 7 days
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )
```
**Source:** [FastAPI OAuth2 JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/), [SlowAPI Docs](https://slowapi.readthedocs.io/)

### Login Form with Password Visibility Toggle

```typescript
// src/features/auth/components/LoginForm.tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import { useLogin } from '../api';

const loginSchema = z.object({
  email: z.string().email('Email invalido'),
  password: z.string().min(1, 'Senha obrigatoria'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export function LoginForm() {
  const [showPassword, setShowPassword] = useState(false);
  const login = useLogin();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      await login.mutateAsync(data);
    } catch (error: any) {
      // Show specific error from backend
      setError('root', {
        message: error.response?.data?.detail || 'Erro ao fazer login'
      });
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label htmlFor="email" className="block text-sm font-medium">
          Email
        </label>
        <input
          {...register('email')}
          type="email"
          id="email"
          className="mt-1 block w-full rounded-md border p-2"
          autoComplete="email"
        />
        {errors.email && (
          <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium">
          Senha
        </label>
        <div className="relative mt-1">
          <input
            {...register('password')}
            type={showPassword ? 'text' : 'password'}
            id="password"
            className="block w-full rounded-md border p-2 pr-10"
            autoComplete="current-password"
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute inset-y-0 right-0 flex items-center pr-3"
            aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}
          >
            {showPassword ? (
              <EyeOff className="h-5 w-5 text-gray-400" />
            ) : (
              <Eye className="h-5 w-5 text-gray-400" />
            )}
          </button>
        </div>
        {errors.password && (
          <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
        )}
      </div>

      {errors.root && (
        <p className="text-sm text-red-600">{errors.root.message}</p>
      )}

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full rounded-md bg-blue-600 px-4 py-2 text-white disabled:opacity-50"
      >
        {isSubmitting ? 'Entrando...' : 'Entrar'}
      </button>
    </form>
  );
}
```
**Source:** [React Hook Form](https://react-hook-form.com/), User CONTEXT.md (password visibility toggle requirement)

### Strong Password Validation Schema

```typescript
// src/features/auth/schemas.ts
import { z } from 'zod';

export const strongPasswordSchema = z
  .string()
  .min(8, 'Senha deve ter no minimo 8 caracteres')
  .regex(/[A-Z]/, 'Senha deve conter pelo menos uma letra maiuscula')
  .regex(/[0-9]/, 'Senha deve conter pelo menos um numero')
  .regex(/[!@#$%^&*(),.?":{}|<>]/, 'Senha deve conter pelo menos um caractere especial');

export const createUserSchema = z.object({
  email: z.string().email('Email invalido'),
  full_name: z.string().min(2, 'Nome deve ter no minimo 2 caracteres'),
  password: strongPasswordSchema,
  role: z.enum(['user', 'manager', 'admin']),
});

export type CreateUserData = z.infer<typeof createUserSchema>;
```
**Source:** [Zod Documentation](https://zod.dev/), User CONTEXT.md (strong password requirements)

### User Creation by Admin

```python
# app/api/v1/routes/users.py
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from app.core.deps import require_role
from app.core.security import hash_password
from app.schemas.user import UserCreate, UserResponse
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: Annotated[User, Depends(require_role("admin", "superadmin"))],
    db: AsyncSession = Depends(get_db)
):
    """Create a new user. Only admins can create users for their tenant."""

    # Admin can only create users in their own tenant
    if current_user.role == "admin":
        tenant_id = current_user.tenant_id
    else:
        # Superadmin can specify any tenant
        tenant_id = user_data.tenant_id or current_user.tenant_id

    # Check if email already exists
    existing = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Email ja cadastrado"
        )

    # Admin cannot create superadmin users
    if current_user.role == "admin" and user_data.role == "superadmin":
        raise HTTPException(
            status_code=403,
            detail="Admin nao pode criar usuarios superadmin"
        )

    # Create user
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        password_hash=hash_password(user_data.password),
        role=user_data.role,
        tenant_id=tenant_id,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user
```
**Source:** User CONTEXT.md (admin creates accounts, no self-registration)

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| python-jose | PyJWT | 2024 | python-jose abandoned, security vulnerabilities unpatched |
| passlib (bcrypt) | pwdlib (Argon2) | 2025 | passlib incompatible with Python 3.13+, Argon2 more secure |
| localStorage JWT | httpOnly cookies + memory | 2023-2024 | XSS mitigation, security best practice |
| Single long-lived token | Access + refresh with rotation | 2023-2024 | Reduced blast radius if token stolen |
| bcrypt work factor 10 | bcrypt 13-14 or Argon2 | 2025-2026 | GPU cracking advances require higher factors |

**Deprecated/outdated:**
- **python-jose:** Abandoned, last release 3+ years ago, known security vulnerabilities
- **passlib:** Not compatible with Python 3.13+ (crypt module removed)
- **localStorage for JWT:** Considered insecure, OWASP recommends cookies
- **Long-lived access tokens:** 1+ hour tokens increase risk; prefer 15-30 min with refresh

## Open Questions

Things that couldn't be fully resolved:

1. **Refresh token storage: Database vs Redis**
   - What we know: Database ensures persistence, Redis offers faster lookups
   - What's unclear: Performance impact at SmartHand's expected scale
   - Recommendation: Start with database (simpler), migrate to Redis if needed

2. **Token blacklist implementation**
   - What we know: Needed for logout to invalidate tokens before expiry
   - What's unclear: Redis vs database for blacklist, cleanup strategy
   - Recommendation: Use Redis SET with TTL matching token expiry for auto-cleanup

3. **Password reset flow for v2**
   - What we know: v1 uses admin reset (per CONTEXT.md), v2 may need email reset
   - What's unclear: Email service integration (SendGrid, SES, etc.)
   - Recommendation: Design token schema to support future email reset (add purpose field)

## Sources

### Primary (HIGH confidence)
- [FastAPI OAuth2 with Password and JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/) - Official FastAPI docs, updated for PyJWT/pwdlib
- [FastAPI Get Current User](https://fastapi.tiangolo.com/tutorial/security/get-current-user/) - Official dependency injection pattern
- [pwdlib GitHub](https://github.com/frankie567/pwdlib) - Official library docs, v0.3.0
- [SlowAPI Documentation](https://slowapi.readthedocs.io/) - Official rate limiting docs
- [Zustand Persist Middleware](https://zustand.docs.pmnd.rs/integrations/persisting-store-data) - Official Zustand docs

### Secondary (MEDIUM confidence)
- [JWT Storage: Cookies vs localStorage](https://cybersierra.co/blog/react-jwt-storage-guide/) - Security analysis with OWASP references
- [Refresh Token Rotation Best Practices](https://auth0.com/blog/refresh-tokens-what-are-they-and-when-to-use-them/) - Auth0 security guide
- [React Router Protected Routes](https://ui.dev/react-router-protected-routes-authentication) - Community standard pattern
- [FastAPI RBAC Implementation](https://www.permit.io/blog/fastapi-rbac-full-implementation-tutorial) - Detailed tutorial
- [React Query + Axios Authentication](https://codevoweb.com/react-query-context-api-axios-interceptors-jwt-auth/) - Integration guide

### Tertiary (LOW confidence)
- Various Medium articles on password hashing comparison (validate with benchmarks before using)
- Community discussions on soft delete vs hard delete (validate with DBA for FK handling)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries verified via official docs, recent releases (2025-2026)
- Architecture: HIGH - Patterns from FastAPI official docs and widely-adopted community standards
- Pitfalls: HIGH - Security issues verified via OWASP, Auth0, and official security guides
- Code examples: HIGH - Based on official documentation with adaptations for CONTEXT.md requirements

**Research date:** 2026-01-29
**Valid until:** 2026-02-28 (30 days - stable auth patterns, but check for library updates)

**Version notes:**
- PyJWT 2.9+ current, FastAPI now officially recommends over python-jose
- pwdlib 0.3.0 released Oct 2025, stable for production
- SlowAPI 0.1.9+ current, Redis backend recommended for distributed systems
- Argon2 recommended by NIST for password hashing (2024 guidelines)
