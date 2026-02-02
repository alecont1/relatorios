# Phase 5: Template Configuration - Research

**Researched:** 2026-02-02
**Domain:** Dynamic form configuration UI, field metadata management, JSON schema
**Confidence:** HIGH

## Summary

Phase 5 extends the basic template management (Excel import) from Phase 4 by adding rich configuration capabilities for template fields. Admins need to configure info fields (project metadata), enhance checklist fields with photo/comment settings, and define signature fields. This is fundamentally about **post-import configuration** - templates already have their structure from Excel, but need additional metadata.

The standard approach combines React Hook Form's `useFieldArray` for dynamic field management, JSON/JSONB columns in PostgreSQL for flexible metadata storage, and accordion-based UI for organizing configuration sections. Key architectural decisions include:
- Store field configuration as JSONB in PostgreSQL (flexible schema, efficient queries)
- Use `useFieldArray` for managing dynamic field arrays in React
- Employ accordion/collapsible UI pattern for section-based configuration
- Separate info fields (template-level metadata) from checklist fields (section-level items)

**Primary recommendation:** Extend TemplateField model with JSONB columns for photo_config, comment_config, and validation_config. Create dedicated InfoField and SignatureField models with proper ordering. Use React Hook Form with accordion UI for configuration interface.

## Standard Stack

### Core Libraries (Already in Project)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| React Hook Form | 7.53.2 | Form state management | Already used project-wide, excellent `useFieldArray` for dynamic fields |
| Zod | 3.24.1 | Schema validation | Already used, ensures type-safe form validation |
| SQLAlchemy | 2.0+ | ORM with JSON support | Already used, native JSONB support for PostgreSQL |
| PostgreSQL | 14+ | Database with JSONB | Already used, efficient JSON querying with GIN indexes |

### Supporting (Need to Add)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| @dnd-kit/core | 6.1.0+ | Drag-and-drop for reordering | Optional: If allowing field reordering via drag-drop |
| @dnd-kit/sortable | 8.0.0+ | Sortable lists | Optional: Works with @dnd-kit/core for field ordering |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| JSONB columns | Separate tables (PhotoConfig, CommentConfig) | JSONB is more flexible for evolving schemas, separate tables add query complexity |
| useFieldArray | Formik FieldArray | React Hook Form already in use, better performance |
| Accordion UI | Modal per section | Accordion keeps all config visible, reduces navigation clicks |
| JSON config | EAV pattern | JSONB avoids EAV anti-pattern while maintaining flexibility |

**Installation:**
```bash
# Optional drag-and-drop (if implementing field reordering UI)
npm install @dnd-kit/core @dnd-kit/sortable
```

## Architecture Patterns

### Recommended Data Model Structure

```
backend/app/models/
├── template.py                  # Existing - add info_fields, signature_fields relationships
├── template_section.py          # Existing - no changes needed
├── template_field.py            # Existing - ADD photo_config, comment_config JSONB columns
├── template_info_field.py       # NEW - Info fields for project metadata
└── template_signature_field.py  # NEW - Signature fields with role names
```

### Pattern 1: JSONB for Field Metadata Configuration

**What:** Store field-level configuration (photo settings, comment settings) as JSONB columns rather than separate tables.

**When to use:** When configuration schema may evolve and different field types need different config options.

**Example:**
```python
# Source: SQLAlchemy PostgreSQL docs + research findings
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

class TemplateField(SimpleBase):
    __tablename__ = "template_fields"

    # Existing fields
    label: Mapped[str] = mapped_column(String(500), nullable=False)
    field_type: Mapped[str] = mapped_column(String(50), nullable=False)
    options: Mapped[str | None] = mapped_column(Text, nullable=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    # NEW: Field-level configuration as JSONB
    photo_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # Example: {"required": true, "min_count": 1, "max_count": 5, "require_gps": true, "watermark": true}

    comment_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # Example: {"enabled": true, "required": false}

    validation_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # Example: {"min": 0, "max": 100} for number fields
```

