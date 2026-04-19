from __future__ import annotations

import enum
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class TipoTransportista(str, enum.Enum):
    PROPIO = "propio"
    SUBCONTRATADO = "subcontratado"
    FLETERO = "fletero"
    ALIADO = "aliado"


class TipoPersonaTransportista(str, enum.Enum):
    FISICA = "fisica"
    MORAL = "moral"


class EstatusTransportista(str, enum.Enum):
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    BLOQUEADO = "bloqueado"


class NivelConfianzaTransportista(str, enum.Enum):
    ALTO = "alto"
    MEDIO = "medio"
    BAJO = "bajo"


class TipoDocumentoTransportista(str, enum.Enum):
    PERMISO_SCT = "permiso_sct"
    CONSTANCIA_FISCAL = "constancia_fiscal"
    SEGURO_RC = "seguro_rc"
    POLIZA_CARGA = "poliza_carga"
    TARJETA_CIRCULACION = "tarjeta_circulacion"
    LICENCIA_OPERADOR = "licencia_operador"
    INE = "ine"
    COMPROBANTE_DOMICILIO = "comprobante_domicilio"
    CONTRATO = "contrato"
    OTRO = "otro"


class EstatusDocumentoTransportista(str, enum.Enum):
    VIGENTE = "vigente"
    VENCIDO = "vencido"
    PENDIENTE = "pendiente"


def _enum_str(cls: type[enum.Enum], length: int) -> Enum:
    return Enum(
        cls,
        values_callable=lambda x: [e.value for e in x],
        native_enum=False,
        length=length,
    )


class Transportista(Base):
    __tablename__ = "transportistas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo_transportista: Mapped[TipoTransportista] = mapped_column(
        _enum_str(TipoTransportista, 32),
        default=TipoTransportista.SUBCONTRATADO,
        nullable=False,
    )
    tipo_persona: Mapped[TipoPersonaTransportista] = mapped_column(
        _enum_str(TipoPersonaTransportista, 16),
        default=TipoPersonaTransportista.MORAL,
        nullable=False,
    )
    nombre_comercial: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rfc: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    curp: Mapped[str | None] = mapped_column(String(18), nullable=True, index=True)
    regimen_fiscal: Mapped[str | None] = mapped_column(String(64), nullable=True)
    fecha_alta: Mapped[date | None] = mapped_column(Date, nullable=True)
    estatus: Mapped[EstatusTransportista] = mapped_column(
        _enum_str(EstatusTransportista, 16),
        default=EstatusTransportista.ACTIVO,
        nullable=False,
    )
    contacto: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telefono: Mapped[str | None] = mapped_column(String(40), nullable=True)
    telefono_general: Mapped[str | None] = mapped_column(String(40), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email_general: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sitio_web: Mapped[str | None] = mapped_column(String(255), nullable=True)
    direccion_fiscal: Mapped[str | None] = mapped_column(Text, nullable=True)
    direccion_operativa: Mapped[str | None] = mapped_column(Text, nullable=True)
    ciudad: Mapped[str | None] = mapped_column(String(120), nullable=True)
    estado: Mapped[str | None] = mapped_column(String(120), nullable=True)
    pais: Mapped[str | None] = mapped_column(String(120), nullable=True)
    codigo_postal: Mapped[str | None] = mapped_column(String(12), nullable=True)
    nivel_confianza: Mapped[NivelConfianzaTransportista] = mapped_column(
        _enum_str(NivelConfianzaTransportista, 16),
        default=NivelConfianzaTransportista.MEDIO,
        nullable=False,
    )
    blacklist: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    prioridad_asignacion: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    notas: Mapped[str | None] = mapped_column(Text, nullable=True)
    notas_operativas: Mapped[str | None] = mapped_column(Text, nullable=True)
    notas_comerciales: Mapped[str | None] = mapped_column(Text, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    contactos: Mapped[list["TransportistaContacto"]] = relationship(
        "TransportistaContacto",
        lazy="selectin",
        back_populates="transportista",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="TransportistaContacto.principal.desc(), TransportistaContacto.nombre.asc(), TransportistaContacto.id.asc()",
    )
    documentos: Mapped[list["TransportistaDocumento"]] = relationship(
        "TransportistaDocumento",
        lazy="selectin",
        back_populates="transportista",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="TransportistaDocumento.fecha_vencimiento.asc(), TransportistaDocumento.id.asc()",
    )
    tarifas_compra: Mapped[list["TarifaCompraTransportista"]] = relationship(
        "TarifaCompraTransportista",
        lazy="selectin",
        back_populates="transportista",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="TarifaCompraTransportista.nombre_tarifa.asc(), TarifaCompraTransportista.id.asc()",
    )


class TransportistaContacto(Base):
    __tablename__ = "transportista_contactos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    transportista_id: Mapped[int] = mapped_column(
        ForeignKey("transportistas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    area: Mapped[str | None] = mapped_column(String(120), nullable=True)
    puesto: Mapped[str | None] = mapped_column(String(120), nullable=True)
    telefono: Mapped[str | None] = mapped_column(String(40), nullable=True)
    extension: Mapped[str | None] = mapped_column(String(20), nullable=True)
    celular: Mapped[str | None] = mapped_column(String(40), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    principal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

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
        back_populates="contactos",
    )


class TransportistaDocumento(Base):
    __tablename__ = "transportista_documentos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    transportista_id: Mapped[int] = mapped_column(
        ForeignKey("transportistas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tipo_documento: Mapped[TipoDocumentoTransportista] = mapped_column(
        _enum_str(TipoDocumentoTransportista, 32),
        nullable=False,
    )
    numero_documento: Mapped[str | None] = mapped_column(String(120), nullable=True)
    fecha_emision: Mapped[date | None] = mapped_column(Date, nullable=True)
    fecha_vencimiento: Mapped[date | None] = mapped_column(Date, nullable=True)
    archivo_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    estatus: Mapped[EstatusDocumentoTransportista] = mapped_column(
        _enum_str(EstatusDocumentoTransportista, 16),
        default=EstatusDocumentoTransportista.PENDIENTE,
        nullable=False,
    )
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
        back_populates="documentos",
    )
