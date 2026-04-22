    function semaforoLabel(raw) {
      const v = String(raw || "").trim().toLowerCase();
      if (v === "verde") return "🟢 Verde";
      if (v === "amarillo") return "🟡 Amarillo";
      if (v === "rojo") return "🔴 Rojo";
      return "—";
    }

    function setDireccionNumber(id, value) {
      const el = document.getElementById(id);
      if (!el) return;
      const n = Number(value || 0);
      el.textContent = Number.isFinite(n) ? String(n) : "0";
    }

    function toISODateInput(d) {
      const year = d.getFullYear();
      const month = String(d.getMonth() + 1).padStart(2, "0");
      const day = String(d.getDate()).padStart(2, "0");
      return `${year}-${month}-${day}`;
    }

    function ensureDireccionDateRange(fromInput, toInput, messageId) {
      const from = (fromInput?.value || "").trim();
      const to = (toInput?.value || "").trim();
      if (!from || !to) {
        setMessage(messageId, "Capture ambas fechas: Desde y Hasta.", "error");
        return null;
      }
      if (from > to) {
        setMessage(messageId, "La fecha Desde no puede ser mayor que Hasta.", "error");
        return null;
      }
      return { from, to };
    }

    function renderDireccionDashboard(data) {
      setDireccionNumber("dir-kpi-fletes", data?.resumen?.fletes);
      setDireccionNumber("dir-kpi-os", data?.resumen?.ordenes_servicio);
      setDireccionNumber("dir-kpi-asignaciones", data?.resumen?.asignaciones);
      setDireccionNumber("dir-kpi-despachos", data?.resumen?.despachos);
      setDireccionNumber("dir-kpi-cerrados", data?.resumen?.despachos_cerrados);
      setDireccionNumber("dir-kpi-facturas", data?.resumen?.facturas);
      setDireccionNumber("dir-kpi-facturas-emitidas", data?.resumen?.facturas_emitidas);
      setDireccionNumber("dir-kpi-incidencias", data?.resumen?.incidencias_despacho);

      const embudo = document.getElementById("direccion-embudo-body");
      if (embudo) {
        embudo.innerHTML = `
          <tr><td>Fletes -> OS</td><td>${Number(data?.embudo?.fletes_a_os_pct || 0).toFixed(2)}%</td></tr>
          <tr><td>OS -> Asignación</td><td>${Number(data?.embudo?.os_a_asignacion_pct || 0).toFixed(2)}%</td></tr>
          <tr><td>Asignación -> Despacho</td><td>${Number(data?.embudo?.asignacion_a_despacho_pct || 0).toFixed(2)}%</td></tr>
          <tr><td>Despacho -> Factura</td><td>${Number(data?.embudo?.despacho_a_factura_pct || 0).toFixed(2)}%</td></tr>
        `;
      }

      const tiempos = document.getElementById("direccion-tiempos-body");
      const fmtHours = (v) => (v === null || v === undefined ? "—" : `${Number(v).toFixed(2)} h`);
      if (tiempos) {
        tiempos.innerHTML = `
          <tr><td>Flete -> Factura</td><td>${fmtHours(data?.tiempos?.flete_a_factura_horas)}</td></tr>
          <tr><td>Orden -> Despacho</td><td>${fmtHours(data?.tiempos?.orden_a_despacho_horas)}</td></tr>
          <tr><td>Despacho -> Factura</td><td>${fmtHours(data?.tiempos?.despacho_a_factura_horas)}</td></tr>
        `;
      }

      const semaforo = document.getElementById("direccion-semaforo-body");
      if (semaforo) {
        semaforo.innerHTML = `
          <tr><td>Operación</td><td>${semaforoLabel(data?.semaforo?.operacion)}</td></tr>
          <tr><td>Sistema</td><td>${semaforoLabel(data?.semaforo?.sistema)}</td></tr>
          <tr><td>Dato</td><td>${semaforoLabel(data?.semaforo?.dato)}</td></tr>
          <tr><td>Cobranza</td><td>${semaforoLabel(data?.semaforo?.cobranza)}</td></tr>
        `;
      }
    }

    function renderDireccionReporteCompleto(data) {
      const money = (v) => `$ ${fmtMoneyList(v)}`;
      const pct = (v) => fmtPctList(v);
      const cfg = getDireccionThresholds();
      const setText = (id, value) => {
        const el = document.getElementById(id);
        if (el) el.textContent = value;
      };
      const setCardTone = (id, tone) => {
        const el = document.getElementById(id);
        if (!el) return;
        el.classList.remove("kpi-verde", "kpi-amarillo", "kpi-rojo");
        if (tone === "verde" || tone === "amarillo" || tone === "rojo") {
          el.classList.add(`kpi-${tone}`);
        }
      };
      const toToneHigh = (value, greenMin, yellowMin) => {
        const n = Number(value || 0);
        if (n >= greenMin) return "verde";
        if (n >= yellowMin) return "amarillo";
        return "rojo";
      };
      const toToneLow = (value, greenMax, yellowMax) => {
        const n = Number(value || 0);
        if (n <= greenMax) return "verde";
        if (n <= yellowMax) return "amarillo";
        return "rojo";
      };
      setText("dir-ri-ingresos", money(data?.financiero?.ingresos_facturados));
      setText("dir-ri-utilidad", money(data?.financiero?.utilidad_real));
      setText("dir-ri-margen", pct(data?.financiero?.margen_pct));
      setText("dir-ri-utilidad-km", money(data?.financiero?.utilidad_por_km));
      setText("dir-ri-conv", pct(data?.conversion?.tasa_conversion_pct));
      setText("dir-ri-vencida", pct(data?.cartera?.cartera_vencida_pct));
      setText("dir-ri-carga", pct(data?.productividad?.viajes_con_carga_pct));
      const estado = String(data?.sostenibilidad?.estado || "—")
        .replaceAll("_", " ")
        .toUpperCase();
      setText("dir-ri-sostenibilidad", estado);
      setCardTone("dir-ri-card-ingresos", Number(data?.financiero?.ingresos_facturados || 0) > 0 ? "verde" : "amarillo");
      setCardTone("dir-ri-card-utilidad", toToneHigh(data?.financiero?.utilidad_real, 1, 0));
      setCardTone("dir-ri-card-margen", toToneHigh(data?.financiero?.margen_pct, cfg.margen_verde_min, cfg.margen_amarillo_min));
      setCardTone("dir-ri-card-utilidad-km", toToneHigh(data?.financiero?.utilidad_por_km, cfg.utilidad_km_verde_min, cfg.utilidad_km_amarillo_min));
      setCardTone("dir-ri-card-conv", toToneHigh(data?.conversion?.tasa_conversion_pct, cfg.conversion_verde_min, cfg.conversion_amarillo_min));
      setCardTone("dir-ri-card-vencida", toToneLow(data?.cartera?.cartera_vencida_pct, cfg.vencida_verde_max, cfg.vencida_amarillo_max));
      setCardTone("dir-ri-card-carga", toToneHigh(data?.productividad?.viajes_con_carga_pct, cfg.carga_verde_min, cfg.carga_amarillo_min));
      const estadoRaw = String(data?.sostenibilidad?.estado || "").toLowerCase();
      const toneSost = estadoRaw === "sostenible" ? "verde" : (estadoRaw === "en_riesgo" ? "amarillo" : "rojo");
      setCardTone("dir-ri-card-sostenibilidad", toneSost);

      const alertasBox = document.getElementById("direccion-reporte-alertas");
      const priorizadasWrap = document.getElementById("direccion-reporte-priorizadas");
      const resumenWrap = document.getElementById("direccion-reporte-resumen-ejecutivo");
      const guerraWrap = document.getElementById("direccion-reporte-estado-guerra");
      const guardrailsWrap = document.getElementById("direccion-reporte-guardrails");
      const seguimientoWrap = document.getElementById("direccion-reporte-seguimiento");
      const classifyAlert = (text) => {
        const t = String(text || "").toLowerCase();
        if (t.includes("negativo") || t.includes("critic") || t.includes("arriba de")) return "rojo";
        if (t.includes("fragil") || t.includes("menor")) return "amarillo";
        return "amarillo";
      };
      if (alertasBox) {
        const alertas = Array.isArray(data?.sostenibilidad?.alertas) ? [...data.sostenibilidad.alertas] : [];
        const guardrails = data?.decision_guardrails || null;
        if (guardrails?.bloqueado) {
          const motivos = Array.isArray(guardrails.motivos_bloqueo) ? guardrails.motivos_bloqueo : [];
          motivos.forEach((msg) => alertas.push(`Bloqueo de decisión: ${msg}`));
        }
        const dq = Array.isArray(guardrails?.alertas_calidad_datos) ? guardrails.alertas_calidad_datos : [];
        dq.forEach((msg) => alertas.push(`Calidad de datos: ${msg}`));
        const disc = Array.isArray(guardrails?.alertas_disciplina) ? guardrails.alertas_disciplina : [];
        disc.forEach((msg) => alertas.push(`Disciplina: ${msg}`));
        if (!alertas.length) {
          alertasBox.textContent = `Sostenibilidad: ${data?.sostenibilidad?.mensaje || "Sin alertas."}`;
          if (priorizadasWrap) {
            priorizadasWrap.innerHTML = '<div class="hint">Sin alertas priorizadas.</div>';
          }
        } else {
          const prioritized = alertas
            .map((text) => ({ text: String(text), tone: classifyAlert(text) }))
            .sort((a, b) => (a.tone === b.tone ? 0 : a.tone === "rojo" ? -1 : 1));
          const pills = prioritized
            .map((item) => `<span class="kpi-pill ${item.tone}">${escapeHtml(item.text)}</span>`)
            .join("");
          alertasBox.innerHTML = `<strong>Alertas:</strong> ${pills}`;
          if (priorizadasWrap) {
            const rows = prioritized
              .map(
                (item, idx) => `
                  <tr>
                    <td>${idx + 1}</td>
                    <td><span class="kpi-pill ${item.tone}">${item.tone.toUpperCase()}</span></td>
                    <td>${escapeHtml(item.text)}</td>
                  </tr>
                `
              )
              .join("");
            priorizadasWrap.innerHTML = `
              <table>
                <thead><tr><th>Prioridad</th><th>Severidad</th><th>Alerta</th></tr></thead>
                <tbody>${rows}</tbody>
              </table>
            `;
          }
        }
      }
      if (resumenWrap) {
        const margen = Number(data?.financiero?.margen_pct || 0).toFixed(2);
        const conv = Number(data?.conversion?.tasa_conversion_pct || 0).toFixed(2);
        const vencida = Number(data?.cartera?.cartera_vencida_pct || 0).toFixed(2);
        const carga = Number(data?.productividad?.viajes_con_carga_pct || 0).toFixed(2);
        const estadoS = String(data?.sostenibilidad?.estado || "en_riesgo").replaceAll("_", " ");
        const guardrails = data?.decision_guardrails || null;
        const bloqueoTxt = guardrails?.bloqueado ? "Guardrails: BLOQUEO ACTIVO." : "Guardrails: operativo.";
        resumenWrap.textContent = `Resumen ejecutivo: margen ${margen}%, conversión ${conv}%, cartera vencida ${vencida}% y viajes con carga ${carga}%. Estado general: ${estadoS}. ${bloqueoTxt}`;
      }
      if (guardrailsWrap) {
        const guardrails = data?.decision_guardrails || null;
        if (!guardrails) {
          guardrailsWrap.innerHTML = '<div class="hint">Sin guardrails calculados.</div>';
        } else {
          const rows = (Array.isArray(guardrails.items) ? guardrails.items : [])
            .map((item) => {
              const raw = String(item?.estado || "").toLowerCase();
              const tone = raw === "ok" ? "verde" : (raw === "bloqueo" ? "rojo" : "amarillo");
              return `
                <tr>
                  <td>${escapeHtml(String(item?.regla || ""))}</td>
                  <td>${escapeHtml(String(item?.politica || ""))}</td>
                  <td>${escapeHtml(String(item?.valor_actual || ""))}</td>
                  <td><span class="kpi-pill ${tone}">${escapeHtml(raw.toUpperCase() || "N/A")}</span></td>
                  <td>${escapeHtml(String(item?.detalle || ""))}</td>
                  <td><button type="button" class="secondary-button" data-guardrail-action data-regla="${escapeHtml(String(item?.regla || ""))}" data-detalle="${escapeHtml(String(item?.detalle || ""))}" data-estado="${escapeHtml(raw)}">Crear acción</button></td>
                </tr>
              `;
            })
            .join("");
          const bloqueoRows = (Array.isArray(guardrails.motivos_bloqueo) ? guardrails.motivos_bloqueo : [])
            .map((x) => `<li>${escapeHtml(String(x || ""))}</li>`)
            .join("");
          const accionRows = (Array.isArray(guardrails.acciones_recomendadas) ? guardrails.acciones_recomendadas : [])
            .map((x) => `<li>${escapeHtml(String(x || ""))}</li>`)
            .join("");
          const dataQualityRows = (Array.isArray(guardrails.alertas_calidad_datos) ? guardrails.alertas_calidad_datos : [])
            .map((x) => `<li>${escapeHtml(String(x || ""))}</li>`)
            .join("");
          const disciplinaRows = (Array.isArray(guardrails.alertas_disciplina) ? guardrails.alertas_disciplina : [])
            .map((x) => `<li>${escapeHtml(String(x || ""))}</li>`)
            .join("");
          guardrailsWrap.innerHTML = `
            <h4>Reglas de Oro (guardrails de decisión)</h4>
            <div class="hint">${guardrails.bloqueado ? "Estado: BLOQUEO ACTIVO. Se recomienda no negociar fuera de política." : "Estado: operativo."}</div>
            <table>
              <thead><tr><th>Regla</th><th>Política</th><th>Valor actual</th><th>Estado</th><th>Detalle</th><th></th></tr></thead>
              <tbody>${rows || '<tr><td colspan="6">Sin reglas evaluadas.</td></tr>'}</tbody>
            </table>
            <div class="two-col" style="margin-top:10px;">
              <div>
                <h4>Motivos de bloqueo</h4>
                <ul>${bloqueoRows || "<li>Sin bloqueos activos.</li>"}</ul>
              </div>
              <div>
                <h4>Acciones recomendadas</h4>
                <ul>${accionRows || "<li>Sin acciones pendientes.</li>"}</ul>
              </div>
            </div>
            <div class="two-col" style="margin-top:10px;">
              <div>
                <h4>Calidad de datos</h4>
                <ul>${dataQualityRows || "<li>Sin alertas de calidad.</li>"}</ul>
              </div>
              <div>
                <h4>Disciplina semanal</h4>
                <ul>${disciplinaRows || "<li>Sin alertas de disciplina.</li>"}</ul>
              </div>
            </div>
          `;
        }
      }
      if (seguimientoWrap) {
        const fromInput = document.getElementById("direccion-desde");
        const toInput = document.getElementById("direccion-hasta");
        if (!fromInput || !toInput) {
          seguimientoWrap.innerHTML = '<div class="hint">Sin rango para seguimiento.</div>';
        } else {
          const range = ensureDireccionDateRange(fromInput, toInput, "direccion-message");
          if (range) {
            const q = new URLSearchParams({ week_start: range.from, week_end: range.to });
            void api(`/direccion/acciones/seguimiento?${q.toString()}`)
              .then((seg) => {
                seguimientoWrap.innerHTML = `
                  <h4>Seguimiento de cumplimiento (semanal)</h4>
                  <table>
                    <thead><tr><th>KPI</th><th>Valor</th></tr></thead>
                    <tbody>
                      <tr><td>Total acciones</td><td>${Number(seg?.total || 0)}</td></tr>
                      <tr><td>Abiertas (pendiente + en curso)</td><td>${Number(seg?.pendientes || 0) + Number(seg?.en_curso || 0)}</td></tr>
                      <tr><td>Completadas</td><td>${Number(seg?.completadas || 0)}</td></tr>
                      <tr><td>Vencidas abiertas</td><td>${Number(seg?.vencidas_abiertas || 0)}</td></tr>
                      <tr><td>Cumplimiento</td><td>${fmtPctList(seg?.cumplimiento_pct)}</td></tr>
                      <tr><td>Cumplimiento en tiempo</td><td>${fmtPctList(seg?.cumplimiento_en_tiempo_pct)}</td></tr>
                    </tbody>
                  </table>
                  <div class="hint" style="margin-top:8px;">${escapeHtml(String(seg?.mensaje || ""))}</div>
                `;
              })
              .catch((error) => {
                seguimientoWrap.innerHTML = `<div class="hint">No se pudo cargar seguimiento: ${escapeHtml(String(error?.message || ""))}</div>`;
              });
            void api(`/direccion/acciones/impacto?${q.toString()}`)
              .then((impacto) => {
                const items = Array.isArray(impacto?.items) ? impacto.items : [];
                const rows = items
                  .map(
                    (it) => `
                      <tr>
                        <td>${Number(it?.accion_id || 0)}</td>
                        <td>${escapeHtml(String(it?.regla || ""))}</td>
                        <td>${escapeHtml(String(it?.before_valor || "—"))}</td>
                        <td>${escapeHtml(String(it?.current_valor || "—"))}</td>
                        <td>${escapeHtml(String(it?.delta || "—"))}</td>
                        <td>$ ${fmtMoneyList(it?.impacto_estimado_mxn || 0)}</td>
                        <td>$ ${fmtMoneyList(it?.impacto_realizado_mxn || 0)}</td>
                        <td>${escapeHtml(String(it?.estado || ""))}</td>
                      </tr>
                    `
                  )
                  .join("");
                seguimientoWrap.insertAdjacentHTML(
                  "beforeend",
                  `
                    <h4 style="margin-top:10px;">Impacto before/after por acción</h4>
                    <table>
                      <thead><tr><th>ID</th><th>Regla</th><th>Antes</th><th>Actual</th><th>Delta</th><th>Recuperación est.</th><th>Recuperación real</th><th>Estatus</th></tr></thead>
                      <tbody>${rows || '<tr><td colspan="8">Sin acciones de guardrail para comparar.</td></tr>'}</tbody>
                    </table>
                    <div class="hint" style="margin-top:8px;">Impacto total estimado recuperado: $ ${fmtMoneyList(impacto?.impacto_total_estimado_mxn || 0)}</div>
                    <div class="hint" style="margin-top:4px;">Impacto total realizado reportado: $ ${fmtMoneyList(impacto?.impacto_total_realizado_mxn || 0)}</div>
                  `
                );
              })
              .catch((_error) => {
                // no-op: el bloque de seguimiento ya tiene fallback propio
              });
            void api(`/direccion/acciones/impacto/roi?${q.toString()}&limit=5`)
              .then((roiData) => {
                const items = Array.isArray(roiData?.items) ? roiData.items : [];
                const rows = items
                  .map(
                    (it) => `
                      <tr>
                        <td>${Number(it?.accion_id || 0)}</td>
                        <td>${escapeHtml(String(it?.regla || ""))}</td>
                        <td>${escapeHtml(String(it?.owner || ""))}</td>
                        <td>$ ${fmtMoneyList(it?.impacto_realizado_mxn || 0)}</td>
                        <td>${it?.roi_real_pct === null || it?.roi_real_pct === undefined ? "N/A" : `${fmtMoneyList(it?.roi_real_pct)}%`}</td>
                        <td>${escapeHtml(String(it?.estatus || ""))}</td>
                      </tr>
                    `
                  )
                  .join("");
                seguimientoWrap.insertAdjacentHTML(
                  "beforeend",
                  `
                    <h4 style="margin-top:10px;">Top acciones por ROI real</h4>
                    <table>
                      <thead><tr><th>ID</th><th>Regla</th><th>Owner</th><th>Impacto real</th><th>ROI real</th><th>Estatus</th></tr></thead>
                      <tbody>${rows || '<tr><td colspan="6">Sin acciones con ROI calculable.</td></tr>'}</tbody>
                    </table>
                  `
                );
              })
              .catch((_error) => {
                // no-op
              });
            const qGuerra = new URLSearchParams({ desde: range.from, hasta: range.to });
            void api(`/direccion/reportes/estado-guerra?${qGuerra.toString()}`)
              .then((guerra) => {
                if (!guerraWrap) return;
                const prioridades = (Array.isArray(guerra?.top_prioridades) ? guerra.top_prioridades : [])
                  .map((x) => `<li>${escapeHtml(String(x || ""))}</li>`)
                  .join("");
                const plan = (Array.isArray(guerra?.plan_semanal) ? guerra.plan_semanal : [])
                  .map((x) => `<li>${escapeHtml(String(x || ""))}</li>`)
                  .join("");
                const tone = String(guerra?.semaforo_general || "amarillo").toLowerCase();
                guerraWrap.innerHTML = `
                  <h4>Estado de Guerra (comité en 1 pantalla)</h4>
                  <table>
                    <thead><tr><th>KPI</th><th>Valor</th></tr></thead>
                    <tbody>
                      <tr><td>Semáforo general</td><td><span class="kpi-pill ${escapeHtml(tone)}">${escapeHtml(String(guerra?.semaforo_general || "N/A").toUpperCase())}</span></td></tr>
                      <tr><td>Bloqueos activos</td><td>${Number(guerra?.bloqueos_activos || 0)}</td></tr>
                      <tr><td>Acciones vencidas</td><td>${Number(guerra?.acciones_vencidas || 0)}</td></tr>
                      <tr><td>Riesgo mensual estimado</td><td>$ ${fmtMoneyList(guerra?.riesgo_mensual_estimado_mxn || 0)}</td></tr>
                      <tr><td>Recuperación realizada</td><td>$ ${fmtMoneyList(guerra?.recuperacion_realizada_mxn || 0)}</td></tr>
                      <tr><td>ROI real promedio</td><td>${fmtMoneyList(guerra?.roi_real_promedio_pct || 0)}%</td></tr>
                    </tbody>
                  </table>
                  <div class="two-col" style="margin-top:10px;">
                    <div><h4>Top prioridades</h4><ul>${prioridades || "<li>Sin prioridades críticas.</li>"}</ul></div>
                    <div><h4>Plan semanal</h4><ul>${plan || "<li>Sin plan.</li>"}</ul></div>
                  </div>
                `;
              })
              .catch((error) => {
                if (!guerraWrap) return;
                guerraWrap.innerHTML = `<div class="hint">No se pudo cargar estado de guerra: ${escapeHtml(String(error?.message || ""))}</div>`;
              });
          }
        }
      }

      const finWrap = document.getElementById("direccion-reporte-finanzas");
      if (finWrap) {
        finWrap.innerHTML = `
          <table>
            <thead><tr><th>KPI financiero</th><th>Valor</th></tr></thead>
            <tbody>
              <tr><td>Ingresos facturados</td><td>${money(data?.financiero?.ingresos_facturados)}</td></tr>
              <tr><td>Cobranza realizada</td><td>${money(data?.financiero?.cobranza_realizada)}</td></tr>
              <tr><td>Saldo pendiente</td><td>${money(data?.financiero?.saldo_pendiente)}</td></tr>
              <tr><td>Costo viaje real</td><td>${money(data?.financiero?.costo_viaje_real)}</td></tr>
              <tr><td>Ingreso por km</td><td>${money(data?.financiero?.ingreso_por_km)}</td></tr>
              <tr><td>Costo por km</td><td>${money(data?.financiero?.costo_por_km)}</td></tr>
              <tr><td>Km totales</td><td>${fmtMoneyList(data?.financiero?.km_totales)}</td></tr>
            </tbody>
          </table>
        `;
      }

      const convWrap = document.getElementById("direccion-reporte-conversion");
      if (convWrap) {
        convWrap.innerHTML = `
          <table>
            <thead><tr><th>KPI conversión</th><th>Valor</th></tr></thead>
            <tbody>
              <tr><td>Cotizaciones enviadas</td><td>${Number(data?.conversion?.cotizaciones_enviadas || 0)}</td></tr>
              <tr><td>Cotizaciones convertidas</td><td>${Number(data?.conversion?.cotizaciones_convertidas || 0)}</td></tr>
              <tr><td>Cotizaciones rechazadas</td><td>${Number(data?.conversion?.cotizaciones_rechazadas || 0)}</td></tr>
              <tr><td>Tasa conversión</td><td>${pct(data?.conversion?.tasa_conversion_pct)}</td></tr>
              <tr><td>Tasa rechazo</td><td>${pct(data?.conversion?.tasa_rechazo_pct)}</td></tr>
              <tr><td>Conversión por valor</td><td>${pct(data?.conversion?.conversion_por_valor_pct)}</td></tr>
            </tbody>
          </table>
        `;
      }

      const carteraWrap = document.getElementById("direccion-reporte-cartera");
      if (carteraWrap) {
        const antiguedad = Array.isArray(data?.cartera?.antiguedad) ? data.cartera.antiguedad : [];
        const antRows = antiguedad
          .map(
            (it) => `<tr><td>${escapeHtml(String(it?.bucket || ""))}</td><td>${money(it?.monto)}</td><td>${Number(it?.facturas || 0)}</td></tr>`
          )
          .join("");
        carteraWrap.innerHTML = `
          <table>
            <thead><tr><th>KPI cartera</th><th>Valor</th></tr></thead>
            <tbody>
              <tr><td>Cuentas por cobrar</td><td>${money(data?.cartera?.cuentas_por_cobrar)}</td></tr>
              <tr><td>Cartera vencida</td><td>${money(data?.cartera?.cartera_vencida)}</td></tr>
              <tr><td>Cartera vencida %</td><td>${pct(data?.cartera?.cartera_vencida_pct)}</td></tr>
              <tr><td>DSO (días)</td><td>${data?.cartera?.dso_dias === null || data?.cartera?.dso_dias === undefined ? "—" : fmtMoneyList(data.cartera.dso_dias)}</td></tr>
              <tr><td>Índice de recuperación</td><td>${pct(data?.cartera?.indice_recuperacion_pct)}</td></tr>
              <tr><td>Concentración top 3</td><td>${pct(data?.cartera?.concentracion_top3_pct)}</td></tr>
            </tbody>
          </table>
          <table style="margin-top:8px;">
            <thead><tr><th>Antigüedad</th><th>Monto</th><th>Facturas</th></tr></thead>
            <tbody>${antRows || '<tr><td colspan="3">Sin datos.</td></tr>'}</tbody>
          </table>
        `;
      }

      const prodWrap = document.getElementById("direccion-reporte-productividad");
      if (prodWrap) {
        prodWrap.innerHTML = `
          <table>
            <thead><tr><th>KPI productividad</th><th>Valor</th></tr></thead>
            <tbody>
              <tr><td>Fletes totales</td><td>${Number(data?.productividad?.fletes_totales || 0)}</td></tr>
              <tr><td>Fletes entregados</td><td>${Number(data?.productividad?.fletes_entregados || 0)}</td></tr>
              <tr><td>Facturas emitidas</td><td>${Number(data?.productividad?.facturas_emitidas || 0)}</td></tr>
              <tr><td>Facturas cobradas</td><td>${Number(data?.productividad?.facturas_cobradas || 0)}</td></tr>
              <tr><td>Viajes con carga</td><td>${pct(data?.productividad?.viajes_con_carga_pct)}</td></tr>
              <tr><td>Despacho → factura</td><td>${pct(data?.productividad?.despacho_a_factura_pct)}</td></tr>
              <tr><td>Cumplimiento cobranza</td><td>${pct(data?.productividad?.cumplimiento_cobranza_pct)}</td></tr>
            </tbody>
          </table>
        `;
      }

      const clientesWrap = document.getElementById("direccion-reporte-clientes");
      const destruyeMargenWrap = document.getElementById("direccion-reporte-destruye-margen");
      if (clientesWrap) {
        const items = Array.isArray(data?.top_clientes_rentabilidad) ? data.top_clientes_rentabilidad : [];
        if (!items.length) {
          clientesWrap.innerHTML = '<div class="hint">Sin datos de clientes para el rango seleccionado.</div>';
        } else {
          const rows = items
            .map(
              (it) => `
                <tr>
                  <td>${escapeHtml(String(it?.cliente || ""))}</td>
                  <td>${money(it?.ingresos)}</td>
                  <td>${money(it?.costo)}</td>
                  <td>${money(it?.utilidad)}</td>
                  <td>${pct(it?.margen_pct)}</td>
                  <td>${Number(it?.fletes || 0)}</td>
                </tr>
              `
            )
            .join("");
          clientesWrap.innerHTML = `
            <table>
              <thead><tr><th>Cliente</th><th>Ingresos</th><th>Costo</th><th>Utilidad</th><th>Margen</th><th>Fletes</th></tr></thead>
              <tbody>${rows}</tbody>
            </table>
          `;
        }
      }
      if (destruyeMargenWrap) {
        const fromInput = document.getElementById("direccion-desde");
        const toInput = document.getElementById("direccion-hasta");
        if (!fromInput || !toInput) {
          destruyeMargenWrap.innerHTML = '<div class="hint">Sin rango para destruye-margen.</div>';
        } else {
          const range = ensureDireccionDateRange(fromInput, toInput, "direccion-message");
          if (range) {
            const q = new URLSearchParams({ desde: range.from, hasta: range.to, limit: "5" });
            void api(`/direccion/reportes/destruye-margen?${q.toString()}`)
              .then((dm) => {
                const clientes = Array.isArray(dm?.clientes) ? dm.clientes : [];
                const rutas = Array.isArray(dm?.rutas) ? dm.rutas : [];
                const clienteRows = clientes
                  .map(
                    (it) => `
                      <tr>
                        <td>${escapeHtml(String(it?.cliente || ""))}</td>
                        <td>${money(it?.ingresos)}</td>
                        <td>${money(it?.costo)}</td>
                        <td>${money(it?.utilidad)}</td>
                        <td>${pct(it?.margen_pct)}</td>
                        <td>${escapeHtml(String(it?.accion_sugerida || ""))}</td>
                        <td><button type="button" class="secondary-button" data-dm-action data-source-type="cliente" data-source-name="${escapeHtml(String(it?.cliente || ""))}" data-accion="${escapeHtml(String(it?.accion_sugerida || ""))}">Crear acción</button></td>
                      </tr>
                    `
                  )
                  .join("");
                const rutaRows = rutas
                  .map(
                    (it) => `
                      <tr>
                        <td>${escapeHtml(String(it?.ruta || ""))}</td>
                        <td>${Number(it?.fletes || 0)}</td>
                        <td>${money(it?.ingresos)}</td>
                        <td>${money(it?.costo)}</td>
                        <td>${money(it?.utilidad)}</td>
                        <td>${pct(it?.margen_pct)}</td>
                        <td>${escapeHtml(String(it?.accion_sugerida || ""))}</td>
                        <td><button type="button" class="secondary-button" data-dm-action data-source-type="ruta" data-source-name="${escapeHtml(String(it?.ruta || ""))}" data-accion="${escapeHtml(String(it?.accion_sugerida || ""))}">Crear acción</button></td>
                      </tr>
                    `
                  )
                  .join("");
                destruyeMargenWrap.innerHTML = `
                  <h4>Clientes destruye-margen (prioridad)</h4>
                  <table>
                    <thead><tr><th>Cliente</th><th>Ingresos</th><th>Costo</th><th>Utilidad</th><th>Margen</th><th>Acción sugerida</th><th></th></tr></thead>
                    <tbody>${clienteRows || '<tr><td colspan="7">Sin clientes bajo margen crítico en el rango.</td></tr>'}</tbody>
                  </table>
                  <h4 style="margin-top:10px;">Rutas destruye-margen (prioridad)</h4>
                  <table>
                    <thead><tr><th>Ruta</th><th>Fletes</th><th>Ingresos</th><th>Costo</th><th>Utilidad</th><th>Margen</th><th>Acción sugerida</th><th></th></tr></thead>
                    <tbody>${rutaRows || '<tr><td colspan="8">Sin rutas bajo margen crítico en el rango.</td></tr>'}</tbody>
                  </table>
                `;
              })
              .catch((error) => {
                destruyeMargenWrap.innerHTML = `<div class="hint">No se pudo cargar destruye-margen: ${escapeHtml(String(error?.message || ""))}</div>`;
              });
          }
        }
      }
    }

    async function refreshDireccionReporteCompleto() {
      const fromInput = document.getElementById("direccion-desde");
      const toInput = document.getElementById("direccion-hasta");
      if (!fromInput || !toInput) return;
      const range = ensureDireccionDateRange(fromInput, toInput, "direccion-message");
      if (!range) return;
      const q = new URLSearchParams({ desde: range.from, hasta: range.to });
      const data = await api(`/direccion/reportes/completo?${q.toString()}`);
      renderDireccionReporteCompleto(data);
    }

    const DIRECCION_THRESHOLDS_KEY = "sife_direccion_thresholds_v1";
    const DIRECCION_THRESHOLDS_HISTORY_KEY = "sife_direccion_thresholds_history_v1";
    let direccionThresholdsCache = null;
    let direccionThresholdHistoryCache = [];
    let direccionUserOverrideAllowed = true;
    let direccionThresholdEditAllowed = true;

    function defaultDireccionThresholds() {
      return {
        margen_verde_min: 15,
        margen_amarillo_min: 8,
        utilidad_km_verde_min: 5,
        utilidad_km_amarillo_min: 2,
        conversion_verde_min: 30,
        conversion_amarillo_min: 20,
        vencida_verde_max: 20,
        vencida_amarillo_max: 35,
        carga_verde_min: 80,
        carga_amarillo_min: 65,
      };
    }

    function direccionThresholdPresets() {
      return {
        ceo: {
          margen_verde_min: 18,
          margen_amarillo_min: 10,
          utilidad_km_verde_min: 6,
          utilidad_km_amarillo_min: 3,
          conversion_verde_min: 32,
          conversion_amarillo_min: 22,
          vencida_verde_max: 18,
          vencida_amarillo_max: 30,
          carga_verde_min: 82,
          carga_amarillo_min: 68,
        },
        operacion: {
          margen_verde_min: 14,
          margen_amarillo_min: 8,
          utilidad_km_verde_min: 4,
          utilidad_km_amarillo_min: 2,
          conversion_verde_min: 25,
          conversion_amarillo_min: 18,
          vencida_verde_max: 22,
          vencida_amarillo_max: 35,
          carga_verde_min: 88,
          carga_amarillo_min: 75,
        },
        cobranza: {
          margen_verde_min: 15,
          margen_amarillo_min: 9,
          utilidad_km_verde_min: 5,
          utilidad_km_amarillo_min: 2.5,
          conversion_verde_min: 30,
          conversion_amarillo_min: 20,
          vencida_verde_max: 15,
          vencida_amarillo_max: 25,
          carga_verde_min: 78,
          carga_amarillo_min: 65,
        },
      };
    }

    function getDireccionThresholds() {
      const base = defaultDireccionThresholds();
      if (direccionThresholdsCache) {
        return { ...base, ...direccionThresholdsCache };
      }
      try {
        const raw = localStorage.getItem(DIRECCION_THRESHOLDS_KEY);
        if (!raw) return base;
        const parsed = JSON.parse(raw);
        const merged = { ...base, ...parsed };
        direccionThresholdsCache = merged;
        return merged;
      } catch (_error) {
        return base;
      }
    }

    function setDireccionThresholds(nextCfg) {
      direccionThresholdsCache = { ...nextCfg };
      localStorage.setItem(DIRECCION_THRESHOLDS_KEY, JSON.stringify(nextCfg));
    }

    function getDireccionThresholdHistory() {
      if (Array.isArray(direccionThresholdHistoryCache) && direccionThresholdHistoryCache.length) {
        return [...direccionThresholdHistoryCache];
      }
      try {
        const raw = localStorage.getItem(DIRECCION_THRESHOLDS_HISTORY_KEY);
        if (!raw) return [];
        const parsed = JSON.parse(raw);
        const rows = Array.isArray(parsed) ? parsed : [];
        direccionThresholdHistoryCache = rows;
        return rows;
      } catch (_error) {
        return [];
      }
    }

    function pushDireccionThresholdHistory(entry) {
      const history = getDireccionThresholdHistory();
      history.unshift(entry);
      direccionThresholdHistoryCache = history.slice(0, 20);
      localStorage.setItem(DIRECCION_THRESHOLDS_HISTORY_KEY, JSON.stringify(history.slice(0, 20)));
    }

    async function loadDireccionThresholdsFromApi() {
      try {
        const data = await api("/direccion/reportes/thresholds");
        const thresholds = data?.thresholds || null;
        if (thresholds && typeof thresholds === "object") {
          setDireccionThresholds({ ...defaultDireccionThresholds(), ...thresholds });
        }
        const history = Array.isArray(data?.history) ? data.history : [];
        direccionUserOverrideAllowed = data?.user_override_allowed !== false;
        direccionThresholdEditAllowed = data?.edit_allowed !== false;
        const winMsgEl = document.getElementById("direccion-threshold-edit-window-msg");
        if (winMsgEl) {
          if (data?.edit_window_enabled && data?.edit_allowed === false) {
            winMsgEl.style.display = "block";
            winMsgEl.textContent = data?.edit_blocked_reason || "Operación cerrada para edición de umbrales.";
          } else {
            winMsgEl.style.display = "none";
            winMsgEl.textContent = "";
          }
        }
        direccionThresholdHistoryCache = history.map((x) => ({
          at: x?.created_at || "",
          mode: x?.mode || "manual",
          changes: Array.isArray(x?.changes) ? x.changes : [],
        }));
        localStorage.setItem(DIRECCION_THRESHOLDS_HISTORY_KEY, JSON.stringify(direccionThresholdHistoryCache));
      } catch (_error) {
        // fallback a localStorage para no romper UI si backend no está disponible.
      }
    }

    async function saveDireccionThresholdsToApi(nextCfg, mode) {
      try {
        const payload = {
          mode: String(mode || "manual"),
          thresholds: nextCfg,
        };
        const data = await api("/direccion/reportes/thresholds", {
          method: "PUT",
          body: JSON.stringify(payload),
        });
        const thresholds = data?.thresholds || null;
        if (thresholds && typeof thresholds === "object") {
          setDireccionThresholds({ ...defaultDireccionThresholds(), ...thresholds });
        }
        const history = Array.isArray(data?.history) ? data.history : [];
        direccionThresholdHistoryCache = history.map((x) => ({
          at: x?.created_at || "",
          mode: x?.mode || "manual",
          changes: Array.isArray(x?.changes) ? x.changes : [],
        }));
        localStorage.setItem(DIRECCION_THRESHOLDS_HISTORY_KEY, JSON.stringify(direccionThresholdHistoryCache));
        return { ok: true, forbidden: false, locked: false };
      } catch (error) {
        const msg = String(error?.message || "");
        if (msg.toLowerCase().includes("bloquea override")) {
          direccionUserOverrideAllowed = false;
          return { ok: false, forbidden: true, locked: false };
        }
        if (msg.includes("Operación cerrada") || msg.includes("Operacion cerrada")) {
          return { ok: false, forbidden: false, locked: true, lockedMessage: msg };
        }
        return { ok: false, forbidden: false, locked: false };
      }
    }

    function hydrateDireccionThresholdsForm() {
      const form = document.getElementById("direccion-umbrales-form");
      if (!form) return;
      const cfg = getDireccionThresholds();
      Object.entries(cfg).forEach(([key, value]) => {
        if (form.elements[key]) {
          form.elements[key].value = String(value);
        }
      });
      const submitBtn = form.querySelector('button[type="submit"]');
      const canEditUmbrales = direccionUserOverrideAllowed && direccionThresholdEditAllowed;
      if (submitBtn) {
        submitBtn.disabled = !canEditUmbrales;
        if (!direccionUserOverrideAllowed) {
          submitBtn.title = "La política del rol bloquea override por usuario.";
        } else if (!direccionThresholdEditAllowed) {
          submitBtn.title = "Operación cerrada: fuera de la ventana de edición de umbrales.";
        } else {
          submitBtn.title = "";
        }
      }
      const presetIds = [
        "direccion-threshold-preset-ceo-btn",
        "direccion-threshold-preset-operacion-btn",
        "direccion-threshold-preset-cobranza-btn",
        "direccion-threshold-reset-btn",
      ];
      presetIds.forEach((id) => {
        const el = document.getElementById(id);
        if (!el) return;
        el.disabled = !canEditUmbrales;
        if (!canEditUmbrales) {
          el.title = !direccionUserOverrideAllowed
            ? "La política del rol bloquea override por usuario."
            : "Operación cerrada: fuera de la ventana de edición de umbrales.";
        } else {
          el.title = "";
        }
      });
    }

    function renderDireccionThresholdHistory() {
      const box = document.getElementById("direccion-threshold-history");
      if (!box) return;
      const rows = getDireccionThresholdHistory();
      if (!rows.length) {
        box.innerHTML = '<div class="hint">Sin historial de umbrales.</div>';
        return;
      }
      const body = rows
        .map((item, idx) => {
          const when = escapeHtml(String(item?.at || ""));
          const mode = escapeHtml(String(item?.mode || "manual"));
          const changes = Array.isArray(item?.changes) ? item.changes : [];
          const changeText = changes.length ? changes.map((c) => escapeHtml(String(c))).join("<br>") : "Sin cambios";
          return `<tr><td>${idx + 1}</td><td>${when}</td><td>${mode}</td><td>${changeText}</td></tr>`;
        })
        .join("");
      box.innerHTML = `
        <table>
          <thead><tr><th>#</th><th>Fecha</th><th>Modo</th><th>Cambios</th></tr></thead>
          <tbody>${body}</tbody>
        </table>
      `;
    }

    function direccionThresholdDiff(beforeCfg, afterCfg) {
      return Object.keys(afterCfg)
        .filter((k) => Number(beforeCfg?.[k]) !== Number(afterCfg?.[k]))
        .map((k) => `${k}: ${beforeCfg?.[k]} -> ${afterCfg?.[k]}`);
    }

    function exportDireccionResumenEjecutivo() {
      const from = document.getElementById("direccion-desde")?.value || "";
      const to = document.getElementById("direccion-hasta")?.value || "";
      const resumen = document.getElementById("direccion-reporte-resumen-ejecutivo")?.textContent || "Sin resumen.";
      const alertas = document.getElementById("direccion-reporte-alertas")?.textContent || "Sin alertas.";
      const cfg = getDireccionThresholds();
      const lines = [
        `Resumen ejecutivo comité`,
        `Periodo: ${from} a ${to}`,
        "",
        resumen,
        "",
        alertas,
        "",
        "Umbrales activos:",
        ...Object.entries(cfg).map(([k, v]) => `- ${k}: ${v}`),
      ];
      const blob = new Blob([lines.join("\\n")], { type: "text/plain;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `direccion_resumen_comite_${from || "desde"}_${to || "hasta"}.txt`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    }

    async function refreshDireccionCommitteeSnapshots() {
      const box = document.getElementById("direccion-snapshot-list");
      if (!box) return;
      try {
        const data = await api("/direccion/reportes/committee/snapshots?limit=16");
        const items = Array.isArray(data?.items) ? data.items : [];
        if (!items.length) {
          box.innerHTML = '<div class="hint">Sin snapshots registrados.</div>';
          return;
        }
        const rows = items
          .map(
            (it) => `
              <tr>
                <td>${escapeHtml(String(it.week_start || ""))}</td>
                <td>${escapeHtml(String(it.week_end || ""))}</td>
                <td>${escapeHtml(String(it.created_at || ""))}</td>
                <td>${it.created_by_user_id != null ? Number(it.created_by_user_id) : "—"}</td>
              </tr>`
          )
          .join("");
        box.innerHTML = `
          <table>
            <thead><tr><th>Semana inicio</th><th>Semana fin</th><th>Creado</th><th>Usuario</th></tr></thead>
            <tbody>${rows}</tbody>
          </table>`;
      } catch (_error) {
        box.innerHTML = '<div class="hint">No se pudo cargar la lista de snapshots.</div>';
      }
    }

    async function initDireccionRoleThresholdAdmin() {
      const wrap = document.getElementById("direccion-role-threshold-admin");
      const role = String(window.__SIFE_ROLE_NAME__ || "").trim().toLowerCase();
      const hasJwt = !!sessionStorage.getItem("sife_access_token");
      if (!wrap) return;
      if (!hasJwt || role !== "admin") {
        wrap.style.display = "none";
        return;
      }
      wrap.style.display = "";
      const select = document.getElementById("direccion-threshold-role-select");
      const loadBtn = document.getElementById("direccion-threshold-role-load-btn");
      const applyBtn = document.getElementById("direccion-threshold-role-apply-btn");
      const policyToggle = document.getElementById("direccion-threshold-role-override-toggle");
      const savePolicyBtn = document.getElementById("direccion-threshold-role-policy-save-btn");
      const clearOverridesBtn = document.getElementById("direccion-threshold-role-clear-overrides-btn");
      const msg = document.getElementById("direccion-role-threshold-message");
      const govWrap = document.getElementById("direccion-role-threshold-governance");
      const usersWrap = document.getElementById("direccion-role-threshold-users");
      if (!select || !loadBtn || !applyBtn || !policyToggle || !savePolicyBtn || !clearOverridesBtn) return;
      const refreshGovernance = async () => {
        if (!govWrap) return;
        try {
          const data = await api("/direccion/reportes/thresholds/governance");
          const items = Array.isArray(data?.items) ? data.items : [];
          if (!items.length) {
            govWrap.innerHTML = '<div class="hint">Sin datos de gobierno.</div>';
            return;
          }
          const rows = items
            .map(
              (it) => `
                <tr>
                  <td>${escapeHtml(String(it?.role_name || ""))}</td>
                  <td>${it?.has_role_thresholds ? "Sí" : "No"}</td>
                  <td>${it?.user_override_allowed ? "Permitido" : "Bloqueado"}</td>
                </tr>
              `
            )
            .join("");
          govWrap.innerHTML = `
            <table>
              <thead><tr><th>Rol</th><th>Umbrales rol</th><th>Override usuario</th></tr></thead>
              <tbody>${rows}</tbody>
            </table>
          `;
        } catch (_error) {
          govWrap.innerHTML = '<div class="hint">No se pudo cargar gobierno de umbrales.</div>';
        }
      };
      const refreshGovernanceUsers = async () => {
        if (!usersWrap) return;
        const roleName = String(select.value || "").trim().toLowerCase();
        if (!roleName) {
          usersWrap.innerHTML = '<div class="hint">Seleccione un rol para ver cumplimiento por usuario.</div>';
          return;
        }
        try {
          const data = await api(`/direccion/reportes/thresholds/governance/users?role_name=${encodeURIComponent(roleName)}`);
          const items = Array.isArray(data?.items) ? data.items : [];
          if (!items.length) {
            usersWrap.innerHTML = '<div class="hint">Sin usuarios para este rol.</div>';
            return;
          }
          const rows = items
            .map(
              (it) => `
                <tr>
                  <td>${Number(it?.user_id || 0)}</td>
                  <td>${escapeHtml(String(it?.username || ""))}</td>
                  <td>${it?.is_active ? "Sí" : "No"}</td>
                  <td>${it?.has_user_override ? "Sí" : "No"}</td>
                  <td>${it?.user_override_allowed ? "Permitido" : "Bloqueado"}</td>
                  <td>${escapeHtml(String(it?.effective_source || ""))}</td>
                </tr>
              `
            )
            .join("");
          usersWrap.innerHTML = `
            <table>
              <thead><tr><th>ID</th><th>Usuario</th><th>Activo</th><th>Override</th><th>Política</th><th>Fuente efectiva</th></tr></thead>
              <tbody>${rows}</tbody>
            </table>
          `;
        } catch (_error) {
          usersWrap.innerHTML = '<div class="hint">No se pudo cargar cumplimiento por usuario.</div>';
        }
      };
      if (!select.dataset.loaded) {
        try {
          const roles = await api("/usuarios/roles");
          const rows = Array.isArray(roles) ? roles : [];
          select.innerHTML = rows
            .map((r) => {
              const name = String(r?.name || "").trim();
              if (!name) return "";
              return `<option value="${escapeHtml(name.toLowerCase())}">${escapeHtml(name)}</option>`;
            })
            .join("");
          select.dataset.loaded = "true";
        } catch (error) {
          if (msg) msg.textContent = error?.message || "No se pudo cargar catálogo de roles.";
        }
        await refreshGovernance();
      }
      if (loadBtn.dataset.bound !== "true") {
        loadBtn.dataset.bound = "true";
        loadBtn.addEventListener("click", async () => {
          const roleName = String(select.value || "").trim().toLowerCase();
          if (!roleName) return;
          if (msg) msg.textContent = "";
          try {
            const data = await api(`/direccion/reportes/thresholds/role/${encodeURIComponent(roleName)}`);
            const cfg = data?.thresholds || {};
            setDireccionThresholds({ ...defaultDireccionThresholds(), ...cfg });
            hydrateDireccionThresholdsForm();
            const policy = await api(`/direccion/reportes/thresholds/policy/${encodeURIComponent(roleName)}`);
            policyToggle.checked = !!policy?.user_override_allowed;
            if (msg) msg.textContent = `Umbrales del rol ${roleName} cargados. Fuente: ${data?.source || "role"}.`;
            await refreshDireccionReporteCompleto();
            await refreshGovernanceUsers();
          } catch (error) {
            if (msg) msg.textContent = error?.message || "No se pudo cargar umbrales del rol.";
          }
        });
      }
      if (applyBtn.dataset.bound !== "true") {
        applyBtn.dataset.bound = "true";
        applyBtn.addEventListener("click", async () => {
          const roleName = String(select.value || "").trim().toLowerCase();
          if (!roleName) return;
          if (msg) msg.textContent = "";
          try {
            const cfg = getDireccionThresholds();
            await api(`/direccion/reportes/thresholds/role/${encodeURIComponent(roleName)}`, {
              method: "PUT",
              body: JSON.stringify({
                mode: "admin_role_update",
                thresholds: cfg,
              }),
            });
            if (msg) msg.textContent = `Umbrales actuales aplicados al rol ${roleName}.`;
            await refreshGovernance();
          } catch (error) {
            if (msg) msg.textContent = error?.message || "No se pudo aplicar umbrales al rol.";
          }
        });
      }
      if (savePolicyBtn.dataset.bound !== "true") {
        savePolicyBtn.dataset.bound = "true";
        savePolicyBtn.addEventListener("click", async () => {
          const roleName = String(select.value || "").trim().toLowerCase();
          if (!roleName) return;
          if (msg) msg.textContent = "";
          try {
            await api(`/direccion/reportes/thresholds/policy/${encodeURIComponent(roleName)}`, {
              method: "PUT",
              body: JSON.stringify({ user_override_allowed: !!policyToggle.checked }),
            });
            if (msg) {
              msg.textContent = `Política del rol ${roleName} guardada. Override por usuario: ${
                policyToggle.checked ? "permitido" : "bloqueado"
              }.`;
            }
            await refreshGovernance();
            await refreshGovernanceUsers();
          } catch (error) {
            if (msg) msg.textContent = error?.message || "No se pudo guardar política de rol.";
          }
        });
      }
      if (clearOverridesBtn.dataset.bound !== "true") {
        clearOverridesBtn.dataset.bound = "true";
        clearOverridesBtn.addEventListener("click", async () => {
          const roleName = String(select.value || "").trim().toLowerCase();
          if (!roleName) return;
          if (msg) msg.textContent = "";
          try {
            const data = await api(`/direccion/reportes/thresholds/role/${encodeURIComponent(roleName)}/clear-user-overrides`, {
              method: "POST",
            });
            if (msg) {
              msg.textContent = `Overrides eliminados para rol ${roleName}: ${Number(data?.deleted_user_overrides || 0)}.`;
            }
            await refreshGovernanceUsers();
          } catch (error) {
            if (msg) msg.textContent = error?.message || "No se pudo limpiar overrides de usuarios.";
          }
        });
      }
      await refreshGovernance();
      await refreshGovernanceUsers();
    }

    async function refreshDireccionDashboard() {
      const fromInput = document.getElementById("direccion-desde");
      const toInput = document.getElementById("direccion-hasta");
      if (!fromInput || !toInput) {
        return;
      }
      const range = ensureDireccionDateRange(fromInput, toInput, "direccion-message");
      if (!range) {
        return;
      }
      const q = new URLSearchParams({
        desde: range.from,
        hasta: range.to,
      });
      clearMessage("direccion-message");
      try {
        const data = await api(`/direccion/dashboard?${q.toString()}`);
        renderDireccionDashboard(data);
        try {
          await refreshDireccionReporteCompleto();
        } catch (_reportError) {
          // El tablero clásico debe mantenerse funcional aunque falle el bloque integral.
        }
        await refreshDireccionResumenSemanal();
        await refreshDireccionHistoricoSemanal();
        await Promise.all([refreshDireccionIncidencias(), refreshDireccionAcciones()]);
        setMessage("direccion-message", `Rango consultado: ${data.desde} a ${data.hasta}.`, "ok");
      } catch (error) {
        setMessage("direccion-message", error?.message || "No se pudo cargar tablero de dirección.", "error");
      }
    }

    async function refreshDireccionResumenSemanal() {
      const fromInput = document.getElementById("direccion-desde");
      const toInput = document.getElementById("direccion-hasta");
      const resumenEl = document.getElementById("direccion-resumen-texto");
      const riesgosEl = document.getElementById("direccion-riesgos-texto");
      if (!fromInput || !toInput || !resumenEl || !riesgosEl) {
        return;
      }
      const range = ensureDireccionDateRange(fromInput, toInput, "direccion-message");
      if (!range) return;
      try {
        const q = new URLSearchParams({ desde: range.from, hasta: range.to });
        const data = await api(`/direccion/resumen-semanal?${q.toString()}`);
        resumenEl.textContent = data?.mensaje || "Sin resumen disponible.";
        const crit = Number(data?.riesgos?.incidencias_criticas_abiertas || 0);
        const pend = Number(data?.riesgos?.acciones_pendientes || 0);
        const total = Number(data?.riesgos?.acciones_total || 0);
        riesgosEl.textContent = `Riesgos: ${crit} incidencias críticas/altas abiertas; ${pend} acciones pendientes de ${total} registradas.`;
      } catch (error) {
        resumenEl.textContent = "No se pudo generar el resumen semanal.";
        riesgosEl.textContent = error?.message || "";
      }
    }

    function renderDireccionHistorico(data) {
      const svg = document.getElementById("direccion-historico-chart");
      const tableWrap = document.getElementById("direccion-historico-tabla");
      const items = Array.isArray(data?.items) ? data.items : [];
      if (!svg || !tableWrap) return;
      if (!items.length) {
        svg.innerHTML = "";
        tableWrap.innerHTML = '<div class="hint">Sin histórico semanal disponible.</div>';
        return;
      }

      const W = 720;
      const H = 220;
      const p = { l: 44, r: 16, t: 16, b: 32 };
      const pw = W - p.l - p.r;
      const ph = H - p.t - p.b;
      const maxY = Math.max(
        1,
        ...items.map((x) => Number(x.despachos_cerrados || 0)),
        ...items.map((x) => Number(x.facturas_emitidas || 0))
      );
      const stepX = items.length > 1 ? pw / (items.length - 1) : 0;
      const xAt = (i) => p.l + stepX * i;
      const yAt = (v) => p.t + (1 - Number(v || 0) / maxY) * ph;
      const mkPath = (key) =>
        items
          .map((it, idx) => `${idx === 0 ? "M" : "L"} ${xAt(idx).toFixed(1)} ${yAt(it[key]).toFixed(1)}`)
          .join(" ");

      const despPath = mkPath("despachos_cerrados");
      const facPath = mkPath("facturas_emitidas");
      const xTicks = items
        .map((it, idx) => {
          const label = String(it.week_start || "").slice(5);
          return `<text x="${xAt(idx).toFixed(1)}" y="${H - 10}" font-size="10" text-anchor="middle" fill="#64748b">${label}</text>`;
        })
        .join("");

      svg.innerHTML = `
        <rect x="0" y="0" width="${W}" height="${H}" fill="#ffffff"></rect>
        <line x1="${p.l}" y1="${p.t + ph}" x2="${W - p.r}" y2="${p.t + ph}" stroke="#cbd5e1" stroke-width="1"></line>
        <line x1="${p.l}" y1="${p.t}" x2="${p.l}" y2="${p.t + ph}" stroke="#cbd5e1" stroke-width="1"></line>
        <path d="${despPath}" fill="none" stroke="#0b6ead" stroke-width="2.5"></path>
        <path d="${facPath}" fill="none" stroke="#0f766e" stroke-width="2.5"></path>
        <text x="${p.l}" y="${p.t - 4}" font-size="10" fill="#64748b">Volumen semanal (máx ${maxY})</text>
        <text x="${W - p.r - 170}" y="${p.t + 12}" font-size="10" fill="#0b6ead">● Despachos cerrados</text>
        <text x="${W - p.r - 170}" y="${p.t + 26}" font-size="10" fill="#0f766e">● Facturas emitidas</text>
        ${xTicks}
      `;

      const rows = items
        .map(
          (it) => `
            <tr>
              <td>${escapeHtml(it.week_start || "")}</td>
              <td>${escapeHtml(it.week_end || "")}</td>
              <td>${Number(it.despachos_cerrados || 0)}</td>
              <td>${Number(it.facturas_emitidas || 0)}</td>
              <td>${Number(it.despacho_a_factura_pct || 0).toFixed(2)}%</td>
              <td>${semaforoLabel(it?.semaforo?.operacion)}</td>
              <td>${semaforoLabel(it?.semaforo?.cobranza)}</td>
            </tr>
          `
        )
        .join("");
      tableWrap.innerHTML = `
        <table>
          <thead><tr><th>Semana inicio</th><th>Semana fin</th><th>Despachos cerrados</th><th>Facturas emitidas</th><th>Despacho->Factura</th><th>Operación</th><th>Cobranza</th></tr></thead>
          <tbody>${rows}</tbody>
        </table>
      `;
    }

    async function refreshDireccionHistoricoSemanal() {
      try {
        const data = await api("/direccion/historico-semanal?semanas=8");
        renderDireccionHistorico(data);
      } catch (_error) {
        renderDireccionHistorico({ items: [] });
      }
    }

    function renderDireccionIncidencias(items) {
      const box = document.getElementById("direccion-incidencias-lista");
      if (!box) return;
      if (!items || items.length === 0) {
        box.innerHTML = '<div class="hint">Sin incidencias en el rango seleccionado.</div>';
        return;
      }
      const rows = items
        .map(
          (it) => `
            <tr data-incidencia-id="${it.id}">
              <td>${it.id}</td>
              <td>${escapeHtml(it.fecha_detectada || "")}</td>
              <td>${escapeHtml(it.modulo || "")}</td>
              <td>${escapeHtml(it.titulo || "")}</td>
              <td>
                <select data-incidencia-severidad>
                  ${["baja", "media", "alta", "critica"]
                    .map((x) => `<option value="${x}" ${x === it.severidad ? "selected" : ""}>${x}</option>`)
                    .join("")}
                </select>
              </td>
              <td>
                <select data-incidencia-estatus>
                  ${["abierta", "en_progreso", "resuelta"]
                    .map((x) => `<option value="${x}" ${x === it.estatus ? "selected" : ""}>${x}</option>`)
                    .join("")}
                </select>
              </td>
              <td><input data-incidencia-responsable value="${escapeHtml(it.responsable || "")}" /></td>
              <td><button type="button" class="secondary-button" data-incidencia-save>Guardar</button></td>
            </tr>
          `
        )
        .join("");
      box.innerHTML = `
        <table>
          <thead>
            <tr>
              <th>ID</th><th>Fecha</th><th>Módulo</th><th>Título</th><th>Severidad</th><th>Estatus</th><th>Responsable</th><th></th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      `;
    }

    async function refreshDireccionIncidencias() {
      const fromInput = document.getElementById("direccion-desde");
      const toInput = document.getElementById("direccion-hasta");
      if (!fromInput || !toInput) return;
      const range = ensureDireccionDateRange(fromInput, toInput, "direccion-incidencia-message");
      if (!range) return;
      const q = new URLSearchParams({ desde: range.from, hasta: range.to });
      const rows = await api(`/direccion/incidencias?${q.toString()}`);
      renderDireccionIncidencias(rows);
    }

    function renderDireccionAcciones(items) {
      const box = document.getElementById("direccion-acciones-lista");
      if (!box) return;
      if (!items || items.length === 0) {
        box.innerHTML = '<div class="hint">Sin acciones para el rango semanal seleccionado.</div>';
        return;
      }
      const rows = items
        .map(
          (it) => `
            <tr data-accion-id="${it.id}">
              <td>${it.id}</td>
              <td>${escapeHtml(it.week_start || "")}</td>
              <td>${escapeHtml(it.week_end || "")}</td>
              <td>${escapeHtml(it.titulo || "")}</td>
              <td><input data-accion-owner value="${escapeHtml(it.owner || "")}" /></td>
              <td>
                <select data-accion-estatus>
                  ${["pendiente", "en_curso", "completada", "cancelada"]
                    .map((x) => `<option value="${x}" ${x === it.estatus ? "selected" : ""}>${x}</option>`)
                    .join("")}
                </select>
              </td>
              <td>${escapeHtml(it.impacto || "")}</td>
              <td>
                <button type="button" class="secondary-button" data-accion-save>Guardar</button>
                <button type="button" class="secondary-button" data-accion-close-impact style="margin-left:6px;">Cerrar impacto</button>
              </td>
            </tr>
          `
        )
        .join("");
      box.innerHTML = `
        <table>
          <thead>
            <tr>
              <th>ID</th><th>Semana inicio</th><th>Semana fin</th><th>Título</th><th>Responsable</th><th>Estatus</th><th>Impacto</th><th></th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      `;
    }

    async function refreshDireccionAcciones() {
      const fromInput = document.getElementById("direccion-desde");
      const toInput = document.getElementById("direccion-hasta");
      if (!fromInput || !toInput) return;
      const range = ensureDireccionDateRange(fromInput, toInput, "direccion-accion-message");
      if (!range) return;
      const q = new URLSearchParams({ week_start: range.from, week_end: range.to });
      const rows = await api(`/direccion/acciones?${q.toString()}`);
      renderDireccionAcciones(rows);
    }

    async function createActionFromGuardrail(regla, detalle, estado) {
      const status = String(estado || "").trim().toLowerCase();
      const ownerByRule = (r) => {
        const x = String(r || "").toLowerCase();
        if (x.includes("margen")) return "comercial";
        if (x.includes("pago") || x.includes("dso")) return "finanzas";
        if (x.includes("vacio") || x.includes("retorno")) return "operaciones";
        return "direccion";
      };
      const payload = {
        regla: String(regla || "guardrail").trim().toLowerCase(),
        motivo: String(detalle || "Guardrail detectado por tablero ejecutivo."),
        owner: ownerByRule(regla),
        impacto: status === "bloqueo" ? "Riesgo alto: bloqueo activo." : "Mitigación preventiva.",
        dias_compromiso: status === "bloqueo" ? 5 : 10,
      };
      return api("/direccion/acciones/from-guardrail", { method: "POST", body: JSON.stringify(payload) });
    }

    async function closeAccionImpacto(accionId) {
      const rawImpact = window.prompt("Impacto realizado (MXN):", "0");
      if (rawImpact === null) return null;
      const impacto = Number(String(rawImpact).replace(",", ".").trim());
      if (!Number.isFinite(impacto) || impacto < 0) {
        throw new Error("Impacto realizado inválido.");
      }
      const comentario = window.prompt("Comentario de cierre (obligatorio):", "");
      if (comentario === null) return null;
      const clean = String(comentario).trim();
      if (!clean || clean.length < 3) {
        throw new Error("Capture comentario de cierre con al menos 3 caracteres.");
      }
      return api(`/direccion/acciones/${Number(accionId)}/cerrar-impacto`, {
        method: "POST",
        body: JSON.stringify({
          impacto_realizado_mxn: impacto,
          comentario_cierre: clean,
          marcar_completada: true,
        }),
      });
    }

    async function createActionFromDestroyMargin(sourceType, sourceName, accionSugerida) {
      const ownerDefault = sourceType === "cliente" ? "comercial" : "operaciones";
      return api("/direccion/acciones/from-recommendation", {
        method: "POST",
        body: JSON.stringify({
          source_type: String(sourceType || "").trim().toLowerCase(),
          source_name: String(sourceName || "").trim(),
          accion_sugerida: String(accionSugerida || "").trim() || "Revisar estructura de margen y recotizar.",
          owner: ownerDefault,
          dias_compromiso: 7,
        }),
      });
    }

    function initDireccionModule() {
      const form = document.getElementById("direccion-filtros-form");
      const fromInput = document.getElementById("direccion-desde");
      const toInput = document.getElementById("direccion-hasta");
      if (!form || !fromInput || !toInput) {
        return;
      }
      if (!toInput.value) {
        toInput.value = toISODateInput(new Date());
      }
      if (!fromInput.value) {
        const d = new Date();
        d.setDate(d.getDate() - 6);
        fromInput.value = toISODateInput(d);
      }
      const incForm = document.getElementById("direccion-incidencia-form");
      const accForm = document.getElementById("direccion-accion-form");
      const exportDashboardBtn = document.getElementById("direccion-export-dashboard-btn");
      const exportCompletoBtn = document.getElementById("direccion-export-completo-btn");
      const exportIncBtn = document.getElementById("direccion-export-incidencias-btn");
      const exportAccBtn = document.getElementById("direccion-export-acciones-btn");
      const umbralesForm = document.getElementById("direccion-umbrales-form");
      const presetCeoBtn = document.getElementById("direccion-threshold-preset-ceo-btn");
      const presetOperacionBtn = document.getElementById("direccion-threshold-preset-operacion-btn");
      const presetCobranzaBtn = document.getElementById("direccion-threshold-preset-cobranza-btn");
      const resetThresholdBtn = document.getElementById("direccion-threshold-reset-btn");
      const exportResumenBtn = document.getElementById("direccion-export-resumen-btn");
      const exportEstadoGuerraBtn = document.getElementById("direccion-export-estado-guerra-btn");
      const snapshotCreateBtn = document.getElementById("direccion-snapshot-create-btn");
      const snapshotRefreshBtn = document.getElementById("direccion-snapshot-refresh-btn");
      const guardrailsWrap = document.getElementById("direccion-reporte-guardrails");
      const destruyeMargenWrap = document.getElementById("direccion-reporte-destruye-margen");
      void (async () => {
        await loadDireccionThresholdsFromApi();
        hydrateDireccionThresholdsForm();
        renderDireccionThresholdHistory();
        await initDireccionRoleThresholdAdmin();
        await refreshDireccionCommitteeSnapshots();
      })();
      if (incForm && !incForm.dataset.defaultsSet) {
        const f = incForm;
        if (f.elements.fecha_detectada && !f.elements.fecha_detectada.value) {
          f.elements.fecha_detectada.value = toInput.value;
        }
        incForm.dataset.defaultsSet = "true";
      }
      if (accForm && !accForm.dataset.defaultsSet) {
        const f = accForm;
        if (f.elements.week_start) f.elements.week_start.value = fromInput.value;
        if (f.elements.week_end) f.elements.week_end.value = toInput.value;
        accForm.dataset.defaultsSet = "true";
      }
      if (form.dataset.bound === "true") {
        return;
      }
      form.dataset.bound = "true";
      form.addEventListener("submit", (event) => {
        event.preventDefault();
        void refreshDireccionDashboard();
      });
      if (exportDashboardBtn && exportDashboardBtn.dataset.bound !== "true") {
        exportDashboardBtn.dataset.bound = "true";
        exportDashboardBtn.addEventListener("click", async () => {
          clearMessage("direccion-message");
          const range = ensureDireccionDateRange(fromInput, toInput, "direccion-message");
          if (!range) return;
          try {
            const q = new URLSearchParams({ desde: range.from, hasta: range.to });
            await apiDownload(`/direccion/export/dashboard.csv?${q.toString()}`, "direccion_dashboard.csv");
            setMessage("direccion-message", "Exportación de dashboard iniciada.", "ok");
          } catch (error) {
            setMessage("direccion-message", error?.message || "No se pudo exportar dashboard.", "error");
          }
        });
      }
      if (exportCompletoBtn && exportCompletoBtn.dataset.bound !== "true") {
        exportCompletoBtn.dataset.bound = "true";
        exportCompletoBtn.addEventListener("click", async () => {
          clearMessage("direccion-message");
          const range = ensureDireccionDateRange(fromInput, toInput, "direccion-message");
          if (!range) return;
          try {
            const q = new URLSearchParams({ desde: range.from, hasta: range.to });
            await apiDownload(`/direccion/export/reportes-completo.csv?${q.toString()}`, "direccion_reporte_completo.csv");
            setMessage("direccion-message", "Exportación de reporte integral iniciada.", "ok");
          } catch (error) {
            setMessage("direccion-message", error?.message || "No se pudo exportar reporte integral.", "error");
          }
        });
      }
      if (exportIncBtn && exportIncBtn.dataset.bound !== "true") {
        exportIncBtn.dataset.bound = "true";
        exportIncBtn.addEventListener("click", async () => {
          clearMessage("direccion-incidencia-message");
          const range = ensureDireccionDateRange(fromInput, toInput, "direccion-incidencia-message");
          if (!range) return;
          try {
            const q = new URLSearchParams({ desde: range.from, hasta: range.to });
            await apiDownload(`/direccion/export/incidencias.csv?${q.toString()}`, "direccion_incidencias.csv");
            setMessage("direccion-incidencia-message", "Exportación de incidencias iniciada.", "ok");
          } catch (error) {
            setMessage("direccion-incidencia-message", error?.message || "No se pudo exportar incidencias.", "error");
          }
        });
      }
      if (exportAccBtn && exportAccBtn.dataset.bound !== "true") {
        exportAccBtn.dataset.bound = "true";
        exportAccBtn.addEventListener("click", async () => {
          clearMessage("direccion-accion-message");
          const range = ensureDireccionDateRange(fromInput, toInput, "direccion-accion-message");
          if (!range) return;
          try {
            const q = new URLSearchParams({ week_start: range.from, week_end: range.to });
            await apiDownload(`/direccion/export/acciones.csv?${q.toString()}`, "direccion_acciones.csv");
            setMessage("direccion-accion-message", "Exportación de acciones iniciada.", "ok");
          } catch (error) {
            setMessage("direccion-accion-message", error?.message || "No se pudo exportar acciones.", "error");
          }
        });
      }
      if (umbralesForm && umbralesForm.dataset.bound !== "true") {
        umbralesForm.dataset.bound = "true";
        umbralesForm.addEventListener("submit", async (event) => {
          event.preventDefault();
          const beforeCfg = getDireccionThresholds();
          const nextCfg = { ...defaultDireccionThresholds() };
          Object.keys(nextCfg).forEach((key) => {
            const raw = umbralesForm.elements[key] ? String(umbralesForm.elements[key].value || "").trim() : "";
            const n = Number(raw);
            if (Number.isFinite(n)) {
              nextCfg[key] = n;
            }
          });
          if (
            nextCfg.margen_verde_min < nextCfg.margen_amarillo_min ||
            nextCfg.utilidad_km_verde_min < nextCfg.utilidad_km_amarillo_min ||
            nextCfg.conversion_verde_min < nextCfg.conversion_amarillo_min ||
            nextCfg.vencida_verde_max > nextCfg.vencida_amarillo_max ||
            nextCfg.carga_verde_min < nextCfg.carga_amarillo_min
          ) {
            setMessage("direccion-message", "Revise umbrales: verde debe ser más estricto que amarillo.", "error");
            return;
          }
          setDireccionThresholds(nextCfg);
          const changes = direccionThresholdDiff(beforeCfg, nextCfg);
          const saveResult = await saveDireccionThresholdsToApi(nextCfg, "manual");
          if (!saveResult.ok && saveResult.forbidden) {
            setMessage("direccion-message", "La política del rol bloquea override de usuario.", "error");
            hydrateDireccionThresholdsForm();
            return;
          }
          if (!saveResult.ok && saveResult.locked) {
            setMessage(
              "direccion-message",
              saveResult.lockedMessage || "Operación cerrada: no se guardaron umbrales.",
              "error"
            );
            hydrateDireccionThresholdsForm();
            return;
          }
          if (!saveResult.ok) {
            pushDireccionThresholdHistory({
              at: new Date().toISOString(),
              mode: "manual",
              changes,
            });
          }
          renderDireccionThresholdHistory();
          setMessage("direccion-message", "Umbrales guardados. Recalculando semáforos...", "ok");
          try {
            await refreshDireccionReporteCompleto();
          } catch (_error) {
            // no-op
          }
        });
      }
      const applyPreset = async (presetName) => {
        const presets = direccionThresholdPresets();
        const preset = presets[presetName];
        if (!preset) return;
        const beforeCfg = getDireccionThresholds();
        setDireccionThresholds(preset);
        hydrateDireccionThresholdsForm();
        const changes = direccionThresholdDiff(beforeCfg, preset);
        const saveResult = await saveDireccionThresholdsToApi(preset, `preset_${presetName}`);
        if (!saveResult.ok && saveResult.forbidden) {
          if (msg) msg.textContent = "Política del rol bloquea override de usuario.";
          hydrateDireccionThresholdsForm();
          return;
        }
        if (!saveResult.ok && saveResult.locked) {
          setMessage(
            "direccion-message",
            saveResult.lockedMessage || "Operación cerrada: no se aplicó el preset.",
            "error"
          );
          hydrateDireccionThresholdsForm();
          return;
        }
        if (!saveResult.ok) {
          pushDireccionThresholdHistory({
            at: new Date().toISOString(),
            mode: `preset_${presetName}`,
            changes,
          });
        }
        renderDireccionThresholdHistory();
        setMessage("direccion-message", `Preset ${presetName.toUpperCase()} aplicado.`, "ok");
        try {
          await refreshDireccionReporteCompleto();
        } catch (_error) {
          // no-op
        }
      };
      if (presetCeoBtn && presetCeoBtn.dataset.bound !== "true") {
        presetCeoBtn.dataset.bound = "true";
        presetCeoBtn.addEventListener("click", () => {
          void applyPreset("ceo");
        });
      }
      if (presetOperacionBtn && presetOperacionBtn.dataset.bound !== "true") {
        presetOperacionBtn.dataset.bound = "true";
        presetOperacionBtn.addEventListener("click", () => {
          void applyPreset("operacion");
        });
      }
      if (presetCobranzaBtn && presetCobranzaBtn.dataset.bound !== "true") {
        presetCobranzaBtn.dataset.bound = "true";
        presetCobranzaBtn.addEventListener("click", () => {
          void applyPreset("cobranza");
        });
      }
      if (resetThresholdBtn && resetThresholdBtn.dataset.bound !== "true") {
        resetThresholdBtn.dataset.bound = "true";
        resetThresholdBtn.addEventListener("click", async () => {
          const beforeCfg = getDireccionThresholds();
          const base = defaultDireccionThresholds();
          setDireccionThresholds(base);
          hydrateDireccionThresholdsForm();
          const changes = direccionThresholdDiff(beforeCfg, base);
          const saveResult = await saveDireccionThresholdsToApi(base, "reset_base");
          if (!saveResult.ok && saveResult.forbidden) {
            setMessage("direccion-message", "Política del rol bloquea override de usuario.", "error");
            hydrateDireccionThresholdsForm();
            return;
          }
          if (!saveResult.ok && saveResult.locked) {
            setMessage(
              "direccion-message",
              saveResult.lockedMessage || "Operación cerrada: no se restauró la base en servidor.",
              "error"
            );
            hydrateDireccionThresholdsForm();
            return;
          }
          if (!saveResult.ok) {
            pushDireccionThresholdHistory({
              at: new Date().toISOString(),
              mode: "reset_base",
              changes,
            });
          }
          renderDireccionThresholdHistory();
          setMessage("direccion-message", "Umbrales restaurados a base.", "ok");
          void refreshDireccionReporteCompleto();
        });
      }
      if (exportResumenBtn && exportResumenBtn.dataset.bound !== "true") {
        exportResumenBtn.dataset.bound = "true";
        exportResumenBtn.addEventListener("click", () => {
          try {
            exportDireccionResumenEjecutivo();
            setMessage("direccion-message", "Resumen ejecutivo exportado.", "ok");
          } catch (_error) {
            setMessage("direccion-message", "No se pudo exportar el resumen ejecutivo.", "error");
          }
        });
      }
      if (exportEstadoGuerraBtn && exportEstadoGuerraBtn.dataset.bound !== "true") {
        exportEstadoGuerraBtn.dataset.bound = "true";
        exportEstadoGuerraBtn.addEventListener("click", async () => {
          clearMessage("direccion-message");
          const range = ensureDireccionDateRange(fromInput, toInput, "direccion-message");
          if (!range) return;
          try {
            const q = new URLSearchParams({ desde: range.from, hasta: range.to });
            await apiDownload(`/direccion/export/estado-guerra.csv?${q.toString()}`, "direccion_estado_guerra.csv");
            setMessage("direccion-message", "Exportación de estado de guerra iniciada.", "ok");
          } catch (error) {
            setMessage("direccion-message", error?.message || "No se pudo exportar estado de guerra.", "error");
          }
        });
      }
      if (snapshotRefreshBtn && snapshotRefreshBtn.dataset.bound !== "true") {
        snapshotRefreshBtn.dataset.bound = "true";
        snapshotRefreshBtn.addEventListener("click", () => {
          void refreshDireccionCommitteeSnapshots();
        });
      }
      if (snapshotCreateBtn && snapshotCreateBtn.dataset.bound !== "true") {
        snapshotCreateBtn.dataset.bound = "true";
        snapshotCreateBtn.addEventListener("click", async () => {
          clearMessage("direccion-message");
          try {
            const data = await api("/direccion/reportes/committee/snapshot", { method: "POST" });
            const created = !!data?.created;
            setMessage(
              "direccion-message",
              created
                ? `Snapshot de comité creado (${data?.week_start || ""} → ${data?.week_end || ""}).`
                : `Ya existía snapshot para esa semana (${data?.week_start || ""}).`,
              "ok"
            );
            await refreshDireccionCommitteeSnapshots();
          } catch (error) {
            setMessage("direccion-message", error?.message || "No se pudo crear el snapshot.", "error");
          }
        });
      }
      if (guardrailsWrap && guardrailsWrap.dataset.bound !== "true") {
        guardrailsWrap.dataset.bound = "true";
        guardrailsWrap.addEventListener("click", async (event) => {
          const btn = event.target.closest("[data-guardrail-action]");
          if (!btn) return;
          clearMessage("direccion-message");
          const regla = btn.dataset.regla || "guardrail";
          const detalle = btn.dataset.detalle || "Guardrail detectado por tablero ejecutivo.";
          const estado = btn.dataset.estado || "";
          try {
            const action = await createActionFromGuardrail(regla, detalle, estado);
            setMessage("direccion-message", `Acción correctiva #${Number(action?.id || 0)} creada desde guardrail.`, "ok");
            await refreshDireccionAcciones();
            await refreshDireccionReporteCompleto();
          } catch (error) {
            setMessage("direccion-message", error?.message || "No se pudo crear acción desde guardrail.", "error");
          }
        });
      }
      if (destruyeMargenWrap && destruyeMargenWrap.dataset.bound !== "true") {
        destruyeMargenWrap.dataset.bound = "true";
        destruyeMargenWrap.addEventListener("click", async (event) => {
          const btn = event.target.closest("[data-dm-action]");
          if (!btn) return;
          clearMessage("direccion-message");
          const sourceType = btn.dataset.sourceType || "";
          const sourceName = btn.dataset.sourceName || "";
          const accion = btn.dataset.accion || "";
          try {
            const created = await createActionFromDestroyMargin(sourceType, sourceName, accion);
            setMessage(
              "direccion-message",
              `Acción correctiva #${Number(created?.id || 0)} creada desde destruye-margen (${sourceType}).`,
              "ok"
            );
            await refreshDireccionAcciones();
            await refreshDireccionReporteCompleto();
          } catch (error) {
            setMessage("direccion-message", error?.message || "No se pudo crear acción desde destruye-margen.", "error");
          }
        });
      }

      if (incForm && incForm.dataset.bound !== "true") {
        incForm.dataset.bound = "true";
        incForm.addEventListener("submit", async (event) => {
          event.preventDefault();
          clearMessage("direccion-incidencia-message");
          const fd = new FormData(incForm);
          const payload = {
            titulo: String(fd.get("titulo") || "").trim(),
            modulo: String(fd.get("modulo") || "general").trim(),
            severidad: String(fd.get("severidad") || "media"),
            estatus: String(fd.get("estatus") || "abierta"),
            fecha_detectada: String(fd.get("fecha_detectada") || ""),
            detalle: String(fd.get("detalle") || "").trim() || null,
            responsable: String(fd.get("responsable") || "").trim() || null,
          };
          if (!payload.fecha_detectada) {
            setMessage("direccion-incidencia-message", "Capture la fecha detectada de la incidencia.", "error");
            return;
          }
          try {
            await api("/direccion/incidencias", { method: "POST", body: JSON.stringify(payload) });
            setMessage("direccion-incidencia-message", "Incidencia registrada.", "ok");
            incForm.reset();
            if (incForm.elements.fecha_detectada) incForm.elements.fecha_detectada.value = toInput.value;
            await refreshDireccionIncidencias();
            await refreshDireccionDashboard();
          } catch (error) {
            setMessage("direccion-incidencia-message", error?.message || "No se pudo registrar incidencia.", "error");
          }
        });
      }

      if (accForm && accForm.dataset.bound !== "true") {
        accForm.dataset.bound = "true";
        accForm.addEventListener("submit", async (event) => {
          event.preventDefault();
          clearMessage("direccion-accion-message");
          const fd = new FormData(accForm);
          const payload = {
            week_start: String(fd.get("week_start") || ""),
            week_end: String(fd.get("week_end") || ""),
            titulo: String(fd.get("titulo") || "").trim(),
            descripcion: String(fd.get("descripcion") || "").trim() || null,
            owner: String(fd.get("owner") || "").trim(),
            due_date: String(fd.get("due_date") || "").trim() || null,
            impacto: String(fd.get("impacto") || "").trim() || null,
            estatus: String(fd.get("estatus") || "pendiente"),
          };
          if (!payload.week_start || !payload.week_end) {
            setMessage("direccion-accion-message", "Capture semana inicio y semana fin para la acción.", "error");
            return;
          }
          if (payload.week_start > payload.week_end) {
            setMessage("direccion-accion-message", "Semana inicio no puede ser mayor que semana fin.", "error");
            return;
          }
          try {
            await api("/direccion/acciones", { method: "POST", body: JSON.stringify(payload) });
            setMessage("direccion-accion-message", "Acción guardada.", "ok");
            accForm.reset();
            if (accForm.elements.week_start) accForm.elements.week_start.value = fromInput.value;
            if (accForm.elements.week_end) accForm.elements.week_end.value = toInput.value;
            await refreshDireccionAcciones();
          } catch (error) {
            setMessage("direccion-accion-message", error?.message || "No se pudo guardar acción.", "error");
          }
        });
      }

      const incList = document.getElementById("direccion-incidencias-lista");
      if (incList && incList.dataset.bound !== "true") {
        incList.dataset.bound = "true";
        incList.addEventListener("click", async (event) => {
          const btn = event.target.closest("[data-incidencia-save]");
          if (!btn) return;
          const tr = btn.closest("tr[data-incidencia-id]");
          if (!tr) return;
          const id = Number(tr.dataset.incidenciaId);
          const severidad = tr.querySelector("[data-incidencia-severidad]")?.value || "media";
          const estatus = tr.querySelector("[data-incidencia-estatus]")?.value || "abierta";
          const responsable = tr.querySelector("[data-incidencia-responsable]")?.value || "";
          try {
            await api(`/direccion/incidencias/${id}`, {
              method: "PATCH",
              body: JSON.stringify({ severidad, estatus, responsable: String(responsable).trim() || null }),
            });
            setMessage("direccion-incidencia-message", `Incidencia #${id} actualizada.`, "ok");
            await refreshDireccionIncidencias();
            await refreshDireccionDashboard();
          } catch (error) {
            setMessage("direccion-incidencia-message", error?.message || "No se pudo actualizar incidencia.", "error");
          }
        });
      }

      const accList = document.getElementById("direccion-acciones-lista");
      if (accList && accList.dataset.bound !== "true") {
        accList.dataset.bound = "true";
        accList.addEventListener("click", async (event) => {
          const closeBtn = event.target.closest("[data-accion-close-impact]");
          if (closeBtn) {
            const trClose = closeBtn.closest("tr[data-accion-id]");
            if (!trClose) return;
            const closeId = Number(trClose.dataset.accionId);
            try {
              const updated = await closeAccionImpacto(closeId);
              if (!updated) return;
              setMessage("direccion-accion-message", `Acción #${closeId} cerrada con evidencia de impacto.`, "ok");
              await refreshDireccionAcciones();
              await refreshDireccionReporteCompleto();
            } catch (error) {
              setMessage("direccion-accion-message", error?.message || "No se pudo cerrar impacto de la acción.", "error");
            }
            return;
          }
          const btn = event.target.closest("[data-accion-save]");
          if (!btn) return;
          const tr = btn.closest("tr[data-accion-id]");
          if (!tr) return;
          const id = Number(tr.dataset.accionId);
          const owner = tr.querySelector("[data-accion-owner]")?.value || "";
          const estatus = tr.querySelector("[data-accion-estatus]")?.value || "pendiente";
          try {
            await api(`/direccion/acciones/${id}`, {
              method: "PATCH",
              body: JSON.stringify({ owner: String(owner).trim(), estatus }),
            });
            setMessage("direccion-accion-message", `Acción #${id} actualizada.`, "ok");
            await refreshDireccionAcciones();
          } catch (error) {
            setMessage("direccion-accion-message", error?.message || "No se pudo actualizar acción.", "error");
          }
        });
      }

      void refreshDireccionIncidencias().catch(() => {});
      void refreshDireccionAcciones().catch(() => {});
    }

    if (typeof window.sifePanelBoot === "function") {
      window.sifePanelBoot();
    } else {
      console.error("[SIFE panel] sifePanelBoot no disponible.");
    }
