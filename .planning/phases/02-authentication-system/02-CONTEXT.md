# Phase 2: Authentication System - Context

**Gathered:** 2026-01-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Users can securely log in, maintain sessions, and access features based on their assigned roles. This phase covers: login flow, session management, user CRUD by admins, and role-based access control (RBAC) with 4 roles.

**Out of scope:** Password recovery via email (admin resets manually), OAuth/SSO, public registration.

</domain>

<decisions>
## Implementation Decisions

### Login UX
- Login identifier: **email** (not username)
- Error messages: **specific** ("Email não encontrado" or "Senha incorreta") - user prefers clarity over security-by-obscurity
- Password recovery: **admin resets** - no "forgot password" email flow in v1
- Password visibility: **toggle with eye icon** - important for mobile users

### User Creation
- Flow: **Admin creates complete account** - credentials shared via external channel (WhatsApp, etc)
- Required fields: **email + name + password** (minimum viable)
- Password requirements: **strong** - 8+ characters, must include uppercase, number, and special character
- Deactivation: **hard delete only** - no soft delete/inactive state (note: must handle FK constraints from reports)

### Role Hierarchy
- **user (técnico):** Create/edit/view only their own reports
- **manager:** Everything user can do + view all reports in tenant (read-only on others' reports)
- **admin:** Everything manager can do + full tenant control (users, templates, branding, settings)
- **superadmin:** God mode - full access to all tenants and all data for support/debugging

### Claude's Discretion
- JWT token duration and refresh strategy
- Session storage approach (localStorage vs httpOnly cookies)
- API endpoint structure for auth routes
- Password hashing algorithm (bcrypt recommended)
- Rate limiting on login attempts

</decisions>

<specifics>
## Specific Ideas

- Mobile-first: eye icon for password visibility is essential for field technicians
- Admin creates users with full credentials - no email infrastructure needed in v1
- Specific error messages prioritized over security-by-obscurity (internal tool, not public)
- Hard delete for users - simpler than soft delete but must cascade properly

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope

</deferred>

---

*Phase: 02-authentication-system*
*Context gathered: 2026-01-29*
