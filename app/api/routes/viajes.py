from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import viaje as crud_viaje
from app.models.viaje import EstadoViaje
from app.schemas.viaje import ViajeCreate, ViajeListResponse, ViajeRead, ViajeUpdate

router = APIRouter()


@router.post(
    "",
    response_model=ViajeRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear viaje",
    description="Registra un viaje. El código debe ser único.",
)
def crear_viaje(
    payload: ViajeCreate,
    db: Session = Depends(get_db),
) -> ViajeRead:
    if crud_viaje.get_by_codigo(db, payload.codigo_viaje):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un viaje con el código '{payload.codigo_viaje}'.",
        )
    return crud_viaje.create(db, payload)


@router.get(
    "",
    response_model=ViajeListResponse,
    summary="Listar viajes",
    description="Lista paginada; orden por fecha de salida descendente. Filtros opcionales.",
)
def listar_viajes(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Offset de registros."),
    limit: int = Query(100, ge=1, le=500, description="Máximo de registros por página."),
    estado: EstadoViaje | None = Query(None, description="Filtrar por estado."),
    origen: str | None = Query(
        None,
        max_length=255,
        description="Coincidencia parcial en origen (sin distinguir mayúsculas).",
    ),
    destino: str | None = Query(
        None,
        max_length=255,
        description="Coincidencia parcial en destino (sin distinguir mayúsculas).",
    ),
) -> ViajeListResponse:
    items, total = crud_viaje.list_viajes(
        db,
        skip=skip,
        limit=limit,
        estado=estado,
        origen_contains=origen,
        destino_contains=destino,
    )
    return ViajeListResponse(
        items=[ViajeRead.model_validate(v) for v in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{viaje_id}",
    response_model=ViajeRead,
    summary="Obtener viaje",
    description="Consulta un viaje por su ID numérico.",
)
def obtener_viaje(
    viaje_id: int,
    db: Session = Depends(get_db),
) -> ViajeRead:
    viaje = crud_viaje.get_by_id(db, viaje_id)
    if not viaje:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Viaje no encontrado.",
        )
    return ViajeRead.model_validate(viaje)


@router.patch(
    "/{viaje_id}",
    response_model=ViajeRead,
    summary="Actualizar viaje",
    description="Actualización parcial: solo se modifican los campos enviados.",
)
def actualizar_viaje(
    viaje_id: int,
    payload: ViajeUpdate,
    db: Session = Depends(get_db),
) -> ViajeRead:
    viaje = crud_viaje.get_by_id(db, viaje_id)
    if not viaje:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Viaje no encontrado.",
        )
    if payload.codigo_viaje is not None and payload.codigo_viaje != viaje.codigo_viaje:
        existente = crud_viaje.get_by_codigo(db, payload.codigo_viaje)
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un viaje con el código '{payload.codigo_viaje}'.",
            )
    return crud_viaje.update(db, viaje, payload)


@router.delete(
    "/{viaje_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar viaje",
    description="Elimina el registro de forma permanente.",
)
def eliminar_viaje(
    viaje_id: int,
    db: Session = Depends(get_db),
) -> None:
    viaje = crud_viaje.get_by_id(db, viaje_id)
    if not viaje:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Viaje no encontrado.",
        )
    crud_viaje.delete(db, viaje)