**Pydantic schema:**
```python
# backend/app/schemas/template.py
from pydantic import BaseModel, Field

class PhotoConfig(BaseModel):
    required: bool = False
    min_count: int = Field(default=0, ge=0)
    max_count: int = Field(default=10, ge=1, le=20)
    require_gps: bool = False
    watermark: bool = True

class CommentConfig(BaseModel):
    enabled: bool = True
    required: bool = False

class ValidationConfig(BaseModel):
    min: int | float | None = None
    max: int | float | None = None

class TemplateFieldUpdate(BaseModel):
    label: str | None = None
    photo_config: PhotoConfig | None = None
    comment_config: CommentConfig | None = None
    validation_config: ValidationConfig | None = None
```

**Why JSONB:** Modern PostgreSQL JSONB is efficient, queryable with GIN indexes, and allows schema evolution without migrations. Research shows JSONB is preferable for configuration data with variable structures.

### Pattern 2: Separate Models for Info Fields and Signature Fields

**What:** Create dedicated models for template-level metadata (info fields) and signature requirements.

**When to use:** When field types have fundamentally different purposes and lifecycles from checklist fields.

**Example:**
```python
# backend/app/models/template_info_field.py
class TemplateInfoField(SimpleBase):
    """
    Info fields capture project-level metadata (project name, date, location, etc.)
    Displayed at the top of reports before checklist sections.
    """
    __tablename__ = "template_info_fields"

    template_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("templates.id", ondelete="CASCADE"),
        nullable=False
    )

    label: Mapped[str] = mapped_column(String(255), nullable=False)
    field_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # Types: text, date, select
    options: Mapped[str | None] = mapped_column(Text, nullable=True)
    # For select type: JSON array of options
    required: Mapped[bool] = mapped_column(Boolean, default=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    template: Mapped["Template"] = relationship(
        "Template",
        back_populates="info_fields"
    )

# backend/app/models/template_signature_field.py
class TemplateSignatureField(SimpleBase):
    """
    Signature fields define who must sign the report.
    Each field has a role name (e.g., "Technician", "Supervisor") and required flag.
    """
    __tablename__ = "template_signature_fields"

    template_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("templates.id", ondelete="CASCADE"),
        nullable=False
    )

    role_name: Mapped[str] = mapped_column(String(100), nullable=False)
    # Examples: "Technician", "Supervisor", "Client Representative"
    required: Mapped[bool] = mapped_column(Boolean, default=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    template: Mapped["Template"] = relationship(
        "Template",
        back_populates="signature_fields"
    )
```

**Why separate models:** Info fields and signature fields have distinct purposes, different field sets, and different UI placement. Mixing them with checklist fields would create confusion.

### Pattern 3: useFieldArray for Dynamic Field Configuration UI

**What:** Use React Hook Form's `useFieldArray` hook to manage arrays of configurable fields.

**When to use:** When users need to add, remove, or reorder fields dynamically.

**Example:**
```typescript
// Source: React Hook Form docs + research findings
import { useForm, useFieldArray, Controller } from 'react-hook-form'

interface InfoFieldConfig {
  id?: string
  label: string
  field_type: 'text' | 'date' | 'select'
  options?: string[]
  required: boolean
  order: number
}

export function InfoFieldsConfigurator({ templateId }: { templateId: string }) {
  const { control, register, handleSubmit } = useForm<{
    info_fields: InfoFieldConfig[]
  }>()

  const { fields, append, remove, move } = useFieldArray({
    control,
    name: 'info_fields',
    keyName: 'key' // IMPORTANT: Use 'key' instead of 'id' to avoid conflicts
  })

  return (
    <div className="space-y-4">
      {fields.map((field, index) => (
        <div key={field.key} className="border rounded-lg p-4">
          <input
            {...register(`info_fields.${index}.label`)}
            placeholder="Field label"
            className="w-full px-3 py-2 border rounded"
          />

          <select
            {...register(`info_fields.${index}.field_type`)}
            className="w-full px-3 py-2 border rounded mt-2"
          >
            <option value="text">Text</option>
            <option value="date">Date</option>
            <option value="select">Select</option>
          </select>

          <label className="flex items-center mt-2">
            <input
              {...register(`info_fields.${index}.required`)}
              type="checkbox"
              className="mr-2"
            />
            Required
          </label>

          <button
            type="button"
            onClick={() => remove(index)}
            className="mt-2 text-red-600"
          >
            Remove
          </button>
        </div>
      ))}

      <button
        type="button"
        onClick={() => append({
          label: '',
          field_type: 'text',
          required: true,
          order: fields.length
        })}
        className="px-4 py-2 bg-blue-600 text-white rounded"
      >
        Add Info Field
      </button>
    </div>
  )
}
```

