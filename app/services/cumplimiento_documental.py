from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.asignacion import Asignacion
from app.models.despacho import Despacho
from app.models.documento_operador import DocumentoOperador, TipoDocumentoOperador
from app.models.flete import Flete
from app.models.operador import Operador
from app.models.tarifa_flete import AmbitoTarifaFlete
from app.models.transportista import (
    EstatusDocumentoTransportista,
    TipoDocumentoTransportista,
    Transportista,
    TransportistaDocumento,
)
from app.models.unidad import Unidad
from app.schemas.cumplimiento import (
    CatalogoRequisitosResponse,
    ChequeoCumplimiento,
    EstadoChequeo,
    ModuloRequisitos,
    ValidacionSalidaResponse,
)


def _estado_from_bool(ok: bool, warn: bool = False) -> EstadoChequeo:
    if ok:
        return EstadoChequeo.CUMPLE
    if warn:
        return EstadoChequeo.ADVERTENCIA
    return EstadoChequeo.NO_CUMPLE


def _transportista_doc_vigente(
    docs: list[TransportistaDocumento],
    tipo: TipoDocumentoTransportista,
    ref: date,
) -> tuple[bool, TransportistaDocumento | None]:
    candidatos = [d for d in docs if d.tipo_documento == tipo]
    for d in candidatos:
        if d.estatus != EstatusDocumentoTransportista.VIGENTE:
            continue
        if d.fecha_vencimiento is not None and d.fecha_vencimiento < ref:
            continue
        return True, d
    return False, None


def _operador_tiene_doc_vigente(
    docs: list[DocumentoOperador], tipo: TipoDocumentoOperador, ref: date
) -> bool:
    for d in docs:
        if d.tipo_documento != tipo:
            continue
        if d.fecha_vencimiento is not None and d.fecha_vencimiento < ref:
            continue
        return True
    return False


def _apto_medico_operador(op: Operador, ref: date) -> tuple[bool, str]:
    if op.proxima_revision_medica is not None and op.proxima_revision_medica >= ref:
        return True, "Próxima revisión médica vigente."
    if op.ultima_revision_medica is not None and op.resultado_apto is True:
        limite = op.ultima_revision_medica + timedelta(days=730)
        if limite >= ref:
            return True, "Última revisión apta dentro de ventana operativa."
    return False, "Sin apto médico vigente según fechas registradas."


