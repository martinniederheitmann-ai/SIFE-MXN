from __future__ import annotations

import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

from sqlalchemy import and_, select

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.database import SessionLocal
from app.models.tarifa_flete import AmbitoTarifaFlete, ModalidadCobroTarifa, TarifaFlete


SEED_TARIFAS = [
    {
        "nombre_tarifa": "Local torton general por viaje",
        "ambito": AmbitoTarifaFlete.LOCAL,
        "modalidad_cobro": ModalidadCobroTarifa.POR_VIAJE,
        "origen": "Veracruz",
        "destino": "Veracruz",
        "tipo_unidad": "torton",
        "tipo_carga": "general",
        "tarifa_base": Decimal("2800.00"),
        "tarifa_km": Decimal("0"),
        "tarifa_kg": Decimal("0"),
        "tarifa_tonelada": Decimal("0"),
        "tarifa_hora": Decimal("0"),
        "tarifa_dia": Decimal("0"),
        "recargo_minimo": Decimal("300.00"),
        "porcentaje_utilidad": Decimal("0.22"),
        "porcentaje_riesgo": Decimal("0.03"),
        "porcentaje_urgencia": Decimal("0.20"),
        "porcentaje_retorno_vacio": Decimal("0.00"),
        "porcentaje_carga_especial": Decimal("0.15"),
        "moneda": "MXN",
        "activo": True,
        "vigencia_inicio": date(2026, 1, 1),
        "vigencia_fin": None,
    },
    {
        "nombre_tarifa": "Estatal torton general por km",
        "ambito": AmbitoTarifaFlete.ESTATAL,
        "modalidad_cobro": ModalidadCobroTarifa.POR_KM,
        "origen": "Veracruz",
        "destino": "Xalapa",
        "tipo_unidad": "torton",
        "tipo_carga": "general",
        "tarifa_base": Decimal("1200.00"),
        "tarifa_km": Decimal("19.5000"),
        "tarifa_kg": Decimal("0"),
        "tarifa_tonelada": Decimal("0"),
        "tarifa_hora": Decimal("0"),
        "tarifa_dia": Decimal("0"),
        "recargo_minimo": Decimal("250.00"),
        "porcentaje_utilidad": Decimal("0.24"),
        "porcentaje_riesgo": Decimal("0.04"),
        "porcentaje_urgencia": Decimal("0.20"),
        "porcentaje_retorno_vacio": Decimal("0.12"),
        "porcentaje_carga_especial": Decimal("0.18"),
        "moneda": "MXN",
        "activo": True,
        "vigencia_inicio": date(2026, 1, 1),
        "vigencia_fin": None,
    },
    {
        "nombre_tarifa": "Federal tracto general por km",
        "ambito": AmbitoTarifaFlete.FEDERAL,
        "modalidad_cobro": ModalidadCobroTarifa.POR_KM,
        "origen": "Veracruz",
        "destino": "Ciudad de Mexico",
        "tipo_unidad": "tractocamion",
        "tipo_carga": "general",
        "tarifa_base": Decimal("2500.00"),
        "tarifa_km": Decimal("31.0000"),
        "tarifa_kg": Decimal("0"),
        "tarifa_tonelada": Decimal("0"),
        "tarifa_hora": Decimal("0"),
        "tarifa_dia": Decimal("0"),
        "recargo_minimo": Decimal("650.00"),
        "porcentaje_utilidad": Decimal("0.28"),
        "porcentaje_riesgo": Decimal("0.06"),
        "porcentaje_urgencia": Decimal("0.25"),
        "porcentaje_retorno_vacio": Decimal("0.15"),
        "porcentaje_carga_especial": Decimal("0.22"),
        "moneda": "MXN",
        "activo": True,
        "vigencia_inicio": date(2026, 1, 1),
        "vigencia_fin": None,
    },
    {
        "nombre_tarifa": "Federal tracto refrigerada por km",
        "ambito": AmbitoTarifaFlete.FEDERAL,
        "modalidad_cobro": ModalidadCobroTarifa.POR_KM,
        "origen": "Veracruz",
        "destino": "Monterrey",
        "tipo_unidad": "tractocamion",
        "tipo_carga": "refrigerada",
        "tarifa_base": Decimal("3500.00"),
        "tarifa_km": Decimal("36.5000"),
        "tarifa_kg": Decimal("0"),
        "tarifa_tonelada": Decimal("0"),
        "tarifa_hora": Decimal("0"),
        "tarifa_dia": Decimal("0"),
        "recargo_minimo": Decimal("900.00"),
        "porcentaje_utilidad": Decimal("0.30"),
        "porcentaje_riesgo": Decimal("0.08"),
        "porcentaje_urgencia": Decimal("0.25"),
        "porcentaje_retorno_vacio": Decimal("0.18"),
        "porcentaje_carga_especial": Decimal("0.30"),
        "moneda": "MXN",
        "activo": True,
        "vigencia_inicio": date(2026, 1, 1),
        "vigencia_fin": None,
    },
    {
        "nombre_tarifa": "Federal material pesado por tonelada",
        "ambito": AmbitoTarifaFlete.FEDERAL,
        "modalidad_cobro": ModalidadCobroTarifa.POR_TONELADA,
        "origen": "Veracruz",
        "destino": "Guadalajara",
        "tipo_unidad": "tractocamion",
        "tipo_carga": "general",
        "tarifa_base": Decimal("1800.00"),
        "tarifa_km": Decimal("0"),
        "tarifa_kg": Decimal("0"),
        "tarifa_tonelada": Decimal("1100.0000"),
        "tarifa_hora": Decimal("0"),
        "tarifa_dia": Decimal("0"),
        "recargo_minimo": Decimal("700.00"),
        "porcentaje_utilidad": Decimal("0.26"),
        "porcentaje_riesgo": Decimal("0.07"),
        "porcentaje_urgencia": Decimal("0.20"),
        "porcentaje_retorno_vacio": Decimal("0.14"),
        "porcentaje_carga_especial": Decimal("0.18"),
        "moneda": "MXN",
        "activo": True,
        "vigencia_inicio": date(2026, 1, 1),
        "vigencia_fin": None,
    },
]


def upsert_tarifas() -> tuple[int, int]:
    created = 0
    updated = 0
    db = SessionLocal()
    try:
        for payload in SEED_TARIFAS:
            stmt = select(TarifaFlete).where(
                and_(
                    TarifaFlete.nombre_tarifa == payload["nombre_tarifa"],
                    TarifaFlete.ambito == payload["ambito"],
                    TarifaFlete.origen == payload["origen"],
                    TarifaFlete.destino == payload["destino"],
                    TarifaFlete.tipo_unidad == payload["tipo_unidad"],
                    TarifaFlete.tipo_carga == payload["tipo_carga"],
                )
            )
            existing = db.execute(stmt).scalar_one_or_none()
            if existing is None:
                db.add(TarifaFlete(**payload))
                created += 1
                continue

            for key, value in payload.items():
                setattr(existing, key, value)
            db.add(existing)
            updated += 1

        db.commit()
        return created, updated
    finally:
        db.close()


if __name__ == "__main__":
    created, updated = upsert_tarifas()
    print(f"Tarifas procesadas. Nuevas: {created}. Actualizadas: {updated}.")
