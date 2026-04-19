from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Asignacion(Base):
    __tablename__ = "asignaciones"

    id_asignacion: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_operador: Mapped[int] = mapped_column(
        ForeignKey("operadores.id_operador", ondelete="RESTRICT"), nullable=False, index=True
    )
    id_unidad: Mapped[int] = mapped_column(
        ForeignKey("unidades.id_unidad", ondelete="RESTRICT"), nullable=False, index=True
    )
    id_viaje: Mapped[int] = mapped_column(
        ForeignKey("viajes.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    fecha_salida: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fecha_regreso: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    km_inicial: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    km_final: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    rendimiento_combustible: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 3), nullable=True, comment="Ej. km/L o L/100km según política interna"
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

    operador: Mapped["Operador"] = relationship("Operador", lazy="select")
    unidad: Mapped["Unidad"] = relationship("Unidad", lazy="select")
    viaje: Mapped["Viaje"] = relationship("Viaje", lazy="select")
