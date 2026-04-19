from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from app.api.deps import require_api_key
from app.api.routes import api_router
from app.core.config import settings
from app.web import router as web_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API REST del ERP logístico SIFE-MXN.",
    version="0.1.0",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "viajes", "description": "Operaciones CRUD sobre viajes."},
        {"name": "clientes", "description": "Catálogo de clientes (embarcadores / pagadores)."},
        {"name": "facturas", "description": "Facturación administrativa y simulación de cobro al cliente."},
        {"name": "transportistas", "description": "Catálogo de transportistas."},
        {"name": "fletes", "description": "Ejercicios de flete: carga, costo estimado y vínculo a viaje."},
        {"name": "gastos-viaje", "description": "Registro de costos reales asociados a un flete para medir rentabilidad."},
        {"name": "tarifas-compra-transportista", "description": "Catálogo de tarifas de compra negociadas con cada transportista."},
        {"name": "tarifas-flete", "description": "Catálogo de tarifas para cotización y propuesta comercial del flete."},
        {
            "name": "motor-tarifas",
            "description": "Motor de costos/márgenes por tipo de operación (propio, subcontratado, fletero, aliado), híbrido MAX y ranking de asignación.",
        },
        {"name": "ordenes-servicio", "description": "Puente entre cotización, compromiso comercial y ejecución operativa."},
        {"name": "operadores", "description": "Expediente integral de operadores y subrecursos."},
        {"name": "unidades", "description": "Catálogo mínimo de unidades para asignación operativa."},
        {"name": "asignaciones", "description": "Asignación de operador, unidad y viaje."},
        {"name": "despachos", "description": "Seguimiento operativo de salidas, eventos, entregas y cierres."},
        {
            "name": "cumplimiento-documental",
            "description": "Requisitos de documentación (Carta Porte, SCT, operador) y validación previa a salida.",
        },
        {"name": "sistema", "description": "Comprobación de disponibilidad del servicio."},
    ],
)

app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX,
    dependencies=[Depends(require_api_key)],
)
app.include_router(web_router)


@app.get(
    "/health",
    tags=["sistema"],
    summary="Salud del API",
    response_description="Estado del servicio y datos de conexion MySQL leidos de .env (sin credenciales), para verificar que el proceso usa la misma base que se inspecciona en el cliente SQL.",
)
def health() -> dict[str, str | int]:
    return {
        "status": "ok",
        "servicio": settings.PROJECT_NAME,
        "mysql_host": settings.MYSQL_HOST,
        "mysql_port": settings.MYSQL_PORT,
        "mysql_db": settings.MYSQL_DB,
    }
