"""
Ejecuta en cadena: cliente → transportista → viaje → flete → factura administrativa.

Requisitos: API en marcha (uvicorn), MySQL migrado, .env con misma API_KEY.

  set SIFE_API_BASE=http://127.0.0.1:8000
  set SIFE_API_KEY=tu-api-key
  python scripts/demo_flujo_factura.py

La factura es solo registro interno (no timbrado SAT).
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any


def _env(name: str, default: str) -> str:
    return os.environ.get(name, default).strip()


def _post_json(url: str, payload: dict[str, Any], api_key: str) -> dict[str, Any]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    req.add_header("X-API-Key", api_key)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {e.code} {e.reason}\n{err_body}") from e


def main() -> None:
    base = _env("SIFE_API_BASE", "http://127.0.0.1:8000").rstrip("/")
    api_key = _env("SIFE_API_KEY", "cambia-esta-api-key")
    run_id = datetime.now(timezone.utc).strftime("demo%Y%m%d%H%M%S")

    print(f"Base: {base}  run_id={run_id}\n")

    cliente = _post_json(
        f"{base}/api/v1/clientes",
        {
            "razon_social": "COMPONENTES INDUSTRIALES DEL BAJIO SA DE CV",
            "nombre_comercial": "CIBSA Autopartes",
            "rfc": "CIN040316JH4",
            "tipo_cliente": "embarcador",
            "sector": "Automotriz - Tier 2",
            "origen_prospecto": "referido",
            "email": f"compras.logistica.{run_id}@cibsa-demo.mx",
            "telefono": "4422120045",
            "direccion": "Av. Constituyentes Oriente 145, Col. Centro, Santiago de Querétaro, Qro., CP 76000",
            "domicilio_fiscal": "Av. Constituyentes Oriente 145, Col. Centro, Santiago de Querétaro, Qro., CP 76000",
            "sitio_web": "https://www.cibsa-demo.mx",
            "notas_operativas": "Cita de carga L-V 08:00-16:00.",
            "notas_comerciales": "Pago 30 días; remisión firmada en destino.",
            "activo": True,
        },
        api_key,
    )
    cliente_id = int(cliente["id"])
    print(f"Cliente id={cliente_id}")

    transportista = _post_json(
        f"{base}/api/v1/transportistas",
        {
            "nombre": "TRANSPORTES FRONTERA NORTE SA DE CV",
            "nombre_razon_social": "TRANSPORTES FRONTERA NORTE SA DE CV",
            "tipo_transportista": "subcontratado",
            "tipo_persona": "moral",
            "nombre_comercial": "TFN Cargo",
            "rfc": "TFN980512XYZ",
            "regimen_fiscal": "601 - General de Ley Personas Morales",
            "estatus": "activo",
            "contacto": "Mesa de tráfico nacional",
            "telefono": "8183309900",
            "email": f"trafico.{run_id}@tfn-cargo-demo.mx",
            "direccion_fiscal": "Av. Lincoln 6400, Valle Verde 1er Sector, San Nicolás de los Garza, NL, CP 66460",
            "direccion_operativa": "Mismo domicilio fiscal",
            "ciudad": "San Nicolás de los Garza",
            "estado": "Nuevo León",
            "pais": "México",
            "codigo_postal": "66460",
            "nivel_confianza": "alto",
            "prioridad_asignacion": 10,
            "notas": "Flota propia tractocamión.",
            "activo": True,
        },
        api_key,
    )
    transportista_id = int(transportista["id"])
    print(f"Transportista id={transportista_id}")

    viaje = _post_json(
        f"{base}/api/v1/viajes",
        {
            "codigo_viaje": f"VJ-2026-QRO-NL-{run_id}",
            "descripcion": "Traslado autopartes Querétaro - Monterrey (Apodaca)",
            "origen": "Parque industrial FINSA, El Marqués, Querétaro",
            "destino": "Ciudad Apodaca, Nuevo León (bodega cliente)",
            "fecha_salida": "2026-04-07T06:30:00",
            "fecha_llegada_estimada": "2026-04-07T22:00:00",
            "estado": "planificado",
            "kilometros_estimados": "820.0",
            "notas": "Demo demo_flujo_factura.py",
        },
        api_key,
    )
    viaje_id = int(viaje["id"])
    print(f"Viaje id={viaje_id}")

    flete = _post_json(
        f"{base}/api/v1/fletes",
        {
            "codigo_flete": f"FLT-2026-QRO-NL-{run_id}",
            "cliente_id": cliente_id,
            "transportista_id": transportista_id,
            "viaje_id": viaje_id,
            "descripcion_carga": "Autopartes; 22 tarimas; embalaje stretch film.",
            "peso_kg": "18500.00",
            "volumen_m3": "62.5",
            "numero_bultos": 22,
            "distancia_km": "820.0",
            "tipo_operacion": "subcontratado",
            "tipo_unidad": "tractocamion",
            "tipo_carga": "general",
            "monto_estimado": "48500.00",
            "precio_venta": "48500.00",
            "costo_transporte_estimado": "35200.00",
            "costo_transporte_real": "34850.00",
            "metodo_calculo": "manual",
            "moneda": "MXN",
            "estado": "entregado",
            "notas": "Entrega conforme (script demo).",
        },
        api_key,
    )
    flete_id = int(flete["id"])
    print(f"Flete id={flete_id} codigo={flete.get('codigo_flete')}")

    factura = _post_json(
        f"{base}/api/v1/facturas",
        {
            "serie": "A",
            "cliente_id": cliente_id,
            "flete_id": flete_id,
            "orden_servicio_id": None,
            "fecha_emision": "2026-04-08",
            "fecha_vencimiento": "2026-05-08",
            "concepto": "Flete terrestre tractocamión: Querétaro a Apodaca, NL (demo script).",
            "referencia": f"OC-demo / {run_id}",
            "moneda": "MXN",
            "subtotal": "48500.00",
            "iva_pct": "0.16",
            "iva_monto": "7760.00",
            "retencion_monto": "0.00",
            "total": "56260.00",
            "saldo_pendiente": "56260.00",
            "forma_pago": "03 - Transferencia electrónica de fondos",
            "metodo_pago": "PPD",
            "uso_cfdi": "G03",
            "estatus": "emitida",
            "timbrada": False,
            "observaciones": "Registro interno SIFE-MXN; no es CFDI del SAT.",
        },
        api_key,
    )
    print(
        f"Factura id={factura['id']} folio={factura.get('folio')} "
        f"total={factura.get('total')} timbrada={factura.get('timbrada')}"
    )
    print("\nListo. Revisa en el panel web o GET /api/v1/facturas/{id}.")


if __name__ == "__main__":
    main()
