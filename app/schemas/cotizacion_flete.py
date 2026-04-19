from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.cotizacion_flete import EstatusCotizacionFlete
from app.models.tarifa_flete import AmbitoTarifaFlete, ModalidadCobroTarifa
from app.schemas.flete import FleteCotizacionRequest


class CotizacionFleteCreate(FleteCotizacionRequest):
    observaciones: str | None = None


class CotizacionFleteCambiarEstatus(BaseModel):
    estatus: EstatusCotizacionFlete
    observaciones: str | None = None


class CotizacionFleteConvertir(BaseModel):
    codigo_flete: str = Field(..., max_length=64)
    transportista_id: int
    viaje_id: int | None = None
    descripcion_carga: str | None = Field(None, max_length=500)
    numero_bultos: int | None = Field(None, ge=0)
    volumen_m3: Decimal | None = Field(None, ge=0)
    notas: str | None = None


class CotizacionFleteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    folio: str
    cliente_id: int | None
    tarifa_flete_id: int
    tarifa_especial_cliente_id: int | None
    flete_id: int | None
    ambito: AmbitoTarifaFlete
    modalidad_cobro: ModalidadCobroTarifa
    origen: str
    destino: str
    tipo_unidad: str
    tipo_carga: str | None
    distancia_km: Decimal
    peso_kg: Decimal
    horas_servicio: Decimal
    dias_servicio: Decimal
    urgencia: bool
    retorno_vacio: bool
    riesgo_pct_extra: Decimal
    recargos: Decimal
    costo_base_estimado: Decimal
    subtotal_estimado: Decimal
    utilidad_aplicada: Decimal
    riesgo_aplicado: Decimal
    urgencia_aplicada: Decimal
    retorno_vacio_aplicado: Decimal
    carga_especial_aplicada: Decimal
    descuento_cliente_aplicado: Decimal
    incremento_cliente_aplicado: Decimal
    recargo_fijo_cliente_aplicado: Decimal
    precio_venta_sugerido: Decimal
    moneda: str
    detalle_calculo: str
    estatus: EstatusCotizacionFlete
    observaciones: str | None
    created_at: datetime
    updated_at: datetime


class CotizacionFleteListResponse(BaseModel):
    items: list[CotizacionFleteRead]
    total: int
    skip: int
    limit: int
