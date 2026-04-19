from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.incidente_operador import TipoIncidenteOperador


class IncidenteOperadorBase(BaseModel):
    tipo: TipoIncidenteOperador
    fecha: date
    descripcion: str
    costo_estimado: Decimal | None = Field(None, ge=0)
    resolucion: str | None = None


class IncidenteOperadorCreate(IncidenteOperadorBase):
    pass


class IncidenteOperadorUpdate(BaseModel):
    tipo: TipoIncidenteOperador | None = None
    fecha: date | None = None
    descripcion: str | None = None
    costo_estimado: Decimal | None = Field(None, ge=0)
    resolucion: str | None = None


class IncidenteOperadorRead(IncidenteOperadorBase):
    model_config = ConfigDict(from_attributes=True)

    id_incidente: int
    id_operador: int
    created_at: datetime
    updated_at: datetime


class IncidenteOperadorListResponse(BaseModel):
    items: list[IncidenteOperadorRead]
    total: int
