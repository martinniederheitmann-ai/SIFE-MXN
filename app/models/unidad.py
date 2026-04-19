from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Unidad(Base):
    """Unidad (vehículo) mínima para asignaciones operador–viaje."""

    __tablename__ = "unidades"

    id_unidad: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    transportista_id: Mapped[int | None] = mapped_column(
        ForeignKey("transportistas.id", ondelete="SET NULL"), nullable=True, index=True
    )
    economico: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    placas: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    tipo_propiedad: Mapped[str | None] = mapped_column(String(32), nullable=True)
    estatus_documental: Mapped[str | None] = mapped_column(String(32), nullable=True)
    descripcion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    detalle: Mapped[str | None] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    vigencia_seguro: Mapped[date | None] = mapped_column(Date, nullable=True)
    vigencia_permiso_sct: Mapped[date | None] = mapped_column(Date, nullable=True)
    vigencia_tarjeta_circulacion: Mapped[date | None] = mapped_column(Date, nullable=True)
    vigencia_verificacion_fisico_mecanica: Mapped[date | None] = mapped_column(
        Date, nullable=True
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
