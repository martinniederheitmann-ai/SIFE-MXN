from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field

from app.models.tarifa_flete import AmbitoTarifaFlete


class EstadoChequeo(str, Enum):
    CUMPLE = "cumple"
    ADVERTENCIA = "advertencia"
    NO_CUMPLE = "no_cumple"


class ChequeoCumplimiento(BaseModel):
    codigo: str
    titulo: str
    detalle: str
    estado: EstadoChequeo
    referencia_normativa: str | None = Field(
        None,
        description="Referencia orientativa (SAT / SCT / normativa aplicable en sentido amplio).",
    )


class ModuloRequisitos(BaseModel):
    id: str
    titulo: str
    descripcion: str | None = None
    documentos: list[str]


class CatalogoRequisitosResponse(BaseModel):
    ambito: AmbitoTarifaFlete
    nota_legal: str
    modulos: list[ModuloRequisitos]


class ValidacionSalidaResponse(BaseModel):
    fecha_referencia: date
    ambito: AmbitoTarifaFlete
    id_despacho: int | None = None
    id_asignacion: int | None = None
    id_flete: int | None = None
    autorizado: bool
    bloqueos: list[str] = Field(default_factory=list)
    advertencias: list[str] = Field(default_factory=list)
    chequeos: list[ChequeoCumplimiento]
    insights: list[str] = Field(
        default_factory=list,
        description="Resumen heurístico; no sustituye asesoría fiscal ni legal.",
    )
