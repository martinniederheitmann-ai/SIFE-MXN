from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.operador import EstadoCivil, TipoSangre


class OperadorBase(BaseModel):
    transportista_id: int | None = None
    tipo_contratacion: str | None = Field(None, max_length=32)
    licencia: str | None = Field(None, max_length=64)
    tipo_licencia: str | None = Field(None, max_length=32)
    vigencia_licencia: date | None = None
    estatus_documental: str | None = Field(None, max_length=32)
    nombre: str = Field(..., max_length=100)
    apellido_paterno: str = Field(..., max_length=100)
    apellido_materno: str | None = Field(None, max_length=100)
    fecha_nacimiento: date
    curp: str = Field(..., min_length=18, max_length=18)
    rfc: str = Field(..., max_length=13)
    nss: str = Field(..., min_length=11, max_length=11)
    estado_civil: EstadoCivil
    tipo_sangre: TipoSangre
    fotografia: str | None = Field(None, max_length=1024)

    telefono_principal: str = Field(..., max_length=20)
    telefono_emergencia: str | None = Field(None, max_length=20)
    nombre_contacto_emergencia: str | None = Field(None, max_length=255)
    direccion: str = Field(..., max_length=255)
    colonia: str = Field(..., max_length=120)
    municipio: str = Field(..., max_length=120)
    estado_geografico: str = Field(
        ...,
        max_length=64,
        description="Entidad federativa (estado del domicilio)",
    )
    codigo_postal: str = Field(..., min_length=5, max_length=5)
    correo_electronico: str = Field(..., max_length=255)

    anios_experiencia: int | None = Field(None, ge=0)
    tipos_unidad_manejadas: list[str] | None = None
    rutas_conocidas: str | None = None
    tipos_carga_experiencia: list[str] | None = None
    certificaciones: str | None = None

    ultima_revision_medica: date | None = None
    resultado_apto: bool | None = None
    restricciones_medicas: str | None = None
    proxima_revision_medica: date | None = None

    puntualidad: Decimal | None = Field(None, ge=0, le=100)
    consumo_diesel_promedio: Decimal | None = Field(None, ge=0)
    consumo_gasolina_promedio: Decimal | None = Field(None, ge=0)
    incidencias_desempeno: str | None = None
    calificacion_general: Decimal | None = Field(None, ge=0, le=100)
    comentarios_desempeno: str | None = None

    @field_validator("curp", "nss", "codigo_postal", mode="before")
    @classmethod
    def strip_upper_ids(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return str(v).strip().upper()


class OperadorCreate(OperadorBase):
    pass


class OperadorUpdate(BaseModel):
    transportista_id: int | None = None
    tipo_contratacion: str | None = Field(None, max_length=32)
    licencia: str | None = Field(None, max_length=64)
    tipo_licencia: str | None = Field(None, max_length=32)
    vigencia_licencia: date | None = None
    estatus_documental: str | None = Field(None, max_length=32)
    nombre: str | None = Field(None, max_length=100)
    apellido_paterno: str | None = Field(None, max_length=100)
    apellido_materno: str | None = Field(None, max_length=100)
    fecha_nacimiento: date | None = None
    curp: str | None = Field(None, min_length=18, max_length=18)
    rfc: str | None = Field(None, max_length=13)
    nss: str | None = Field(None, min_length=11, max_length=11)
    estado_civil: EstadoCivil | None = None
    tipo_sangre: TipoSangre | None = None
    fotografia: str | None = Field(None, max_length=1024)
    telefono_principal: str | None = Field(None, max_length=20)
    telefono_emergencia: str | None = Field(None, max_length=20)
    nombre_contacto_emergencia: str | None = Field(None, max_length=255)
    direccion: str | None = Field(None, max_length=255)
    colonia: str | None = Field(None, max_length=120)
    municipio: str | None = Field(None, max_length=120)
    estado_geografico: str | None = Field(None, max_length=64)
    codigo_postal: str | None = Field(None, min_length=5, max_length=5)
    correo_electronico: str | None = Field(None, max_length=255)
    anios_experiencia: int | None = Field(None, ge=0)
    tipos_unidad_manejadas: list[str] | None = None
    rutas_conocidas: str | None = None
    tipos_carga_experiencia: list[str] | None = None
    certificaciones: str | None = None
    ultima_revision_medica: date | None = None
    resultado_apto: bool | None = None
    restricciones_medicas: str | None = None
    proxima_revision_medica: date | None = None
    puntualidad: Decimal | None = Field(None, ge=0, le=100)
    consumo_diesel_promedio: Decimal | None = Field(None, ge=0)
    consumo_gasolina_promedio: Decimal | None = Field(None, ge=0)
    incidencias_desempeno: str | None = None
    calificacion_general: Decimal | None = Field(None, ge=0, le=100)
    comentarios_desempeno: str | None = None

    @field_validator("curp", "nss", "codigo_postal", mode="before")
    @classmethod
    def strip_upper_ids_optional(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return str(v).strip().upper()


class OperadorRead(OperadorBase):
    model_config = ConfigDict(from_attributes=True)

    id_operador: int
    created_at: datetime
    updated_at: datetime


class OperadorCumplimientoFederalRead(BaseModel):
    id_operador: int
    cumple_transporte_federal: bool
    licencia_federal_vigente: bool
    apto_medico_sct_vigente: bool
    faltantes: list[str]


class OperadorListResponse(BaseModel):
    items: list[OperadorRead]
    total: int
    skip: int
    limit: int
