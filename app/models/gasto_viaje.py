from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class GastoViaje(Base):
    __tablename__ = "gastos_viaje"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    flete_id: Mapped[int] = mapped_column(
        ForeignKey("fletes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tipo_gasto: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    monto: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    fecha_gasto: Mapped[date] = mapped_column(Date, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    referencia: Mapped[str | None] = mapped_column(String(120), nullable=True)
    comprobante: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    flete: Mapped["Flete"] = relationship(
        "Flete",
        lazy="select",
        back_populates="gastos_viaje",
    )
