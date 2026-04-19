from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.tarifa_flete import AmbitoTarifaFlete
from app.models.transportista import TipoTransportista


class EstadoFlete(str, enum.Enum):
    COTIZADO = "cotizado"
    CONFIRMADO = "confirmado"
    ASIGNADO = "asignado"
    EN_TRANSITO = "en_transito"
    ENTREGADO = "entregado"
    CANCELADO = "cancelado"


class MetodoCalculoFlete(str, enum.Enum):
    MANUAL = "manual"
    TARIFA = "tarifa"
    MOTOR = "motor"


def _enum_str(cls: type[enum.Enum], length: int) -> Enum:
    return Enum(
        cls,
        values_callable=lambda x: [e.value for e in x],
        native_enum=False,
        length=length,
    )


class Flete(Base):
    __tablename__ = "fletes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo_flete: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("clientes.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    transportista_id: Mapped[int] = mapped_column(
        ForeignKey("transportistas.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    viaje_id: Mapped[int | None] = mapped_column(
        ForeignKey("viajes.id", ondelete="SET NULL"), nullable=True, index=True
    )

    descripcion_carga: Mapped[str | None] = mapped_column(String(500), nullable=True)
    peso_kg: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    volumen_m3: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)
    numero_bultos: Mapped[int | None] = mapped_column(nullable=True)
    distancia_km: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    tipo_operacion: Mapped[TipoTransportista] = mapped_column(
        _enum_str(TipoTransportista, 32),
        default=TipoTransportista.SUBCONTRATADO,
        nullable=False,
    )
    tipo_unidad: Mapped[str | None] = mapped_column(String(64), nullable=True)
    tipo_carga: Mapped[str | None] = mapped_column(String(64), nullable=True)

    monto_estimado: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    precio_venta: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    costo_transporte_estimado: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    costo_transporte_real: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    margen_estimado: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    margen_real: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    metodo_calculo: Mapped[MetodoCalculoFlete] = mapped_column(
        _enum_str(MetodoCalculoFlete, 24),
        default=MetodoCalculoFlete.MANUAL,
        nullable=False,
    )
    moneda: Mapped[str] = mapped_column(String(3), default="MXN", nullable=False)

    estado: Mapped[EstadoFlete] = mapped_column(
        _enum_str(EstadoFlete, 32),
        default=EstadoFlete.COTIZADO,
        nullable=False,
    )
    ambito_operacion: Mapped[AmbitoTarifaFlete | None] = mapped_column(
        _enum_str(AmbitoTarifaFlete, 16),
        nullable=True,
        comment="Ámbito para reglas de cumplimiento (local, estatal, federal)",
    )
    carta_porte_uuid: Mapped[str | None] = mapped_column(String(64), nullable=True)
    carta_porte_folio: Mapped[str | None] = mapped_column(String(64), nullable=True)
    factura_mercancia_folio: Mapped[str | None] = mapped_column(String(64), nullable=True)
    mercancia_documentacion_ok: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        comment="Acuse de que la documentación de la mercancía está lista (factura, empaque, etc.)",
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

    cliente: Mapped["Cliente"] = relationship("Cliente", lazy="select")
    transportista: Mapped["Transportista"] = relationship("Transportista", lazy="select")
    viaje: Mapped["Viaje | None"] = relationship("Viaje", lazy="select")
    gastos_viaje: Mapped[list["GastoViaje"]] = relationship(
        "GastoViaje",
        back_populates="flete",
        lazy="selectin",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
