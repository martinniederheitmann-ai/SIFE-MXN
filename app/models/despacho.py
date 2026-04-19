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


class EstadoDespacho(str, enum.Enum):
    PROGRAMADO = "programado"
    DESPACHADO = "despachado"
    EN_TRANSITO = "en_transito"
    ENTREGADO = "entregado"
    CERRADO = "cerrado"
    CANCELADO = "cancelado"


class TipoEventoDespacho(str, enum.Enum):
    SALIDA = "salida"
    CHECKPOINT = "checkpoint"
    INCIDENCIA = "incidencia"
    ENTREGA = "entrega"
    CIERRE = "cierre"
    CANCELACION = "cancelacion"


class Despacho(Base):
    __tablename__ = "despachos"

    id_despacho: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_asignacion: Mapped[int] = mapped_column(
        ForeignKey("asignaciones.id_asignacion", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
        index=True,
    )
    id_flete: Mapped[int | None] = mapped_column(
        ForeignKey("fletes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    estatus: Mapped[EstadoDespacho] = mapped_column(
        _enum_str(EstadoDespacho, 24),
        default=EstadoDespacho.PROGRAMADO,
        nullable=False,
    )
    salida_programada: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    salida_real: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    fecha_entrega: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    llegada_real: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    km_salida: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    km_llegada: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    evidencia_entrega: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    firma_recibe: Mapped[str | None] = mapped_column(String(255), nullable=True)
    observaciones_salida: Mapped[str | None] = mapped_column(Text, nullable=True)
    observaciones_transito: Mapped[str | None] = mapped_column(Text, nullable=True)
    observaciones_entrega: Mapped[str | None] = mapped_column(Text, nullable=True)
    observaciones_cierre: Mapped[str | None] = mapped_column(Text, nullable=True)
    motivo_cancelacion: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    asignacion: Mapped["Asignacion"] = relationship("Asignacion", lazy="select")
    flete: Mapped["Flete | None"] = relationship("Flete", lazy="select")
    eventos: Mapped[list["DespachoEvento"]] = relationship(
        "DespachoEvento",
        back_populates="despacho",
        lazy="selectin",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class DespachoEvento(Base):
    __tablename__ = "despacho_eventos"

    id_evento: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_despacho: Mapped[int] = mapped_column(
        ForeignKey("despachos.id_despacho", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tipo_evento: Mapped[TipoEventoDespacho] = mapped_column(
        _enum_str(TipoEventoDespacho, 24),
        nullable=False,
    )
    fecha_evento: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ubicacion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    latitud: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    longitud: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    despacho: Mapped["Despacho"] = relationship(
        "Despacho",
        lazy="select",
        back_populates="eventos",
    )
