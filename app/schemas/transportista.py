from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.transportista import (
    EstatusDocumentoTransportista,
    EstatusTransportista,
    NivelConfianzaTransportista,
    TipoDocumentoTransportista,
    TipoPersonaTransportista,
    TipoTransportista,
)


class TransportistaContactoBase(BaseModel):
    nombre: str = Field(..., max_length=255)
    area: str | None = Field(None, max_length=120)
    puesto: str | None = Field(None, max_length=120)
    telefono: str | None = Field(None, max_length=40)
    extension: str | None = Field(None, max_length=20)
    celular: str | None = Field(None, max_length=40)
    email: str | None = Field(None, max_length=255)
    principal: bool = False
    activo: bool = True


class TransportistaContactoCreate(TransportistaContactoBase):
    pass


class TransportistaContactoUpdate(BaseModel):
    nombre: str | None = Field(None, max_length=255)
    area: str | None = Field(None, max_length=120)
    puesto: str | None = Field(None, max_length=120)
    telefono: str | None = Field(None, max_length=40)
    extension: str | None = Field(None, max_length=20)
    celular: str | None = Field(None, max_length=40)
    email: str | None = Field(None, max_length=255)
    principal: bool | None = None
    activo: bool | None = None


class TransportistaContactoRead(TransportistaContactoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    transportista_id: int
    created_at: datetime
    updated_at: datetime


class TransportistaContactoListResponse(BaseModel):
    items: list[TransportistaContactoRead]
    total: int


class TransportistaDocumentoBase(BaseModel):
    tipo_documento: TipoDocumentoTransportista
    numero_documento: str | None = Field(None, max_length=120)
    fecha_emision: date | None = None
    fecha_vencimiento: date | None = None
    archivo_url: str | None = Field(None, max_length=1024)
    estatus: EstatusDocumentoTransportista = EstatusDocumentoTransportista.PENDIENTE
    observaciones: str | None = None


class TransportistaDocumentoCreate(TransportistaDocumentoBase):
    pass


class TransportistaDocumentoUpdate(BaseModel):
    tipo_documento: TipoDocumentoTransportista | None = None
    numero_documento: str | None = Field(None, max_length=120)
    fecha_emision: date | None = None
    fecha_vencimiento: date | None = None
    archivo_url: str | None = Field(None, max_length=1024)
    estatus: EstatusDocumentoTransportista | None = None
    observaciones: str | None = None


class TransportistaDocumentoRead(TransportistaDocumentoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    transportista_id: int
    created_at: datetime
    updated_at: datetime


class TransportistaDocumentoListResponse(BaseModel):
    items: list[TransportistaDocumentoRead]
    total: int


class TransportistaBase(BaseModel):
    nombre: str | None = Field(None, max_length=255)
    nombre_razon_social: str | None = Field(None, max_length=255)
    tipo_transportista: TipoTransportista = TipoTransportista.SUBCONTRATADO
    tipo_persona: TipoPersonaTransportista = TipoPersonaTransportista.MORAL
    nombre_comercial: str | None = Field(None, max_length=255)
    rfc: str | None = Field(None, max_length=20)
    curp: str | None = Field(None, max_length=18)
    regimen_fiscal: str | None = Field(None, max_length=64)
    fecha_alta: date | None = None
    estatus: EstatusTransportista = EstatusTransportista.ACTIVO
    contacto: str | None = Field(None, max_length=255)
    telefono: str | None = Field(None, max_length=40)
    telefono_general: str | None = Field(None, max_length=40)
    email: str | None = Field(None, max_length=255)
    email_general: str | None = Field(None, max_length=255)
    sitio_web: str | None = Field(None, max_length=255)
    direccion_fiscal: str | None = None
    direccion_operativa: str | None = None
    ciudad: str | None = Field(None, max_length=120)
    estado: str | None = Field(None, max_length=120)
    pais: str | None = Field(None, max_length=120)
    codigo_postal: str | None = Field(None, max_length=12)
    nivel_confianza: NivelConfianzaTransportista = NivelConfianzaTransportista.MEDIO
    blacklist: bool = False
    prioridad_asignacion: int = Field(default=0, ge=0)
    notas: str | None = None
    notas_operativas: str | None = None
    notas_comerciales: str | None = None
    activo: bool = True

    @model_validator(mode="after")
    def sync_legacy_fields(self) -> "TransportistaBase":
        if self.nombre is None and self.nombre_razon_social is not None:
            self.nombre = self.nombre_razon_social
        if self.nombre_razon_social is None and self.nombre is not None:
            self.nombre_razon_social = self.nombre
        if self.telefono_general is None and self.telefono is not None:
            self.telefono_general = self.telefono
        if self.telefono is None and self.telefono_general is not None:
            self.telefono = self.telefono_general
        if self.email_general is None and self.email is not None:
            self.email_general = self.email
        if self.email is None and self.email_general is not None:
            self.email = self.email_general
        return self


class TransportistaCreate(TransportistaBase):
    @model_validator(mode="after")
    def require_name(self) -> "TransportistaCreate":
        if not self.nombre:
            raise ValueError("Debes enviar nombre o nombre_razon_social.")
        return self


class TransportistaUpdate(BaseModel):
    nombre: str | None = Field(None, max_length=255)
    nombre_razon_social: str | None = Field(None, max_length=255)
    tipo_transportista: TipoTransportista | None = None
    tipo_persona: TipoPersonaTransportista | None = None
    nombre_comercial: str | None = Field(None, max_length=255)
    rfc: str | None = Field(None, max_length=20)
    curp: str | None = Field(None, max_length=18)
    regimen_fiscal: str | None = Field(None, max_length=64)
    fecha_alta: date | None = None
    estatus: EstatusTransportista | None = None
    contacto: str | None = Field(None, max_length=255)
    telefono: str | None = Field(None, max_length=40)
    telefono_general: str | None = Field(None, max_length=40)
    email: str | None = Field(None, max_length=255)
    email_general: str | None = Field(None, max_length=255)
    sitio_web: str | None = Field(None, max_length=255)
    direccion_fiscal: str | None = None
    direccion_operativa: str | None = None
    ciudad: str | None = Field(None, max_length=120)
    estado: str | None = Field(None, max_length=120)
    pais: str | None = Field(None, max_length=120)
    codigo_postal: str | None = Field(None, max_length=12)
    nivel_confianza: NivelConfianzaTransportista | None = None
    blacklist: bool | None = None
    prioridad_asignacion: int | None = Field(None, ge=0)
    notas: str | None = None
    notas_operativas: str | None = None
    notas_comerciales: str | None = None
    activo: bool | None = None

    @model_validator(mode="after")
    def sync_legacy_fields(self) -> "TransportistaUpdate":
        if self.nombre is None and self.nombre_razon_social is not None:
            self.nombre = self.nombre_razon_social
        if self.nombre_razon_social is None and self.nombre is not None:
            self.nombre_razon_social = self.nombre
        if self.telefono_general is None and self.telefono is not None:
            self.telefono_general = self.telefono
        if self.telefono is None and self.telefono_general is not None:
            self.telefono = self.telefono_general
        if self.email_general is None and self.email is not None:
            self.email_general = self.email
        if self.email is None and self.email_general is not None:
            self.email = self.email_general
        return self


class TransportistaRead(TransportistaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    contactos: list[TransportistaContactoRead] = []
    documentos: list[TransportistaDocumentoRead] = []


class TransportistaListResponse(BaseModel):
    items: list[TransportistaRead]
    total: int
    skip: int
    limit: int
