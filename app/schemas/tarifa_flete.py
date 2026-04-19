from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.tarifa_flete import AmbitoTarifaFlete, ModalidadCobroTarifa
from app.models.transportista import TipoTransportista


class TarifaFleteBase(BaseModel):
    nombre_tarifa: str = Field(..., max_length=120)
    tipo_operacion: TipoTransportista = TipoTransportista.SUBCONTRATADO
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
    porcentaje_utilidad: Decimal = Field(default=Decimal("0.20"), ge=0)
    porcentaje_riesgo: Decimal = Field(default=Decimal("0"), ge=0)
    porcentaje_urgencia: Decimal = Field(default=Decimal("0"), ge=0)
    porcentaje_retorno_vacio: Decimal = Field(default=Decimal("0"), ge=0)
    porcentaje_carga_especial: Decimal = Field(default=Decimal("0"), ge=0)
    moneda: str = Field(default="MXN", max_length=3)
    activo: bool = True
    vigencia_inicio: date | None = None
    vigencia_fin: date | None = None


class TarifaFleteCreate(TarifaFleteBase):
    pass


class TarifaFleteUpdate(BaseModel):
    nombre_tarifa: str | None = Field(None, max_length=120)
    tipo_operacion: TipoTransportista | None = None
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
    porcentaje_utilidad: Decimal | None = Field(None, ge=0)
    porcentaje_riesgo: Decimal | None = Field(None, ge=0)
    porcentaje_urgencia: Decimal | None = Field(None, ge=0)
    porcentaje_retorno_vacio: Decimal | None = Field(None, ge=0)
    porcentaje_carga_especial: Decimal | None = Field(None, ge=0)
    moneda: str | None = Field(None, max_length=3)
    activo: bool | None = None
    vigencia_inicio: date | None = None
    vigencia_fin: date | None = None


class TarifaFleteRead(TarifaFleteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class TarifaFleteListResponse(BaseModel):
    items: list[TarifaFleteRead]
    total: int
    skip: int
    limit: int
