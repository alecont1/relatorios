# User Setup Guide: Phase 1 Infrastructure

**Generated:** 2026-01-24
**Phase:** 01-setup-infrastructure
**Status:** Required before Phase 2 deployment

---

## Overview

Phase 1 configured deployment to three external services. Before the application can run in production, you need to:

1. **Vercel** - Deploy frontend (React + Vite SPA)
2. **Railway** - Deploy backend (FastAPI + PostgreSQL + Redis)
3. **Cloudflare R2** - Configure object storage for photos

This guide walks through creating projects, configuring environment variables, and verifying the setup.

---

## 1. Vercel Setup (Frontend)

### Why Needed
Frontend hosting with automatic preview deployments for every git push and pull request.

### Dashboard Configuration

**1.1. Import Git Repository**
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"New Project"**
3. Click **"Import"** next to your `smarthand-reports` repository
4. Click **"Import"**

**1.2. Configure Project Settings**
1. **Framework Preset:** Vite (should auto-detect)
2. **Root Directory:** `frontend/` (IMPORTANT - click "Edit" and set this)
3. **Build Command:** `npm run build` (default is correct)
4. **Output Directory:** `dist` (default is correct)
5. Click **"Deploy"**

**1.3. Add Environment Variables**

After initial deployment, add environment variables:

1. Go to **Project Settings → Environment Variables**
2. Add the following:

| Variable Name | Value | Notes |
|--------------|-------|-------|
| `VITE_API_URL` | `https://your-backend.up.railway.app` | Railway backend URL (get from step 2) |

3. Click **"Save"**
4. Redeploy to apply variables: **Deployments → ... → Redeploy**

### Verification

```bash
# Frontend should be live at https://your-project.vercel.app
curl https://your-project.vercel.app

# Should return HTML with React app
# Check Network tab: Should load index.html, assets/*.js, assets/*.css
```

---

## 2. Railway Setup (Backend)

### Why Needed
Backend hosting with PostgreSQL database and Redis instance for background jobs.

### Dashboard Configuration

**2.1. Create New Project**
1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Select your `smarthand-reports` repository
5. Click **"Deploy Now"**

**2.2. Configure Backend Service**
1. Click on the deployed service (should be auto-detected as Python)
2. Go to **Settings → Root Directory**
3. Set to `backend/` (IMPORTANT)
4. Go to **Settings → Deploy**
5. Verify **Start Command** is: `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`
   (Should auto-detect from railway.json)

**2.3. Add PostgreSQL Database**
1. In your Railway project, click **"New"**
2. Select **"Database"**
3. Select **"PostgreSQL"**
4. PostgreSQL service will be created
5. Railway automatically sets `DATABASE_URL` environment variable on your backend service

**2.4. Add Redis Service**
1. In your Railway project, click **"New"**
2. Select **"Database"**
3. Select **"Redis"**
4. Redis service will be created
5. Railway automatically sets `REDIS_URL` environment variable on your backend service

**2.5. Add Cloudflare R2 Environment Variables**

After creating R2 bucket (see step 3), add these to backend service:

1. Go to backend service → **Variables**
2. Add the following:

| Variable Name | Value | Notes |
|--------------|-------|-------|
| `R2_ENDPOINT_URL` | `https://[account-id].r2.cloudflarestorage.com` | From Cloudflare R2 dashboard |
| `R2_ACCESS_KEY_ID` | `[your-access-key-id]` | From R2 API token creation |
| `R2_SECRET_ACCESS_KEY` | `[your-secret-key]` | From R2 API token creation |
| `R2_BUCKET_NAME` | `smarthand-photos` | Bucket name from step 3 |

3. Backend will automatically redeploy with new variables

**2.6. Run Database Migrations**

After PostgreSQL is provisioned:

```bash
# SSH into Railway service (or use local with DATABASE_URL)
railway run alembic upgrade head

# Or locally with Railway DATABASE_URL:
# 1. Install Railway CLI: npm install -g @railway/cli
# 2. Login: railway login
# 3. Link project: railway link
# 4. Run migration: railway run alembic upgrade head
```

### Verification

```bash
# Backend should be live at https://your-backend.up.railway.app
curl https://your-backend.up.railway.app/api/v1/health

# Expected response:
# {"status": "healthy", "database": "connected", "redis": "connected"}
```

---

## 3. Cloudflare R2 Setup (Object Storage)

### Why Needed
Zero egress fees for storing and serving report photos (S3-compatible API).

### Dashboard Configuration

**3.1. Create R2 Bucket**
1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/) → **R2**
2. Click **"Create bucket"**
3. **Bucket name:** `smarthand-photos`
4. **Region:** Automatic
5. Click **"Create bucket"**

**3.2. Generate API Tokens**
1. In R2 dashboard, click **"Manage R2 API Tokens"**
2. Click **"Create API token"**
3. **Token name:** `smarthand-backend-access`
4. **Permissions:**
   - Object Read & Write
5. **Bucket scope:** Apply to specific buckets only → Select `smarthand-photos`
6. Click **"Create API token"**
7. **IMPORTANT:** Copy the following and save securely:
   - Access Key ID
   - Secret Access Key
   - Endpoint URL (format: `https://[account-id].r2.cloudflarestorage.com`)

