"""
Motor de tarifas — costos (CF, CV, CR, CU), márgenes por ámbito (local/estatal/federal),
tipos de operación (propio, subcontratado, fletero, aliado), modo híbrido MAX,
ajustes (urgencia, clima, diesel, riesgo) y tres niveles de venta.

Los valores por defecto incorporan rangos de mercado referenciales (México / Veracruz)
documentados para el proyecto; son configurables vía MotorTarifaEntrada.
"""

from __future__ import annotations

from decimal import Decimal

from app.models.tarifa_flete import AmbitoTarifaFlete
from app.models.transportista import TipoTransportista
from app.schemas.motor_tarifa import (
    DesgloseCostos,
    ModoCalculoMotor,
    MotorAsignacionEntrada,
    MotorAsignacionResultado,
    MotorTarifaEntrada,
    MotorTarifaResultado,
    NivelZonaMX,
    ResultadoScore,
    TresNivelesPrecio,
    ZonaRiesgo,
)


def _norm_unidad(u: str) -> str:
    return u.strip().lower()


def _cpk_referencia(tipo_unidad: str, nivel_zona: NivelZonaMX) -> Decimal:
    """
    Costo/precio por km de referencia por tipo de unidad + ajuste regional suave.
    Rangos mercado MX (documentación proyecto): rabón 16-25, torton 22-35, trailer 28-45.
    """
    u = _norm_unidad(tipo_unidad)
    if u in {"rabon", "rabón", "3.5"}:
        base = Decimal("20")
    elif u in {"torton", "tortón"}:
        base = Decimal("26")
    elif u in {"tractocamion", "tractocamión", "trailer", "tráiler", "full"}:
        base = Decimal("36")
    else:
        base = Decimal("24")

    mult = Decimal("1")
    if nivel_zona == NivelZonaMX.VERACRUZ_SURESTE:
        mult = Decimal("0.95")
    elif nivel_zona == NivelZonaMX.CENTRO:
        mult = Decimal("1.08")
    elif nivel_zona == NivelZonaMX.NORTE:
        mult = Decimal("1.12")
    elif nivel_zona == NivelZonaMX.BAJIO:
        mult = Decimal("1.02")
    return (base * mult).quantize(Decimal("0.01"))


def _pct_riesgo(z: ZonaRiesgo, p: MotorTarifaEntrada) -> Decimal:
    if z == ZonaRiesgo.BAJO:
        return p.pct_riesgo_bajo
    if z == ZonaRiesgo.MEDIO:
        return p.pct_riesgo_medio
    return p.pct_riesgo_alto


def _mu_por_ambito(p: MotorTarifaEntrada) -> Decimal:
    if p.ambito == AmbitoTarifaFlete.LOCAL:
        return p.mu_local
    if p.ambito == AmbitoTarifaFlete.ESTATAL:
        return p.mu_estatal
    return p.mu_federal


def _cf_prorrateado(p: MotorTarifaEntrada) -> Decimal:
    if p.costos_mensuales_unidad is None or p.viajes_mensuales is None:
        return Decimal("0")
    return (p.costos_mensuales_unidad / p.viajes_mensuales).quantize(Decimal("0.01"))


def _cv(p: MotorTarifaEntrada, cpk: Decimal) -> Decimal:
    km_part = p.km * cpk
    return (km_part + p.casetas + p.viaticos + p.maniobras).quantize(Decimal("0.01"))


def calcular_modo_propio(p: MotorTarifaEntrada, cpk: Decimal) -> tuple[DesgloseCostos, str]:
    cf = _cf_prorrateado(p)
    cv = _cv(p, cpk)
    pr = _pct_riesgo(p.zona_riesgo, p)
    cr = ((cv + cf) * pr).quantize(Decimal("0.01"))
    cu = ((cv + cf) * p.cu_sobre_cf_cv).quantize(Decimal("0.01"))
    sub = (cf + cv + cr + cu).quantize(Decimal("0.01"))
    mu = _mu_por_ambito(p)
    tarifa = (sub * mu).quantize(Decimal("0.01"))
    desc = (
        f"PROPIO: CF={cf}, CV={cv} (km×CPK+casetas+viáticos+maniobras), "
        f"CR={cr} ((CF+CV)×{pr}), CU={cu}, subtotal={sub}, MU(ámbito)={mu}, tarifa={tarifa}."
    )
    return (
        DesgloseCostos(
            cf=cf,
            cv=cv,
            cr=cr,
            cu=cu,
            subtotal_costos=sub,
            mu_aplicado=mu,
            tarifa_antes_ajustes=tarifa,
        ),
        desc,
    )


