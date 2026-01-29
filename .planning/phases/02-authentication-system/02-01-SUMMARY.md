---
phase: 02-authentication-system
plan: 01
subsystem: auth
tags: [jwt, pyjwt, argon2, pwdlib, fastapi, security, password-hashing]

# Dependency graph
requires:
  - phase: 01-project-setup
    provides: FastAPI backend structure with config and database modules
provides:
  - JWT access/refresh token creation and validation
  - Password hashing with Argon2 via pwdlib
  - FastAPI dependencies for route protection (get_current_user, require_role)
  - OAuth2 bearer token extraction scheme
affects: [02-02 user-model-endpoints, 02-03 login-endpoints, 02-04 registration, auth-routes]

# Tech tracking
tech-stack:
  added: [PyJWT>=2.9.0, pwdlib[argon2]>=0.3.0, slowapi>=0.1.9]
  patterns: [JWT with type claim, OAuth2PasswordBearer dependency injection, role-based access control factory]

key-files:
  created:
    - backend/app/core/security.py
    - backend/app/core/deps.py
  modified:
    - backend/requirements.txt
    - backend/app/core/config.py

key-decisions:
  - "JWT tokens include type claim (access/refresh) for differentiation"
  - "15-minute access token expiry, 7-day refresh token expiry"
  - "jwt_secret_key required field with no default (must be set via env)"
  - "Error messages in Portuguese for Brazilian user base"
  - "Role-based access via require_role dependency factory"

patterns-established:
  - "Security utilities in core/security.py"
  - "FastAPI dependencies in core/deps.py"
  - "OAuth2PasswordBearer with tokenUrl /api/v1/auth/login"

# Metrics
duration: 5min
completed: 2026-01-29
---

# Phase 2 Plan 1: Backend Security Core Summary

**JWT token management with PyJWT, Argon2 password hashing via pwdlib, and FastAPI auth dependencies for route protection**

## Performance

- **Duration:** 5 min
- **Started:** 2026-01-29T20:30:00Z
- **Completed:** 2026-01-29T20:35:00Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments
- Added PyJWT, pwdlib[argon2], and slowapi to requirements.txt
- Created security.py with JWT creation/decoding and password hash/verify functions
- Created deps.py with oauth2_scheme, get_current_user, and require_role dependencies
- Added JWT configuration settings to config.py

## Task Commits

Each task was committed atomically:

1. **Task 1: Add auth dependencies and update config** - `8baed36` (chore)
2. **Task 2: Create security utilities module** - `a9b05a1` (feat)
3. **Task 3: Create auth dependencies module** - `e324236` (feat)

## Files Created/Modified
- `backend/requirements.txt` - Added PyJWT, pwdlib[argon2], slowapi dependencies
- `backend/app/core/config.py` - Added jwt_secret_key, jwt_algorithm, token expiry settings
- `backend/app/core/security.py` - JWT token creation/decoding, Argon2 password hashing
- `backend/app/core/deps.py` - OAuth2 scheme, get_current_user, require_role dependencies

## Decisions Made
- JWT tokens include "type" claim ("access" or "refresh") to differentiate token types
- Access tokens expire in 15 minutes (configurable via access_token_expire_minutes)
- Refresh tokens expire in 7 days (configurable via refresh_token_expire_days)
- jwt_secret_key is a required field with no default - must be set in environment
- Error messages in Portuguese: "Token invalido ou expirado", "Usuario inativo", "Acesso negado - permissao insuficiente"
- OAuth2 token URL set to /api/v1/auth/login for future login endpoint

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required

Environment variable required before running backend:
- `JWT_SECRET_KEY` - Secret key for JWT signing (required, no default)

Generate with: `openssl rand -hex 32`

## Next Phase Readiness
- Security utilities ready for user authentication endpoints
- get_current_user dependency ready for protected routes
- require_role factory ready for admin-only endpoints
- Next plan (02-02) can implement User model extensions and auth endpoints

---
*Phase: 02-authentication-system*
*Completed: 2026-01-29*
