from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.viaje import EstadoViaje


class ViajeBase(BaseModel):
    codigo_viaje: str = Field(..., max_length=64, description="Código único del viaje.")
    descripcion: str | None = Field(None, max_length=255, description="Descripción breve.")
    origen: str = Field(..., max_length=255, description="Origen del trayecto.")
    destino: str = Field(..., max_length=255, description="Destino del trayecto.")
    fecha_salida: datetime = Field(..., description="Fecha y hora de salida.")
    fecha_llegada_estimada: datetime | None = Field(None, description="Llegada estimada.")
    fecha_llegada_real: datetime | None = Field(None, description="Llegada real.")
    estado: EstadoViaje = Field(default=EstadoViaje.PLANIFICADO, description="Estado del viaje.")
    kilometros_estimados: Decimal | None = Field(
        None,
        ge=0,
        description="Kilómetros estimados (numérico, no negativo; uso en cotizaciones y fórmulas).",
    )
    notas: str | None = Field(None, description="Notas adicionales.")


class ViajeCreate(ViajeBase):
    pass


class ViajeUpdate(BaseModel):
    codigo_viaje: str | None = Field(None, max_length=64)
    descripcion: str | None = Field(None, max_length=255)
    origen: str | None = Field(None, max_length=255)
    destino: str | None = Field(None, max_length=255)
    fecha_salida: datetime | None = None
    fecha_llegada_estimada: datetime | None = None
    fecha_llegada_real: datetime | None = None
    estado: EstadoViaje | None = None
    kilometros_estimados: Decimal | None = Field(None, ge=0)
    notas: str | None = None


class ViajeRead(ViajeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Identificador interno.")
    created_at: datetime = Field(..., description="Fecha de creación del registro.")
    updated_at: datetime = Field(..., description="Fecha de última actualización.")


class ViajeListResponse(BaseModel):
    items: list[ViajeRead] = Field(..., description="Registros de la página actual.")
    total: int = Field(..., description="Total de registros que cumplen el filtro.")
    skip: int = Field(..., description="Offset aplicado.")
    limit: int = Field(..., description="Límite de página aplicado.")