**Best practices:**
- Always use `field.key` (or custom keyName) as React key, never index
- Provide complete default values when calling `append()`
- Don't stack multiple actions (append, then remove) - keep them separate
- Use Controller for custom components, register for native inputs

### Pattern 4: Accordion UI for Configuration Sections

**What:** Use accordion/collapsible pattern to organize configuration into logical sections.

**When to use:** When configuration has multiple related sections (info fields, sections with fields, photo settings, signatures).

**Example:**
```typescript
// Lightweight accordion implementation (no external library needed)
import { useState } from 'react'
import { ChevronDown } from 'lucide-react'

interface AccordionSectionProps {
  title: string
  defaultOpen?: boolean
  children: React.ReactNode
}

function AccordionSection({ title, defaultOpen = false, children }: AccordionSectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen)

  return (
    <div className="border rounded-lg">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50"
      >
        <h3 className="text-lg font-medium">{title}</h3>
        <ChevronDown
          className={`w-5 h-5 transition-transform ${isOpen ? 'rotate-180' : ''}`}
        />
      </button>

      {isOpen && (
        <div className="p-4 border-t">
          {children}
        </div>
      )}
    </div>
  )
}

// Usage in configuration page
export function TemplateConfigurationPage() {
  return (
    <div className="space-y-4">
      <AccordionSection title="Info Fields" defaultOpen={true}>
        <InfoFieldsConfigurator />
      </AccordionSection>

      <AccordionSection title="Checklist Sections">
        <ChecklistSectionsConfigurator />
      </AccordionSection>

      <AccordionSection title="Signature Fields">
        <SignatureFieldsConfigurator />
      </AccordionSection>
    </div>
  )
}
```

**Alternative:** Use Material-UI Accordion (if adding MUI), but custom implementation is lightweight and sufficient.

### Anti-Patterns to Avoid

- **EAV Pattern for Configuration:** Don't create generic key-value tables for field config - use JSONB instead
- **Mixing Field Types:** Don't store info fields, checklist fields, and signature fields in same table with type discriminator
- **Index as React Key:** Never use array index as key in `useFieldArray` - always use generated `id`/`key`
- **Stacking useFieldArray Actions:** Don't chain `append().then(() => remove())` - keep operations separate
- **Nested Field Arrays Without Control:** Always pass `control` from parent form to nested `useFieldArray` hooks

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Drag-and-drop reordering | Custom mouse event handling | @dnd-kit/sortable | Handles touch, keyboard a11y, ghost elements, drop animations |
| JSON validation in DB | Manual JSON string parsing | PostgreSQL JSONB + CHECK constraints | Database enforces data integrity |
| Form state tracking | Custom useState per field | React Hook Form useFieldArray | Automatic validation, dirty tracking, error handling |
| Accordion components | Custom show/hide logic | Simple controlled accordion (see Pattern 4) | Needs animation, a11y, keyboard nav |
| Field ordering | Manual index manipulation | useFieldArray's `move()` method | Handles all edge cases correctly |

**Key insight:** Field configuration UIs look simple but have complex state management (add, remove, reorder, validate). React Hook Form's `useFieldArray` handles this complexity with proper dirty tracking, validation, and error handling.

## Common Pitfalls

### Pitfall 1: JSONB Mutation Tracking in SQLAlchemy

**What goes wrong:** Changes to nested JSONB fields aren't detected by SQLAlchemy, so updates don't persist.

**Why it happens:** SQLAlchemy doesn't track mutations inside JSON objects by default.

**How to avoid:**
```python
# Option 1: Use flag_modified (recommended for simple cases)
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

field.photo_config['required'] = True
flag_modified(field, 'photo_config')
session.commit()

# Option 2: Reassign entire dict (simple but less efficient)
field.photo_config = {**field.photo_config, 'required': True}
session.commit()

# Option 3: Use MutableDict (for complex nested updates)
from sqlalchemy.ext.mutable import MutableDict
# In model definition:
photo_config: Mapped[dict | None] = mapped_column(
    MutableDict.as_mutable(JSONB),
    nullable=True
)
```

**Warning signs:** Changes appear to save but disappear after refetching from database.

