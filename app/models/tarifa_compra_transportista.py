from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.tarifa_flete import AmbitoTarifaFlete, ModalidadCobroTarifa, _enum_str
from app.models.transportista import TipoTransportista


class TarifaCompraTransportista(Base):
    __tablename__ = "tarifas_compra_transportista"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    transportista_id: Mapped[int] = mapped_column(
        ForeignKey("transportistas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tipo_transportista: Mapped[TipoTransportista] = mapped_column(
        _enum_str(TipoTransportista, 32),
        nullable=False,
        default=TipoTransportista.SUBCONTRATADO,
    )
    nombre_tarifa: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
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
    dias_credito: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    moneda: Mapped[str] = mapped_column(String(3), nullable=False, default="MXN")
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    vigencia_inicio: Mapped[date | None] = mapped_column(Date, nullable=True)
    vigencia_fin: Mapped[date | None] = mapped_column(Date, nullable=True)
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

    transportista: Mapped["Transportista"] = relationship(
        "Transportista",
        lazy="select",
        back_populates="tarifas_compra",
    )
