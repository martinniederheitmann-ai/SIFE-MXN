"""
Demo end-to-end: carga general federal Veracruz, Ver. -> Villahermosa, Tab.
Operación propia, tarifa mixta (base + km). Crea cliente, transportista, tarifas,
cotización, flete, orden de servicio, operador, unidad, asignación, despacho,
eventos, gastos y factura administrativa.

Uso (desde la raíz del proyecto, con venv activado):
    python scripts/seed_demo_veracruz_villahermosa.py
"""

from __future__ import annotations

import sys
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.database import SessionLocal
from app.crud import asignacion as crud_asignacion
from app.crud import cliente as crud_cliente
from app.crud import cotizacion_flete as crud_cotizacion_flete
from app.crud import despacho as crud_despacho
from app.crud import factura as crud_factura
from app.crud import flete as crud_flete
import app.crud.gasto_viaje as crud_gasto_viaje
from app.crud import orden_servicio as crud_orden_servicio
from app.crud import operador as crud_operador
from app.crud import tarifa_compra_transportista as crud_tarifa_compra
from app.crud import tarifa_flete as crud_tarifa_flete
from app.crud import transportista as crud_transportista
from app.crud import unidad as crud_unidad
from app.crud import viaje as crud_viaje
from app.models.cotizacion_flete import EstatusCotizacionFlete
from app.models.factura import EstatusFactura
from app.models.flete import EstadoFlete, MetodoCalculoFlete
from app.models.orden_servicio import EstatusOrdenServicio
from app.models.tarifa_flete import AmbitoTarifaFlete, ModalidadCobroTarifa
from app.models.transportista import (
    EstatusDocumentoTransportista,
    TipoDocumentoTransportista,
    TipoPersonaTransportista,
    TipoTransportista,
)
from app.models.despacho import TipoEventoDespacho
from app.models.cliente import TipoCliente
from app.models.operador import EstadoCivil, TipoSangre
from app.schemas.cliente import (
    ClienteCondicionComercialUpsert,
    ClienteContactoCreate,
    ClienteCreate,
    ClienteDomicilioCreate,
)
from app.schemas.cotizacion_flete import CotizacionFleteConvertir
from app.schemas.despacho import (
    DespachoCerrar,
    DespachoCreate,
    DespachoEventoCreate,
    DespachoRegistrarEntrega,
    DespachoRegistrarSalida,
)
from app.schemas.flete import FleteCotizacionRequest, FleteCreate, FleteUpdate
from app.schemas.gasto_viaje import GastoViajeCreate
from app.schemas.operador import OperadorCreate
from app.schemas.tarifa_compra_transportista import TarifaCompraTransportistaCreate
from app.schemas.tarifa_flete import TarifaFleteCreate
from app.schemas.transportista import (
    TransportistaContactoCreate,
    TransportistaCreate,
    TransportistaDocumentoCreate,
)
from app.schemas.unidad import UnidadCreate
from app.schemas.viaje import ViajeCreate
from app.models.viaje import EstadoViaje
from app.schemas.asignacion import AsignacionCreate
from app.services.cotizacion_flete import cotizar_venta_con_tarifa
from app.services.facturacion_flete import construir_factura_create

MX = timezone(timedelta(hours=-6))

ORIGEN_TARIFA = "Veracruz"
DESTINO_TARIFA = "Villahermosa"
DISTANCIA_KM = Decimal("518")
PESO_KG = Decimal("15000")


