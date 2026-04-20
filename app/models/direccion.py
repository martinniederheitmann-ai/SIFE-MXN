from __future__ import annotations

import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


def _enum_str(cls: type[enum.Enum], length: int) -> Enum:
    return Enum(
        cls,
        values_callable=lambda x: [e.value for e in x],
        native_enum=False,
        length=length,
    )


class IncidenciaSeveridad(str, enum.Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class IncidenciaEstatus(str, enum.Enum):
    ABIERTA = "abierta"
    EN_PROGRESO = "en_progreso"
    RESUELTA = "resuelta"


class AccionEstatus(str, enum.Enum):
    PENDIENTE = "pendiente"
    EN_CURSO = "en_curso"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"


class DireccionIncidencia(Base):
    __tablename__ = "direccion_incidencias"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    titulo: Mapped[str] = mapped_column(String(160), nullable=False)
    modulo: Mapped[str] = mapped_column(String(64), nullable=False, default="general")
    severidad: Mapped[IncidenciaSeveridad] = mapped_column(
        _enum_str(IncidenciaSeveridad, 16),
        nullable=False,
        default=IncidenciaSeveridad.MEDIA,
    )
    estatus: Mapped[IncidenciaEstatus] = mapped_column(
        _enum_str(IncidenciaEstatus, 16),
        nullable=False,
        default=IncidenciaEstatus.ABIERTA,
    )
    fecha_detectada: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    detalle: Mapped[str | None] = mapped_column(Text, nullable=True)
    responsable: Mapped[str | None] = mapped_column(String(120), nullable=True)
    resuelta_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class DireccionAccion(Base):
    __tablename__ = "direccion_acciones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    week_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    week_end: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    titulo: Mapped[str] = mapped_column(String(180), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner: Mapped[str] = mapped_column(String(120), nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    impacto: Mapped[str | None] = mapped_column(String(255), nullable=True)
    estatus: Mapped[AccionEstatus] = mapped_column(
        _enum_str(AccionEstatus, 16),
        nullable=False,
        default=AccionEstatus.PENDIENTE,
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