def calcular_subcontratado(p: MotorTarifaEntrada) -> tuple[Decimal, str]:
    if p.costo_proveedor is None:
        raise ValueError("Subcontratado requiere costo_proveedor.")
    t = (p.costo_proveedor * p.factor_utilidad_subcontratado).quantize(Decimal("0.01"))
    return t, f"SUBCONTRATADO: {p.costo_proveedor} × {p.factor_utilidad_subcontratado} = {t}"


def calcular_fletero(p: MotorTarifaEntrada) -> tuple[Decimal, str]:
    if p.tarifa_fletero_publicada is None:
        raise ValueError("Fletero requiere tarifa_fletero_publicada.")
    com = p.comision_fija + (p.tarifa_fletero_publicada * p.comision_pct_sobre_fletero)
    t = (p.tarifa_fletero_publicada + com).quantize(Decimal("0.01"))
    return t, f"FLETERO: tarifa_fletero {p.tarifa_fletero_publicada} + comisión {com} = {t}"


def calcular_aliado(p: MotorTarifaEntrada) -> tuple[Decimal, str]:
    if p.costo_preferencial_aliado is None:
        raise ValueError("Aliado requiere costo_preferencial_aliado.")
    t = (p.costo_preferencial_aliado * (Decimal("1") + p.margen_aliado_pct)).quantize(Decimal("0.01"))
    return t, f"ALIADO: {p.costo_preferencial_aliado} × (1+{p.margen_aliado_pct}) = {t}"


def calcular_hibrido_max(p: MotorTarifaEntrada, cpk: Decimal) -> tuple[Decimal, str]:
    pk = p.precio_km_mercado or cpk
    tarifa_km = (p.km * pk).quantize(Decimal("0.01"))
    pt = p.precio_ton_mercado
    if pt is None:
        pt = Decimal("250")
    tarifa_ton = (p.toneladas * pt).quantize(Decimal("0.01"))
    costo_int = p.costo_total_interno
    if costo_int is None:
        cf = _cf_prorrateado(p)
        cv = _cv(p, cpk)
        pr = _pct_riesgo(p.zona_riesgo, p)
        cr = ((cv + cf) * pr).quantize(Decimal("0.01"))
        cu = ((cv + cf) * p.cu_sobre_cf_cv).quantize(Decimal("0.01"))
        costo_int = (cf + cv + cr + cu).quantize(Decimal("0.01"))
    tarifa_costo = (costo_int * p.margen_sobre_costo_hibrido).quantize(Decimal("0.01"))
    m = max(tarifa_km, tarifa_ton, tarifa_costo)
    detalle = (
        f"HÍBRIDO MAX: max(km×precio_km={tarifa_km}, ton×precio_ton={tarifa_ton}, "
        f"costo×margen={tarifa_costo}) = {m}"
    )
    return m, detalle


def _ajustes_finales(base: Decimal, p: MotorTarifaEntrada) -> Decimal:
    x = base
    if p.urgencia:
        x = (x * p.factor_urgencia).quantize(Decimal("0.01"))
    x = (x * p.factor_clima).quantize(Decimal("0.01"))
    x = (x * p.factor_diesel).quantize(Decimal("0.01"))
    return x


def _inferir_modo(p: MotorTarifaEntrada) -> ModoCalculoMotor:
    if p.modo is not None:
        return p.modo
    m = {
        TipoTransportista.PROPIO: ModoCalculoMotor.COSTO_COMPLETO_PROPIO,
        TipoTransportista.SUBCONTRATADO: ModoCalculoMotor.SUBCONTRATADO,
        TipoTransportista.FLETERO: ModoCalculoMotor.FLETERO,
        TipoTransportista.ALIADO: ModoCalculoMotor.ALIADO,
    }
    return m[p.tipo_transportista]


