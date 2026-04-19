from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from app.models.flete import EstadoFlete, MetodoCalculoFlete
from app.models.transportista import TipoTransportista
from app.models.tarifa_flete import AmbitoTarifaFlete, ModalidadCobroTarifa


class ClienteEnFlete(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    razon_social: str


class TransportistaEnFlete(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str


class ViajeEnFlete(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo_viaje: str


class FleteBase(BaseModel):
    codigo_flete: str = Field(..., max_length=64)
    cliente_id: int
    transportista_id: int
    viaje_id: int | None = None
    descripcion_carga: str | None = Field(None, max_length=500)
    peso_kg: Decimal = Field(..., ge=0)
    volumen_m3: Decimal | None = Field(None, ge=0)
    numero_bultos: int | None = Field(None, ge=0)
    distancia_km: Decimal | None = Field(None, ge=0)
    tipo_operacion: TipoTransportista = TipoTransportista.SUBCONTRATADO
    tipo_unidad: str | None = Field(None, max_length=64)
    tipo_carga: str | None = Field(None, max_length=64)
    monto_estimado: Decimal | None = Field(None, ge=0)
    precio_venta: Decimal | None = Field(None, ge=0)
    costo_transporte_estimado: Decimal | None = Field(None, ge=0)
    costo_transporte_real: Decimal | None = Field(None, ge=0)
    margen_estimado: Decimal | None = None
    margen_real: Decimal | None = None
    metodo_calculo: MetodoCalculoFlete = MetodoCalculoFlete.MANUAL
    moneda: str = Field(default="MXN", max_length=3)
    estado: EstadoFlete = EstadoFlete.COTIZADO
    ambito_operacion: AmbitoTarifaFlete | None = None
    carta_porte_uuid: str | None = Field(None, max_length=64)
    carta_porte_folio: str | None = Field(None, max_length=64)
    factura_mercancia_folio: str | None = Field(None, max_length=64)
    mercancia_documentacion_ok: bool = False
    notas: str | None = None

    @model_validator(mode="after")
    def sync_amounts(self) -> "FleteBase":
        if self.precio_venta is None and self.monto_estimado is None:
            raise ValueError("Debes enviar precio_venta o monto_estimado.")
        if self.precio_venta is None:
            self.precio_venta = self.monto_estimado
        if self.monto_estimado is None:
            self.monto_estimado = self.precio_venta
        # Margenes: siempre derivados de precio y costos (se ignoran valores enviados por el cliente).
        if self.precio_venta is not None and self.costo_transporte_estimado is not None:
            self.margen_estimado = (self.precio_venta - self.costo_transporte_estimado).quantize(
                Decimal("0.01")
            )
        else:
            self.margen_estimado = None
        if self.precio_venta is not None and self.costo_transporte_real is not None:
            self.margen_real = (self.precio_venta - self.costo_transporte_real).quantize(Decimal("0.01"))
        else:
            self.margen_real = None
        return self


class FleteCreate(FleteBase):
    pass


class FleteUpdate(BaseModel):
    codigo_flete: str | None = Field(None, max_length=64)
    cliente_id: int | None = None
    transportista_id: int | None = None
    viaje_id: int | None = None
    descripcion_carga: str | None = Field(None, max_length=500)
    peso_kg: Decimal | None = Field(None, ge=0)
    volumen_m3: Decimal | None = Field(None, ge=0)
    numero_bultos: int | None = Field(None, ge=0)
    distancia_km: Decimal | None = Field(None, ge=0)
    tipo_operacion: TipoTransportista | None = None
    tipo_unidad: str | None = Field(None, max_length=64)
    tipo_carga: str | None = Field(None, max_length=64)
    monto_estimado: Decimal | None = Field(None, ge=0)
    precio_venta: Decimal | None = Field(None, ge=0)
    costo_transporte_estimado: Decimal | None = Field(None, ge=0)
    costo_transporte_real: Decimal | None = Field(None, ge=0)
    margen_estimado: Decimal | None = None
    margen_real: Decimal | None = None
    metodo_calculo: MetodoCalculoFlete | None = None
    moneda: str | None = Field(None, max_length=3)
    estado: EstadoFlete | None = None
    ambito_operacion: AmbitoTarifaFlete | None = None
    carta_porte_uuid: str | None = Field(None, max_length=64)
    carta_porte_folio: str | None = Field(None, max_length=64)
    factura_mercancia_folio: str | None = Field(None, max_length=64)
    mercancia_documentacion_ok: bool | None = None
    notas: str | None = None

    @model_validator(mode="after")
    def sync_amounts(self) -> "FleteUpdate":
        if self.precio_venta is None and self.monto_estimado is not None:
            self.precio_venta = self.monto_estimado
        if self.monto_estimado is None and self.precio_venta is not None:
            self.monto_estimado = self.precio_venta
        # margen_estimado / margen_real se recalculan en crud.flete.update tras fusionar con el registro.
        return self


class FleteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo_flete: str
    cliente_id: int
    transportista_id: int
    viaje_id: int | None
    descripcion_carga: str | None
    peso_kg: Decimal
    volumen_m3: Decimal | None
    numero_bultos: int | None
    distancia_km: Decimal | None
    tipo_operacion: TipoTransportista
    tipo_unidad: str | None
    tipo_carga: str | None
    monto_estimado: Decimal
    precio_venta: Decimal
    costo_transporte_estimado: Decimal | None
    costo_transporte_real: Decimal | None
    margen_estimado: Decimal | None
    margen_real: Decimal | None
    metodo_calculo: MetodoCalculoFlete
    moneda: str
    estado: EstadoFlete
    ambito_operacion: AmbitoTarifaFlete | None
    carta_porte_uuid: str | None
    carta_porte_folio: str | None
    factura_mercancia_folio: str | None
    mercancia_documentacion_ok: bool
    notas: str | None
    created_at: datetime
    updated_at: datetime
    cliente: ClienteEnFlete
    transportista: TransportistaEnFlete
    viaje: ViajeEnFlete | None

    @computed_field
    @property
    def margen_estimado_pct(self) -> Decimal | None:
        if self.margen_estimado is None or self.precio_venta == 0:
            return None
        return (self.margen_estimado / self.precio_venta * Decimal("100")).quantize(Decimal("0.01"))


class FleteListResponse(BaseModel):
    items: list[FleteRead]
    total: int
    skip: int
    limit: int


class FleteCotizacionRequest(BaseModel):
    cliente_id: int | None = None
    tipo_operacion: TipoTransportista = TipoTransportista.SUBCONTRATADO
    ambito: AmbitoTarifaFlete | None = None
    origen: str = Field(..., max_length=255)
    destino: str = Field(..., max_length=255)
    tipo_unidad: str = Field(..., max_length=64)
    tipo_carga: str | None = Field(None, max_length=64)
    distancia_km: Decimal = Field(..., ge=0)
    peso_kg: Decimal = Field(..., ge=0)
    horas_servicio: Decimal = Field(default=Decimal("0"), ge=0)
    dias_servicio: Decimal = Field(default=Decimal("0"), ge=0)
    urgencia: bool = False
    retorno_vacio: bool = False
    riesgo_pct_extra: Decimal = Field(default=Decimal("0"), ge=0)
    recargos: Decimal = Field(default=Decimal("0"), ge=0)


class FleteCompraCotizacionRequest(BaseModel):
    transportista_id: int
    ambito: AmbitoTarifaFlete | None = None
    origen: str = Field(..., max_length=255)
    destino: str = Field(..., max_length=255)
    tipo_unidad: str = Field(..., max_length=64)
    tipo_carga: str | None = Field(None, max_length=64)
    distancia_km: Decimal = Field(..., ge=0)
    peso_kg: Decimal = Field(..., ge=0)
    horas_servicio: Decimal = Field(default=Decimal("0"), ge=0)
    dias_servicio: Decimal = Field(default=Decimal("0"), ge=0)
    recargos: Decimal = Field(default=Decimal("0"), ge=0)


class FleteCotizacionRead(BaseModel):
    tarifa_id: int
    nombre_tarifa: str
    cliente_id: int | None
    tarifa_especial_cliente_id: int | None
    nombre_acuerdo_cliente: str | None
    ambito: AmbitoTarifaFlete
    modalidad_cobro: ModalidadCobroTarifa
    linea_modalidad: str = Field(
        default="",
        description="Texto del desglose segun modalidad de cobro del catalogo.",
    )
    advertencias: list[str] = Field(
        default_factory=list,
        description="Alertas de configuracion o doble cobro (auditoria).",
    )
    toneladas_estimadas: Decimal
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
    recargos: Decimal
    precio_venta_sugerido: Decimal
    moneda: str
    detalle_calculo: str


class FleteCompraCotizacionRead(BaseModel):
    tarifa_id: int
    transportista_id: int
    nombre_tarifa: str
    ambito: AmbitoTarifaFlete
    modalidad_cobro: ModalidadCobroTarifa
    linea_modalidad: str = Field(default="", description="Desglose segun modalidad de cobro.")
    advertencias: list[str] = Field(default_factory=list, description="Alertas de auditoria.")
    toneladas_estimadas: Decimal
    costo_base_estimado: Decimal
    subtotal_estimado: Decimal
    recargos: Decimal
    dias_credito: int
    costo_compra_sugerido: Decimal
    moneda: str
    detalle_calculo: str
