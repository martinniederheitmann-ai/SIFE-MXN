from __future__ import annotations

import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class TipoContratoOperador(str, enum.Enum):
    PLANTA = "planta"
    EVENTUAL = "eventual"


class PuestoOperador(str, enum.Enum):
    OPERADOR_LOCAL = "operador_local"
    OPERADOR_FEDERAL = "operador_federal"


class TipoPagoLaboral(str, enum.Enum):
    VIAJE = "viaje"
    SEMANAL = "semanal"
    MIXTO = "mixto"


class EstatusLaboralOperador(str, enum.Enum):
    ACTIVO = "activo"
    BAJA = "baja"
    SUSPENDIDO = "suspendido"


def _lab_enum(cls: type[enum.Enum], length: int) -> Enum:
    return Enum(
        cls,
        values_callable=lambda x: [e.value for e in x],
        native_enum=False,
        length=length,
    )


class OperadorLaboral(Base):
    __tablename__ = "operador_laboral"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_operador: Mapped[int] = mapped_column(
        ForeignKey("operadores.id_operador", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    fecha_ingreso: Mapped[date] = mapped_column(Date, nullable=False)
    tipo_contrato: Mapped[TipoContratoOperador] = mapped_column(
        _lab_enum(TipoContratoOperador, 24), nullable=False
    )
    puesto: Mapped[PuestoOperador] = mapped_column(_lab_enum(PuestoOperador, 32), nullable=False)
    salario_base: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    tipo_pago: Mapped[TipoPagoLaboral] = mapped_column(
        _lab_enum(TipoPagoLaboral, 24), nullable=False
    )
    estatus: Mapped[EstatusLaboralOperador] = mapped_column(
        _lab_enum(EstatusLaboralOperador, 24),
        default=EstatusLaboralOperador.ACTIVO,
        nullable=False,
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