def validar_salida_por_despacho(
    db: Session,
    *,
    id_despacho: int,
    ambito_override: AmbitoTarifaFlete | None = None,
    fecha_referencia: date | None = None,
) -> ValidacionSalidaResponse:
    ref = fecha_referencia or date.today()
    stmt = (
        select(Despacho)
        .where(Despacho.id_despacho == id_despacho)
        .options(
            selectinload(Despacho.asignacion).selectinload(Asignacion.operador),
            selectinload(Despacho.asignacion).selectinload(Asignacion.unidad),
            selectinload(Despacho.asignacion).selectinload(Asignacion.viaje),
            selectinload(Despacho.flete),
        )
    )
    despacho = db.execute(stmt).scalar_one_or_none()
    if despacho is None:
        raise ValueError("Despacho no encontrado.")

    asignacion = despacho.asignacion
    op = asignacion.operador
    unidad = asignacion.unidad
    flete = despacho.flete

    ambito = ambito_override or (
        flete.ambito_operacion if flete and flete.ambito_operacion else AmbitoTarifaFlete.FEDERAL
    )

    transportista_id = flete.transportista_id if flete else op.transportista_id
    if transportista_id is None:
        raise ValueError("No hay transportista asociado al flete u operador.")

    t_stmt = (
        select(Transportista)
        .where(Transportista.id == transportista_id)
        .options(selectinload(Transportista.documentos))
    )
    transportista = db.execute(t_stmt).scalar_one()

    op_docs = db.execute(
        select(DocumentoOperador).where(DocumentoOperador.id_operador == op.id_operador)
    ).scalars().all()

    chequeos: list[ChequeoCumplimiento] = []

    # Fiscal — Carta Porte
    tiene_cp = False
    if flete:
        tiene_cp = bool(
            (flete.carta_porte_uuid and flete.carta_porte_uuid.strip())
            or (flete.carta_porte_folio and flete.carta_porte_folio.strip())
        )
    chequeos.append(
        ChequeoCumplimiento(
            codigo="CP_CARTA_PORTE",
            titulo="Carta Porte (CFDI con complemento de traslado)",
            detalle="Registrado UUID o folio de Carta Porte en el flete."
            if tiene_cp
            else "Falta UUID o folio de Carta Porte en el flete vinculado al despacho.",
            estado=_estado_from_bool(tiene_cp),
            referencia_normativa="SAT — CFDI con complemento Carta Porte",
        )
    )

    # Mercancía
    mercancia_ok = False
    if flete:
        mercancia_ok = bool(
            flete.mercancia_documentacion_ok
            or (flete.factura_mercancia_folio and flete.factura_mercancia_folio.strip())
        )
    chequeos.append(
        ChequeoCumplimiento(
            codigo="MER_FACTURA_EM",
            titulo="Documentación de la mercancía",
            detalle="Factura / evidencia de mercancía indicada o bandera de documentación lista."
            if mercancia_ok
            else "Sin folio de factura de mercancía ni confirmación documental.",
            estado=_estado_from_bool(mercancia_ok),
            referencia_normativa="Comprobante fiscal de la mercancía (cliente / embarque)",
        )
    )

    rfc_ok = bool(transportista.rfc and transportista.rfc.strip())
    chequeos.append(
        ChequeoCumplimiento(
            codigo="EMP_RFC",
            titulo="RFC del transportista",
            detalle="RFC capturado." if rfc_ok else "RFC del transportista no capturado.",
            estado=_estado_from_bool(rfc_ok),
            referencia_normativa="SAT — Identificación fiscal",
        )
    )

    seguro_rc_ok, _ = _transportista_doc_vigente(
        transportista.documentos, TipoDocumentoTransportista.SEGURO_RC, ref
    )
    chequeos.append(
        ChequeoCumplimiento(
            codigo="EMP_SEGURO_RC",
            titulo="Seguro de responsabilidad civil (transportista)",
            detalle="Documento SEGURO_RC vigente en expediente."
            if seguro_rc_ok
            else "Sin póliza RC vigente en documentos del transportista.",
            estado=_estado_from_bool(seguro_rc_ok),
            referencia_normativa="Cobertura civil del transportista",
        )
    )

    permiso_ok, _ = _transportista_doc_vigente(
        transportista.documentos, TipoDocumentoTransportista.PERMISO_SCT, ref
    )
    permiso_unidad_ok = unidad.vigencia_permiso_sct is not None and unidad.vigencia_permiso_sct >= ref
    sct_combinado_ok = permiso_ok or permiso_unidad_ok
    requiere_permiso = ambito in (AmbitoTarifaFlete.ESTATAL, AmbitoTarifaFlete.FEDERAL)
    if sct_combinado_ok:
        est_permiso = EstadoChequeo.CUMPLE
        if permiso_ok and permiso_unidad_ok:
            det_permiso = "Permiso SCT vigente en transportista y fecha coherente en unidad."
        elif permiso_ok:
            det_permiso = "Permiso SCT vigente en expediente del transportista."
        else:
            det_permiso = (
                f"Permiso SCT tomado de vigencia en unidad ({unidad.vigencia_permiso_sct}); "
                "verifique alineación con el servicio."
            )
    elif requiere_permiso:
        est_permiso = EstadoChequeo.NO_CUMPLE
        det_permiso = (
            "Sin permiso SCT vigente en transportista ni fecha válida en unidad "
            "(requerido en ámbito estatal/federal)."
        )
    else:
        est_permiso = EstadoChequeo.ADVERTENCIA
        det_permiso = "Sin permiso SCT registrado; confirmar si el servicio local lo exige."
    chequeos.append(
        ChequeoCumplimiento(
            codigo="EMP_PERMISO_SCT",
            titulo="Permiso SCT (transportista y/o unidad)",
            detalle=det_permiso,
            estado=est_permiso,
            referencia_normativa="SCT / permisos de autotransporte",
        )
    )

    licencia_fecha_ok = op.vigencia_licencia is not None and op.vigencia_licencia >= ref
    chequeos.append(
        ChequeoCumplimiento(
            codigo="OP_LICENCIA",
            titulo="Licencia del operador (vigencia)",
            detalle=f"Vigencia al {ref}: {op.vigencia_licencia}."
            if licencia_fecha_ok
            else "Vencida o sin fecha de vigencia.",
            estado=_estado_from_bool(licencia_fecha_ok),
            referencia_normativa="Licencia federal conforme a tipo de unidad",
        )
    )

    licencia_expediente = _operador_tiene_doc_vigente(
        op_docs, TipoDocumentoOperador.LICENCIA_FEDERAL_B, ref
    ) or _operador_tiene_doc_vigente(op_docs, TipoDocumentoOperador.LICENCIA_FEDERAL_E, ref)
    chequeos.append(
        ChequeoCumplimiento(
            codigo="OP_LICENCIA_EXP",
            titulo="Expediente: licencia federal en documentos del operador",
            detalle="Constancia de licencia tipo B o E vigente en expediente."
            if licencia_expediente
            else "No hay licencia federal (B/E) vigente en documentos del operador.",
            estado=_estado_from_bool(licencia_expediente, warn=not licencia_expediente),
            referencia_normativa="Expediente operador",
        )
    )

    apto_ok, apto_msg = _apto_medico_operador(op, ref)
    chequeos.append(
        ChequeoCumplimiento(
            codigo="OP_APTO_MEDICO",
            titulo="Apto médico / control psicofísico",
            detalle=apto_msg,
            estado=_estado_from_bool(apto_ok),
            referencia_normativa="NOM-087 / criterios SCT para operadores",
        )
    )

    apto_exp = _operador_tiene_doc_vigente(op_docs, TipoDocumentoOperador.APTO_MEDICO_SCT, ref)
    chequeos.append(
        ChequeoCumplimiento(
            codigo="OP_APTO_EXP",
            titulo="Expediente: apto médico SCT",
            detalle="Documento de apto médico vigente."
            if apto_exp
            else "Sin apto médico SCT en expediente (opcional si fechas en operador cubren el requisito).",
            estado=_estado_from_bool(apto_exp or apto_ok, warn=not (apto_exp or apto_ok)),
            referencia_normativa="Expediente operador",
        )
    )

    placas_ok = bool(unidad.placas and unidad.placas.strip())
    chequeos.append(
        ChequeoCumplimiento(
            codigo="UN_PLACAS",
            titulo="Placas de la unidad",
            detalle=f"Placas: {unidad.placas}." if placas_ok else "Placas no registradas.",
            estado=_estado_from_bool(placas_ok),
            referencia_normativa="Identificación vehicular",
        )
    )

    if unidad.vigencia_seguro is not None:
        seg_u_ok = unidad.vigencia_seguro >= ref
        det = f"Vigencia seguro unidad al {ref}: {unidad.vigencia_seguro}."
    else:
        seg_u_ok = False
        det = "Sin fecha de vigencia de seguro en la unidad (completar para validación automática)."
    chequeos.append(
        ChequeoCumplimiento(
            codigo="UN_SEGURO",
            titulo="Seguro de la unidad",
            detalle=det if unidad.vigencia_seguro is not None else det,
            estado=_estado_from_bool(seg_u_ok, warn=unidad.vigencia_seguro is None),
            referencia_normativa="Póliza del vehículo",
        )
    )

    if unidad.vigencia_tarjeta_circulacion is not None:
        tc_ok = unidad.vigencia_tarjeta_circulacion >= ref
        chequeos.append(
            ChequeoCumplimiento(
                codigo="UN_TARJETA_CIRC",
                titulo="Tarjeta de circulación",
                detalle=f"Vigencia: {unidad.vigencia_tarjeta_circulacion}.",
                estado=_estado_from_bool(tc_ok),
                referencia_normativa="Tarjeta de circulación estatal",
            )
        )

    if unidad.vigencia_verificacion_fisico_mecanica is not None:
        vm_ok = unidad.vigencia_verificacion_fisico_mecanica >= ref
        chequeos.append(
            ChequeoCumplimiento(
                codigo="UN_VERIFICACION",
                titulo="Verificación físico-mecánica",
                detalle=f"Vigencia: {unidad.vigencia_verificacion_fisico_mecanica}.",
                estado=_estado_from_bool(vm_ok),
                referencia_normativa="Verificación vehicular aplicable",
            )
        )

    bloqueos: list[str] = []
    advertencias: list[str] = []
    for c in chequeos:
        if c.estado == EstadoChequeo.NO_CUMPLE:
            bloqueos.append(f"{c.titulo}: {c.detalle}")
        elif c.estado == EstadoChequeo.ADVERTENCIA:
            advertencias.append(f"{c.titulo}: {c.detalle}")

    criticos = {
        "CP_CARTA_PORTE",
        "MER_FACTURA_EM",
        "EMP_RFC",
        "EMP_SEGURO_RC",
        "OP_LICENCIA",
        "OP_APTO_MEDICO",
        "UN_PLACAS",
    }
    if ambito in (AmbitoTarifaFlete.ESTATAL, AmbitoTarifaFlete.FEDERAL):
        criticos.add("EMP_PERMISO_SCT")

    autorizado = all(
        c.estado != EstadoChequeo.NO_CUMPLE for c in chequeos if c.codigo in criticos
    )

    insights: list[str] = []
    if not autorizado:
        insights.append(
            "La salida no está autorizada por validación automática: corrija los ítems en rojo "
            "antes de despachar."
        )
    else:
        insights.append(
            "Validación automática superada en puntos críticos; revise advertencias antes de ruta."
        )
    insights.append(
        "Este resultado es operativo y no sustituye dictamen fiscal, legal ni de autoridad."
    )
    if ambito == AmbitoTarifaFlete.LOCAL:
        insights.append(
            "Ámbito local: mantenga Carta Porte y documentación aunque el trayecto sea corto."
        )
    elif ambito == AmbitoTarifaFlete.FEDERAL:
        insights.append(
            "Ámbito federal: refuerce permisos de autotransporte y dimensiones NOM en carga."
        )

    return ValidacionSalidaResponse(
        fecha_referencia=ref,
        ambito=ambito,
        id_despacho=despacho.id_despacho,
        id_asignacion=asignacion.id_asignacion,
        id_flete=flete.id if flete else None,
        autorizado=autorizado,
        bloqueos=bloqueos,
        advertencias=advertencias,
        chequeos=chequeos,
        insights=insights,
    )


