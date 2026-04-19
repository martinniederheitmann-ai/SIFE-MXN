"""Esquemas del motor de tarifas (costos + márgenes + tipos de operación)."""

from __future__ import annotations

from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.models.tarifa_flete import AmbitoTarifaFlete
from app.models.transportista import TipoTransportista


class ZonaRiesgo(str, Enum):
    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"


class NivelZonaMX(str, Enum):
    """Referencia de mercado por región (ajuste opcional sobre CPK)."""

    GENERICA = "generica"
    VERACRUZ_SURESTE = "veracruz_sureste"
    CENTRO = "centro"
    NORTE = "norte"
    BAJIO = "bajio"


class ModoCalculoMotor(str, Enum):
    """Cómo combinar componentes cuando aplica modo híbrido."""

    COSTO_COMPLETO_PROPIO = "costo_completo_propio"
    SUBCONTRATADO = "subcontratado"
    FLETERO = "fletero"
    ALIADO = "aliado"
    HIBRIDO_MAX = "hibrido_max"


class MotorTarifaEntrada(BaseModel):
    """Entrada al motor: mínima para cotizar; el resto usa defaults de mercado."""

    km: Decimal = Field(..., ge=0, description="Distancia total del servicio.")
    toneladas: Decimal = Field(..., ge=0, description="Peso en toneladas (peso_kg/1000).")
    tipo_unidad: str = Field(
        ...,
        max_length=64,
        description="Ej. rabon, torton, tractocamion, trailer",
    )
    tipo_carga: str | None = Field(None, max_length=64)
    ambito: AmbitoTarifaFlete = Field(
        default=AmbitoTarifaFlete.FEDERAL,
        description="local / estatal / federal — define márgenes MU sugeridos.",
    )
    tipo_transportista: TipoTransportista = Field(
        default=TipoTransportista.SUBCONTRATADO,
        description="propio: costos internos; subcontratado: costo proveedor × factor; fletero: + comisión; aliado: × margen reducido.",
    )
    modo: ModoCalculoMotor | None = Field(
        None,
        description="Si es None, se infiere del tipo_transportista.",
    )

    zona_riesgo: ZonaRiesgo = Field(default=ZonaRiesgo.BAJO)
    nivel_zona: NivelZonaMX = Field(
        default=NivelZonaMX.VERACRUZ_SURESTE,
        description="Ajuste suave de CPK de referencia (mercado MX).",
    )
    urgencia: bool = False
    factor_clima: Decimal = Field(default=Decimal("1"), ge=Decimal("1"), le=Decimal("1.25"))
    factor_diesel: Decimal = Field(
        default=Decimal("1"),
        ge=Decimal("0.5"),
        le=Decimal("2"),
        description="Precio diesel actual / precio base (ej. 1.08).",
    )

    # --- Propio / costo interno ---
    costos_mensuales_unidad: Decimal | None = Field(None, ge=0)
    viajes_mensuales: Decimal | None = Field(None, gt=0)
    cpk_variable: Decimal | None = Field(
        None,
        ge=0,
        description="Costo por km variable; si null, usa tabla por tipo_unidad + zona.",
    )
    casetas: Decimal = Field(default=Decimal("0"), ge=0)
    viaticos: Decimal = Field(default=Decimal("0"), ge=0)
    maniobras: Decimal = Field(default=Decimal("0"), ge=0)

    # --- Subcontratado ---
    costo_proveedor: Decimal | None = Field(None, ge=0)
    factor_utilidad_subcontratado: Decimal = Field(default=Decimal("1.25"), gt=0)

    # --- Fletero ---
    tarifa_fletero_publicada: Decimal | None = Field(None, ge=0)
    comision_fija: Decimal = Field(default=Decimal("0"), ge=0)
    comision_pct_sobre_fletero: Decimal = Field(default=Decimal("0"), ge=0, le=Decimal("1"))

    # --- Aliado ---
    costo_preferencial_aliado: Decimal | None = Field(None, ge=0)
    margen_aliado_pct: Decimal = Field(default=Decimal("0.15"), ge=0, le=Decimal("1"))

    # --- Híbrido MAX (precios por km y por ton de mercado) ---
    precio_km_mercado: Decimal | None = Field(None, ge=0)
    precio_ton_mercado: Decimal | None = Field(None, ge=0)
    costo_total_interno: Decimal | None = Field(None, ge=0)
    margen_sobre_costo_hibrido: Decimal = Field(default=Decimal("1.30"), gt=0)

    # --- Márgenes MU por ámbito (1 + % ganancia) — se pueden sobreescribir ---
    mu_local: Decimal = Field(default=Decimal("1.28"))
    mu_estatal: Decimal = Field(default=Decimal("1.32"))
    mu_federal: Decimal = Field(default=Decimal("1.40"))

    pct_riesgo_bajo: Decimal = Field(default=Decimal("0.02"))
    pct_riesgo_medio: Decimal = Field(default=Decimal("0.05"))
    pct_riesgo_alto: Decimal = Field(default=Decimal("0.10"))

    cu_sobre_cf_cv: Decimal = Field(
        default=Decimal("0.10"),
        description="CU = (CF+CV)*este porcentaje (colchón operativo).",
    )
    factor_urgencia: Decimal = Field(default=Decimal("1.25"), gt=0)


