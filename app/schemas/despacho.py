from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.despacho import EstadoDespacho, TipoEventoDespacho


class OperadorEnDespacho(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_operador: int
    nombre: str
    apellido_paterno: str


class UnidadEnDespacho(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_unidad: int
    economico: str
    placas: str | None


class ViajeEnDespacho(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo_viaje: str
    origen: str
    destino: str


class AsignacionEnDespacho(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_asignacion: int
    id_operador: int
    id_unidad: int
    id_viaje: int
    fecha_salida: datetime
    operador: OperadorEnDespacho
    unidad: UnidadEnDespacho
    viaje: ViajeEnDespacho


class FleteEnDespacho(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo_flete: str
    estado: str


class DespachoEventoBase(BaseModel):
    tipo_evento: TipoEventoDespacho
    fecha_evento: datetime
    ubicacion: str | None = Field(None, max_length=255)
    descripcion: str
    latitud: Decimal | None = None
    longitud: Decimal | None = None


class DespachoEventoCreate(DespachoEventoBase):
    pass


class DespachoEventoRead(DespachoEventoBase):
    model_config = ConfigDict(from_attributes=True)

    id_evento: int
    id_despacho: int
    created_at: datetime
    updated_at: datetime


class DespachoEventoListResponse(BaseModel):
    items: list[DespachoEventoRead]
    total: int


class DespachoBase(BaseModel):
    id_asignacion: int
    id_flete: int | None = None
    salida_programada: datetime | None = None
    observaciones_transito: str | None = None


class DespachoCreate(DespachoBase):
    pass


class DespachoUpdate(BaseModel):
    id_flete: int | None = None
    salida_programada: datetime | None = None
    estatus: EstadoDespacho | None = None
    observaciones_transito: str | None = None
    motivo_cancelacion: str | None = None


class DespachoRegistrarSalida(BaseModel):
    salida_real: datetime
    km_salida: Decimal | None = Field(None, ge=0)
    observaciones_salida: str | None = None


class DespachoRegistrarEntrega(BaseModel):
    fecha_entrega: datetime
    evidencia_entrega: str | None = Field(None, max_length=1024)
    firma_recibe: str | None = Field(None, max_length=255)
    observaciones_entrega: str | None = None


class DespachoCerrar(BaseModel):
    llegada_real: datetime
    km_llegada: Decimal | None = Field(None, ge=0)
    observaciones_cierre: str | None = None


class DespachoCancelar(BaseModel):
    motivo_cancelacion: str = Field(..., min_length=3)


class DespachoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_despacho: int
    id_asignacion: int
    id_flete: int | None
    estatus: EstadoDespacho
    salida_programada: datetime | None
    salida_real: datetime | None
    fecha_entrega: datetime | None
    llegada_real: datetime | None
    km_salida: Decimal | None
    km_llegada: Decimal | None
    evidencia_entrega: str | None
    firma_recibe: str | None
    observaciones_salida: str | None
    observaciones_transito: str | None
    observaciones_entrega: str | None
    observaciones_cierre: str | None
    motivo_cancelacion: str | None
    created_at: datetime
    updated_at: datetime
    asignacion: AsignacionEnDespacho
    flete: FleteEnDespacho | None
    eventos: list[DespachoEventoRead]


class DespachoListResponse(BaseModel):
    items: list[DespachoRead]
    total: int
    skip: int
    limit: int
