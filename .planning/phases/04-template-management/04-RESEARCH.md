# Phase 4: Template Management - Research

**Researched:** 2026-01-31
**Confidence:** HIGH

---

## 1. Excel Parsing in Python

### Library Choice: openpyxl

**Why openpyxl over pandas:**
- Row-by-row validation with granular error collection
- Memory-efficient streaming for large files
- Native Excel format support (.xlsx)
- Better control over cell-level validation

**Installation:**
```bash
pip install openpyxl
```

**Key patterns:**
```python
from openpyxl import load_workbook
from io import BytesIO

# Load from bytes (FastAPI UploadFile)
wb = load_workbook(filename=BytesIO(file_content), read_only=True)
sheet = wb.active

# Row-by-row with error collection
errors = []
rows = []
for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
    section, step, result_type, options = row[:4]
    if not section:
        errors.append(f"Row {row_num}: Section is required")
    if result_type not in ["Drop Down", "Text"]:
        errors.append(f"Row {row_num}: Invalid Result Type '{result_type}'")
    # Continue collecting ALL errors, don't fail early
```

### Expected Excel Format

| Section | Script Step | Result Type | Step Result Values |
|---------|-------------|-------------|-------------------|
| General | Check power supply | Drop Down | Yes/No/NA |
| General | Serial number | Text | |
| Electrical | Voltage reading | Text | |

---

## 2. Template Data Model

### Database Schema

```python
# Template model
class Template(TenantScopedBase):
    __tablename__ = "templates"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)

    # Metadata
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)  # COM-001, INS-002
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # Commissioning, Inspection, etc.
    version: Mapped[int] = mapped_column(Integer, default=1)

    # Header fields (TMPL-05)
    title: Mapped[str | None] = mapped_column(String(500))
    reference_standards: Mapped[str | None] = mapped_column(Text)
    planning_requirements: Mapped[str | None] = mapped_column(Text)

    # Lifecycle
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    sections: Mapped[list["TemplateSection"]] = relationship(back_populates="template", cascade="all, delete-orphan")

# Section model
class TemplateSection(Base):
    __tablename__ = "template_sections"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    template_id: Mapped[UUID] = mapped_column(ForeignKey("templates.id"), nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    template: Mapped["Template"] = relationship(back_populates="sections")
    fields: Mapped[list["TemplateField"]] = relationship(back_populates="section", cascade="all, delete-orphan")

# Field model (checklist items)
class TemplateField(Base):
    __tablename__ = "template_fields"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    section_id: Mapped[UUID] = mapped_column(ForeignKey("template_sections.id"), nullable=False)

    label: Mapped[str] = mapped_column(String(500), nullable=False)  # Script Step
    field_type: Mapped[str] = mapped_column(String(50), nullable=False)  # dropdown, text
    options: Mapped[str | None] = mapped_column(Text)  # JSON array for dropdown options
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    section: Mapped["TemplateSection"] = relationship(back_populates="fields")
```

### Code Auto-Generation

Pattern: `{CATEGORY_PREFIX}-{SEQUENCE}`

```python
async def generate_template_code(db: AsyncSession, tenant_id: UUID, category: str) -> str:
    """Generate next code like COM-001, INS-002."""
    prefix_map = {
        "Commissioning": "COM",
        "Inspection": "INS",
        "Maintenance": "MNT",
        "Testing": "TST",
    }
    prefix = prefix_map[category]

    # Get max sequence for this category in tenant
    result = await db.execute(
        select(func.max(Template.code))
        .where(Template.tenant_id == tenant_id)
        .where(Template.code.like(f"{prefix}-%"))
    )
    max_code = result.scalar()

    if max_code:
        # Extract number and increment
        seq = int(max_code.split("-")[1]) + 1
    else:
        seq = 1

    return f"{prefix}-{seq:03d}"
```

---

## 3. Two-Phase Upload Workflow

### Phase 1: Validate & Preview (No DB writes)

