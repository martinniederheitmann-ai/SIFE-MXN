from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class UnidadBase(BaseModel):
    transportista_id: int | None = None
    economico: str = Field(..., max_length=64)
    placas: str | None = Field(None, max_length=20)
    tipo_propiedad: str | None = Field(None, max_length=32)
    estatus_documental: str | None = Field(None, max_length=32)
    descripcion: str | None = Field(None, max_length=255)
    detalle: str | None = None
    activo: bool = True
    vigencia_seguro: date | None = None
    vigencia_permiso_sct: date | None = None
    vigencia_tarjeta_circulacion: date | None = None
    vigencia_verificacion_fisico_mecanica: date | None = None


class UnidadCreate(UnidadBase):
    pass


class UnidadUpdate(BaseModel):
    transportista_id: int | None = None
    economico: str | None = Field(None, max_length=64)
    placas: str | None = Field(None, max_length=20)
    tipo_propiedad: str | None = Field(None, max_length=32)
    estatus_documental: str | None = Field(None, max_length=32)
    descripcion: str | None = Field(None, max_length=255)
    detalle: str | None = None
    activo: bool | None = None
    vigencia_seguro: date | None = None
    vigencia_permiso_sct: date | None = None
    vigencia_tarjeta_circulacion: date | None = None
    vigencia_verificacion_fisico_mecanica: date | None = None


class UnidadRead(UnidadBase):
    model_config = ConfigDict(from_attributes=True)

    id_unidad: int
    created_at: datetime
    updated_at: datetime


class UnidadListResponse(BaseModel):
    items: list[UnidadRead]
    total: int
    skip: int
    limit: int