def _tres_niveles(tarifa_ajustada: Decimal, p: MotorTarifaEntrada) -> TresNivelesPrecio:
    """
    Piso comercial (económico), recomendado (mercado), premium (valor / urgencia implícita).
    """
    eco = (tarifa_ajustada * Decimal("0.92")).quantize(Decimal("0.01"))
    rec = tarifa_ajustada
    prem = (tarifa_ajustada * (Decimal("1.18") if not p.urgencia else Decimal("1.28"))).quantize(
        Decimal("0.01")
    )
    notas = (
        "Económico: -8% aprox. competitivo; Recomendado: post-ajustes; "
        "Premium: +18% valor o +28% si urgencia."
    )
    return TresNivelesPrecio(economico=eco, recomendado=rec, premium=prem, notas=notas)


def ejecutar_motor(p: MotorTarifaEntrada) -> MotorTarifaResultado:
    cpk = p.cpk_variable or _cpk_referencia(p.tipo_unidad, p.nivel_zona)
    modo = _inferir_modo(p)
    desglose = None
    detalle = ""
    tarifa_base = Decimal("0")

    if modo == ModoCalculoMotor.HIBRIDO_MAX:
        tarifa_base, detalle = calcular_hibrido_max(p, cpk)
    elif modo == ModoCalculoMotor.COSTO_COMPLETO_PROPIO or p.tipo_transportista == TipoTransportista.PROPIO:
        desglose, detalle = calcular_modo_propio(p, cpk)
        tarifa_base = desglose.tarifa_antes_ajustes
    elif modo == ModoCalculoMotor.SUBCONTRATADO:
        tarifa_base, detalle = calcular_subcontratado(p)
    elif modo == ModoCalculoMotor.FLETERO:
        tarifa_base, detalle = calcular_fletero(p)
    elif modo == ModoCalculoMotor.ALIADO:
        tarifa_base, detalle = calcular_aliado(p)
    else:
        tarifa_base, detalle = calcular_subcontratado(p)

    tarifa_fin = _ajustes_finales(tarifa_base, p)
    tres = _tres_niveles(tarifa_fin, p)

    params: dict[str, str] = {
        "cpk_usado": str(cpk),
        "mu_ambito": str(_mu_por_ambito(p)),
        "pct_riesgo": str(_pct_riesgo(p.zona_riesgo, p)),
        "ambito": p.ambito.value,
    }

    return MotorTarifaResultado(
        tipo_transportista=p.tipo_transportista,
        modo_aplicado=modo,
        desglose=desglose,
        tarifa_base=tarifa_base,
        tarifa_tras_ajustes=tarifa_fin,
        tres_niveles=tres,
        detalle_calculo=detalle,
        parametros_usados=params,
    )


def ejecutar_asignacion(body: MotorAsignacionEntrada) -> MotorAsignacionResultado:
    """Score simple: ganancia, confianza, penalización distancia/tiempo, disponibilidad."""
    ranked: list[ResultadoScore] = []
    for c in body.candidatos:
        if not c.disponible:
            continue
        g = float(c.ganancia)
        conf = float(c.nivel_confianza)
        dist = float(c.distancia_km_desde_base)
        tresp = float(c.tiempo_respuesta_hrs)
        score = (
            g * float(body.peso_ganancia)
            + conf * 1000 * float(body.peso_confianza)
            - dist * float(body.peso_distancia)
            - tresp * 100 * float(body.peso_tiempo)
            + (1000 if c.disponible else 0) * float(body.peso_disponible)
        )
        if body.urgente:
            score -= tresp * 200
        if body.ganancia_minima is not None and c.ganancia < body.ganancia_minima:
            continue
        ranked.append(
            ResultadoScore(
                transportista_id=c.transportista_id,
                score=Decimal(str(round(score, 4))),
                tarifa_venta=c.tarifa_venta,
                ganancia=c.ganancia,
                razon=f"g={c.ganancia} conf={c.nivel_confianza} dist={c.distancia_km_desde_base}h",
            )
        )
    ranked.sort(key=lambda x: x.score, reverse=True)
    best = ranked[0].transportista_id if ranked else None
    return MotorAsignacionResultado(ranking=ranked, recomendado_id=best)
