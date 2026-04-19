from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class UnidadEnAsignacion(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_unidad: int
    economico: str
    placas: str | None


class ViajeEnAsignacion(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo_viaje: str


class OperadorEnAsignacion(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_operador: int
    nombre: str
    apellido_paterno: str


class AsignacionBase(BaseModel):
    id_operador: int
    id_unidad: int
    id_viaje: int
    fecha_salida: datetime
    fecha_regreso: datetime | None = None
    km_inicial: Decimal | None = Field(None, ge=0)
    km_final: Decimal | None = Field(None, ge=0)
    rendimiento_combustible: Decimal | None = Field(None, ge=0)


class AsignacionCreate(AsignacionBase):
    pass


class AsignacionUpdate(BaseModel):
    id_operador: int | None = None
    id_unidad: int | None = None
    id_viaje: int | None = None
    fecha_salida: datetime | None = None
    fecha_regreso: datetime | None = None
    km_inicial: Decimal | None = Field(None, ge=0)
    km_final: Decimal | None = Field(None, ge=0)
    rendimiento_combustible: Decimal | None = Field(None, ge=0)


class AsignacionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_asignacion: int
    id_operador: int
    id_unidad: int
    id_viaje: int
    fecha_salida: datetime
    fecha_regreso: datetime | None
    km_inicial: Decimal | None
    km_final: Decimal | None
    rendimiento_combustible: Decimal | None
    created_at: datetime
    updated_at: datetime
    operador: OperadorEnAsignacion
    unidad: UnidadEnAsignacion
    viaje: ViajeEnAsignacion


class AsignacionListResponse(BaseModel):
    items: list[AsignacionRead]
    total: int
    skip: int
    limit: int
