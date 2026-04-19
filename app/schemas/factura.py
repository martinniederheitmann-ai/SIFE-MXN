from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.factura import EstatusFactura


class ClienteEnFactura(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    razon_social: str


class FleteEnFactura(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo_flete: str


class OrdenServicioEnFactura(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    folio: str


class FacturaBase(BaseModel):
    serie: str | None = Field(None, max_length=12)
    cliente_id: int
    flete_id: int | None = None
    orden_servicio_id: int | None = None
    fecha_emision: date
    fecha_vencimiento: date | None = None
    concepto: str = Field(..., max_length=255)
    referencia: str | None = Field(None, max_length=120)
    moneda: str = Field(default="MXN", max_length=3)
    subtotal: Decimal = Field(..., ge=0)
    iva_pct: Decimal = Field(default=Decimal("0.16"), ge=0)
    iva_monto: Decimal | None = Field(None, ge=0)
    retencion_monto: Decimal = Field(default=Decimal("0"), ge=0)
    total: Decimal | None = Field(None, ge=0)
    saldo_pendiente: Decimal | None = Field(None, ge=0)
    forma_pago: str | None = Field(None, max_length=64)
    metodo_pago: str | None = Field(None, max_length=16)
    uso_cfdi: str | None = Field(None, max_length=16)
    estatus: EstatusFactura = EstatusFactura.BORRADOR
    timbrada: bool = False
    observaciones: str | None = None

    @model_validator(mode="after")
    def sync_amounts(self) -> "FacturaBase":
        iva_monto = self.iva_monto
        if iva_monto is None:
            iva_monto = self.subtotal * self.iva_pct
            self.iva_monto = iva_monto
        total = self.total
        if total is None:
            total = self.subtotal + iva_monto - self.retencion_monto
            self.total = total
        if self.saldo_pendiente is None:
            self.saldo_pendiente = total
        return self


class FacturaCreate(FacturaBase):
    pass


class FacturaUpdate(BaseModel):
    serie: str | None = Field(None, max_length=12)
    cliente_id: int | None = None
    flete_id: int | None = None
    orden_servicio_id: int | None = None
    fecha_emision: date | None = None
    fecha_vencimiento: date | None = None
    concepto: str | None = Field(None, max_length=255)
    referencia: str | None = Field(None, max_length=120)
    moneda: str | None = Field(None, max_length=3)
    subtotal: Decimal | None = Field(None, ge=0)
    iva_pct: Decimal | None = Field(None, ge=0)
    iva_monto: Decimal | None = Field(None, ge=0)
    retencion_monto: Decimal | None = Field(None, ge=0)
    total: Decimal | None = Field(None, ge=0)
    saldo_pendiente: Decimal | None = Field(None, ge=0)
    forma_pago: str | None = Field(None, max_length=64)
    metodo_pago: str | None = Field(None, max_length=16)
    uso_cfdi: str | None = Field(None, max_length=16)
    estatus: EstatusFactura | None = None
    timbrada: bool | None = None
    observaciones: str | None = None


class FacturaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    folio: str
    serie: str | None
    cliente_id: int
    flete_id: int | None
    orden_servicio_id: int | None
    fecha_emision: date
    fecha_vencimiento: date | None
    concepto: str
    referencia: str | None
    moneda: str
    subtotal: Decimal
    iva_pct: Decimal
    iva_monto: Decimal
    retencion_monto: Decimal
    total: Decimal
    saldo_pendiente: Decimal
    forma_pago: str | None
    metodo_pago: str | None
    uso_cfdi: str | None
    estatus: EstatusFactura
    timbrada: bool
    observaciones: str | None
    created_at: datetime
    updated_at: datetime
    cliente: ClienteEnFactura
    flete: FleteEnFactura | None
    orden_servicio: OrdenServicioEnFactura | None


class FacturaPreviewDesdeFlete(BaseModel):
    """Vista previa para facturación asistida: precio del flete vs recálculo con tarifas vigentes."""

    flete_id: int
    cliente_id: int
    codigo_flete: str
    metodo_calculo_flete: str
    subtotal_desde_flete: Decimal
    subtotal_desde_tarifa_recalculado: Decimal | None = None
    diferencia_tarifa_vs_flete: Decimal | None = None
    nombre_tarifa: str | None = None
    detalle_tarifa: str | None = None
    recotizacion_disponible: bool
    observaciones_sistema: str
    iva_pct: Decimal
    retencion_monto: Decimal
    iva_monto: Decimal
    total: Decimal
    iva_monto_si_precio_tarifa: Decimal | None = None
    total_si_precio_tarifa: Decimal | None = None
    concepto_sugerido: str
    referencia_sugerida: str
    moneda: str


class FacturaGenerarDesdeFlete(BaseModel):
    """Captura mínima: flete + parámetros fiscales; montos desde flete o desde tarifa recalculada."""

    flete_id: int
    fecha_emision: date | None = None
    fecha_vencimiento: date | None = None
    serie: str | None = Field(None, max_length=12)
    iva_pct: Decimal = Field(default=Decimal("0.16"), ge=0)
    retencion_monto: Decimal = Field(default=Decimal("0"), ge=0)
    usar_precio_tarifa_recalculado: bool = Field(
        default=False,
        description="Si es true y hay tarifa coincidente, el subtotal será precio_venta_sugerido del motor.",
    )
    forma_pago: str | None = Field(None, max_length=64)
    metodo_pago: str | None = Field(None, max_length=16)
    uso_cfdi: str | None = Field(None, max_length=16)
    estatus: EstatusFactura = EstatusFactura.BORRADOR
    timbrada: bool = False
    concepto: str | None = Field(None, max_length=255)
    referencia: str | None = Field(None, max_length=120)
    observaciones: str | None = None


class FacturaListResponse(BaseModel):
    items: list[FacturaRead]
    total: int
    skip: int
    limit: int
