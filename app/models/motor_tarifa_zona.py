"""Presets de CPK / márgenes por región y tipo de unidad (mercado MX)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class MotorTarifaZonaPreset(Base):
    __tablename__ = "motor_tarifa_zona_presets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    region_key: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    tipo_unidad_norm: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    cpk_referencia: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    mu_local: Mapped[Decimal | None] = mapped_column(Numeric(8, 4), nullable=True)
    mu_estatal: Mapped[Decimal | None] = mapped_column(Numeric(8, 4), nullable=True)
    mu_federal: Mapped[Decimal | None] = mapped_column(Numeric(8, 4), nullable=True)
    notas: Mapped[str | None] = mapped_column(String(500), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
