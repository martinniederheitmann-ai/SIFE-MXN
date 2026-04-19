from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.tarifa_flete import AmbitoTarifaFlete, ModalidadCobroTarifa


def _enum_str(cls: type[enum.Enum], length: int) -> Enum:
    return Enum(
        cls,
        values_callable=lambda x: [e.value for e in x],
        native_enum=False,
        length=length,
    )


class EstatusCotizacionFlete(str, enum.Enum):
    BORRADOR = "borrador"
    ENVIADA = "enviada"
    ACEPTADA = "aceptada"
    RECHAZADA = "rechazada"
    CONVERTIDA = "convertida"


class CotizacionFlete(Base):
    __tablename__ = "cotizaciones_flete"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    folio: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    cliente_id: Mapped[int | None] = mapped_column(
        ForeignKey("clientes.id", ondelete="SET NULL"), nullable=True, index=True
    )
    tarifa_flete_id: Mapped[int] = mapped_column(
        ForeignKey("tarifas_flete.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    tarifa_especial_cliente_id: Mapped[int | None] = mapped_column(
        ForeignKey("cliente_tarifas_especiales.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    flete_id: Mapped[int | None] = mapped_column(
        ForeignKey("fletes.id", ondelete="SET NULL"), nullable=True, index=True
    )

    ambito: Mapped[AmbitoTarifaFlete] = mapped_column(
        _enum_str(AmbitoTarifaFlete, 24), nullable=False
    )
    modalidad_cobro: Mapped[ModalidadCobroTarifa] = mapped_column(
        _enum_str(ModalidadCobroTarifa, 24), nullable=False
    )
    origen: Mapped[str] = mapped_column(String(255), nullable=False)
    destino: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo_unidad: Mapped[str] = mapped_column(String(64), nullable=False)
    tipo_carga: Mapped[str | None] = mapped_column(String(64), nullable=True)
    distancia_km: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    peso_kg: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    horas_servicio: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0"))
    dias_servicio: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0"))
    urgencia: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    retorno_vacio: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    riesgo_pct_extra: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False, default=Decimal("0"))
    recargos: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))

    costo_base_estimado: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    subtotal_estimado: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    utilidad_aplicada: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    riesgo_aplicado: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    urgencia_aplicada: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    retorno_vacio_aplicado: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    carga_especial_aplicada: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    descuento_cliente_aplicado: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    incremento_cliente_aplicado: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    recargo_fijo_cliente_aplicado: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    precio_venta_sugerido: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    moneda: Mapped[str] = mapped_column(String(3), nullable=False, default="MXN")
    detalle_calculo: Mapped[str] = mapped_column(Text, nullable=False)
    estatus: Mapped[EstatusCotizacionFlete] = mapped_column(
        _enum_str(EstatusCotizacionFlete, 24),
        nullable=False,
        default=EstatusCotizacionFlete.BORRADOR,
    )
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    cliente: Mapped["Cliente | None"] = relationship("Cliente", lazy="select")
    tarifa_flete: Mapped["TarifaFlete"] = relationship("TarifaFlete", lazy="select")
    tarifa_especial_cliente: Mapped["ClienteTarifaEspecial | None"] = relationship(
        "ClienteTarifaEspecial", lazy="select"
    )
    flete: Mapped["Flete | None"] = relationship("Flete", lazy="select")
