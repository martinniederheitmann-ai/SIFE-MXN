from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.tarifa_flete import AmbitoTarifaFlete, ModalidadCobroTarifa
from app.models.transportista import TipoTransportista


class TarifaCompraTransportistaBase(BaseModel):
    transportista_id: int
    tipo_transportista: TipoTransportista = TipoTransportista.SUBCONTRATADO
    nombre_tarifa: str = Field(..., max_length=120)
    ambito: AmbitoTarifaFlete = AmbitoTarifaFlete.FEDERAL
    modalidad_cobro: ModalidadCobroTarifa = ModalidadCobroTarifa.MIXTA
    origen: str = Field(..., max_length=255)
    destino: str = Field(..., max_length=255)
    tipo_unidad: str = Field(..., max_length=64)
    tipo_carga: str | None = Field(None, max_length=64)
    tarifa_base: Decimal = Field(..., ge=0)
    tarifa_km: Decimal = Field(default=Decimal("0"), ge=0)
    tarifa_kg: Decimal = Field(default=Decimal("0"), ge=0)
    tarifa_tonelada: Decimal = Field(default=Decimal("0"), ge=0)
    tarifa_hora: Decimal = Field(default=Decimal("0"), ge=0)
    tarifa_dia: Decimal = Field(default=Decimal("0"), ge=0)
    recargo_minimo: Decimal = Field(default=Decimal("0"), ge=0)
    dias_credito: int = Field(default=0, ge=0)
    moneda: str = Field(default="MXN", max_length=3)
    activo: bool = True
    vigencia_inicio: date | None = None
    vigencia_fin: date | None = None
    observaciones: str | None = None


class TarifaCompraTransportistaCreate(TarifaCompraTransportistaBase):
    pass


class TarifaCompraTransportistaUpdate(BaseModel):
    transportista_id: int | None = None
    tipo_transportista: TipoTransportista | None = None
    nombre_tarifa: str | None = Field(None, max_length=120)
    ambito: AmbitoTarifaFlete | None = None
    modalidad_cobro: ModalidadCobroTarifa | None = None
    origen: str | None = Field(None, max_length=255)
    destino: str | None = Field(None, max_length=255)
    tipo_unidad: str | None = Field(None, max_length=64)
    tipo_carga: str | None = Field(None, max_length=64)
    tarifa_base: Decimal | None = Field(None, ge=0)
    tarifa_km: Decimal | None = Field(None, ge=0)
    tarifa_kg: Decimal | None = Field(None, ge=0)
    tarifa_tonelada: Decimal | None = Field(None, ge=0)
    tarifa_hora: Decimal | None = Field(None, ge=0)
    tarifa_dia: Decimal | None = Field(None, ge=0)
    recargo_minimo: Decimal | None = Field(None, ge=0)
    dias_credito: int | None = Field(None, ge=0)
    moneda: str | None = Field(None, max_length=3)
    activo: bool | None = None
    vigencia_inicio: date | None = None
    vigencia_fin: date | None = None
    observaciones: str | None = None


class TarifaCompraTransportistaRead(TarifaCompraTransportistaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class TarifaCompraTransportistaListResponse(BaseModel):
    items: list[TarifaCompraTransportistaRead]
    total: int
    skip: int
    limit: int
