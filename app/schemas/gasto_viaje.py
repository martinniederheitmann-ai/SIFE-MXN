from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class GastoViajeBase(BaseModel):
    flete_id: int
    tipo_gasto: str = Field(..., max_length=64)
    monto: Decimal = Field(..., ge=0)
    fecha_gasto: date
    descripcion: str | None = None
    referencia: str | None = Field(None, max_length=120)
    comprobante: str | None = Field(None, max_length=1024)


class GastoViajeCreate(GastoViajeBase):
    pass


class GastoViajeUpdate(BaseModel):
    tipo_gasto: str | None = Field(None, max_length=64)
    monto: Decimal | None = Field(None, ge=0)
    fecha_gasto: date | None = None
    descripcion: str | None = None
    referencia: str | None = Field(None, max_length=120)
    comprobante: str | None = Field(None, max_length=1024)


class GastoViajeRead(GastoViajeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class GastoViajeListResponse(BaseModel):
    items: list[GastoViajeRead]
    total: int
    skip: int
    limit: int