def catalogo_requisitos(ambito: AmbitoTarifaFlete) -> CatalogoRequisitosResponse:
    nota = (
        "Resumen orientativo para operación de carga general en México. "
        "Verifique siempre normativa vigente y el caso concreto (materiales peligrosos, "
        "frío, sobre dimensionado, import/export, etc.)."
    )
    base_fiscal = [
        "CFDI con complemento Carta Porte (traslado de mercancías).",
        "Comprobante fiscal que respalde la mercancía (factura / documento equivalente).",
    ]
    base_unidad = [
        "Tarjeta de circulación vigente.",
        "Placas y permisos del vehículo conforme al servicio.",
        "Seguro de responsabilidad civil del transportista y póliza del vehículo.",
        "Verificación físico-mecánica y contaminantes cuando aplique.",
    ]
    base_op = [
        "Licencia federal de chofer (tipo acorde a la unidad).",
        "Constancia de aptitud psicofísica vigente.",
        "Identificación oficial del operador.",
    ]
    base_merc = [
        "Lista de empaque o descripción de bultos.",
        "Documentos adicionales según carga (pedimento, permisos sanitarios, materiales peligrosos, etc.).",
    ]

    if ambito == AmbitoTarifaFlete.LOCAL:
        modulos = [
            {
                "id": "fiscal",
                "titulo": "Módulo fiscal (SAT)",
                "descripcion": "Traslado aun intramunicipal requiere Carta Porte cuando aplique reglamento fiscal.",
                "documentos": base_fiscal,
            },
            {
                "id": "unidad",
                "titulo": "Unidad",
                "documentos": base_unidad,
            },
            {
                "id": "operador",
                "titulo": "Operador",
                "documentos": base_op,
            },
            {
                "id": "mercancia",
                "titulo": "Mercancía",
                "documentos": base_merc,
            },
        ]
    elif ambito == AmbitoTarifaFlete.ESTATAL:
        modulos = [
            {
                "id": "fiscal",
                "titulo": "Módulo fiscal (SAT)",
                "documentos": base_fiscal,
            },
            {
                "id": "unidad",
                "titulo": "Unidad",
                "descripcion": "Mayor revisión en carreteras estatales; seguros y documentación al día.",
                "documentos": base_unidad + ["Permisos estatales cuando la carga o ruta lo requieran."],
            },
            {
                "id": "operador",
                "titulo": "Operador",
                "documentos": base_op,
            },
            {
                "id": "mercancia",
                "titulo": "Mercancía",
                "documentos": base_merc,
            },
        ]
    else:
        modulos = [
            {
                "id": "fiscal",
                "titulo": "Módulo fiscal (SAT)",
                "documentos": base_fiscal,
            },
            {
                "id": "unidad",
                "titulo": "Unidad",
                "descripcion": "Autotransporte federal: permisos SCT, peso y dimensiones (NOM-012-SCT2-2017, etc.).",
                "documentos": base_unidad
                + [
                    "Permiso federal de autotransporte cuando corresponda.",
                    "Cumplimiento de pesos y dimensiones autorizados.",
                ],
            },
            {
                "id": "operador",
                "titulo": "Operador",
                "documentos": base_op,
            },
            {
                "id": "mercancia",
                "titulo": "Mercancía",
                "documentos": base_merc,
            },
            {
                "id": "control",
                "titulo": "Inspección en ruta",
                "descripcion": "Guardia Nacional y autoridades: Carta Porte, licencia, permisos y seguros.",
                "documentos": [
                    "Carta Porte disponible (digital o impresa).",
                    "Identificación del operador y del transportista.",
                    "Documentación de la carga acorde a lo declarado.",
                ],
            },
        ]

    return CatalogoRequisitosResponse(
        ambito=ambito,
        nota_legal=nota,
        modulos=[ModuloRequisitos(**m) for m in modulos],
    )