```
POST /api/v1/templates/parse
Content-Type: multipart/form-data

file: (Excel file)
```

Response:
```json
{
  "valid": true,
  "sections": [
    {
      "name": "General",
      "fields": [
        {"label": "Check power supply", "field_type": "dropdown", "options": ["Yes", "No", "NA"]},
        {"label": "Serial number", "field_type": "text", "options": null}
      ]
    }
  ],
  "summary": {
    "section_count": 3,
    "field_count": 15
  }
}
```

Or with errors:
```json
{
  "valid": false,
  "errors": [
    "Row 5: Section is required",
    "Row 8: Invalid Result Type 'Checkbox'"
  ]
}
```

### Phase 2: Confirm & Save

```
POST /api/v1/templates
Content-Type: application/json

{
  "name": "Commissioning Report v1",
  "category": "Commissioning",
  "sections": [...parsed sections from preview...]
}
```

---

## 4. Frontend Implementation

### File Upload: react-dropzone

```bash
npm install react-dropzone
```

```tsx
import { useDropzone } from 'react-dropzone';

function ExcelUploader({ onParsed }) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
    },
    maxFiles: 1,
    onDrop: async (files) => {
      const formData = new FormData();
      formData.append('file', files[0]);
      const result = await api.post('/templates/parse', formData);
      onParsed(result.data);
    }
  });

  return (
    <div {...getRootProps()} className="border-2 border-dashed p-8 text-center">
      <input {...getInputProps()} />
      {isDragActive ? 'Drop here...' : 'Drag Excel file or click to select'}
    </div>
  );
}
```

### Template List with Search

```tsx
function TemplateList() {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'inactive'>('active');

  const { data: templates } = useQuery({
    queryKey: ['templates', search, statusFilter],
    queryFn: () => api.get('/templates', { params: { search, status: statusFilter } }),
    // Debounced search happens via query key change
  });
}
```

### Debounced Search Hook

```tsx
function useDebouncedValue<T>(value: T, delay: number = 300): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}
```

---

## 5. API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/templates` | GET | List templates (search, status filter) |
| `/templates` | POST | Create template (after preview confirm) |
| `/templates/{id}` | GET | Get single template with sections/fields |
| `/templates/{id}` | PATCH | Update template metadata |
| `/templates/{id}` | DELETE | Delete template (soft delete via is_active) |
| `/templates/parse` | POST | Parse Excel and return preview |

---

## 6. Tenant Isolation

All template queries MUST include tenant filtering:

```python
@router.get("/templates")
async def list_templates(
    tenant_id: Annotated[UUID, Depends(get_tenant_filter)],
    db: AsyncSession = Depends(get_db),
    search: str = "",
    status: str = "active",
):
    query = select(Template).where(Template.tenant_id == tenant_id)

    if search:
        query = query.where(
            or_(
                Template.name.ilike(f"%{search}%"),
                Template.code.ilike(f"%{search}%")
            )
        )

    if status == "active":
        query = query.where(Template.is_active == True)
    elif status == "inactive":
        query = query.where(Template.is_active == False)

    query = query.order_by(Template.name.asc())

    result = await db.execute(query)
    return result.scalars().all()
```

---

## 7. Key Decisions

1. **No global templates** - User clarified TMPL-04 is deferred; each tenant has own templates
2. **Excel-only creation** - No manual field-by-field entry
3. **Preview required** - Must show parsed content before saving
4. **All errors at once** - Don't fail on first error, collect all
5. **Predefined categories** - Commissioning, Inspection, Maintenance, Testing
6. **Code auto-generation** - Category prefix + sequence number

---

## 8. Open Questions for Planning

1. **Version handling** - Auto-increment on edit or manual?
2. **Template deletion** - Soft delete (is_active=false) or hard delete?
3. **Cascade behavior** - What happens to reports using deleted template?

---

*Research completed: 2026-01-31*
*Phase: 04-template-management*
