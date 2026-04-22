from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles

from app.api.rbac import require_rbac
from app.api.routes import api_router
from app.api.routes import auth as auth_routes
from app.api.routes import internal_cron as internal_cron_routes
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
        {"name": "bajas-danos", "description": "Registro de bajas operativas y daños a activo o carga."},
        {
            "name": "cumplimiento-documental",
            "description": "Requisitos de documentación (Carta Porte, SCT, operador) y validación previa a salida.",
        },
        {"name": "auth", "description": "Login JWT, perfil y cambio de contraseña propia (Bearer)."},
        {"name": "usuarios", "description": "Alta y mantenimiento de usuarios y roles (JWT admin o direccion; API key sin filtro de rol)."},
        {
            "name": "auditoria",
            "description": "Consulta de pista de auditoría (JWT admin o dirección; API key denegada).",
        },
        {"name": "sistema", "description": "Comprobación de disponibilidad del servicio."},
    ],
)

app.include_router(
    auth_routes.router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["auth"],
)
app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX,
    dependencies=[Depends(require_rbac)],
)
app.include_router(
    internal_cron_routes.router,
    prefix=f"{settings.API_V1_PREFIX}/internal",
    tags=["sistema"],
)
_static_dir = Path(__file__).resolve().parent / "static"
if _static_dir.is_dir():
    app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")
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


def custom_openapi() -> dict:
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema.setdefault("components", {}).setdefault("securitySchemes", {})
    openapi_schema["components"]["securitySchemes"]["ApiKeyAuth"] = {
        "type": "apiKey",
        "in": "header",
        "name": settings.API_KEY_HEADER,
    }
    openapi_schema["components"]["securitySchemes"]["BearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }
    openapi_schema["security"] = [{"ApiKeyAuth": []}, {"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
