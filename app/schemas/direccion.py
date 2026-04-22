from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class DireccionKpiResumen(BaseModel):
    fletes: int
    ordenes_servicio: int
    asignaciones: int
    despachos: int
    despachos_cerrados: int
    facturas: int
    facturas_emitidas: int
    incidencias_despacho: int


class DireccionEmbudo(BaseModel):
    fletes_a_os_pct: float
    os_a_asignacion_pct: float
    asignacion_a_despacho_pct: float
    despacho_a_factura_pct: float


class DireccionTiemposCiclo(BaseModel):
    flete_a_factura_horas: float | None = None
    orden_a_despacho_horas: float | None = None
    despacho_a_factura_horas: float | None = None


class DireccionSemaforo(BaseModel):
    operacion: str
    sistema: str
    dato: str
    cobranza: str


class DireccionDashboardResponse(BaseModel):
    desde: date
    hasta: date
    resumen: DireccionKpiResumen
    embudo: DireccionEmbudo
    tiempos: DireccionTiemposCiclo
    semaforo: DireccionSemaforo


class DireccionIncidenciaBase(BaseModel):
    titulo: str = Field(min_length=3, max_length=160)
    modulo: str = Field(min_length=2, max_length=64, default="general")
    severidad: str = Field(default="media")
    estatus: str = Field(default="abierta")
    fecha_detectada: date
    detalle: str | None = None
    responsable: str | None = Field(default=None, max_length=120)


class DireccionIncidenciaCreate(DireccionIncidenciaBase):
    pass


class DireccionIncidenciaUpdate(BaseModel):
    titulo: str | None = Field(default=None, min_length=3, max_length=160)
    modulo: str | None = Field(default=None, min_length=2, max_length=64)
    severidad: str | None = None
    estatus: str | None = None
    fecha_detectada: date | None = None
    detalle: str | None = None
    responsable: str | None = Field(default=None, max_length=120)


class DireccionIncidenciaRead(DireccionIncidenciaBase):
    id: int
    resuelta_at: str | None = None
    created_at: str
    updated_at: str


class DireccionAccionBase(BaseModel):
    week_start: date
    week_end: date
    titulo: str = Field(min_length=3, max_length=180)
    descripcion: str | None = None
    owner: str = Field(min_length=2, max_length=120)
    due_date: date | None = None
    impacto: str | None = Field(default=None, max_length=255)
    estatus: str = Field(default="pendiente")


class DireccionAccionCreate(DireccionAccionBase):
    pass


class DireccionAccionUpdate(BaseModel):
    week_start: date | None = None
    week_end: date | None = None
    titulo: str | None = Field(default=None, min_length=3, max_length=180)
    descripcion: str | None = None
    owner: str | None = Field(default=None, min_length=2, max_length=120)
    due_date: date | None = None
    impacto: str | None = Field(default=None, max_length=255)
    estatus: str | None = None


class DireccionAccionRead(DireccionAccionBase):
    id: int
    created_at: str
    updated_at: str


class DireccionAccionFromGuardrailCreate(BaseModel):
    regla: str = Field(min_length=2, max_length=64)
    motivo: str = Field(min_length=3, max_length=255)
    owner: str = Field(default="direccion", min_length=2, max_length=120)
    impacto: str | None = Field(default=None, max_length=255)
    dias_compromiso: int = Field(default=7, ge=1, le=60)


class DireccionAccionFromRecommendationCreate(BaseModel):
    source_type: str = Field(min_length=4, max_length=16)
    source_name: str = Field(min_length=2, max_length=180)
    accion_sugerida: str = Field(min_length=3, max_length=255)
    owner: str | None = Field(default=None, min_length=2, max_length=120)
    impacto: str | None = Field(default=None, max_length=255)
    dias_compromiso: int = Field(default=7, ge=1, le=60)


class DireccionAccionCerrarImpactoCreate(BaseModel):
    impacto_realizado_mxn: float = Field(ge=0)
    comentario_cierre: str = Field(min_length=3, max_length=300)
    marcar_completada: bool = True


class DireccionAccionSeguimientoRead(BaseModel):
    desde: date
    hasta: date
    total: int
    pendientes: int
    en_curso: int
    completadas: int
    canceladas: int
    vencidas_abiertas: int
    cumplimiento_pct: float
    cumplimiento_en_tiempo_pct: float
    mensaje: str


class DireccionAccionImpactoItem(BaseModel):
    accion_id: int
    titulo: str
    regla: str
    estado: str
    owner: str
    before_valor: str
    current_valor: str
    delta: str
    impacto_estimado_mxn: float
    impacto_realizado_mxn: float = 0.0
    comentario_cierre: str | None = None


class DireccionAccionImpactoRead(BaseModel):
    generated_at: str
    items: list[DireccionAccionImpactoItem] = Field(default_factory=list)
    impacto_total_estimado_mxn: float
    impacto_total_realizado_mxn: float = 0.0


class DireccionAccionRoiItem(BaseModel):
    accion_id: int
    regla: str
    owner: str
    estatus: str
    impacto_estimado_mxn: float
    impacto_realizado_mxn: float
    roi_real_pct: float | None = None


class DireccionAccionRoiRead(BaseModel):
    generated_at: str
    items: list[DireccionAccionRoiItem] = Field(default_factory=list)


