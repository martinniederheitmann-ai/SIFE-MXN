from __future__ import annotations

import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from sqlalchemy import select

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.database import SessionLocal
from app.models.cliente import Cliente, ClienteCondicionComercial, ClienteTarifaEspecial, TipoCliente
from app.models.tarifa_flete import TarifaFlete


CLIENTES = [
    {
        "razon_social": "Abarrotes del Golfo SA de CV",
        "nombre_comercial": "Abarrotes del Golfo",
        "rfc": "AGO260101AB1",
        "tipo_cliente": TipoCliente.EMBARCADOR,
        "sector": "Consumo",
        "origen_prospecto": "Ventas directas",
        "email": "trafico@abarrotesgolfo.mx",
        "telefono": "2291002000",
        "direccion": "Veracruz, Veracruz",
        "domicilio_fiscal": "Veracruz, Veracruz",
        "notas_comerciales": "Cliente frecuente con volumen semanal.",
        "activo": True,
        "condicion_comercial": {
            "dias_credito": 15,
            "limite_credito": Decimal("150000.00"),
            "moneda_preferida": "MXN",
            "forma_pago": "transferencia",
            "uso_cfdi": "G03",
            "requiere_oc": False,
            "requiere_cita": True,
            "bloqueado_credito": False,
            "observaciones_credito": "Aplica tarifa preferencial por volumen.",
        },
    },
    {
        "razon_social": "FrioNorte Logistica SA de CV",
        "nombre_comercial": "FrioNorte",
        "rfc": "FNL260101CD2",
        "tipo_cliente": TipoCliente.CORPORATIVO,
        "sector": "Alimentos",
        "origen_prospecto": "Referencia",
        "email": "compras@frionorte.mx",
        "telefono": "8182003000",
        "direccion": "Monterrey, Nuevo Leon",
        "domicilio_fiscal": "Monterrey, Nuevo Leon",
        "notas_comerciales": "Cliente refrigerado con servicio prioritario.",
        "activo": True,
        "condicion_comercial": {
            "dias_credito": 7,
            "limite_credito": Decimal("250000.00"),
            "moneda_preferida": "MXN",
            "forma_pago": "transferencia",
            "uso_cfdi": "G03",
            "requiere_oc": True,
            "requiere_cita": True,
            "bloqueado_credito": False,
            "observaciones_credito": "Precio fijo para ruta prioritaria.",
        },
    },
]


ACUERDOS = [
    {
        "cliente_rfc": "AGO260101AB1",
        "tarifa_nombre": "Federal tracto general por km",
        "nombre_acuerdo": "Descuento por volumen CDMX",
        "descuento_pct": Decimal("0.08"),
        "incremento_pct": Decimal("0"),
        "recargo_fijo": Decimal("0"),
        "prioridad": 10,
        "activo": True,
        "vigencia_inicio": datetime(2026, 1, 1, tzinfo=timezone.utc),
        "vigencia_fin": None,
        "observaciones": "8% por contrato mensual y frecuencia alta.",
    },
    {
        "cliente_rfc": "FNL260101CD2",
        "tarifa_nombre": "Federal tracto refrigerada por km",
        "nombre_acuerdo": "Precio fijo refrigerado Monterrey",
        "precio_fijo": Decimal("56500.00"),
        "descuento_pct": Decimal("0"),
        "incremento_pct": Decimal("0"),
        "recargo_fijo": Decimal("1500.00"),
        "prioridad": 5,
        "activo": True,
        "vigencia_inicio": datetime(2026, 1, 1, tzinfo=timezone.utc),
        "vigencia_fin": None,
        "observaciones": "Incluye maniobra y ventana de cita.",
    },
]


def _upsert_clientes(db) -> tuple[int, int]:
    created = 0
    updated = 0
    for payload in CLIENTES:
        cond = payload.pop("condicion_comercial")
        stmt = select(Cliente).where(Cliente.rfc == payload["rfc"])
        row = db.execute(stmt).scalar_one_or_none()
        if row is None:
            row = Cliente(**payload)
            db.add(row)
            db.flush()
            created += 1
        else:
            for key, value in payload.items():
                setattr(row, key, value)
            db.add(row)
            updated += 1

        if row.condicion_comercial is None:
            row.condicion_comercial = ClienteCondicionComercial(**cond)
        else:
            for key, value in cond.items():
                setattr(row.condicion_comercial, key, value)
        db.add(row)
    db.flush()
    return created, updated


def _upsert_acuerdos(db) -> tuple[int, int]:
    created = 0
    updated = 0
    for payload in ACUERDOS:
        cliente = db.execute(select(Cliente).where(Cliente.rfc == payload["cliente_rfc"])).scalar_one()
        tarifa = db.execute(
            select(TarifaFlete).where(TarifaFlete.nombre_tarifa == payload["tarifa_nombre"])
        ).scalar_one()
        stmt = select(ClienteTarifaEspecial).where(
            ClienteTarifaEspecial.cliente_id == cliente.id,
            ClienteTarifaEspecial.tarifa_flete_id == tarifa.id,
            ClienteTarifaEspecial.nombre_acuerdo == payload["nombre_acuerdo"],
        )
        row = db.execute(stmt).scalar_one_or_none()
        data = {
            "cliente_id": cliente.id,
            "tarifa_flete_id": tarifa.id,
            "nombre_acuerdo": payload["nombre_acuerdo"],
            "precio_fijo": payload.get("precio_fijo"),
            "descuento_pct": payload.get("descuento_pct", Decimal("0")),
            "incremento_pct": payload.get("incremento_pct", Decimal("0")),
            "recargo_fijo": payload.get("recargo_fijo", Decimal("0")),
            "prioridad": payload.get("prioridad", 100),
            "activo": payload.get("activo", True),
            "vigencia_inicio": payload.get("vigencia_inicio"),
            "vigencia_fin": payload.get("vigencia_fin"),
            "observaciones": payload.get("observaciones"),
        }
        if row is None:
            db.add(ClienteTarifaEspecial(**data))
            created += 1
        else:
            for key, value in data.items():
                setattr(row, key, value)
            db.add(row)
            updated += 1
    db.flush()
    return created, updated


def run() -> None:
    db = SessionLocal()
    try:
        c_created, c_updated = _upsert_clientes(db)
        a_created, a_updated = _upsert_acuerdos(db)
        db.commit()
        print(
            "Clientes procesados. "
            f"Nuevos: {c_created}. Actualizados: {c_updated}. "
            f"Acuerdos nuevos: {a_created}. Acuerdos actualizados: {a_updated}."
        )
    finally:
        db.close()


if __name__ == "__main__":
    run()
