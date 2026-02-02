# Phase 7: Photo Capture & Processing

**Goal:** Users can capture photos with automatic metadata, watermarks, and secure storage.

**Requirements:** PHOT-01 through PHOT-09

---

## Phase Overview

This phase implements the complete photo workflow for field inspections:
1. Capture photos from device camera
2. Automatically capture GPS and timestamp
3. Generate watermarked images with tenant branding
4. Compress and upload to Cloudflare R2
5. Associate photos with checklist responses

---

## Technical Architecture

### Storage Strategy
- **Cloudflare R2** for photo storage (S3-compatible)
- Path pattern: `{tenant_id}/reports/{report_id}/{field_id}/{uuid}.jpg`
- Metadata stored in `report_checklist_responses.photos` JSONB

### Photo Metadata Schema (JSONB)
```json
{
  "id": "uuid",
  "url": "https://r2.../path/image.jpg",
  "thumbnail_url": "https://r2.../path/thumb.jpg",
  "original_filename": "IMG_1234.jpg",
  "size_bytes": 245000,
  "width": 1920,
  "height": 1080,
  "captured_at": "2026-02-02T14:30:00Z",
  "gps": {
    "latitude": -23.5505,
    "longitude": -46.6333,
    "accuracy": 10.5
  },
  "address": "Av. Paulista, 1000 - Bela Vista, São Paulo - SP",
  "watermarked": true
}
```

### Processing Pipeline
1. **Client-side:** Capture → Get GPS → Compress → Generate watermark → Upload
2. **Server-side:** Validate → Store in R2 → Update response → Return URL

---

## Plan Breakdown

### Plan 07-01: Photo Models & Storage Setup
**Focus:** Backend infrastructure

**Tasks:**
1. Configure Cloudflare R2 client (boto3 with S3 API)
2. Create `StorageService` with methods:
   - `upload_photo(file, path)` → returns URL
   - `delete_photo(path)`
   - `generate_presigned_url(path)` (for direct uploads)
3. Update `ReportChecklistResponse.photos` JSONB handling
4. Create Pydantic schemas for photo metadata

**Output:** R2 integration ready for uploads

---

### Plan 07-02: Photo Upload API
**Focus:** Backend endpoints

**Tasks:**
1. Create photo router with endpoints:
   - `POST /reports/{report_id}/photos` - Upload photo
   - `DELETE /reports/{report_id}/photos/{photo_id}` - Remove photo
   - `GET /reports/{report_id}/photos` - List all photos for report

2. Implement upload handler:
   - Accept multipart file upload
   - Accept metadata (GPS, timestamp, field_id)
   - Store in R2 with proper path
   - Update response photos array
   - Return photo metadata with URL

3. Enforce photo limits from field config

**Output:** Complete photo CRUD API

---

### Plan 07-03: Frontend Camera Capture
**Focus:** Camera integration

**Tasks:**
1. Create `useCamera` hook:
   - Request camera permission
   - Capture photo from video stream
   - Handle file input fallback
   - Return captured image blob

2. Create `useGeolocation` hook:
   - Get current GPS coordinates
   - Handle permission denied
   - Show accuracy indicator

3. Create `CameraCapture` component:
   - Camera preview
   - Capture button
   - GPS status indicator
   - Switch camera (front/back)

**Output:** Camera capture working on mobile

---

### Plan 07-04: Watermark & Compression
**Focus:** Client-side image processing

**Tasks:**
1. Create `imageProcessor` service:
   - `compress(blob, maxWidth, quality)` → compressed blob
   - `generateWatermark(blob, metadata, tenantLogo)` → watermarked blob
   - `generateThumbnail(blob, size)` → thumbnail blob

2. Watermark layout:
   - Top-left: Tenant logo (small)
   - Bottom strip: Timestamp + Address
   - Semi-transparent overlay

3. Compression settings:
   - Max width: 1920px
   - Quality: 85% JPEG
   - Maintain aspect ratio

**Output:** Photos compressed and watermarked before upload

---

### Plan 07-05: Photo Gallery UI
**Focus:** Photo display and management

**Tasks:**
1. Create `PhotoGallery` component:
   - Grid of thumbnails
   - Tap to view full-size
   - Delete button (if editable)
   - Photo count indicator

2. Create `PhotoViewer` modal:
   - Full-screen view
   - Swipe between photos
   - Metadata display (GPS, time)
   - Close button

3. Integrate with `FieldRow` in ReportFillPage:
   - Show camera button
   - Show photo count
   - Show thumbnails
   - Required indicator

**Output:** Complete photo UI in report filling

---

### Plan 07-06: Human Verification
**Focus:** Test complete flow

**Tasks:**
1. Test photo capture on mobile device
2. Verify GPS coordinates captured
3. Verify watermark applied
4. Verify upload to R2
5. Verify photos display in report
6. Verify photo limits enforced
7. Test delete functionality

**Output:** Human approval of Phase 7

---

## Success Criteria Mapping

| Requirement | Plan | Criteria |
|-------------|------|----------|
| PHOT-01 | 07-03 | Capture from camera |
| PHOT-02 | 07-03 | GPS coordinates captured |
| PHOT-03 | 07-03 | Timestamp recorded |
| PHOT-04 | 07-04 | Reverse geocoding |
| PHOT-05 | 07-04 | Watermark overlay |
| PHOT-06 | 07-04 | Client-side compression |
| PHOT-07 | 07-01, 07-02 | R2 storage |
| PHOT-08 | 07-05 | Multiple photos per field |
| PHOT-09 | 07-02, 07-03 | Immutable metadata |

---

## Dependencies

**From Phase 3:**
- Tenant branding (logo for watermark)

**From Phase 5:**
- Field photo_config (required, min/max count)

**From Phase 6:**
- ReportChecklistResponse.photos JSONB array
- Report filling workflow

**External:**
- Cloudflare R2 credentials (check .env)
- Google Maps Geocoding API key (for reverse geocoding)

---

## Environment Variables Required

```env
# Cloudflare R2
R2_ACCOUNT_ID=...
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_BUCKET_NAME=smarthand-photos
R2_PUBLIC_URL=https://...

# Google Geocoding (optional - can use free alternatives)
GOOGLE_MAPS_API_KEY=...
```

---

## Estimated Plans: 6
## Estimated Duration: ~3 hours
