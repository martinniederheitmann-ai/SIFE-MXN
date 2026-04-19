from __future__ import annotations

import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, Enum, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.transportista import TipoTransportista


def _enum_str(cls: type[enum.Enum], length: int) -> Enum:
    return Enum(
        cls,
        values_callable=lambda x: [e.value for e in x],
        native_enum=False,
        length=length,
    )


class AmbitoTarifaFlete(str, enum.Enum):
    LOCAL = "local"
    ESTATAL = "estatal"
    FEDERAL = "federal"


class ModalidadCobroTarifa(str, enum.Enum):
    MIXTA = "mixta"
    POR_VIAJE = "por_viaje"
    POR_KM = "por_km"
    POR_TONELADA = "por_tonelada"
    POR_HORA = "por_hora"
    POR_DIA = "por_dia"


class TarifaFlete(Base):
    __tablename__ = "tarifas_flete"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre_tarifa: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    tipo_operacion: Mapped[TipoTransportista] = mapped_column(
        _enum_str(TipoTransportista, 32),
        nullable=False,
        default=TipoTransportista.SUBCONTRATADO,
    )
    ambito: Mapped[AmbitoTarifaFlete] = mapped_column(
        _enum_str(AmbitoTarifaFlete, 24),
        nullable=False,
        default=AmbitoTarifaFlete.FEDERAL,
    )
    modalidad_cobro: Mapped[ModalidadCobroTarifa] = mapped_column(
        _enum_str(ModalidadCobroTarifa, 24),
        nullable=False,
        default=ModalidadCobroTarifa.MIXTA,
    )
    origen: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    destino: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    tipo_unidad: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    tipo_carga: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    tarifa_base: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    tarifa_km: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False, default=Decimal("0"))
    tarifa_kg: Mapped[Decimal] = mapped_column(Numeric(14, 6), nullable=False, default=Decimal("0"))
    tarifa_tonelada: Mapped[Decimal] = mapped_column(
        Numeric(14, 4), nullable=False, default=Decimal("0")
    )
    tarifa_hora: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0")
    )
    tarifa_dia: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0")
    )
    recargo_minimo: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    porcentaje_utilidad: Mapped[Decimal] = mapped_column(
        Numeric(8, 4), nullable=False, default=Decimal("0.20")
    )
    porcentaje_riesgo: Mapped[Decimal] = mapped_column(
        Numeric(8, 4), nullable=False, default=Decimal("0")
    )
    porcentaje_urgencia: Mapped[Decimal] = mapped_column(
        Numeric(8, 4), nullable=False, default=Decimal("0")
    )
    porcentaje_retorno_vacio: Mapped[Decimal] = mapped_column(
        Numeric(8, 4), nullable=False, default=Decimal("0")
    )
    porcentaje_carga_especial: Mapped[Decimal] = mapped_column(
        Numeric(8, 4), nullable=False, default=Decimal("0")
    )
    moneda: Mapped[str] = mapped_column(String(3), nullable=False, default="MXN")
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    vigencia_inicio: Mapped[date | None] = mapped_column(Date, nullable=True)
    vigencia_fin: Mapped[date | None] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
