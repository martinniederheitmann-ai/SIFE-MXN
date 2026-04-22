from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.baja_dano import EstatusBajaDano, TipoBajaDano


class BajaDanoCreate(BaseModel):
    tipo: TipoBajaDano
    titulo: str = Field(min_length=1, max_length=255)
    detalle: str | None = None
    fecha_evento: date
    flete_id: int | None = None
    id_unidad: int | None = None
    id_operador: int | None = None
    estatus: EstatusBajaDano = EstatusBajaDano.ABIERTA
    costo_estimado: Decimal | None = None


class BajaDanoUpdate(BaseModel):
    titulo: str | None = Field(default=None, min_length=1, max_length=255)
    detalle: str | None = None
    fecha_evento: date | None = None
    flete_id: int | None = None
    id_unidad: int | None = None
    id_operador: int | None = None
    estatus: EstatusBajaDano | None = None
    costo_estimado: Decimal | None = None


class BajaDanoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: TipoBajaDano
    titulo: str
    detalle: str | None
    fecha_evento: date
    flete_id: int | None
    id_unidad: int | None
    id_operador: int | None
    estatus: EstatusBajaDano
    costo_estimado: Decimal | None
    created_at: object
    updated_at: object


class BajaDanoListResponse(BaseModel):
    items: list[BajaDanoRead]
    total: int
    skip: int
    limit: int
