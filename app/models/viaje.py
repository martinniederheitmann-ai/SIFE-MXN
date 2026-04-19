import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class EstadoViaje(str, enum.Enum):
    PLANIFICADO = "planificado"
    EN_RUTA = "en_ruta"
    COMPLETADO = "completado"
    CANCELADO = "cancelado"


class Viaje(Base):
    __tablename__ = "viajes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo_viaje: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    descripcion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    origen: Mapped[str] = mapped_column(String(255), nullable=False)
    destino: Mapped[str] = mapped_column(String(255), nullable=False)
    fecha_salida: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fecha_llegada_estimada: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    fecha_llegada_real: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    estado: Mapped[EstadoViaje] = mapped_column(
        Enum(
            EstadoViaje,
            values_callable=lambda x: [e.value for e in x],
            native_enum=False,
            length=32,
        ),
        default=EstadoViaje.PLANIFICADO,
        nullable=False,
    )
    kilometros_estimados: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
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
