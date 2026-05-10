from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, DateTime, func


# =========================
# BASE ORM (SQLAlchemy 2.0)
# =========================
class Base(DeclarativeBase):
    pass


# =========================
# MIXIN: MULTI-TENANT OBRIGATÓRIO
# =========================
class TenantMixin:
    company_id: Mapped[int] = mapped_column(
        Integer,
        index=True,
        nullable=False
    )


# =========================
# MIXIN: AUDITORIA (SAA S READY)
# =========================
class TimestampMixin:
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


# =========================
# BASE COMPLETA (OPCIONAL USO DIRETO)
# =========================
class BaseModel(Base, TenantMixin, TimestampMixin):
    """
    Use esta base quando quiser que o model já venha:
    - multi-tenant
    - com timestamps
    """
    __abstract__ = True