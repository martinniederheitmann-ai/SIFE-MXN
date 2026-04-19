from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.orden_servicio import EstatusOrdenServicio


class ClienteEnOrdenServicio(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    razon_social: str


class CotizacionEnOrdenServicio(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    folio: str
    precio_venta_sugerido: Decimal
    estatus: str


class FleteEnOrdenServicio(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo_flete: str


class ViajeEnOrdenServicio(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo_viaje: str


class DespachoEnOrdenServicio(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_despacho: int
    estatus: str


class OrdenServicioBase(BaseModel):
    cliente_id: int
    cotizacion_id: int | None = None
    flete_id: int | None = None
    viaje_id: int | None = None
    despacho_id: int | None = None
    origen: str = Field(..., max_length=255)
    destino: str = Field(..., max_length=255)
    tipo_unidad: str = Field(..., max_length=64)
    tipo_carga: str | None = Field(None, max_length=64)
    peso_kg: Decimal = Field(..., ge=0)
    distancia_km: Decimal | None = Field(None, ge=0)
    precio_comprometido: Decimal = Field(..., ge=0)
    moneda: str = Field(default="MXN", max_length=3)
    fecha_programada: datetime | None = None
    observaciones: str | None = None


class OrdenServicioCreate(OrdenServicioBase):
    pass


class OrdenServicioDesdeCotizacionCreate(BaseModel):
    cotizacion_id: int
    fecha_programada: datetime | None = None
    observaciones: str | None = None


class OrdenServicioUpdate(BaseModel):
    flete_id: int | None = None
    viaje_id: int | None = None
    despacho_id: int | None = None
    origen: str | None = Field(None, max_length=255)
    destino: str | None = Field(None, max_length=255)
    tipo_unidad: str | None = Field(None, max_length=64)
    tipo_carga: str | None = Field(None, max_length=64)
    peso_kg: Decimal | None = Field(None, ge=0)
    distancia_km: Decimal | None = Field(None, ge=0)
    precio_comprometido: Decimal | None = Field(None, ge=0)
    moneda: str | None = Field(None, max_length=3)
    fecha_programada: datetime | None = None
    observaciones: str | None = None


class OrdenServicioCambiarEstatus(BaseModel):
    estatus: EstatusOrdenServicio
    observaciones: str | None = None


class OrdenServicioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    folio: str
    cliente_id: int
    cotizacion_id: int | None
    flete_id: int | None
    viaje_id: int | None
    despacho_id: int | None
    origen: str
    destino: str
    tipo_unidad: str
    tipo_carga: str | None
    peso_kg: Decimal
    distancia_km: Decimal | None
    precio_comprometido: Decimal
    moneda: str
    fecha_solicitud: datetime
    fecha_programada: datetime | None
    estatus: EstatusOrdenServicio
    observaciones: str | None
    created_at: datetime
    updated_at: datetime
    cliente: ClienteEnOrdenServicio
    cotizacion: CotizacionEnOrdenServicio | None
    flete: FleteEnOrdenServicio | None
    viaje: ViajeEnOrdenServicio | None
    despacho: DespachoEnOrdenServicio | None


class OrdenServicioListResponse(BaseModel):
    items: list[OrdenServicioRead]
    total: int
    skip: int
    limit: int
