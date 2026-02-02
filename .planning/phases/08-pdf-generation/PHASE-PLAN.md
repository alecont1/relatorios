# Phase 8: PDF Generation System

**Goal:** Users can generate professional branded PDF reports with all data, photos, and signatures.

**Requirements:** PDF-01 through PDF-07

---

## Phase Overview

This phase implements server-side PDF generation using WeasyPrint:
1. HTML/CSS templates with Jinja2
2. Tenant branding (logos, colors)
3. Info fields and checklist responses
4. Photo grid with metadata
5. Download endpoint

---

## Technical Architecture

### Stack
- **WeasyPrint** - HTML/CSS to PDF conversion
- **Jinja2** - Template rendering
- **FastAPI** - Download endpoint

### PDF Layout Structure
```
+------------------------------------------+
|  [Logo 1]    REPORT TITLE      [Logo 2]  |  Header
|  Template: XXX | Date: XXX | Code: XXX   |
+------------------------------------------+
|  PROJECT INFORMATION                      |  Info Fields
|  Field 1: Value                          |
|  Field 2: Value                          |
+------------------------------------------+
|  SECTION 1: Name                         |  Checklist
|  ☑ Field 1: OK                          |
|  ☑ Field 2: Not OK - Comment            |
|  [Photo Grid]                            |
+------------------------------------------+
|  SECTION 2: Name                         |
|  ...                                     |
+------------------------------------------+
|  SIGNATURES                              |  Footer
|  [Sig 1]        [Sig 2]                 |
|  Role Name      Role Name               |
+------------------------------------------+
```

---

## Plan Breakdown

### Plan 08-01: PDF Dependencies & Templates
**Focus:** Setup and HTML templates

**Tasks:**
1. Add WeasyPrint to requirements.txt
2. Create templates directory structure
3. Create base PDF template (base.html)
4. Create report PDF template (report.html)
5. Create CSS stylesheet for PDF

**Output:** Template files ready for rendering

---

### Plan 08-02: PDF Generation Service
**Focus:** Backend service

**Tasks:**
1. Create PDFService class:
   - `generate_report_pdf(report, tenant)` → bytes
   - Template rendering with Jinja2
   - WeasyPrint conversion
2. Handle image embedding (photos, logos)
3. Handle page breaks between sections

**Output:** Service that generates PDF bytes

---

### Plan 08-03: PDF API Endpoint
**Focus:** Download endpoint

**Tasks:**
1. Create endpoint: `GET /reports/{id}/pdf`
2. Verify report is completed
3. Generate PDF on-the-fly
4. Return as file download with proper headers

**Output:** Working download endpoint

---

### Plan 08-04: Frontend Download Button
**Focus:** UI integration

**Tasks:**
1. Add "Download PDF" button to ReportFillPage (completed reports)
2. Handle download via blob/link
3. Show loading state during generation

**Output:** Users can download PDF

---

### Plan 08-05: Human Verification
**Focus:** Test PDF output

**Tasks:**
1. Generate PDF for completed report
2. Verify header with logos
3. Verify info fields section
4. Verify checklist with responses
5. Verify photo grid
6. Verify branding consistency

**Output:** Human approval of Phase 8

---

## Success Criteria Mapping

| Requirement | Plan | Criteria |
|-------------|------|----------|
| PDF-01 | 08-01, 08-02 | WeasyPrint + Jinja2 |
| PDF-02 | 08-01 | Header with logos |
| PDF-03 | 08-01 | Bilingual checklist |
| PDF-04 | 08-01, 08-02 | Photo grid |
| PDF-05 | 08-01 | Signatures in footer |
| PDF-06 | 08-01 | Tenant branding |
| PDF-07 | 08-03, 08-04 | Download from UI |

---

## Estimated Plans: 5
## Estimated Duration: ~2 hours
