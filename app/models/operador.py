from __future__ import annotations

import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import JSON, Boolean, Date, DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class EstadoCivil(str, enum.Enum):
    SOLTERO = "soltero"
    CASADO = "casado"
    DIVORCIADO = "divorciado"
    VIUDO = "viudo"
    UNION_LIBRE = "union_libre"


class TipoSangre(str, enum.Enum):
    AP = "A+"
    AN = "A-"
    BP = "B+"
    BN = "B-"
    ABP = "AB+"
    ABN = "AB-"
    OP = "O+"
    ON = "O-"


def _enum_str(cls: type[enum.Enum], length: int) -> Enum:
    return Enum(
        cls,
        values_callable=lambda x: [e.value for e in x],
        native_enum=False,
        length=length,
    )


class Operador(Base):
    __tablename__ = "operadores"

    id_operador: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    transportista_id: Mapped[int | None] = mapped_column(
        ForeignKey("transportistas.id", ondelete="SET NULL"), nullable=True, index=True
    )
    tipo_contratacion: Mapped[str | None] = mapped_column(String(32), nullable=True)
    licencia: Mapped[str | None] = mapped_column(String(64), nullable=True)
    tipo_licencia: Mapped[str | None] = mapped_column(String(32), nullable=True)
    vigencia_licencia: Mapped[date | None] = mapped_column(Date, nullable=True)
    estatus_documental: Mapped[str | None] = mapped_column(String(32), nullable=True)

    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido_paterno: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido_materno: Mapped[str | None] = mapped_column(String(100), nullable=True)
    fecha_nacimiento: Mapped[date] = mapped_column(Date, nullable=False)
    curp: Mapped[str] = mapped_column(String(18), unique=True, index=True, nullable=False)
    rfc: Mapped[str] = mapped_column(String(13), index=True, nullable=False)
    nss: Mapped[str] = mapped_column(String(11), unique=True, index=True, nullable=False)
    estado_civil: Mapped[EstadoCivil] = mapped_column(
        _enum_str(EstadoCivil, 32), nullable=False
    )
    tipo_sangre: Mapped[TipoSangre] = mapped_column(_enum_str(TipoSangre, 8), nullable=False)
    fotografia: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    telefono_principal: Mapped[str] = mapped_column(String(20), nullable=False)
    telefono_emergencia: Mapped[str | None] = mapped_column(String(20), nullable=True)
    nombre_contacto_emergencia: Mapped[str | None] = mapped_column(String(255), nullable=True)
    direccion: Mapped[str] = mapped_column(String(255), nullable=False)
    colonia: Mapped[str] = mapped_column(String(120), nullable=False)
    municipio: Mapped[str] = mapped_column(String(120), nullable=False)
    estado_geografico: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="Entidad federativa (campo 'estado' del domicilio)"
    )
    codigo_postal: Mapped[str] = mapped_column(String(5), nullable=False)
    correo_electronico: Mapped[str] = mapped_column(String(255), nullable=False)

    anios_experiencia: Mapped[int | None] = mapped_column(nullable=True)
    tipos_unidad_manejadas: Mapped[list | None] = mapped_column(JSON, nullable=True)
    rutas_conocidas: Mapped[str | None] = mapped_column(Text, nullable=True)
    tipos_carga_experiencia: Mapped[list | None] = mapped_column(JSON, nullable=True)
    certificaciones: Mapped[str | None] = mapped_column(Text, nullable=True)

    ultima_revision_medica: Mapped[date | None] = mapped_column(Date, nullable=True)
    resultado_apto: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    restricciones_medicas: Mapped[str | None] = mapped_column(Text, nullable=True)
    proxima_revision_medica: Mapped[date | None] = mapped_column(Date, nullable=True)

    puntualidad: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    consumo_diesel_promedio: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True, comment="Consumo promedio con unidades diesel (km/L u otra unidad acordada)."
    )
    consumo_gasolina_promedio: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True, comment="Consumo promedio con unidades de gasolina (km/L u otra unidad acordada)."
    )
    incidencias_desempeno: Mapped[str | None] = mapped_column(Text, nullable=True)
    calificacion_general: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    comentarios_desempeno: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