def _cotizacion_row_dict(
    request: FleteCotizacionRequest,
    result,
    folio: str,
    observaciones: str | None,
) -> dict:
    return {
        "folio": folio,
        "cliente_id": result.cliente_id,
        "tarifa_flete_id": result.tarifa_id,
        "tarifa_especial_cliente_id": result.tarifa_especial_cliente_id,
        "ambito": result.ambito,
        "modalidad_cobro": result.modalidad_cobro,
        "origen": request.origen,
        "destino": request.destino,
        "tipo_unidad": request.tipo_unidad,
        "tipo_carga": request.tipo_carga,
        "distancia_km": request.distancia_km,
        "peso_kg": request.peso_kg,
        "horas_servicio": request.horas_servicio,
        "dias_servicio": request.dias_servicio,
        "urgencia": request.urgencia,
        "retorno_vacio": request.retorno_vacio,
        "riesgo_pct_extra": request.riesgo_pct_extra,
        "recargos": request.recargos,
        "costo_base_estimado": result.costo_base_estimado,
        "subtotal_estimado": result.subtotal_estimado,
        "utilidad_aplicada": result.utilidad_aplicada,
        "riesgo_aplicado": result.riesgo_aplicado,
        "urgencia_aplicada": result.urgencia_aplicada,
        "retorno_vacio_aplicado": result.retorno_vacio_aplicado,
        "carga_especial_aplicada": result.carga_especial_aplicada,
        "descuento_cliente_aplicado": result.descuento_cliente_aplicado,
        "incremento_cliente_aplicado": result.incremento_cliente_aplicado,
        "recargo_fijo_cliente_aplicado": result.recargo_fijo_cliente_aplicado,
        "precio_venta_sugerido": result.precio_venta_sugerido,
        "moneda": result.moneda,
        "detalle_calculo": result.detalle_calculo,
        "estatus": EstatusCotizacionFlete.BORRADOR,
        "observaciones": observaciones,
    }


