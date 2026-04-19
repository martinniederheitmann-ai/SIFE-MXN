from __future__ import annotations

import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class TipoPagoOperadorEnum(str, enum.Enum):
    VIAJE = "viaje"
    BONO = "bono"
    VIATICOS = "viaticos"


class EstatusPagoOperador(str, enum.Enum):
    PENDIENTE = "pendiente"
    PAGADO = "pagado"
    CANCELADO = "cancelado"


def _pago_enum(cls: type[enum.Enum], length: int) -> Enum:
    return Enum(
        cls,
        values_callable=lambda x: [e.value for e in x],
        native_enum=False,
        length=length,
    )


class PagoOperador(Base):
    __tablename__ = "pagos_operador"

    id_pago: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_operador: Mapped[int] = mapped_column(
        ForeignKey("operadores.id_operador", ondelete="CASCADE"), nullable=False, index=True
    )
    tipo_pago: Mapped[TipoPagoOperadorEnum] = mapped_column(
        _pago_enum(TipoPagoOperadorEnum, 24), nullable=False
    )
    monto: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    concepto: Mapped[str | None] = mapped_column(String(500), nullable=True)
    estatus: Mapped[EstatusPagoOperador] = mapped_column(
        _pago_enum(EstatusPagoOperador, 16),
        default=EstatusPagoOperador.PENDIENTE,
        nullable=False,
    )
    notas: Mapped[str | None] = mapped_column(Text, nullable=True)

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
