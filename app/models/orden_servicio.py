from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


def _enum_str(cls: type[enum.Enum], length: int) -> Enum:
    return Enum(
        cls,
        values_callable=lambda x: [e.value for e in x],
        native_enum=False,
        length=length,
    )


class EstatusOrdenServicio(str, enum.Enum):
    BORRADOR = "borrador"
    CONFIRMADA = "confirmada"
    PROGRAMADA = "programada"
    EN_EJECUCION = "en_ejecucion"
    CERRADA = "cerrada"
    CANCELADA = "cancelada"


class OrdenServicio(Base):
    __tablename__ = "ordenes_servicio"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    folio: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("clientes.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    cotizacion_id: Mapped[int | None] = mapped_column(
        ForeignKey("cotizaciones_flete.id", ondelete="SET NULL"), nullable=True, index=True
    )
    flete_id: Mapped[int | None] = mapped_column(
        ForeignKey("fletes.id", ondelete="SET NULL"), nullable=True, index=True
    )
    viaje_id: Mapped[int | None] = mapped_column(
        ForeignKey("viajes.id", ondelete="SET NULL"), nullable=True, index=True
    )
    despacho_id: Mapped[int | None] = mapped_column(
        ForeignKey("despachos.id_despacho", ondelete="SET NULL"), nullable=True, index=True
    )

    origen: Mapped[str] = mapped_column(String(255), nullable=False)
    destino: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo_unidad: Mapped[str] = mapped_column(String(64), nullable=False)
    tipo_carga: Mapped[str | None] = mapped_column(String(64), nullable=True)
    peso_kg: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    distancia_km: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    precio_comprometido: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    moneda: Mapped[str] = mapped_column(String(3), nullable=False, default="MXN")
    fecha_solicitud: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    fecha_programada: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    estatus: Mapped[EstatusOrdenServicio] = mapped_column(
        _enum_str(EstatusOrdenServicio, 24),
        default=EstatusOrdenServicio.BORRADOR,
        nullable=False,
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

    cliente: Mapped["Cliente"] = relationship("Cliente", lazy="select")
    cotizacion: Mapped["CotizacionFlete | None"] = relationship("CotizacionFlete", lazy="select")
    flete: Mapped["Flete | None"] = relationship("Flete", lazy="select")
    viaje: Mapped["Viaje | None"] = relationship("Viaje", lazy="select")
    despacho: Mapped["Despacho | None"] = relationship("Despacho", lazy="select")
