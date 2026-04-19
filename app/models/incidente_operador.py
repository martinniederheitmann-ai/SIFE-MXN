from __future__ import annotations

import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class TipoIncidenteOperador(str, enum.Enum):
    ACCIDENTE = "accidente"
    INFRACCION = "infraccion"
    ROBO = "robo"


def _inc_enum(cls: type[enum.Enum], length: int) -> Enum:
    return Enum(
        cls,
        values_callable=lambda x: [e.value for e in x],
        native_enum=False,
        length=length,
    )


class IncidenteOperador(Base):
    __tablename__ = "incidentes_operador"

    id_incidente: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_operador: Mapped[int] = mapped_column(
        ForeignKey("operadores.id_operador", ondelete="CASCADE"), nullable=False, index=True
    )
    tipo: Mapped[TipoIncidenteOperador] = mapped_column(
        _inc_enum(TipoIncidenteOperador, 24), nullable=False
    )
    fecha: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    costo_estimado: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    resolucion: Mapped[str | None] = mapped_column(Text, nullable=True)

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
