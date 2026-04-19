from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.tarifa_flete import AmbitoTarifaFlete
from app.schemas.cumplimiento import CatalogoRequisitosResponse, ValidacionSalidaResponse
from app.services.cumplimiento_documental import catalogo_requisitos, validar_salida_por_despacho

router = APIRouter()


@router.get(
    "/requisitos-documentacion",
    response_model=CatalogoRequisitosResponse,
    summary="Catálogo de documentación por ámbito (local, estatal, federal)",
)
def requisitos_documentacion(
    ambito: AmbitoTarifaFlete = Query(
        AmbitoTarifaFlete.FEDERAL,
        description="Ámbito del servicio para listar requisitos orientativos.",
    ),
) -> CatalogoRequisitosResponse:
    return catalogo_requisitos(ambito)


@router.get(
    "/validacion-pre-salida/{id_despacho}",
    response_model=ValidacionSalidaResponse,
    summary="Validación documental previa a salida (checklist)",
)
def validacion_pre_salida(
    id_despacho: int,
    db: Session = Depends(get_db),
    ambito: AmbitoTarifaFlete | None = Query(
        None,
        description="Si se omite, se usa el ámbito del flete o federal por defecto.",
    ),
    fecha_referencia: date | None = Query(
        None,
        description="Fecha para vigencias (por defecto hoy).",
    ),
) -> ValidacionSalidaResponse:
    try:
        return validar_salida_por_despacho(
            db,
            id_despacho=id_despacho,
            ambito_override=ambito,
            fecha_referencia=fecha_referencia,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
