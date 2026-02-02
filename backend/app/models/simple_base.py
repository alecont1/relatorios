"""
SimpleBase - Base class for models that don't need tenant_id.

Models inheriting from SimpleBase:
- TemplateSection (inherits tenant isolation via Template)
- TemplateField (inherits tenant isolation via TemplateSection)
- TemplateInfoField (inherits tenant isolation via Template)
- TemplateSignatureField (inherits tenant isolation via Template)
"""

from app.models.base import Base


class SimpleBase(Base):
    """
    Simple base model for child tables that don't need tenant_id.

    Used for models that inherit tenant isolation through their parent
    (e.g., TemplateSection belongs to Template which has tenant_id).

    Inherits from Base but marks tenant_id as excluded by setting
    __abstract__ = True and relying on Base's declared_attr logic
    that checks class name.
    """

    __abstract__ = True

    # Override tenant_id to be None for SimpleBase subclasses
    # The Base.tenant_id declared_attr will return None if __tablename__
    # starts with 'template_' (child tables)
    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Mark that this class should not have tenant_id
        cls._exclude_tenant_id = True
