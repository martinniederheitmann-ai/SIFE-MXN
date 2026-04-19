"""
Ejemplo completo (1 flete) con campos alineados al catálogo y facturación automática.

Flujo: cliente → transportista → tarifa de venta (ruta) → viaje → flete →
preview opcional → POST /facturas/generar-desde-flete (montos desde flete o tarifa).

La factura se genera por API (subtotal/IVA/total calculados en servidor). No es CFDI SAT.

Requisitos: API (uvicorn), MySQL migrado, .env con API_KEY.

  set SIFE_API_BASE=http://127.0.0.1:8000
  set SIFE_API_KEY=cambia-esta-api-key
  python scripts/demo_flujo_factura_automatico.py
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from typing import Any


def _env(name: str, default: str) -> str:
    return os.environ.get(name, default).strip()


def _post_json(url: str, payload: dict[str, Any], api_key: str) -> dict[str, Any]:
    data = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
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


def _get_json(url: str, api_key: str) -> dict[str, Any]:
    req = urllib.request.Request(url, method="GET")
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
    run_id = datetime.now(timezone.utc).strftime("auto%Y%m%d%H%M%S")

    # Debe coincidir exactamente (misma cadena) entre tarifa de venta, viaje y cotización del flete.
    origen = "Parque industrial FINSA, El Marqués, Querétaro"
    destino = "Ciudad Apodaca, Nuevo León (bodega cliente)"
    km = "820.0"
    peso_kg = "18500.00"
    tipo_unidad = "tractocamion"
    tipo_carga = "general"
    tipo_operacion = "subcontratado"

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
            "email": f"logistica.{run_id}@cibsa-demo.mx",
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
            "notas": "Flota tractocamión (demo automático).",
            "activo": True,
        },
        api_key,
    )
    transportista_id = int(transportista["id"])
    print(f"Transportista id={transportista_id}")

    # Tarifa de venta alineada al trayecto (permite recálculo en preview/factura).
    tarifa = _post_json(
        f"{base}/api/v1/tarifas-flete",
        {
            "nombre_tarifa": f"Ruta QRO-Apodaca demo auto {run_id}",
            "tipo_operacion": tipo_operacion,
            "ambito": "federal",
            "modalidad_cobro": "mixta",
            "origen": origen,
            "destino": destino,
            "tipo_unidad": tipo_unidad,
            "tipo_carga": None,
            "tarifa_base": "12000.00",
            "tarifa_km": "34.50",
            "tarifa_kg": "0",
            "tarifa_tonelada": "0",
            "recargo_minimo": "0",
            "porcentaje_utilidad": "0.20",
            "porcentaje_riesgo": "0",
            "moneda": "MXN",
            "activo": True,
        },
        api_key,
    )
    print(f"Tarifa venta id={tarifa['id']} ({tarifa.get('nombre_tarifa')})")

    viaje = _post_json(
        f"{base}/api/v1/viajes",
        {
            "codigo_viaje": f"VJ-AUTO-QRO-NL-{run_id}",
            "descripcion": "Traslado autopartes Querétaro - Apodaca (demo factura automática)",
            "origen": origen,
            "destino": destino,
            "fecha_salida": "2026-04-07T06:30:00",
            "fecha_llegada_estimada": "2026-04-07T22:00:00",
            "estado": "planificado",
            "kilometros_estimados": km,
            "notas": "demo_flujo_factura_automatico.py",
        },
        api_key,
    )
    viaje_id = int(viaje["id"])
    print(f"Viaje id={viaje_id}")

    flete = _post_json(
        f"{base}/api/v1/fletes",
        {
            "codigo_flete": f"FLT-AUTO-QRO-NL-{run_id}",
            "cliente_id": cliente_id,
            "transportista_id": transportista_id,
            "viaje_id": viaje_id,
            "descripcion_carga": "Autopartes; 22 tarimas; embalaje stretch film.",
            "peso_kg": peso_kg,
            "volumen_m3": "62.5",
            "numero_bultos": 22,
            "distancia_km": km,
            "tipo_operacion": tipo_operacion,
            "tipo_unidad": tipo_unidad,
            "tipo_carga": tipo_carga,
            "precio_venta": "48348.00",
            "monto_estimado": "48348.00",
            "costo_transporte_estimado": "35200.00",
            "costo_transporte_real": "34850.00",
            "metodo_calculo": "tarifa",
            "moneda": "MXN",
            "estado": "entregado",
            "notas": "Precio placeholder; la factura usará tarifa recalculada si aplica.",
        },
        api_key,
    )
    flete_id = int(flete["id"])
    print(f"Flete id={flete_id} codigo={flete.get('codigo_flete')}")

    q = urllib.parse.urlencode({"iva_pct": "0.16", "retencion_monto": "0"})
    preview = _get_json(
        f"{base}/api/v1/facturas/preview-desde-flete/{flete_id}?{q}",
        api_key,
    )
    print(
        "\n--- Preview factura ---\n"
        f"  Subtotal flete: {preview.get('subtotal_desde_flete')}\n"
        f"  Subtotal tarifa recalculada: {preview.get('subtotal_desde_tarifa_recalculado')}\n"
        f"  Total (precio flete + IVA): {preview.get('total')}\n"
        f"  Concepto sugerido: {preview.get('concepto_sugerido')[:80]}...\n"
    )

    hoy = date.today()
    vencimiento = hoy + timedelta(days=30)

    factura = _post_json(
        f"{base}/api/v1/facturas/generar-desde-flete",
        {
            "flete_id": flete_id,
            "fecha_emision": hoy.isoformat(),
            "fecha_vencimiento": vencimiento.isoformat(),
            "serie": "A",
            "iva_pct": "0.16",
            "retencion_monto": "0",
            "usar_precio_tarifa_recalculado": True,
            "forma_pago": "03 - Transferencia electrónica de fondos",
            "metodo_pago": "PPD",
            "uso_cfdi": "G03",
            "estatus": "emitida",
            "timbrada": False,
            "referencia": f"OC-AUTO / {run_id}",
            "observaciones": "Generada en automático por demo_flujo_factura_automatico.py (registro interno).",
        },
        api_key,
    )

    print(
        "--- Factura emitida ---\n"
        f"  id={factura['id']} folio={factura.get('folio')}\n"
        f"  subtotal={factura.get('subtotal')} iva={factura.get('iva_monto')} "
        f"total={factura.get('total')}\n"
        f"  concepto: {str(factura.get('concepto'))[:100]}...\n"
    )
    print(f"Panel: {base}/ui  |  API: GET {base}/api/v1/facturas/{factura['id']}")


if __name__ == "__main__":
    main()
