# Phase 9: Digital Signatures

## Overview
Implement digital signature capture and storage for report completion, allowing multiple signatories (technician, supervisor, client) to sign reports with canvas-based signatures.

## Plans

### Plan 09-01: Signature Data Model
- Create `ReportSignature` model
- Add migration for `report_signatures` table
- Create Pydantic schemas
- Add relationship to Report model

### Plan 09-02: Signature API Endpoints
- POST `/reports/{id}/signatures` - Upload signature
- GET `/reports/{id}/signatures` - List signatures
- DELETE `/reports/{id}/signatures/{sig_id}` - Delete signature

### Plan 09-03: Frontend Signature Capture
- Create `SignaturePad` component using canvas
- Touch and mouse support
- Clear/undo functionality
- Export as PNG blob

### Plan 09-04: Signature Integration
- Add signatures section to ReportFillPage
- Show required vs optional signatures from template
- Track signature completion status
- Block report completion if required signatures missing

### Plan 09-05: PDF Signature Integration
- Update PDFService to include captured signatures
- Add signature images with role labels and timestamps
- Format signature grid in PDF

## Dependencies
- Phase 6: Report Core (report model)
- Phase 7: Photo Capture (storage patterns)
- Phase 5: Template Configuration (signature_fields in snapshot)

## Success Criteria
- [ ] Users can draw signatures on canvas
- [ ] Signatures are uploaded and stored in R2
- [ ] PDF includes signature images
- [ ] Required signatures block completion