class DireccionDestruyeMargenClienteItem(BaseModel):
    cliente_id: int | None = None
    cliente: str
    ingresos: float
    costo: float
    utilidad: float
    margen_pct: float
    accion_sugerida: str


class DireccionDestruyeMargenRutaItem(BaseModel):
    ruta: str
    fletes: int
    ingresos: float
    costo: float
    utilidad: float
    margen_pct: float
    accion_sugerida: str


class DireccionDestruyeMargenRead(BaseModel):
    generated_at: str
    clientes: list[DireccionDestruyeMargenClienteItem] = Field(default_factory=list)
    rutas: list[DireccionDestruyeMargenRutaItem] = Field(default_factory=list)


class DireccionEstadoGuerraRead(BaseModel):
    generated_at: str
    semaforo_general: str
    bloqueos_activos: int
    acciones_vencidas: int
    riesgo_mensual_estimado_mxn: float
    recuperacion_realizada_mxn: float
    roi_real_promedio_pct: float
    top_prioridades: list[str] = Field(default_factory=list)
    plan_semanal: list[str] = Field(default_factory=list)


class DireccionReporteFinanciero(BaseModel):
    ingresos_facturados: float
    cobranza_realizada: float
    saldo_pendiente: float
    costo_viaje_real: float
    utilidad_real: float
    margen_pct: float
    ingreso_por_km: float
    costo_por_km: float
    utilidad_por_km: float
    km_totales: float


class DireccionReporteConversion(BaseModel):
    cotizaciones_enviadas: int
    cotizaciones_convertidas: int
    cotizaciones_rechazadas: int
    tasa_conversion_pct: float
    tasa_rechazo_pct: float
    ingreso_cotizado: float
    ingreso_convertido: float
    conversion_por_valor_pct: float
    clientes_convertedores_unicos: int


class DireccionBucketAntiguedad(BaseModel):
    bucket: str
    monto: float
    facturas: int


class DireccionReporteCartera(BaseModel):
    cuentas_por_cobrar: float
    cartera_vencida: float
    cartera_vencida_pct: float
    dso_dias: float | None = None
    indice_recuperacion_pct: float
    concentracion_top3_pct: float
    antiguedad: list[DireccionBucketAntiguedad]


class DireccionReporteProductividad(BaseModel):
    fletes_totales: int
    fletes_entregados: int
    facturas_emitidas: int
    facturas_cobradas: int
    viajes_con_carga_pct: float
    despacho_a_factura_pct: float
    cumplimiento_cobranza_pct: float


class DireccionReporteSostenibilidad(BaseModel):
    estado: str
    mensaje: str
    alertas: list[str]
    semaforo: DireccionSemaforo


class DireccionDecisionGuardrailItem(BaseModel):
    regla: str
    politica: str
    valor_actual: str
    estado: str
    detalle: str


class DireccionDecisionGuardrailsRead(BaseModel):
    generated_at: str
    bloqueado: bool
    motivos_bloqueo: list[str] = Field(default_factory=list)
    acciones_recomendadas: list[str] = Field(default_factory=list)
    items: list[DireccionDecisionGuardrailItem] = Field(default_factory=list)
    alertas_calidad_datos: list[str] = Field(default_factory=list)
    alertas_disciplina: list[str] = Field(default_factory=list)


class DireccionReporteClienteRentabilidad(BaseModel):
    cliente_id: int | None = None
    cliente: str
    ingresos: float
    costo: float
    utilidad: float
    margen_pct: float
    fletes: int


class DireccionReporteCompletoResponse(BaseModel):
    desde: date
    hasta: date
    financiero: DireccionReporteFinanciero
    conversion: DireccionReporteConversion
    cartera: DireccionReporteCartera
    productividad: DireccionReporteProductividad
    sostenibilidad: DireccionReporteSostenibilidad
    top_clientes_rentabilidad: list[DireccionReporteClienteRentabilidad] = Field(default_factory=list)
    decision_guardrails: DireccionDecisionGuardrailsRead | None = None


class DireccionThresholds(BaseModel):
    margen_verde_min: float
    margen_amarillo_min: float
    utilidad_km_verde_min: float
    utilidad_km_amarillo_min: float
    conversion_verde_min: float
    conversion_amarillo_min: float
    vencida_verde_max: float
    vencida_amarillo_max: float
    carga_verde_min: float
    carga_amarillo_min: float


class DireccionThresholdHistoryRead(BaseModel):
    id: int
    mode: str
    changes: list[str] = Field(default_factory=list)
    created_at: str


class DireccionThresholdsRead(BaseModel):
    source: str
    thresholds: DireccionThresholds
    history: list[DireccionThresholdHistoryRead] = Field(default_factory=list)
    user_override_allowed: bool = True
    edit_window_enabled: bool = False
    edit_allowed: bool = True
    edit_blocked_reason: str | None = None


class DireccionSemanalSnapshotItem(BaseModel):
    id: int
    week_start: date
    week_end: date
    created_at: str
    created_by_user_id: int | None = None


class DireccionSemanalSnapshotListResponse(BaseModel):
    items: list[DireccionSemanalSnapshotItem] = Field(default_factory=list)


class DireccionThresholdsUpdate(BaseModel):
    mode: str = Field(default="manual", max_length=32)
    thresholds: DireccionThresholds


class DireccionThresholdPolicyRead(BaseModel):
    role_name: str
    user_override_allowed: bool


class DireccionThresholdPolicyUpdate(BaseModel):
    user_override_allowed: bool
