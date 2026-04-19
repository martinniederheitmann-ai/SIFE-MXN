from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class TipoCliente(str, enum.Enum):
    EMBARCADOR = "embarcador"
    CONSIGNATARIO = "consignatario"
    PAGADOR = "pagador"
    CORPORATIVO = "corporativo"
    MIXTO = "mixto"


def _enum_str(cls: type[enum.Enum], length: int) -> Enum:
    return Enum(
        cls,
        values_callable=lambda x: [e.value for e in x],
        native_enum=False,
        length=length,
    )


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    razon_social: Mapped[str] = mapped_column(String(255), nullable=False)
    nombre_comercial: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rfc: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    tipo_cliente: Mapped[TipoCliente] = mapped_column(
        _enum_str(TipoCliente, 32),
        default=TipoCliente.MIXTO,
        nullable=False,
    )
    sector: Mapped[str | None] = mapped_column(String(120), nullable=True)
    origen_prospecto: Mapped[str | None] = mapped_column(String(120), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telefono: Mapped[str | None] = mapped_column(String(40), nullable=True)
    direccion: Mapped[str | None] = mapped_column(Text, nullable=True)
    domicilio_fiscal: Mapped[str | None] = mapped_column(Text, nullable=True)
    sitio_web: Mapped[str | None] = mapped_column(String(255), nullable=True)
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

    contactos: Mapped[list["ClienteContacto"]] = relationship(
        "ClienteContacto",
        lazy="selectin",
        back_populates="cliente",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="ClienteContacto.principal.desc(), ClienteContacto.nombre.asc(), ClienteContacto.id.asc()",
    )
    domicilios: Mapped[list["ClienteDomicilio"]] = relationship(
        "ClienteDomicilio",
        lazy="selectin",
        back_populates="cliente",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="ClienteDomicilio.nombre_sede.asc(), ClienteDomicilio.id.asc()",
    )
    condicion_comercial: Mapped["ClienteCondicionComercial | None"] = relationship(
        "ClienteCondicionComercial",
        lazy="selectin",
        back_populates="cliente",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )
    tarifas_especiales: Mapped[list["ClienteTarifaEspecial"]] = relationship(
        "ClienteTarifaEspecial",
        lazy="selectin",
        back_populates="cliente",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="ClienteTarifaEspecial.prioridad.asc(), ClienteTarifaEspecial.id.asc()",
    )


class ClienteContacto(Base):
    __tablename__ = "cliente_contactos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("clientes.id", ondelete="CASCADE"), nullable=False, index=True
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

    cliente: Mapped["Cliente"] = relationship("Cliente", lazy="select", back_populates="contactos")


class ClienteDomicilio(Base):
    __tablename__ = "cliente_domicilios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("clientes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tipo_domicilio: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    nombre_sede: Mapped[str] = mapped_column(String(255), nullable=False)
    direccion_completa: Mapped[str] = mapped_column(Text, nullable=False)
    municipio: Mapped[str | None] = mapped_column(String(120), nullable=True)
    estado: Mapped[str | None] = mapped_column(String(120), nullable=True)
    codigo_postal: Mapped[str | None] = mapped_column(String(12), nullable=True)
    horario_carga: Mapped[str | None] = mapped_column(String(120), nullable=True)
    horario_descarga: Mapped[str | None] = mapped_column(String(120), nullable=True)
    instrucciones_acceso: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    cliente: Mapped["Cliente"] = relationship("Cliente", lazy="select", back_populates="domicilios")


class ClienteCondicionComercial(Base):
    __tablename__ = "cliente_condiciones_comerciales"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("clientes.id", ondelete="CASCADE"), nullable=False, index=True, unique=True
    )
    dias_credito: Mapped[int | None] = mapped_column(Integer, nullable=True)
    limite_credito: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    moneda_preferida: Mapped[str] = mapped_column(String(3), default="MXN", nullable=False)
    forma_pago: Mapped[str | None] = mapped_column(String(64), nullable=True)
    uso_cfdi: Mapped[str | None] = mapped_column(String(64), nullable=True)
    requiere_oc: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requiere_cita: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    bloqueado_credito: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    observaciones_credito: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    cliente: Mapped["Cliente"] = relationship(
        "Cliente",
        lazy="select",
        back_populates="condicion_comercial",
    )


class ClienteTarifaEspecial(Base):
    __tablename__ = "cliente_tarifas_especiales"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("clientes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tarifa_flete_id: Mapped[int] = mapped_column(
        ForeignKey("tarifas_flete.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nombre_acuerdo: Mapped[str] = mapped_column(String(120), nullable=False)
    precio_fijo: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    descuento_pct: Mapped[Decimal] = mapped_column(
        Numeric(8, 4), default=Decimal("0"), nullable=False
    )
    incremento_pct: Mapped[Decimal] = mapped_column(
        Numeric(8, 4), default=Decimal("0"), nullable=False
    )
    recargo_fijo: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=Decimal("0"), nullable=False
    )
    prioridad: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    vigencia_inicio: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    vigencia_fin: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
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

    cliente: Mapped["Cliente"] = relationship(
        "Cliente",
        lazy="select",
        back_populates="tarifas_especiales",
    )
    tarifa_flete: Mapped["TarifaFlete"] = relationship("TarifaFlete", lazy="select")
