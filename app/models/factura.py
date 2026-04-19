from __future__ import annotations

import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


def _enum_str(cls: type[enum.Enum], length: int) -> Enum:
    return Enum(
        cls,
        values_callable=lambda x: [e.value for e in x],
        native_enum=False,
        length=length,
    )


class EstatusFactura(str, enum.Enum):
    BORRADOR = "borrador"
    EMITIDA = "emitida"
    ENVIADA = "enviada"
    PARCIAL = "parcial"
    COBRADA = "cobrada"
    CANCELADA = "cancelada"


class Factura(Base):
    __tablename__ = "facturas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    folio: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    serie: Mapped[str | None] = mapped_column(String(12), nullable=True)
    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("clientes.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    flete_id: Mapped[int | None] = mapped_column(
        ForeignKey("fletes.id", ondelete="SET NULL"), nullable=True, index=True
    )
    orden_servicio_id: Mapped[int | None] = mapped_column(
        ForeignKey("ordenes_servicio.id", ondelete="SET NULL"), nullable=True, index=True
    )
    fecha_emision: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    fecha_vencimiento: Mapped[date | None] = mapped_column(Date, nullable=True)
    concepto: Mapped[str] = mapped_column(String(255), nullable=False)
    referencia: Mapped[str | None] = mapped_column(String(120), nullable=True)
    moneda: Mapped[str] = mapped_column(String(3), nullable=False, default="MXN")
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    iva_pct: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False, default=Decimal("0.16"))
    iva_monto: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    retencion_monto: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    saldo_pendiente: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    forma_pago: Mapped[str | None] = mapped_column(String(64), nullable=True)
    metodo_pago: Mapped[str | None] = mapped_column(String(16), nullable=True)
    uso_cfdi: Mapped[str | None] = mapped_column(String(16), nullable=True)
    estatus: Mapped[EstatusFactura] = mapped_column(
        _enum_str(EstatusFactura, 16),
        nullable=False,
        default=EstatusFactura.BORRADOR,
    )
    timbrada: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
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
    flete: Mapped["Flete | None"] = relationship("Flete", lazy="select")
    orden_servicio: Mapped["OrdenServicio | None"] = relationship("OrdenServicio", lazy="select")
