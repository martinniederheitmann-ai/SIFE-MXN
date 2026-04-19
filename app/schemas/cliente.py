from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.cliente import TipoCliente


class ClienteContactoBase(BaseModel):
    nombre: str = Field(..., max_length=255)
    area: str | None = Field(None, max_length=120)
    puesto: str | None = Field(None, max_length=120)
    telefono: str | None = Field(None, max_length=40)
    extension: str | None = Field(None, max_length=20)
    celular: str | None = Field(None, max_length=40)
    email: str | None = Field(None, max_length=255)
    principal: bool = False
    activo: bool = True


class ClienteContactoCreate(ClienteContactoBase):
    pass


class ClienteContactoUpdate(BaseModel):
    nombre: str | None = Field(None, max_length=255)
    area: str | None = Field(None, max_length=120)
    puesto: str | None = Field(None, max_length=120)
    telefono: str | None = Field(None, max_length=40)
    extension: str | None = Field(None, max_length=20)
    celular: str | None = Field(None, max_length=40)
    email: str | None = Field(None, max_length=255)
    principal: bool | None = None
    activo: bool | None = None
    cliente_id: int | None = Field(
        None,
        description="Si se envia y difiere del cliente actual, el contacto pasa a ese cliente.",
    )


class ClienteContactoRead(ClienteContactoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente_id: int
    created_at: datetime
    updated_at: datetime


class ClienteContactoListResponse(BaseModel):
    items: list[ClienteContactoRead]
    total: int


class ClienteDomicilioBase(BaseModel):
    tipo_domicilio: str = Field(..., max_length=64)
    nombre_sede: str = Field(..., max_length=255)
    direccion_completa: str
    municipio: str | None = Field(None, max_length=120)
    estado: str | None = Field(None, max_length=120)
    codigo_postal: str | None = Field(None, max_length=12)
    horario_carga: str | None = Field(None, max_length=120)
    horario_descarga: str | None = Field(None, max_length=120)
    instrucciones_acceso: str | None = None
    activo: bool = True


class ClienteDomicilioCreate(ClienteDomicilioBase):
    pass


class ClienteDomicilioUpdate(BaseModel):
    tipo_domicilio: str | None = Field(None, max_length=64)
    nombre_sede: str | None = Field(None, max_length=255)
    direccion_completa: str | None = None
    municipio: str | None = Field(None, max_length=120)
    estado: str | None = Field(None, max_length=120)
    codigo_postal: str | None = Field(None, max_length=12)
    horario_carga: str | None = Field(None, max_length=120)
    horario_descarga: str | None = Field(None, max_length=120)
    instrucciones_acceso: str | None = None
    activo: bool | None = None


class ClienteDomicilioRead(ClienteDomicilioBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente_id: int
    created_at: datetime
    updated_at: datetime


class ClienteDomicilioListResponse(BaseModel):
    items: list[ClienteDomicilioRead]
    total: int


class ClienteCondicionComercialBase(BaseModel):
    dias_credito: int | None = Field(None, ge=0)
    limite_credito: Decimal | None = Field(None, ge=0)
    moneda_preferida: str = Field(default="MXN", max_length=3)
    forma_pago: str | None = Field(None, max_length=64)
    uso_cfdi: str | None = Field(None, max_length=64)
    requiere_oc: bool = False
    requiere_cita: bool = False
    bloqueado_credito: bool = False
    observaciones_credito: str | None = None


class ClienteCondicionComercialUpsert(ClienteCondicionComercialBase):
    pass


class ClienteCondicionComercialRead(ClienteCondicionComercialBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente_id: int
    created_at: datetime
    updated_at: datetime


class ClienteTarifaEspecialBase(BaseModel):
    tarifa_flete_id: int
    nombre_acuerdo: str = Field(..., max_length=120)
    precio_fijo: Decimal | None = Field(None, ge=0)
    descuento_pct: Decimal = Field(default=Decimal("0"), ge=0)
    incremento_pct: Decimal = Field(default=Decimal("0"), ge=0)
    recargo_fijo: Decimal = Field(default=Decimal("0"), ge=0)
    prioridad: int = Field(default=100, ge=0)
    activo: bool = True
    vigencia_inicio: datetime | None = None
    vigencia_fin: datetime | None = None
    observaciones: str | None = None


class ClienteTarifaEspecialCreate(ClienteTarifaEspecialBase):
    pass


class ClienteTarifaEspecialUpdate(BaseModel):
    tarifa_flete_id: int | None = None
    nombre_acuerdo: str | None = Field(None, max_length=120)
    precio_fijo: Decimal | None = Field(None, ge=0)
    descuento_pct: Decimal | None = Field(None, ge=0)
    incremento_pct: Decimal | None = Field(None, ge=0)
    recargo_fijo: Decimal | None = Field(None, ge=0)
    prioridad: int | None = Field(None, ge=0)
    activo: bool | None = None
    vigencia_inicio: datetime | None = None
    vigencia_fin: datetime | None = None
    observaciones: str | None = None


class ClienteTarifaEspecialRead(ClienteTarifaEspecialBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente_id: int
    created_at: datetime
    updated_at: datetime


class ClienteTarifaEspecialListResponse(BaseModel):
    items: list[ClienteTarifaEspecialRead]
    total: int


class ClienteBase(BaseModel):
    razon_social: str = Field(..., max_length=255)
    nombre_comercial: str | None = Field(None, max_length=255)
    rfc: str | None = Field(None, max_length=20)
    tipo_cliente: TipoCliente = TipoCliente.MIXTO
    sector: str | None = Field(None, max_length=120)
    origen_prospecto: str | None = Field(None, max_length=120)
    email: str | None = Field(None, max_length=255)
    telefono: str | None = Field(None, max_length=40)
    direccion: str | None = None
    domicilio_fiscal: str | None = None
    sitio_web: str | None = Field(None, max_length=255)
    notas_operativas: str | None = None
    notas_comerciales: str | None = None
    activo: bool = True

    @model_validator(mode="after")
    def sync_addresses(self) -> "ClienteBase":
        if self.domicilio_fiscal is None and self.direccion is not None:
            self.domicilio_fiscal = self.direccion
        if self.direccion is None and self.domicilio_fiscal is not None:
            self.direccion = self.domicilio_fiscal
        return self


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    razon_social: str | None = Field(None, max_length=255)
    nombre_comercial: str | None = Field(None, max_length=255)
    rfc: str | None = Field(None, max_length=20)
    tipo_cliente: TipoCliente | None = None
    sector: str | None = Field(None, max_length=120)
    origen_prospecto: str | None = Field(None, max_length=120)
    email: str | None = Field(None, max_length=255)
    telefono: str | None = Field(None, max_length=40)
    direccion: str | None = None
    domicilio_fiscal: str | None = None
    sitio_web: str | None = Field(None, max_length=255)
    notas_operativas: str | None = None
    notas_comerciales: str | None = None
    activo: bool | None = None

    @model_validator(mode="after")
    def sync_addresses(self) -> "ClienteUpdate":
        if self.domicilio_fiscal is None and self.direccion is not None:
            self.domicilio_fiscal = self.direccion
        if self.direccion is None and self.domicilio_fiscal is not None:
            self.direccion = self.domicilio_fiscal
        return self


class ClienteRead(ClienteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    contactos: list[ClienteContactoRead] = []
    domicilios: list[ClienteDomicilioRead] = []
    condicion_comercial: ClienteCondicionComercialRead | None = None
    tarifas_especiales: list[ClienteTarifaEspecialRead] = []


class ClienteListResponse(BaseModel):
    items: list[ClienteRead]
    total: int
    skip: int
    limit: int
