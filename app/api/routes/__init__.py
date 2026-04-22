from fastapi import APIRouter

from . import asignaciones as asignaciones_routes
from . import bajas_danos as bajas_danos_routes
from . import audit_logs as audit_logs_routes
from . import clientes as clientes_routes
from . import cumplimiento as cumplimiento_routes
from . import direccion as direccion_routes
from . import despachos as despachos_routes
from . import facturas as facturas_routes
from . import fletes as fletes_routes
from . import gastos_viaje as gastos_viaje_routes
from . import motor_tarifas as motor_tarifas_routes
from . import ordenes_servicio as ordenes_servicio_routes
from . import operadores as operadores_routes
from . import tarifas_compra_transportista as tarifas_compra_transportista_routes
from . import tarifas_flete as tarifas_flete_routes
from . import transportistas as transportistas_routes
from . import unidades as unidades_routes
from . import usuarios as usuarios_routes
from . import viajes as viajes_routes

api_router = APIRouter()
api_router.include_router(
    audit_logs_routes.router, prefix="/audit-logs", tags=["auditoria"]
)
api_router.include_router(viajes_routes.router, prefix="/viajes", tags=["viajes"])
api_router.include_router(clientes_routes.router, prefix="/clientes", tags=["clientes"])
api_router.include_router(facturas_routes.router, prefix="/facturas", tags=["facturas"])
api_router.include_router(
    transportistas_routes.router, prefix="/transportistas", tags=["transportistas"]
)
api_router.include_router(fletes_routes.router, prefix="/fletes", tags=["fletes"])
api_router.include_router(
    motor_tarifas_routes.router, prefix="/motor-tarifas", tags=["motor-tarifas"]
)
api_router.include_router(gastos_viaje_routes.router, prefix="/gastos-viaje", tags=["gastos-viaje"])
api_router.include_router(
    tarifas_compra_transportista_routes.router,
    prefix="/tarifas-compra-transportista",
    tags=["tarifas-compra-transportista"],
)
api_router.include_router(tarifas_flete_routes.router, prefix="/tarifas-flete", tags=["tarifas-flete"])
api_router.include_router(
    ordenes_servicio_routes.router, prefix="/ordenes-servicio", tags=["ordenes-servicio"]
)
api_router.include_router(operadores_routes.router, prefix="/operadores", tags=["operadores"])
api_router.include_router(unidades_routes.router, prefix="/unidades", tags=["unidades"])
api_router.include_router(asignaciones_routes.router, prefix="/asignaciones", tags=["asignaciones"])
api_router.include_router(despachos_routes.router, prefix="/despachos", tags=["despachos"])
api_router.include_router(
    bajas_danos_routes.router, prefix="/bajas-danos", tags=["bajas-danos"]
)
api_router.include_router(direccion_routes.router, prefix="/direccion", tags=["direccion"])
api_router.include_router(
    cumplimiento_routes.router, prefix="/cumplimiento", tags=["cumplimiento-documental"]
)
api_router.include_router(usuarios_routes.router, prefix="/usuarios", tags=["usuarios"])