**Source:** [SQLAlchemy JSON mutation tracking](https://amercader.net/blog/beware-of-json-fields-in-sqlalchemy/)

### Pitfall 2: useFieldArray Index as Key

**What goes wrong:** Using array index as React key causes fields to swap values when reordering.

**Why it happens:** React reconciliation reuses components based on key, so wrong data gets rendered.

**How to avoid:**
```typescript
// ❌ WRONG - Will cause bugs
{fields.map((field, index) => (
  <div key={index}>...</div>
))}

// ✅ CORRECT - Use generated ID
{fields.map((field) => (
  <div key={field.id}>...</div>
))}

// ✅ CORRECT - Use custom key name if 'id' conflicts
const { fields } = useFieldArray({
  control,
  name: 'fields',
  keyName: 'key' // Generated as field.key instead of field.id
})

{fields.map((field) => (
  <div key={field.key}>...</div>
))}
```

**Warning signs:** Field values jump to wrong fields after reordering or removing items.

**Source:** [React Hook Form useFieldArray docs](https://react-hook-form.com/docs/usefieldarray)

### Pitfall 3: Empty Default Values in useFieldArray

**What goes wrong:** Appending incomplete objects causes validation errors and missing field registrations.

**Why it happens:** React Hook Form needs complete structure to register all fields properly.

**How to avoid:**
```typescript
// ❌ WRONG - Incomplete object
append({}) // Will cause registration issues

// ❌ WRONG - Partial object
append({ label: 'New Field' }) // Missing required fields

// ✅ CORRECT - Complete object with all fields
append({
  label: '',
  field_type: 'text',
  options: [],
  required: false,
  order: fields.length,
  photo_config: {
    required: false,
    min_count: 0,
    max_count: 10,
    require_gps: false,
    watermark: true
  },
  comment_config: {
    enabled: true,
    required: false
  }
})
```

**Warning signs:** Console warnings about uncontrolled inputs, validation not working on new fields.

**Source:** [React Hook Form useFieldArray best practices](https://refine.dev/blog/dynamic-forms-in-react-hook-form/)

### Pitfall 4: Forgetting Cascade Delete

**What goes wrong:** Orphaned info fields and signature fields remain in DB after template deletion.

**Why it happens:** Missing `ondelete="CASCADE"` on foreign keys.

**How to avoid:**
```python
# ✅ CORRECT - Cascade delete in foreign key
template_id: Mapped[uuid.UUID] = mapped_column(
    ForeignKey("templates.id", ondelete="CASCADE"),
    nullable=False
)

# ✅ CORRECT - Cascade delete in relationship
info_fields: Mapped[list["TemplateInfoField"]] = relationship(
    "TemplateInfoField",
    back_populates="template",
    cascade="all, delete-orphan",
    order_by="TemplateInfoField.order"
)
```

**Warning signs:** Database constraint violations when trying to delete templates.

## Code Examples

Verified patterns from official sources:

### Checklist Field Configuration Form

```typescript
// Source: React Hook Form + research patterns
import { useForm, Controller } from 'react-hook-form'

interface ChecklistFieldConfigForm {
  photo_config: {
    required: boolean
    min_count: number
    max_count: number
    require_gps: boolean
    watermark: boolean
  }
  comment_config: {
    enabled: boolean
    required: boolean
  }
}

export function ChecklistFieldConfigurator({
  fieldId,
  currentConfig
}: {
  fieldId: string
  currentConfig: ChecklistFieldConfigForm
}) {
  const { register, control, handleSubmit } = useForm<ChecklistFieldConfigForm>({
    defaultValues: currentConfig
  })

  const onSubmit = async (data: ChecklistFieldConfigForm) => {
    await api.patch(`/templates/fields/${fieldId}`, data)
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Photo Configuration */}
      <section className="border rounded-lg p-4">
        <h4 className="font-medium mb-3">Photo Settings</h4>

        <label className="flex items-center gap-2 mb-2">
          <input
            {...register('photo_config.required')}
            type="checkbox"
            className="rounded"
          />
          <span>Photos required</span>
        </label>

        <div className="grid grid-cols-2 gap-4 mb-2">
          <div>
            <label className="block text-sm mb-1">Min photos</label>
            <input
              {...register('photo_config.min_count', { valueAsNumber: true })}
              type="number"
              min="0"
              className="w-full px-3 py-2 border rounded"
            />
          </div>

          <div>
            <label className="block text-sm mb-1">Max photos</label>
            <input
              {...register('photo_config.max_count', { valueAsNumber: true })}
              type="number"
              min="1"
              max="20"
              className="w-full px-3 py-2 border rounded"
            />
          </div>
        </div>

        <label className="flex items-center gap-2 mb-2">
          <input
            {...register('photo_config.require_gps')}
            type="checkbox"
            className="rounded"
          />
          <span>Require GPS location</span>
        </label>

        <label className="flex items-center gap-2">
          <input
            {...register('photo_config.watermark')}
            type="checkbox"
            className="rounded"
          />
          <span>Apply watermark</span>
        </label>
      </section>

      {/* Comment Configuration */}
      <section className="border rounded-lg p-4">
        <h4 className="font-medium mb-3">Comment Settings</h4>

        <label className="flex items-center gap-2 mb-2">
          <input
            {...register('comment_config.enabled')}
            type="checkbox"
            className="rounded"
          />
          <span>Enable comments</span>
        </label>

        <label className="flex items-center gap-2">
          <input
            {...register('comment_config.required')}
            type="checkbox"
            className="rounded"
          />
          <span>Comments required</span>
        </label>
      </section>

      <button
        type="submit"
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Save Configuration
      </button>
    </form>
  )
}
```

### Info Fields API Endpoint

```python
# Source: FastAPI + SQLAlchemy patterns
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

router = APIRouter()

@router.post("/templates/{template_id}/info-fields")
async def create_info_field(
    template_id: UUID,
    data: InfoFieldCreate,
    tenant_id: Annotated[UUID, Depends(get_tenant_filter)],
    db: AsyncSession = Depends(get_db),
) -> InfoFieldResponse:
    """Create a new info field for template."""
    # Verify template exists and belongs to tenant
    template = await db.execute(
        select(Template)
        .where(Template.id == template_id)
        .where(Template.tenant_id == tenant_id)
    )
    template = template.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Get current max order
    result = await db.execute(
        select(func.max(TemplateInfoField.order))
        .where(TemplateInfoField.template_id == template_id)
    )
    max_order = result.scalar() or 0

    # Create info field
    info_field = TemplateInfoField(
        template_id=template_id,
        label=data.label,
        field_type=data.field_type,
        options=json.dumps(data.options) if data.options else None,
        required=data.required,
        order=max_order + 1
    )
    db.add(info_field)
    await db.commit()
    await db.refresh(info_field)

    return InfoFieldResponse.model_validate(info_field)

@router.patch("/templates/fields/{field_id}")
async def update_field_configuration(
    field_id: UUID,
    data: FieldConfigUpdate,
    tenant_id: Annotated[UUID, Depends(get_tenant_filter)],
    db: AsyncSession = Depends(get_db),
) -> TemplateFieldResponse:
    """Update field-level configuration (photo/comment settings)."""
    # Verify field exists and template belongs to tenant
    field = await db.execute(
        select(TemplateField)
        .join(TemplateSection)
        .join(Template)
        .where(TemplateField.id == field_id)
        .where(Template.tenant_id == tenant_id)
    )
    field = field.scalar_one_or_none()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")

    # Update configurations (JSONB columns)
    if data.photo_config is not None:
        field.photo_config = data.photo_config.model_dump()
        flag_modified(field, 'photo_config')

    if data.comment_config is not None:
        field.comment_config = data.comment_config.model_dump()
        flag_modified(field, 'comment_config')

    if data.validation_config is not None:
        field.validation_config = data.validation_config.model_dump()
        flag_modified(field, 'validation_config')

    await db.commit()
    await db.refresh(field)

    return TemplateFieldResponse.model_validate(field)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| EAV tables for config | JSONB columns | ~2018 (Postgres 9.2+) | Simpler queries, better performance with GIN indexes |
| Separate PhotoConfig table | photo_config JSONB column | - | Fewer joins, flexible schema evolution |
| Manual form state | React Hook Form useFieldArray | 2021 | Built-in validation, dirty tracking, error handling |
| Class components | Function components with hooks | 2019 (React 16.8) | Cleaner code, better composition |
| Redux for forms | Local form state with RHF | 2020+ | Less boilerplate, better performance |

**Deprecated/outdated:**
- EAV pattern: Replaced by JSONB for configuration data
- Formik: React Hook Form is preferred in 2026 for better performance
- Class-based forms: Function components with hooks are standard

## Open Questions

Things that couldn't be fully resolved:

1. **Field reordering UX**
   - What we know: Can implement drag-and-drop with @dnd-kit or manual up/down buttons
   - What's unclear: User preference - is drag-drop worth the complexity for admin-only UI?
   - Recommendation: Start with simple up/down arrow buttons, add drag-drop if users request it

2. **Info field duplication across templates**
   - What we know: Each template has its own info fields, but many templates likely share common fields (project name, date, etc.)
   - What's unclear: Should there be "standard" info fields that can be copied to new templates?
   - Recommendation: Defer to future phase - start with per-template config, add template cloning if needed

3. **Photo config validation boundaries**
   - What we know: Need min/max photo count, but what are reasonable limits?
   - What's unclear: Is 20 max photos too many? Should it be configurable per tenant?
   - Recommendation: Hard-code 0-20 range initially, make tenant-configurable if users report issues

4. **Signature field ordering vs roles**
   - What we know: Signature fields have order and role_name
   - What's unclear: Does order affect PDF display order or just admin UI sorting?
   - Recommendation: Order should control PDF display order - document this in API clearly

## Sources

### Primary (HIGH confidence)

- [React Hook Form - useFieldArray](https://react-hook-form.com/docs/usefieldarray) - Official API documentation
- [SQLAlchemy PostgreSQL Dialect](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html) - JSONB type usage
- [React Hook Form Dynamic Forms - Refine](https://refine.dev/blog/dynamic-forms-in-react-hook-form/) - Best practices guide
- [Beware of JSON fields in SQLAlchemy](https://amercader.net/blog/beware-of-json-fields-in-sqlalchemy/) - Mutation tracking patterns

### Secondary (MEDIUM confidence)

- [When to use JSON data type in database schema design](https://shekhargulati.com/2022/01/08/when-to-use-json-data-type-in-database-schema-design/) - JSON vs columns decision guide
- [Top 5 Drag-and-Drop Libraries for React in 2026](https://puckeditor.com/blog/top-5-drag-and-drop-libraries-for-react) - dnd-kit recommendation
- [Adobe Acrobat Sign Text Tag Guide](https://helpx.adobe.com/sign/using/text-tag.html) - Signature field patterns
- [UI Form Design Best Practices 2026 - IxDF](https://www.interaction-design.org/literature/article/ui-form-design) - Form UX guidelines
- [Radio Button vs Checkbox - NN/G](https://www.nngroup.com/articles/checkboxes-vs-radio-buttons/) - Field type selection

### Tertiary (LOW confidence)

- [FormEngine - Open-Source Form Builder](https://formengine.io/) - Form builder patterns
- [Builder - React Form Builder](https://builder.coltorapps.com/) - JSON schema forms
- Various Medium articles on React form patterns (verified against official docs)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries already in project or officially documented
- Architecture: HIGH - Patterns verified with official SQLAlchemy and React Hook Form docs
- Pitfalls: HIGH - Sourced from official docs and authoritative blog posts

**Research date:** 2026-02-02
**Valid until:** ~60 days (stable technologies, minimal API changes expected)

**Key technical decisions:**
1. JSONB for field configuration - flexible, performant, queryable
2. Separate models for info/signature fields - clear separation of concerns
3. useFieldArray for dynamic UI - battle-tested, full-featured
4. Accordion pattern for configuration sections - standard UX pattern
5. Order field for explicit sequencing - avoids implicit array index dependencies

**Implementation complexity:** Medium
- Database migrations: 3 new models + JSONB columns on existing model
- API endpoints: ~8-10 endpoints (CRUD for info fields, signatures, field config updates)
- Frontend components: ~6-8 components (accordions, field configurators, lists)
- Estimated effort: 5 plans covering data models, API endpoints, UI components, integration testing

**Risks:**
- JSONB mutation tracking in SQLAlchemy (mitigated with `flag_modified`)
- useFieldArray key management (mitigated by using generated keys)
- Validation complexity across nested config objects (mitigated with Pydantic schemas)

**Dependencies:**
- Phase 4 must be complete (templates, sections, fields must exist)
- No new external services required
- No infrastructure changes needed
