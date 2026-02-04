"""
SimpleBase - Alias for Base (no tenant_id).

Models inheriting from SimpleBase (or Base directly):
- TemplateSection (inherits tenant isolation via Template)
- TemplateField (inherits tenant isolation via TemplateSection)
- TemplateInfoField (inherits tenant isolation via Template)
- TemplateSignatureField (inherits tenant isolation via Template)
- ReportChecklistResponse (inherits tenant isolation via Report)
- ReportInfoValue (inherits tenant isolation via Report)
- ReportPhoto (inherits tenant isolation via Report)
- ReportSignature (inherits tenant isolation via Report)
"""

from app.models.base import Base


class SimpleBase(Base):
    """
    Simple base model for child tables that don't need tenant_id.

    Used for models that inherit tenant isolation through their parent
    (e.g., TemplateSection belongs to Template which has tenant_id).

    This is just an alias for Base to make the intent clear.
    """

    __abstract__ = True
