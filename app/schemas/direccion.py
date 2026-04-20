from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class DireccionKpiResumen(BaseModel):
    fletes: int
    ordenes_servicio: int
    asignaciones: int
    despachos: int
    despachos_cerrados: int
    facturas: int
    facturas_emitidas: int
    incidencias_despacho: int


class DireccionEmbudo(BaseModel):
    fletes_a_os_pct: float
    os_a_asignacion_pct: float
    asignacion_a_despacho_pct: float
    despacho_a_factura_pct: float


class DireccionTiemposCiclo(BaseModel):
    flete_a_factura_horas: float | None = None
    orden_a_despacho_horas: float | None = None
    despacho_a_factura_horas: float | None = None


class DireccionSemaforo(BaseModel):
    operacion: str
    sistema: str
    dato: str
    cobranza: str


class DireccionDashboardResponse(BaseModel):
    desde: date
    hasta: date
    resumen: DireccionKpiResumen
    embudo: DireccionEmbudo
    tiempos: DireccionTiemposCiclo
    semaforo: DireccionSemaforo


class DireccionIncidenciaBase(BaseModel):
    titulo: str = Field(min_length=3, max_length=160)
    modulo: str = Field(min_length=2, max_length=64, default="general")
    severidad: str = Field(default="media")
    estatus: str = Field(default="abierta")
    fecha_detectada: date
    detalle: str | None = None
    responsable: str | None = Field(default=None, max_length=120)


class DireccionIncidenciaCreate(DireccionIncidenciaBase):
    pass


class DireccionIncidenciaUpdate(BaseModel):
    titulo: str | None = Field(default=None, min_length=3, max_length=160)
    modulo: str | None = Field(default=None, min_length=2, max_length=64)
    severidad: str | None = None
    estatus: str | None = None
    fecha_detectada: date | None = None
    detalle: str | None = None
    responsable: str | None = Field(default=None, max_length=120)


class DireccionIncidenciaRead(DireccionIncidenciaBase):
    id: int
    resuelta_at: str | None = None
    created_at: str
    updated_at: str


class DireccionAccionBase(BaseModel):
    week_start: date
    week_end: date
    titulo: str = Field(min_length=3, max_length=180)
    descripcion: str | None = None
    owner: str = Field(min_length=2, max_length=120)
    due_date: date | None = None
    impacto: str | None = Field(default=None, max_length=255)
    estatus: str = Field(default="pendiente")


class DireccionAccionCreate(DireccionAccionBase):
    pass


class DireccionAccionUpdate(BaseModel):
    week_start: date | None = None
    week_end: date | None = None
    titulo: str | None = Field(default=None, min_length=3, max_length=180)
    descripcion: str | None = None
    owner: str | None = Field(default=None, min_length=2, max_length=120)
    due_date: date | None = None
    impacto: str | None = Field(default=None, max_length=255)
    estatus: str | None = None


class DireccionAccionRead(DireccionAccionBase):
    id: int
    created_at: str
    updated_at: str