**3.3. Configure CORS (Optional - for direct browser uploads)**

If enabling client-side photo uploads via presigned URLs:

1. Go to bucket → **Settings → CORS policy**
2. Add CORS rule:

```json
[
  {
    "AllowedOrigins": [
      "https://your-project.vercel.app"
    ],
    "AllowedMethods": [
      "GET",
      "PUT"
    ],
    "AllowedHeaders": [
      "*"
    ],
    "ExposeHeaders": [
      "ETag"
    ],
    "MaxAgeSeconds": 3600
  }
]
```

3. Click **"Save"**

### Verification

```bash
# Test storage service from backend
cd backend
python -c "from app.services.storage import get_storage_service; s = get_storage_service(); print('Storage service OK')"

# Expected output:
# Storage service OK

# Test presigned URL generation
python -c "
from app.services.storage import get_storage_service
import uuid
s = get_storage_service()
url = s.generate_upload_url(tenant_id=uuid.uuid4(), filename='test.jpg')
print(f'Presigned URL: {url[:50]}...')
"

# Expected output:
# Presigned URL: https://[account-id].r2.cloudflarestorage.com/...
```

---

## 4. Update Vercel Environment Variables

After Railway backend is deployed, update Vercel frontend:

1. Go to Vercel project → **Settings → Environment Variables**
2. Update `VITE_API_URL` to your Railway backend URL:
   - Example: `https://smarthand-backend-production.up.railway.app`
3. Click **"Save"**
4. Redeploy frontend: **Deployments → ... → Redeploy**

---

## 5. Verify Full Stack Integration

After all services are configured:

### Backend Health Check
```bash
curl https://your-backend.up.railway.app/api/v1/health
# Expected: {"status": "healthy", "database": "connected", "redis": "connected"}
```

### Frontend Loads
```bash
# Visit in browser:
https://your-project.vercel.app

# Should load React app without errors
# Check browser console - no CORS or API errors
```

### API Connection from Frontend
```bash
# In browser console on https://your-project.vercel.app:
fetch(import.meta.env.VITE_API_URL + '/api/v1/health')
  .then(r => r.json())
  .then(console.log)

# Expected: {status: "healthy", database: "connected", redis: "connected"}
```

### Storage Service
```bash
# SSH into Railway backend:
railway run python -c "from app.services.storage import get_storage_service; get_storage_service()"

# Expected: No errors (service instantiates successfully)
```

---

## Environment Variables Summary

### Vercel (Frontend)
```bash
VITE_API_URL=https://your-backend.up.railway.app
```

### Railway (Backend)
```bash
# Auto-provisioned by Railway:
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
PORT=8000

# You must add:
R2_ENDPOINT_URL=https://[account-id].r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=your-access-key-id
R2_SECRET_ACCESS_KEY=your-secret-access-key
R2_BUCKET_NAME=smarthand-photos
```

### Local Development (.env)
```bash
# Database (use Railway or local PostgreSQL)
DATABASE_URL=postgresql://user:pass@localhost:5432/smarthand

# Redis (use Railway or local Redis)
REDIS_URL=redis://localhost:6379/0

# Cloudflare R2 (same credentials as production)
R2_ENDPOINT_URL=https://[account-id].r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=your-access-key-id
R2_SECRET_ACCESS_KEY=your-secret-access-key
R2_BUCKET_NAME=smarthand-photos
```

---

## Troubleshooting

### Frontend 404 on refresh (React Router routes)
- **Cause:** Vercel SPA fallback not working
- **Fix:** Verify `frontend/vercel.json` has `"routes"` array with filesystem and wildcard fallback
- **Verify:** Redeploy and refresh any route like `/reports` - should load app, not 404

### Backend health check failing
- **Cause:** Database or Redis not connected
- **Fix:** Check Railway environment variables `DATABASE_URL` and `REDIS_URL` are set
- **Verify:** Railway logs should show successful connection to PostgreSQL and Redis

### Storage service import fails
- **Cause:** Missing R2 credentials
- **Fix:** Add all R2_* environment variables to Railway backend service
- **Verify:** `railway run python -c "from app.services.storage import get_storage_service; get_storage_service()"`

### CORS errors on API calls
- **Cause:** Vercel frontend can't call Railway backend
- **Fix:** Add CORS middleware to FastAPI (should already be configured in app/main.py)
- **Verify:** Check browser Network tab for CORS headers in preflight OPTIONS request

### Database migrations not applied
- **Cause:** `alembic upgrade head` not run
- **Fix:** Run migration via Railway CLI: `railway run alembic upgrade head`
- **Verify:** Query PostgreSQL: `SELECT * FROM alembic_version;` - should show latest revision

---

## Next Steps

After completing this setup:

1. ✅ All infrastructure services are deployed and configured
2. ✅ Frontend, backend, database, cache, and storage are connected
3. ✅ CI/CD pipeline runs tests on every push
4. ✅ Ready to begin Phase 2: Authentication System

**Phase 1 Complete!** You can now proceed with feature development starting with JWT authentication.

---

*Last updated: 2026-01-24*
*Phase: 01-setup-infrastructure*
