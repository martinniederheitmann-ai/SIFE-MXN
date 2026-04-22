from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class DireccionKpiConfig(Base):
    __tablename__ = "direccion_kpi_configs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    scope_type: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    scope_value: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    config_json: Mapped[str] = mapped_column(Text, nullable=False)
    updated_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    history: Mapped[list["DireccionKpiConfigHistory"]] = relationship(
        "DireccionKpiConfigHistory",
        lazy="selectin",
        cascade="all, delete-orphan",
        passive_deletes=True,
        back_populates="config",
        order_by="DireccionKpiConfigHistory.id.desc()",
    )


class DireccionKpiConfigHistory(Base):
    __tablename__ = "direccion_kpi_config_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    config_id: Mapped[int] = mapped_column(
        ForeignKey("direccion_kpi_configs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    mode: Mapped[str] = mapped_column(String(32), nullable=False, default="manual")
    changes_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    config: Mapped["DireccionKpiConfig"] = relationship(
        "DireccionKpiConfig",
        lazy="select",
        back_populates="history",
    )
