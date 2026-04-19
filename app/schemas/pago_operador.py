from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.pago_operador import EstatusPagoOperador, TipoPagoOperadorEnum


class PagoOperadorBase(BaseModel):
    tipo_pago: TipoPagoOperadorEnum
    monto: Decimal = Field(..., ge=0)
    fecha: date
    concepto: str | None = Field(None, max_length=500)
    estatus: EstatusPagoOperador = EstatusPagoOperador.PENDIENTE
    notas: str | None = None


class PagoOperadorCreate(PagoOperadorBase):
    pass


class PagoOperadorUpdate(BaseModel):
    tipo_pago: TipoPagoOperadorEnum | None = None
    monto: Decimal | None = Field(None, ge=0)
    fecha: date | None = None
    concepto: str | None = Field(None, max_length=500)
    estatus: EstatusPagoOperador | None = None
    notas: str | None = None


class PagoOperadorRead(PagoOperadorBase):
    model_config = ConfigDict(from_attributes=True)

    id_pago: int
    id_operador: int
    created_at: datetime
    updated_at: datetime


class PagoOperadorListResponse(BaseModel):
    items: list[PagoOperadorRead]
    total: int
