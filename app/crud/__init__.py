from . import asignacion as asignacion_crud
from . import cliente as cliente_crud
from . import cotizacion_flete as cotizacion_flete_crud
from . import documento_operador as documento_operador_crud
from . import flete as flete_crud
from . import incidente_operador as incidente_operador_crud
from . import orden_servicio as orden_servicio_crud
from . import operador as operador_crud
from . import operador_laboral as operador_laboral_crud
from . import pago_operador as pago_operador_crud
from . import tarifa_flete as tarifa_flete_crud
from . import transportista as transportista_crud
from . import unidad as unidad_crud
from . import viaje as viaje_crud

__all__ = [
    "asignacion_crud",
    "cliente_crud",
    "cotizacion_flete_crud",
    "documento_operador_crud",
    "flete_crud",
    "incidente_operador_crud",
    "orden_servicio_crud",
    "operador_crud",
    "operador_laboral_crud",
    "pago_operador_crud",
    "tarifa_flete_crud",
    "transportista_crud",
    "unidad_crud",
    "viaje_crud",
]