class DesgloseCostos(BaseModel):
    cf: Decimal
    cv: Decimal
    cr: Decimal
    cu: Decimal
    subtotal_costos: Decimal
    mu_aplicado: Decimal
    tarifa_antes_ajustes: Decimal


class TresNivelesPrecio(BaseModel):
    economico: Decimal
    recomendado: Decimal
    premium: Decimal
    notas: str


class MotorTarifaResultado(BaseModel):
    tipo_transportista: TipoTransportista
    modo_aplicado: ModoCalculoMotor
    moneda: str = "MXN"
    desglose: DesgloseCostos | None = None
    tarifa_base: Decimal
    tarifa_tras_ajustes: Decimal
    tres_niveles: TresNivelesPrecio
    detalle_calculo: str
    parametros_usados: dict[str, str]


class CandidatoAsignacion(BaseModel):
    transportista_id: int
    tipo: TipoTransportista
    costo_estimado: Decimal = Field(..., ge=0, description="Costo proveedor o costo interno.")
    tarifa_venta: Decimal = Field(..., ge=0)
    ganancia: Decimal
    nivel_confianza: Decimal = Field(default=Decimal("3"), ge=0, le=Decimal("5"))
    distancia_km_desde_base: Decimal = Field(default=Decimal("0"), ge=0)
    tiempo_respuesta_hrs: Decimal = Field(default=Decimal("4"), ge=0)
    disponible: bool = True


class MotorAsignacionEntrada(BaseModel):
    candidatos: list[CandidatoAsignacion]
    peso_ganancia: Decimal = Field(default=Decimal("0.5"))
    peso_confianza: Decimal = Field(default=Decimal("0.2"))
    peso_distancia: Decimal = Field(default=Decimal("0.1"))
    peso_tiempo: Decimal = Field(default=Decimal("0.1"))
    peso_disponible: Decimal = Field(default=Decimal("0.1"))
    urgente: bool = False
    ganancia_minima: Decimal | None = Field(default=None, ge=0)


class ResultadoScore(BaseModel):
    transportista_id: int
    score: Decimal
    tarifa_venta: Decimal
    ganancia: Decimal
    razon: str


class MotorAsignacionResultado(BaseModel):
    ranking: list[ResultadoScore]
    recomendado_id: int | None


class MotorTarifaZonaPresetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    region_key: str
    tipo_unidad_norm: str
    cpk_referencia: Decimal
    mu_local: Decimal | None = None
    mu_estatal: Decimal | None = None
    mu_federal: Decimal | None = None
    notas: str | None = None
    activo: bool


class AsignacionSugeridaEntrada(BaseModel):
    """Sugerir ranking de transportistas usando tarifas de compra + motor de venta."""

    km: Decimal = Field(..., gt=0)
    toneladas: Decimal = Field(..., gt=0)
    tipo_unidad: str = Field(..., min_length=1)
    tipo_carga: str | None = None
    origen: str = Field(..., min_length=1)
    destino: str = Field(..., min_length=1)
    ambito: AmbitoTarifaFlete | None = None
    factor_sobre_costo: Decimal = Field(default=Decimal("1.25"), gt=0)
    limite_candidatos: int = Field(default=30, ge=1, le=100)
    solo_activos: bool = True


class CandidatoAsignacionDetalle(BaseModel):
    transportista_id: int
    nombre: str
    tipo_transportista: str
    costo_compra: Decimal
    tarifa_venta_sugerida: Decimal
    ganancia: Decimal
    nivel_confianza: Decimal
    tarifa_compra_id: int | None = None
    detalle: str | None = None


class AsignacionSugeridaResultado(BaseModel):
    candidatos: list[CandidatoAsignacionDetalle]
    ranking: MotorAsignacionResultado