def run() -> None:
    db = SessionLocal()
    try:
        # --- Cliente ---
        cli = crud_cliente.create(
            db,
            ClienteCreate(
                razon_social="Distribuidora del Golfo SA de CV",
                nombre_comercial="DistriGolfo",
                rfc="DGO850312ABC",
                tipo_cliente=TipoCliente.EMBARCADOR,
                sector="Carga general",
                email="logistica@distrigolfo.demo",
                telefono="2295550100",
                direccion="Blvd. Manuel Avila Camacho 2100, Veracruz, Ver.",
                activo=True,
            ),
        )
        crud_cliente.create_contacto(
            db,
            cli.id,
            ClienteContactoCreate(
                nombre="María Elena Fuentes",
                area="Tráfico",
                puesto="Jefa de embarques",
                telefono="2295550101",
                email="mfuentes@distrigolfo.demo",
                principal=True,
                activo=True,
            ),
        )
        crud_cliente.create_domicilio(
            db,
            cli.id,
            ClienteDomicilioCreate(
                tipo_domicilio="cedis",
                nombre_sede="CEDIS Veracruz Norte",
                direccion_completa="Carretera Xalapa-Veracruz Km 4.5, Col. Industrial",
                municipio="Veracruz",
                estado="Veracruz",
                codigo_postal="91919",
                horario_carga="07:00-18:00",
                horario_descarga="08:00-17:00",
                instrucciones_acceso="Cita 24 h antes; acceso por andén B.",
                activo=True,
            ),
        )
        crud_cliente.upsert_condicion_comercial(
            db,
            cli.id,
            ClienteCondicionComercialUpsert(
                dias_credito=30,
                limite_credito=Decimal("750000.00"),
                moneda_preferida="MXN",
                forma_pago="transferencia",
                uso_cfdi="G03",
                requiere_oc=False,
                requiere_cita=True,
                bloqueado_credito=False,
            ),
        )

        # --- Transportista propio ---
        transp = crud_transportista.create(
            db,
            TransportistaCreate(
                nombre="Transportes Propios Golfo SA de CV",
                nombre_comercial="TPG Flota",
                rfc="TPG900101XYZ",
                tipo_transportista=TipoTransportista.PROPIO,
                tipo_persona=TipoPersonaTransportista.MORAL,
                telefono="2295550200",
                email="operaciones@tpgflota.demo",
                direccion_fiscal="Zona portuaria Lote 12, Veracruz, Ver.",
                ciudad="Veracruz",
                estado="Veracruz",
                pais="México",
                codigo_postal="91700",
                estatus="activo",
                activo=True,
            ),
        )
        crud_transportista.create_contacto(
            db,
            transp.id,
            TransportistaContactoCreate(
                nombre="Luis Ortega",
                puesto="Coordinador de flota",
                telefono="2295550201",
                email="lortega@tpgflota.demo",
                principal=True,
            ),
        )
        crud_transportista.create_documento(
            db,
            transp.id,
            TransportistaDocumentoCreate(
                tipo_documento=TipoDocumentoTransportista.PERMISO_SCT,
                numero_documento="SCT-AUT-2024-TPG-0098",
                estatus=EstatusDocumentoTransportista.VIGENTE,
                observaciones="Demo semilla",
            ),
        )

        # --- Tarifa venta federal / mixta / propio (base + km) ---
        tarifa_v = crud_tarifa_flete.create(
            db,
            TarifaFleteCreate(
                nombre_tarifa="Federal Veracruz-Villahermosa tracto general (propio)",
                tipo_operacion=TipoTransportista.PROPIO,
                ambito=AmbitoTarifaFlete.FEDERAL,
                modalidad_cobro=ModalidadCobroTarifa.MIXTA,
                origen=ORIGEN_TARIFA,
                destino=DESTINO_TARIFA,
                tipo_unidad="tractocamion",
                tipo_carga="general",
                tarifa_base=Decimal("6200.00"),
                tarifa_km=Decimal("36.5000"),
                tarifa_kg=Decimal("0"),
                tarifa_tonelada=Decimal("0"),
                tarifa_hora=Decimal("0"),
                tarifa_dia=Decimal("0"),
                recargo_minimo=Decimal("950.00"),
                porcentaje_utilidad=Decimal("0.18"),
                porcentaje_riesgo=Decimal("0.02"),
                porcentaje_urgencia=Decimal("0"),
                porcentaje_retorno_vacio=Decimal("0"),
                porcentaje_carga_especial=Decimal("0"),
                moneda="MXN",
                activo=True,
            ),
        )

        # --- Tarifa compra (costo interno simulado, mismo corredor) ---
        crud_tarifa_compra.create(
            db,
            TarifaCompraTransportistaCreate(
                transportista_id=transp.id,
                tipo_transportista=TipoTransportista.PROPIO,
                nombre_tarifa="Compra federal Ver-Vhsa tracto (propio)",
                ambito=AmbitoTarifaFlete.FEDERAL,
                modalidad_cobro=ModalidadCobroTarifa.MIXTA,
                origen=ORIGEN_TARIFA,
                destino=DESTINO_TARIFA,
                tipo_unidad="tractocamion",
                tipo_carga="general",
                tarifa_base=Decimal("4100.00"),
                tarifa_km=Decimal("24.0000"),
                recargo_minimo=Decimal("600.00"),
                moneda="MXN",
                activo=True,
            ),
        )

        # --- Viaje ---
        salida = datetime(2026, 4, 14, 6, 0, tzinfo=MX)
        llegada_est = datetime(2026, 4, 15, 8, 0, tzinfo=MX)
        viaje = crud_viaje.create(
            db,
            ViajeCreate(
                codigo_viaje="VIA-DEMO-VVER-VHS-001",
                descripcion="Carga general federal Veracruz, Ver. -> Villahermosa, Tab.",
                # Mismos textos que la tarifa (origen/destino) para alinear recálculo en factura
                origen="Veracruz",
                destino="Villahermosa",
                fecha_salida=salida,
                fecha_llegada_estimada=llegada_est,
                estado=EstadoViaje.PLANIFICADO,
                kilometros_estimados=DISTANCIA_KM,
                notas="Ruta federal por carretera 180 / corredor sureste (demo).",
            ),
        )

        # --- Cotización guardada ---
        req = FleteCotizacionRequest(
            cliente_id=cli.id,
            tipo_operacion=TipoTransportista.PROPIO,
            ambito=AmbitoTarifaFlete.FEDERAL,
            origen=ORIGEN_TARIFA,
            destino=DESTINO_TARIFA,
            tipo_unidad="tractocamion",
            tipo_carga="general",
            distancia_km=DISTANCIA_KM,
            peso_kg=PESO_KG,
            horas_servicio=Decimal("0"),
            dias_servicio=Decimal("0"),
            urgencia=False,
            retorno_vacio=False,
            riesgo_pct_extra=Decimal("0"),
            recargos=Decimal("0"),
        )
        cot_res = cotizar_venta_con_tarifa(db, req)
        cot = crud_cotizacion_flete.create(
            db,
            _cotizacion_row_dict(
                req,
                cot_res,
                folio=crud_cotizacion_flete.next_folio(db),
                observaciones="Cotización demo automática Veracruz-Villahermosa.",
            ),
        )
        crud_cotizacion_flete.update_status(
            db, cot, estatus=EstatusCotizacionFlete.ACEPTADA, observaciones="Aceptada para ejecución demo."
        )

        # --- Convertir a flete (misma lógica que la API) ---
        conv = CotizacionFleteConvertir(
            codigo_flete="FLT-DEMO-VVER-VHS-001",
            transportista_id=transp.id,
            viaje_id=viaje.id,
            descripcion_carga="Productos de carga general emplayados, 15 t.",
            numero_bultos=24,
            volumen_m3=Decimal("62.00"),
            notas="Demo sistema SIFE-MXN — federal.",
        )
        cot_ref = crud_cotizacion_flete.get_by_id(db, cot.id)
        assert cot_ref is not None
        transp_chk = crud_transportista.get_by_id(db, conv.transportista_id)
        tipo_op = (
            transp_chk.tipo_transportista
            if transp_chk is not None
            else TipoTransportista.SUBCONTRATADO
        )
        fle = crud_flete.create(
            db,
            FleteCreate(
                codigo_flete=conv.codigo_flete,
                cliente_id=cot_ref.cliente_id,
                transportista_id=conv.transportista_id,
                viaje_id=conv.viaje_id,
                descripcion_carga=conv.descripcion_carga,
                peso_kg=cot_ref.peso_kg,
                volumen_m3=conv.volumen_m3,
                numero_bultos=conv.numero_bultos,
                distancia_km=cot_ref.distancia_km,
                tipo_operacion=tipo_op,
                tipo_unidad=cot_ref.tipo_unidad,
                tipo_carga=cot_ref.tipo_carga,
                monto_estimado=cot_ref.precio_venta_sugerido,
                precio_venta=cot_ref.precio_venta_sugerido,
                costo_transporte_estimado=cot_ref.costo_base_estimado,
                metodo_calculo=MetodoCalculoFlete.TARIFA,
                moneda=cot_ref.moneda,
                estado=EstadoFlete.COTIZADO,
                ambito_operacion=cot_ref.ambito,
                mercancia_documentacion_ok=True,
                notas=conv.notas,
            ),
        )
        crud_cotizacion_flete.mark_converted(db, cot_ref, fle.id)
        cot_ok = crud_cotizacion_flete.get_by_id(db, cot.id)
        assert cot_ok is not None
        crud_flete.update(
            db, fle, FleteUpdate(estado=EstadoFlete.CONFIRMADO, ambito_operacion=cot_ok.ambito)
        )
        fle = crud_flete.get_by_id(db, fle.id)
        assert fle is not None

        # --- Orden de servicio (post-conversión, con flete vinculado) ---
        orden = crud_orden_servicio.create(
            db,
            {
                "folio": crud_orden_servicio.next_folio(db),
                "cliente_id": cot_ok.cliente_id,
                "cotizacion_id": cot_ok.id,
                "flete_id": cot_ok.flete_id,
                "viaje_id": viaje.id,
                "despacho_id": None,
                "origen": cot_ok.origen,
                "destino": cot_ok.destino,
                "tipo_unidad": cot_ok.tipo_unidad,
                "tipo_carga": cot_ok.tipo_carga,
                "peso_kg": cot_ok.peso_kg,
                "distancia_km": cot_ok.distancia_km,
                "precio_comprometido": cot_ok.precio_venta_sugerido,
                "moneda": cot_ok.moneda,
                "fecha_programada": salida,
                "estatus": EstatusOrdenServicio.CONFIRMADA,
                "observaciones": "OS demo federal Veracruz-Villahermosa.",
            },
        )

        # --- Operador y unidad ---
        op = crud_operador.create(
            db,
            OperadorCreate(
                transportista_id=transp.id,
                tipo_contratacion="planta",
                licencia="VER9010151H1",
                tipo_licencia="Federal",
                vigencia_licencia=date(2029, 12, 31),
                estatus_documental="completo",
                nombre="Carlos",
                apellido_paterno="Ramírez",
                apellido_materno="Nolasco",
                fecha_nacimiento=date(1988, 7, 22),
                curp="RANX880722HVZMLS08",
                rfc="RANX880722",
                nss="15975348620",
                estado_civil=EstadoCivil.CASADO,
                tipo_sangre=TipoSangre.OP,
                telefono_principal="2295550300",
                direccion="Calle Sur 88",
                colonia="Centro",
                municipio="Veracruz",
                estado_geografico="Veracruz",
                codigo_postal="91700",
                correo_electronico="c.ramirez.demo@mail.test",
                anios_experiencia=10,
                tipos_unidad_manejadas=["tractocamion"],
            ),
        )
        uni = crud_unidad.create(
            db,
            UnidadCreate(
                transportista_id=transp.id,
                economico="TPG-TR-088",
                placas="82-AB-12-CD",
                tipo_propiedad="propio",
                estatus_documental="vigente",
                descripcion="Tractocamión 6x4 federal",
                activo=True,
                vigencia_permiso_sct=date(2027, 6, 30),
                vigencia_seguro=date(2026, 12, 31),
            ),
        )

        asig = crud_asignacion.create(
            db,
            AsignacionCreate(
                id_operador=op.id_operador,
                id_unidad=uni.id_unidad,
                id_viaje=viaje.id,
                fecha_salida=salida,
                fecha_regreso=datetime(2026, 4, 16, 18, 0, tzinfo=MX),
                km_inicial=Decimal("198450.00"),
                rendimiento_combustible=Decimal("2.65"),
            ),
        )

        desp = crud_despacho.create(
            db,
            DespachoCreate(
                id_asignacion=asig.id_asignacion,
                id_flete=fle.id,
                salida_programada=salida,
                observaciones_transito="Ruta federal; peajes casetas 180.",
            ),
        )

        crud_orden_servicio.update(
            db,
            orden,
            {"despacho_id": desp.id_despacho, "viaje_id": viaje.id},
        )

        salida_real = salida + timedelta(minutes=25)
        crud_despacho.registrar_salida(
            db,
            desp,
            DespachoRegistrarSalida(
                salida_real=salida_real,
                km_salida=Decimal("198450.00"),
                observaciones_salida="Salida CEDIS Veracruz; sellos OK.",
            ),
        )
        desp = crud_despacho.get_by_id(db, desp.id_despacho)
        assert desp is not None

        crud_despacho.create_evento(
            db,
            desp.id_despacho,
            DespachoEventoCreate(
                tipo_evento=TipoEventoDespacho.CHECKPOINT,
                fecha_evento=salida_real + timedelta(hours=6),
                ubicacion="Coatzacoalcos, Ver.",
                descripcion="Checkpoint: sin incidencias.",
            ),
        )
        entrega_t = llegada_est - timedelta(hours=1)
        crud_despacho.registrar_entrega(
            db,
            desp,
            DespachoRegistrarEntrega(
                fecha_entrega=entrega_t,
                evidencia_entrega="https://demo.local/evidencias/entrega-vhsa-001.jpg",
                firma_recibe="Ing. Pedro Castillo — Almacén central",
                observaciones_entrega="Recibido conforme; 24 bultos vs remisión.",
            ),
        )
        desp = crud_despacho.get_by_id(db, desp.id_despacho)
        assert desp is not None
        crud_despacho.cerrar(
            db,
            desp,
            DespachoCerrar(
                llegada_real=entrega_t + timedelta(minutes=30),
                km_llegada=Decimal("198968.00"),
                observaciones_cierre="Cierre operativo demo; km finales registrados.",
            ),
        )

        crud_flete.update(db, fle, FleteUpdate(estado=EstadoFlete.ENTREGADO))
        crud_orden_servicio.change_status(
            db, orden, EstatusOrdenServicio.CERRADA, "Servicio demo cerrado."
        )

        crud_gasto_viaje.create(
            db,
            GastoViajeCreate(
                flete_id=fle.id,
                tipo_gasto="caseta",
                monto=Decimal("2840.00"),
                fecha_gasto=date(2026, 4, 14),
                descripcion="Casetas ruta 180 (demo)",
                referencia="CAS-180-001",
            ),
        )
        crud_gasto_viaje.create(
            db,
            GastoViajeCreate(
                flete_id=fle.id,
                tipo_gasto="diesel",
                monto=Decimal("11200.00"),
                fecha_gasto=date(2026, 4, 14),
                descripcion="Combustible tracto TPG-TR-088",
                referencia="TICK-DIE-9981",
            ),
        )

        # --- Factura desde flete ---
        fc = construir_factura_create(
            db,
            flete_id=fle.id,
            fecha_emision=date(2026, 4, 16),
            fecha_vencimiento=date(2026, 5, 16),
            serie="A",
            iva_pct=Decimal("0.16"),
            retencion_monto=Decimal("0"),
            usar_precio_tarifa_recalculado=False,
            forma_pago="03",
            metodo_pago="PUE",
            uso_cfdi="G03",
            estatus=EstatusFactura.EMITIDA,
            timbrada=False,
            concepto=None,
            referencia=fle.codigo_flete,
            observaciones="Factura administrativa demo — no timbrada ante SAT.",
        )
        fact = crud_factura.create(
            db,
            {
                **fc.model_dump(),
                "folio": crud_factura.next_folio(db),
                "estatus": EstatusFactura.EMITIDA,
            },
        )

        out_path = ROOT / "scripts" / "factura_demo_veracruz_villahermosa.txt"
        lines = [
            "=" * 72,
            "FACTURA ADMINISTRATIVA (DEMO SIFE-MXN)",
            "=" * 72,
            f"Folio interno:     {fact.folio}",
            f"Serie:             {fact.serie}",
            f"Estatus:           {fact.estatus.value}",
            f"Timbrada (CFDI):   {'Sí' if fact.timbrada else 'No (demo)'}",
            "",
            f"Cliente (razón):   {fact.cliente.razon_social}",
            f"RFC cliente:       {fact.cliente.rfc}",
            "",
            f"Flete:             {fle.codigo_flete}",
            f"Orden servicio:    {orden.folio}",
            f"Cotización:        {cot.folio}",
            "",
            f"Concepto:          {fact.concepto}",
            f"Referencia:        {fact.referencia}",
            f"Moneda:            {fact.moneda}",
            "",
            f"Fecha emisión:     {fact.fecha_emision}",
            f"Fecha vencimiento: {fact.fecha_vencimiento}",
            f"Forma pago:        {fact.forma_pago}",
            f"Método pago:       {fact.metodo_pago}",
            f"Uso CFDI:          {fact.uso_cfdi}",
            "",
            f"Subtotal:          {fact.subtotal}",
            f"IVA ({fact.iva_pct*100}%):        {fact.iva_monto}",
            f"Retención:         {fact.retencion_monto}",
            f"TOTAL:             {fact.total}",
            f"Saldo pendiente:   {fact.saldo_pendiente}",
            "",
            f"Observaciones:     {fact.observaciones}",
            "=" * 72,
            "Precio de venta en flete (tarifa): " + str(fle.precio_venta),
            "Tarifa aplicada id: " + str(tarifa_v.id),
            "=" * 72,
        ]
        text = "\n".join(lines) + "\n"
        out_path.write_text(text, encoding="utf-8")

        print(text)
        print(f"Resumen guardado en: {out_path}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
