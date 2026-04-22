from __future__ import annotations

import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TipoBajaDano(str, enum.Enum):
    BAJA = "baja"
    DANO = "dano"


class EstatusBajaDano(str, enum.Enum):
    ABIERTA = "abierta"
    EN_SEGUIMIENTO = "en_seguimiento"
    CERRADA = "cerrada"


def _bd_enum(cls: type[enum.Enum], length: int) -> Enum:
    return Enum(
        cls,
        values_callable=lambda x: [e.value for e in x],
        native_enum=False,
        length=length,
    )


class BajaDano(Base):
    __tablename__ = "bajas_danos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tipo: Mapped[TipoBajaDano] = mapped_column(_bd_enum(TipoBajaDano, 16), nullable=False, index=True)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    detalle: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha_evento: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    flete_id: Mapped[int | None] = mapped_column(
        ForeignKey("fletes.id", ondelete="SET NULL"), nullable=True, index=True
    )
    id_unidad: Mapped[int | None] = mapped_column(
        ForeignKey("unidades.id_unidad", ondelete="SET NULL"), nullable=True
    )
    id_operador: Mapped[int | None] = mapped_column(
        ForeignKey("operadores.id_operador", ondelete="SET NULL"), nullable=True
    )
    estatus: Mapped[EstatusBajaDano] = mapped_column(
        _bd_enum(EstatusBajaDano, 24),
        nullable=False,
        default=EstatusBajaDano.ABIERTA,
    )
    costo_estimado: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
