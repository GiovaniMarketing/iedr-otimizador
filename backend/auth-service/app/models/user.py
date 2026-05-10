from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

from app.models.base import Base, TenantMixin, TimestampMixin


class User(Base, TenantMixin, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # =========================
    # RBAC (ROLES)
    # =========================
    role: Mapped[str] = mapped_column(
        String(50),
        default="user",
        nullable=False
    )

    # =========================
    # STATUS
    # =========================
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )