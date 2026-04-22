    const panelBoot = window.__SIFE_PANEL_BOOT__ || {};
    const API_BASE = panelBoot.apiBase || "/api/v1";
    const API_KEY = panelBoot.apiKey || "";
    const state = {
      clientes: [],
      transportistas: [],
      viajes: [],
      fletes: [],
      facturas: [],
      gastos: [],
      tarifas: [],
      tarifasCompra: [],
      operadores: [],
      unidades: [],
      asignaciones: [],
      despachos: [],
      ordenesServicio: [],
      catalogLoaded: false,
      unidadesTotalServidor: null,
      catalogRefreshErrors: [],
    };

    const uiState = {
      clienteFilters: { buscar: "", activo: "" },
      transportistaFilters: { buscar: "", estatus: "", tipo_transportista: "" },
      viajeFilters: { buscar: "", estado: "" },
      fleteFilters: { buscar: "", estado: "", cliente_id: "", transportista_id: "" },
      facturaFilters: { buscar: "", cliente_id: "", estatus: "" },
      tarifaCompraFilters: { buscar: "", transportista_id: "", activo: "" },
      tarifaVentaFilters: { buscar: "" },
      gastoFilters: { buscar: "" },
      operadorFilters: { buscar: "" },
      unidadFilters: { buscar: "", tipo_propiedad: "", estatus_documental: "", activo: "" },
      asignacionFilters: { buscar: "", id_operador: "", id_unidad: "", id_viaje: "" },
      despachoFilters: { buscar: "", estatus: "", id_asignacion: "", id_flete: "" },
      ordenServicioFilters: { buscar: "", cliente_id: "", estatus: "" },
      buscarModo: "contiene",
      editing: {
        clienteId: null,
        clienteContactoId: null,
        clienteDomicilioId: null,
        transportistaId: null,
        transportistaContactoId: null,
        transportistaDocumentoId: null,
        viajeId: null,
        fleteId: null,
        facturaId: null,
        tarifaCompraId: null,
        tarifaFleteId: null,
        asignacionId: null,
        despachoId: null,
        gastoId: null,
        operadorId: null,
        unidadId: null,
      },
      clienteSubpage: "alta",
      transportistaSubpage: "consulta",
      viajeSubpage: "consulta",
      fleteSubpage: "consulta",
      facturaSubpage: "consulta",
      tarifaSubpage: "consulta",
      tarifaCompraSubpage: "consulta",
      operadorSubpage: "consulta",
      unidadSubpage: "consulta",
      gastoSubpage: "consulta",
      asignacionSubpage: "consulta",
      despachoSubpage: "consulta",
      seguimientoSubpage: "salida",
    };

    let lastTarifaCompraEditId = null;

    const pageMeta = {
      inicio: ["Inicio", "Resumen del sistema y accesos a cada modulo sin mezclar pantallas."],
      clientes: ["Clientes", "Alta, consulta, contactos, domicilios, condiciones y manual en pantalla con índice y visor."],
      transportistas: ["Transportistas", "Alta, consulta, contactos, documentos y manual en pantalla con índice y visor."],
      viajes: ["Viajes", "Alta, consulta y manual en pantalla con índice y visor."],
      fletes: ["Fletes", "Nuevo flete, consulta y edicion, ordenes de servicio (subpestaña) y manual en pantalla."],
      facturas: ["Facturas", "Alta, consulta y manual en pantalla con índice y visor."],
      gastos: ["Gastos viaje", "Alta, consulta, presupuesto estimado y liquidación vs real."],
      tarifas: ["Tarifa venta", "Alta, consulta y manual en pantalla con índice y visor."],
      "tarifas-compra": ["Tarifas compra", "Alta, consulta y manual en pantalla con índice y visor."],
      operadores: ["Operadores", "Alta, consulta con edición en panel y manual en pantalla."],
      unidades: ["Unidades", "Alta, consulta con filtros, edicion y eliminacion en panel; manual integrado."],
      asignaciones: ["Asignaciones", "Alta, consulta y manual en pantalla con índice y visor."],
      despachos: ["Despachos", "Alta, consulta y manual en pantalla con índice y visor."],
      "bajas-danos": ["Bajas y daños", "Registro de bajas operativas y daños a activo o carga con vínculo opcional a flete."],
      seguimiento: ["Seguimiento", "Salida, evento, entrega, cierre, cancelación y manual en pantalla con índice y visor."],
      direccion: ["Dirección", "Tablero ejecutivo con KPI, embudo, tiempos y semáforo operativo."],
      "usuarios-admin": [
        "Usuarios",
        "Cambio de contraseña propio; altas y permisos por rol (admin y direccion).",
      ],
      "audit-logs": [
        "Auditoría",
        "Consulta de trazabilidad por entidad, acción y actor (solo admin/dirección con JWT).",
      ],
    };

    const GASTO_CATEGORIA_LABELS = {
      combustible: "Combustible (diesel)",
      peajes: "Peajes / casetas",
      viaticos: "Viáticos operador",
      operador: "Mano de obra operador",
      mantenimiento_km: "Mantenimiento y desgaste (por km)",
      imprevistos: "Imprevistos",
      administrativos: "Administrativos del viaje",
      pago_transporte_tercero: "Pago a transportista",
      otros: "Otros",
    };

    function labelGastoCategoria(code) {
      return GASTO_CATEGORIA_LABELS[code] || code;
    }

    function setMessage(id, text, kind = "ok") {
      const node = document.getElementById(id);
      node.className = `message ${kind}`;
      node.textContent = text || "";
    }

    function clearMessage(id) {
      setMessage(id, "", "ok");
    }

    function clearCaptureFormFields(formId) {
      const form = document.getElementById(formId);
      if (!form) {
        return;
      }
      const fieldList =
        form.tagName === "FORM"
          ? [...form.elements]
          : [...form.querySelectorAll("input, select, textarea")];
      for (const field of fieldList) {
        if (!field || field.disabled) {
          continue;
        }
        const tagName = field.tagName || "";
        const type = (field.type || "").toLowerCase();
        if (tagName === "BUTTON" || type === "hidden") {
          continue;
        }
        if (type === "checkbox" || type === "radio") {
          field.checked = false;
          continue;
        }
        if (tagName === "SELECT") {
          if (field.multiple) {
            for (const option of field.options) {
              option.selected = false;
            }
          } else {
            field.selectedIndex = -1;
            field.value = "";
          }
          continue;
        }
        field.value = "";
      }
    }

    function installCaptureFormCancelButtons() {
      const captureForms = [
        { formId: "cliente-form", messageId: "cliente-message" },
        {
          formId: "cliente-domicilio-form",
          messageId: "cliente-domicilio-message",
          afterClear: () => {
            syncClienteModuleSummaries();
            renderClienteDomicilios();
          },
        },
        {
          formId: "cliente-condicion-form",
          messageId: "cliente-condicion-message",
          afterClear: () => {
            syncClienteModuleSummaries();
            renderClienteCondicion();
          },
        },
        { formId: "transportista-form", messageId: "transportista-message" },
        {
          formId: "transportista-contacto-form",
          messageId: "transportista-contacto-message",
          afterClear: () => renderTransportistaContactos(),
        },
        {
          formId: "transportista-documento-form",
          messageId: "transportista-documento-message",
          afterClear: () => renderTransportistaDocumentos(),
        },
        { formId: "viaje-form", messageId: "viaje-message" },
        {
          formId: "flete-form",
          messageId: "flete-message",
          afterClear: () => {
            const venta = document.getElementById("flete-cotizacion-detalle");
            const compra = document.getElementById("flete-cotizacion-compra-detalle");
            if (venta) {
              venta.textContent = "";
            }
            if (compra) {
              compra.textContent = "";
            }
          },
        },
        { formId: "factura-form", messageId: "factura-message" },
        { formId: "tarifa-form", messageId: "tarifa-message" },
        { formId: "tarifa-compra-form", messageId: "tarifa-compra-message" },
        { formId: "operador-form", messageId: "operador-message" },
        { formId: "unidad-form", messageId: "unidad-message" },
        { formId: "gasto-form", messageId: "gasto-message" },
        { formId: "asignacion-form", messageId: "asignacion-message" },
        { formId: "despacho-form", messageId: "despacho-message" },
        { formId: "salida-form", messageId: "salida-message" },
        { formId: "evento-form", messageId: "evento-message" },
        { formId: "entrega-form", messageId: "entrega-message" },
        { formId: "cierre-form", messageId: "cierre-message" },
        { formId: "cancelacion-form", messageId: "cancelacion-message" },
      ];

      for (const config of captureForms) {
        const form = document.getElementById(config.formId);
        if (!form || form.dataset.cancelInstalled === "true") {
          continue;
        }
        const submitButton =
          form.querySelector('button[type="submit"]') ||
          form.querySelector("button[data-primary-action='save']");
        if (!submitButton) {
          continue;
        }
        let actions = submitButton.parentElement;
        if (!actions || !actions.classList.contains("toolbar-actions")) {
          actions = document.createElement("div");
          actions.className = "toolbar-actions";
          submitButton.insertAdjacentElement("beforebegin", actions);
          actions.appendChild(submitButton);
        }
        const cancelButton = document.createElement("button");
        cancelButton.type = "button";
        cancelButton.className = "secondary-button";
        cancelButton.textContent = "Cancelar y limpiar";
        cancelButton.addEventListener("click", () => {
          clearCaptureFormFields(config.formId);
          clearMessage(config.messageId);
          if (typeof config.afterClear === "function") {
            config.afterClear();
          }
        });
        actions.appendChild(cancelButton);
        form.dataset.cancelInstalled = "true";
      }
    }

    function applyCaptureShellStyle() {
      const isCaptureForm = (form) => {
        const raw = form.getAttribute("id");
        const id = (raw == null ? "" : String(raw)).trim().toLowerCase();
        if (!id) {
          return false;
        }
        if (id.includes("filter")) {
          return false;
        }
        return true;
      };

      for (const form of document.querySelectorAll("form")) {
        if (!isCaptureForm(form)) {
          continue;
        }
        const shell =
          form.closest(".toolbar") ||
          form.closest("article.card") ||
          form.closest(".card");
        if (!shell || shell.classList.contains("manual-doc")) {
          continue;
        }
        shell.classList.add("capture-shell");
      }
    }

    function clean(value) {
      if (value === null || value === undefined) {
        return null;
      }
      const text = String(value).trim();
      return text === "" ? null : text;
    }

    const MONEY_LOCALE = "es-MX";

    /**
     * Convierte texto de captura (MXN y variantes habituales) a numero JS.
     * Acepta: 1,234.56 / 1.234,56 / 1234,56 / 1,234 / 1.234.567 / 0,001 / 12.3456
     */
    function parseLocaleNumber(value) {
      const text = clean(value);
      if (text === null) {
        return null;
      }
      let s = String(text)
        .trim()
        .replace(/^\\s*\\$\\s*/u, "")
        .replace(/\\u00a0|\\u202f/g, "")
        .replace(/mxn/gi, "")
        .replace(/\\s+/g, "")
        .replace(/'/g, "");
      if (s === "" || s === "-" || s === "." || s === ",") {
        return null;
      }
      let sign = 1;
      if (s.startsWith("-")) {
        sign = -1;
        s = s.slice(1);
      } else if (s.startsWith("+")) {
        s = s.slice(1);
      }
      s = s.replace(/[^\\d,.]/g, "");
      if (s === "" || s === "." || s === ",") {
        return null;
      }

      const lastComma = s.lastIndexOf(",");
      const lastDot = s.lastIndexOf(".");
      let normalized;

      if (lastComma >= 0 && lastDot >= 0) {
        if (lastComma > lastDot) {
          normalized = s.replace(/\\./g, "").replace(",", ".");
        } else {
          normalized = s.replace(/,/g, "");
        }
      } else if (lastComma >= 0) {
        const parts = s.split(",");
        if (parts.length === 2) {
          const left = parts[0].replace(/\\./g, "");
          const right = parts[1];
          if (/^\\d+$/.test(left) && /^\\d+$/.test(right) && right.length >= 1) {
            if (right.length <= 2) {
              normalized = `${left}.${right}`;
            } else if (left === "0") {
              normalized = `${left}.${right}`;
            } else if (right.length === 3 && left.length === 1) {
              normalized = `${left}${right}`;
            } else {
              normalized = `${left}.${right}`;
            }
          } else {
            normalized = s.replace(/,/g, "");
          }
        } else {
          normalized = s.replace(/,/g, "");
        }
      } else if (lastDot >= 0) {
        const parts = s.split(".");
        if (parts.length > 2) {
          normalized = parts.join("");
        } else {
          normalized = s;
        }
      } else {
        normalized = s;
      }

      if (normalized === "" || normalized === "." || normalized === "-") {
        return null;
      }
      const n = Number(normalized) * sign;
      return Number.isFinite(n) ? n : null;
    }

    function numberOrNull(value) {
      return parseLocaleNumber(value);
    }

    function formatLocaleDecimal(n, minFractionDigits, maxFractionDigits) {
      if (n === null || n === undefined || !Number.isFinite(Number(n))) {
        return "";
      }
      const num = Number(n);
      return new Intl.NumberFormat(MONEY_LOCALE, {
        minimumFractionDigits: minFractionDigits,
        maximumFractionDigits: maxFractionDigits,
        useGrouping: true,
      }).format(num);
    }

    function formatMoneyInputFromEl(n, input) {
      const minF = Math.max(0, parseInt(input.dataset.minFractionDigits ?? "2", 10));
      const maxRaw = parseInt(input.dataset.maxFractionDigits ?? "2", 10);
      const maxF = Math.max(minF, maxRaw);
      return formatLocaleDecimal(n, minF, maxF);
    }

    /** Mismo criterio que al salir del campo, pero sin separadores de miles (mas facil de editar al enfocar). */
    function formatPlainMoneyInputFromEl(n, input) {
      const minF = Math.max(0, parseInt(input.dataset.minFractionDigits ?? "2", 10));
      const maxRaw = parseInt(input.dataset.maxFractionDigits ?? "2", 10);
      const maxF = Math.max(minF, maxRaw);
      if (n === null || n === undefined || !Number.isFinite(Number(n))) {
        return "";
      }
      const num = Number(n);
      return new Intl.NumberFormat(MONEY_LOCALE, {
        minimumFractionDigits: minF,
        maximumFractionDigits: maxF,
        useGrouping: false,
      }).format(num);
    }

    function fmtMoneyList(value) {
      if (value === null || value === undefined || value === "") {
        return "—";
      }
      const n = Number(value);
      if (!Number.isFinite(n)) {
        return String(value);
      }
      return formatLocaleDecimal(n, 2, 2);
    }

    function fmtPctList(value) {
      if (value === null || value === undefined || value === "") {
        return "—";
      }
      const n = Number(value);
      if (!Number.isFinite(n)) {
        return String(value);
      }
      return `${formatLocaleDecimal(n, 2, 2)} %`;
    }

    function fmtTarifaList(value, maxFractionDigits) {
      if (value === null || value === undefined || value === "") {
        return "—";
      }
      const n = Number(value);
      if (!Number.isFinite(n)) {
        return String(value);
      }
      return formatLocaleDecimal(n, 0, maxFractionDigits);
    }

    function wireMoneyInputs(root = document) {
      for (const input of root.querySelectorAll("input.field-money")) {
        if (input.dataset.moneyWired === "1") {
          continue;
        }
        input.dataset.moneyWired = "1";
        input.addEventListener("focus", () => {
          const parsed = parseLocaleNumber(input.value);
          if (parsed === null) {
            return;
          }
          input.value = formatPlainMoneyInputFromEl(parsed, input);
          input.select();
        });
        input.addEventListener("blur", () => {
          const parsed = parseLocaleNumber(input.value);
          input.value = parsed === null ? "" : formatMoneyInputFromEl(parsed, input);
        });
      }
    }

    function applyMoneyFormatToForm(form) {
      if (!form) {
        return;
      }
      for (const input of form.querySelectorAll("input.field-money")) {
        const parsed = parseLocaleNumber(input.value);
        input.value = parsed === null ? "" : formatMoneyInputFromEl(parsed, input);
      }
    }

    /** Valor para input type="number" desde API (acepta coma decimal o miles; evita texto invalido). */
    function htmlNumberInputValue(value) {
      if (value == null || value === "") {
        return "";
      }
      const n = parseLocaleNumber(String(value));
      if (n === null || !Number.isFinite(n)) {
        return "";
      }
      return String(n);
    }

    /** Texto formateado es-MX para field-money al hidratar desde API sin elemento DOM. */
    function moneyFieldFromApi(value, minFractionDigits, maxFractionDigits) {
      const minF = Math.max(0, minFractionDigits ?? 2);
      const maxF = Math.max(minF, maxFractionDigits ?? 2);
      const n = parseLocaleNumber(value == null ? "" : String(value));
      if (n === null) {
        return "";
      }
      return formatLocaleDecimal(n, minF, maxF);
    }

    function integerOrNull(value) {
      const n = parseLocaleNumber(value);
      if (n === null || !Number.isFinite(n)) {
        return null;
      }
      return Math.trunc(n);
    }

    function requirePositiveIntOrThrow(raw, contexto) {
      const id = integerOrNull(raw);
      if (id === null || id < 1) {
        throw new Error(
          `${contexto}: identificador invalido. Cierra el panel de edicion, vuelve a abrirlo con Editar e intenta de nuevo.`,
        );
      }
      return id;
    }

    /** PK entero (sin reglas de miles/decimales de dinero). */
    function parsePositiveIntId(raw) {
      if (raw === null || raw === undefined) {
        return null;
      }
      if (typeof raw === "number" && Number.isFinite(raw)) {
        const t = Math.trunc(raw);
        return t >= 1 ? t : null;
      }
      const s = String(raw).trim();
      if (!s || s === "undefined" || s === "null") {
        return null;
      }
      const id = Number.parseInt(s, 10);
      return Number.isFinite(id) && id >= 1 ? id : null;
    }

    function requirePositiveIntIdOrThrow(raw, contexto) {
      const id = parsePositiveIntId(raw);
      if (id === null) {
        throw new Error(
          `${contexto}: identificador invalido. Cierra el panel de edicion, vuelve a abrirlo con Editar e intenta de nuevo.`,
        );
      }
      return id;
    }

    /** PK del flete en edición: oculto + estado + dataset + búsqueda por código (evita fallos tras refresh o IDs string/number). */
    function resolveFleteEditRecordId(formElement) {
      const idEl = document.getElementById("flete-edit-form-record-id");
      const fromHidden = idEl ? String(idEl.value || "").trim() : "";
      if (fromHidden && fromHidden !== "undefined" && fromHidden !== "null") {
        const n = integerOrNull(fromHidden);
        if (n !== null && n >= 1) {
          return String(n);
        }
      }
      if (formElement && formElement.dataset && formElement.dataset.sifeEditingFleteId) {
        const n = integerOrNull(String(formElement.dataset.sifeEditingFleteId).trim());
        if (n !== null && n >= 1) {
          return String(n);
        }
      }
      if (uiState.editing.fleteId != null && uiState.editing.fleteId !== "") {
        const n = Number(uiState.editing.fleteId);
        if (Number.isFinite(n) && n >= 1) {
          return String(Math.trunc(n));
        }
      }
      const codigo =
        formElement && formElement.elements && formElement.elements.codigo_flete
          ? clean(formElement.elements.codigo_flete.value)
          : null;
      if (codigo) {
        const row = state.fletes.find((f) => f.codigo_flete === codigo);
        if (row && row.id != null) {
          return String(row.id);
        }
      }
      return "";
    }

    /** PK del despacho en edicion: oculto + dataset + estado + id_asignacion en etiqueta (unica por despacho en BD). */
    function resolveDespachoEditRecordId(formElement) {
      const idEl = document.getElementById("despacho-edit-form-id");
      const fromHidden = idEl ? String(idEl.value || "").trim() : "";
      if (fromHidden && fromHidden !== "undefined" && fromHidden !== "null") {
        const n = parsePositiveIntId(fromHidden);
        if (n !== null) {
          return String(n);
        }
      }
      if (formElement && formElement.dataset && formElement.dataset.sifeEditingDespachoId) {
        const n = parsePositiveIntId(String(formElement.dataset.sifeEditingDespachoId).trim());
        if (n !== null) {
          return String(n);
        }
      }
      if (uiState.editing.despachoId != null && uiState.editing.despachoId !== "") {
        const n = parsePositiveIntId(uiState.editing.despachoId);
        if (n !== null) {
          return String(n);
        }
      }
      const label =
        formElement && formElement.elements && formElement.elements.asignacion_label
          ? clean(formElement.elements.asignacion_label.value)
          : "";
      const m = label.match(/^(\d+)\s*-\s*/);
      if (m) {
        const idAsig = Number.parseInt(m[1], 10);
        if (Number.isFinite(idAsig) && idAsig >= 1) {
          const row = state.despachos.find((d) => Number(d.id_asignacion) === idAsig);
          if (row && row.id_despacho != null) {
            const n = parsePositiveIntId(row.id_despacho);
            if (n !== null) {
              return String(n);
            }
          }
        }
      }
      return "";
    }

    function resyncFleteEditPkAfterRefresh() {
      if (uiState.editing.fleteId == null || uiState.editing.fleteId === "") {
        return;
      }
      const panel = document.getElementById("flete-edit-panel");
      if (!panel || panel.classList.contains("hidden")) {
        return;
      }
      const sid = String(uiState.editing.fleteId).trim();
      const idPk = document.getElementById("flete-edit-form-record-id");
      if (idPk) {
        idPk.value = sid;
      }
      const form = document.getElementById("flete-edit-form");
      if (form) {
        form.dataset.sifeEditingFleteId = sid;
      }
    }

    function resyncDespachoEditPkAfterRefresh() {
      if (uiState.editing.despachoId == null || uiState.editing.despachoId === "") {
        return;
      }
      const panel = document.getElementById("despacho-edit-panel");
      if (!panel || panel.classList.contains("hidden")) {
        return;
      }
      const sid = String(uiState.editing.despachoId).trim();
      const idPk = document.getElementById("despacho-edit-form-id");
      if (idPk) {
        idPk.value = sid;
      }
      const form = document.getElementById("despacho-edit-form");
      if (form) {
        form.dataset.sifeEditingDespachoId = sid;
      }
    }

    const SIFE_TARIFA_COMPRA_EDIT_ID_KEY = "sife_tarifa_compra_edit_id";

    function setTarifaCompraEditIdStorage(sid) {
      try {
        if (sid == null || String(sid).trim() === "") {
          sessionStorage.removeItem(SIFE_TARIFA_COMPRA_EDIT_ID_KEY);
        } else {
          sessionStorage.setItem(SIFE_TARIFA_COMPRA_EDIT_ID_KEY, String(sid).trim());
        }
      } catch (_e) {
        /* ignore (private mode, disabled storage) */
      }
    }

    function getTarifaCompraEditIdStorage() {
      try {
        return sessionStorage.getItem(SIFE_TARIFA_COMPRA_EDIT_ID_KEY);
      } catch (_e) {
        return null;
      }
    }

    function tarifaCompraEditIdForPatch(formElement) {
      if (formElement && formElement._sifeTarifaCompraId != null && formElement._sifeTarifaCompraId !== "") {
        const t0 = String(formElement._sifeTarifaCompraId).trim();
        if (t0 !== "" && t0 !== "undefined" && t0 !== "null") {
          return t0;
        }
      }
      const fromStorage = getTarifaCompraEditIdStorage();
      if (fromStorage != null && String(fromStorage).trim() !== "") {
        const ts = String(fromStorage).trim();
        if (ts !== "undefined" && ts !== "null") {
          return ts;
        }
      }
      const saveBtn = document.getElementById("tarifa-compra-edit-save");
      const hiddenEl = document.getElementById("tarifa-compra-edit-record-id");
      let winId = null;
      try {
        winId = typeof window !== "undefined" ? window.__SIFE_tarifaCompraEditId : null;
      } catch (_e) {
        winId = null;
      }
      const candidates = [
        lastTarifaCompraEditId,
        uiState.editing.tarifaCompraId,
        winId,
        saveBtn ? saveBtn.getAttribute("data-tarifa-compra-record-id") : null,
        hiddenEl ? hiddenEl.value : null,
        formElement ? formElement.getAttribute("data-tarifa-compra-id") : null,
      ];
      for (const c of candidates) {
        if (c == null) {
          continue;
        }
        const t = String(c).trim();
        if (t !== "" && t !== "undefined" && t !== "null") {
          return t;
        }
      }
      return null;
    }

    function normalizeDateOnlyForApi(value) {
      const text = clean(value);
      if (text === null) {
        return null;
      }
      let s = String(text).trim();
      if (s === "") {
        return null;
      }
      if (/^\d{4}-\d{2}-\d{2}$/.test(s)) {
        return s;
      }
      if (/^\d{4}-\d{2}-\d{2}[T\s]/.test(s)) {
        return s.slice(0, 10);
      }
      const mLoose = s.match(/^(\d{4})-(\d{1,2})-(\d{1,2})/);
      if (mLoose) {
        const yyyy = mLoose[1];
        const mm = mLoose[2].padStart(2, "0");
        const dd = mLoose[3].padStart(2, "0");
        const cand = `${yyyy}-${mm}-${dd}`;
        if (/^\d{4}-\d{2}-\d{2}$/.test(cand)) {
          return cand;
        }
      }
      const mSlash = s.match(/^(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})$/);
      if (mSlash) {
        const dd = mSlash[1].padStart(2, "0");
        const mm = mSlash[2].padStart(2, "0");
        const yyyy = mSlash[3];
        return `${yyyy}-${mm}-${dd}`;
      }
      return null;
    }

    function normalizeDateTimeForApi(value) {
      const text = clean(value);
      if (text === null) {
        return null;
      }
      let s = String(text).trim().replace(" ", "T");
      s = s.replace(/([+-]\d{2}(:\d{2})?|Z)$/i, "");
      if (s.includes(".")) {
        s = s.slice(0, s.indexOf("."));
      }
      if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(s)) {
        return `${s}:00`;
      }
      const mFull = s.match(/^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})/);
      if (mFull) {
        return mFull[1];
      }
      if (/^\d{4}-\d{2}-\d{2}$/.test(s)) {
        return `${s}T00:00:00`;
      }
      const m = s.match(
        /^(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})[T ](\d{1,2}):(\d{2})(?::(\d{2}))?/,
      );
      if (m) {
        const dd = m[1].padStart(2, "0");
        const mm = m[2].padStart(2, "0");
        const yyyy = m[3];
        const hh = m[4].padStart(2, "0");
        const min = m[5].padStart(2, "0");
        const ss = (m[6] || "00").padStart(2, "0");
        return `${yyyy}-${mm}-${dd}T${hh}:${min}:${ss}`;
      }
      return null;
    }

    function toDateInputValue(value) {
      if (value == null || value === "") {
        return "";
      }
      if (typeof value === "number" && Number.isFinite(value)) {
        const d = new Date(value);
        if (!Number.isNaN(d.getTime())) {
          const y = d.getUTCFullYear();
          const m = String(d.getUTCMonth() + 1).padStart(2, "0");
          const day = String(d.getUTCDate()).padStart(2, "0");
          return `${y}-${m}-${day}`;
        }
      }
      const n = normalizeDateOnlyForApi(value);
      return typeof n === "string" && /^\d{4}-\d{2}-\d{2}$/.test(n) ? n : "";
    }

    function integerStringForNumberInput(n) {
      if (n == null || n === "") {
        return "0";
      }
      const x = Number(n);
      if (!Number.isFinite(x)) {
        return "0";
      }
      return String(Math.max(0, Math.trunc(x)));
    }

    function optionalNonNegativeIntString(n) {
      if (n == null || n === "") {
        return "";
      }
      const x = Number(n);
      if (!Number.isFinite(x)) {
        return "";
      }
      return String(Math.max(0, Math.trunc(x)));
    }

    function formatLocalDateTimeLocal(d) {
      if (!(d instanceof Date) || Number.isNaN(d.getTime())) {
        return "";
      }
      const y = d.getFullYear();
      const mo = String(d.getMonth() + 1).padStart(2, "0");
      const day = String(d.getDate()).padStart(2, "0");
      const hh = String(d.getHours()).padStart(2, "0");
      const mm = String(d.getMinutes()).padStart(2, "0");
      return `${y}-${mo}-${day}T${hh}:${mm}`;
    }

    /** Valor para input datetime-local (YYYY-MM-DDTHH:mm) desde API ISO, SQL o fechas sueltas. */
    function toDateTimeLocal(value) {
      if (value == null || value === "") {
        return "";
      }
      if (typeof value === "number" && Number.isFinite(value)) {
        return formatLocalDateTimeLocal(new Date(value));
      }
      let s = String(value).trim().replace(/[\\u00a0\\u202f]/g, " ");
      if (s === "") {
        return "";
      }
      const onlyDate = s.match(/^(\\d{4})-(\\d{1,2})-(\\d{1,2})$/);
      if (onlyDate) {
        return `${onlyDate[1]}-${onlyDate[2].padStart(2, "0")}-${onlyDate[3].padStart(2, "0")}T00:00`;
      }
      if (!s.includes("T") && /^\\d{4}-\\d{1,2}-\\d{1,2}\\s+\\d/.test(s)) {
        s = s.replace(/\\s+/, "T");
      }
      const parsed = new Date(s);
      if (!Number.isNaN(parsed.getTime())) {
        return formatLocalDateTimeLocal(parsed);
      }
      const noTz = s.replace(/([+-]\\d{2}(:\\d{2})?|Z)$/i, "");
      const noFrac = /T\\d{2}:\\d{2}:\\d{2}\\./.test(noTz) ? noTz.slice(0, noTz.indexOf(".")) : noTz;
      const normalized = noFrac.includes("T") ? noFrac : noFrac.replace(/\\s+/, "T");
      const mLoose = normalized.match(/^(\\d{4})-(\\d{1,2})-(\\d{1,2})[T ](\\d{1,2}):(\\d{2})(?::(\\d{2}))?/);
      if (mLoose) {
        const yyyy = mLoose[1];
        const mo = mLoose[2].padStart(2, "0");
        const dd = mLoose[3].padStart(2, "0");
        const hh = mLoose[4].padStart(2, "0");
        const min = mLoose[5].padStart(2, "0");
        return `${yyyy}-${mo}-${dd}T${hh}:${min}`;
      }
      const mIsoSpace = noFrac.match(/^(\\d{4}-\\d{2}-\\d{2}) (\\d{2}):(\\d{2})/);
      if (mIsoSpace) {
        return `${mIsoSpace[1]}T${mIsoSpace[2]}:${mIsoSpace[3]}`;
      }
      const mDateOnly = normalized.match(/^(\\d{4}-\\d{2}-\\d{2})$/);
      if (mDateOnly) {
        return `${mDateOnly[1]}T00:00`;
      }
      const mSlash = noFrac.match(/^(\\d{1,2})[\\/\\-](\\d{1,2})[\\/\\-](\\d{4})[T ](\\d{1,2}):(\\d{2})/);
      if (mSlash) {
        const dd = mSlash[1].padStart(2, "0");
        const mm = mSlash[2].padStart(2, "0");
        const yyyy = mSlash[3];
        const hh = mSlash[4].padStart(2, "0");
        const min = mSlash[5].padStart(2, "0");
        return `${yyyy}-${mm}-${dd}T${hh}:${min}`;
      }
      return "";
    }

    function buildClientePayload(form) {
      return {
        razon_social: clean(form.get("razon_social")),
        nombre_comercial: clean(form.get("nombre_comercial")),
        rfc: clean(form.get("rfc")),
        tipo_cliente: clean(form.get("tipo_cliente")) || "mixto",
        sector: clean(form.get("sector")),
        origen_prospecto: clean(form.get("origen_prospecto")),
        email: clean(form.get("email")),
        telefono: clean(form.get("telefono")),
        direccion: clean(form.get("direccion")),
        domicilio_fiscal: clean(form.get("direccion")),
        sitio_web: clean(form.get("sitio_web")),
        notas_operativas: clean(form.get("notas_operativas")),
        notas_comerciales: clean(form.get("notas_comerciales")),
        activo: form.get("activo") === "on",
      };
    }

    function buildTransportistaPayload(form) {
      return {
        nombre: clean(form.get("nombre")),
        nombre_razon_social: clean(form.get("nombre")),
        tipo_transportista: clean(form.get("tipo_transportista")) || "subcontratado",
        tipo_persona: clean(form.get("tipo_persona")) || "moral",
        nombre_comercial: clean(form.get("nombre_comercial")),
        rfc: clean(form.get("rfc")),
        curp: clean(form.get("curp")),
        regimen_fiscal: clean(form.get("regimen_fiscal")),
        fecha_alta: normalizeDateOnlyForApi(form.get("fecha_alta")),
        estatus: clean(form.get("estatus")) || "activo",
        contacto: clean(form.get("contacto")),
        telefono: clean(form.get("telefono")),
        telefono_general: clean(form.get("telefono")),
        email: clean(form.get("email")),
        email_general: clean(form.get("email")),
        sitio_web: clean(form.get("sitio_web")),
        direccion_fiscal: clean(form.get("direccion_fiscal")),
        direccion_operativa: clean(form.get("direccion_operativa")),
        ciudad: clean(form.get("ciudad")),
        estado: clean(form.get("estado")),
        pais: clean(form.get("pais")),
        codigo_postal: clean(form.get("codigo_postal")),
        nivel_confianza: clean(form.get("nivel_confianza")) || "medio",
        blacklist: form.get("blacklist") === "on",
        prioridad_asignacion: integerOrNull(form.get("prioridad_asignacion")) ?? 0,
        notas: clean(form.get("notas_operativas")),
        notas_operativas: clean(form.get("notas_operativas")),
        notas_comerciales: clean(form.get("notas_comerciales")),
        activo: form.get("activo") === "on",
      };
    }

    function buildTransportistaContactoPayload(form) {
      return {
        transportista_id: integerOrNull(form.get("transportista_id")),
        nombre: clean(form.get("nombre")),
        area: clean(form.get("area")),
        puesto: clean(form.get("puesto")),
        telefono: clean(form.get("telefono")),
        extension: clean(form.get("extension")),
        celular: clean(form.get("celular")),
        email: clean(form.get("email")),
        principal: form.get("principal") === "on",
        activo: form.get("activo") === "on",
      };
    }

    function buildTransportistaDocumentoPayload(form) {
      return {
        transportista_id: integerOrNull(form.get("transportista_id")),
        tipo_documento: clean(form.get("tipo_documento")),
        numero_documento: clean(form.get("numero_documento")),
        fecha_emision: normalizeDateOnlyForApi(form.get("fecha_emision")),
        fecha_vencimiento: normalizeDateOnlyForApi(form.get("fecha_vencimiento")),
        archivo_url: clean(form.get("archivo_url")),
        estatus: clean(form.get("estatus")) || "pendiente",
        observaciones: clean(form.get("observaciones")),
      };
    }

    function buildViajePayload(form) {
      const km = numberOrNull(form.get("kilometros_estimados"));
      return {
        codigo_viaje: clean(form.get("codigo_viaje")),
        descripcion: clean(form.get("descripcion")),
        origen: clean(form.get("origen")),
        destino: clean(form.get("destino")),
        fecha_salida: normalizeDateTimeForApi(form.get("fecha_salida")),
        fecha_llegada_estimada: normalizeDateTimeForApi(form.get("fecha_llegada_estimada")),
        fecha_llegada_real: normalizeDateTimeForApi(form.get("fecha_llegada_real")),
        estado: clean(form.get("estado")),
        kilometros_estimados: km === null ? null : Number(km),
        notas: clean(form.get("notas")),
      };
    }

    function buildAsignacionPayload(form) {
      return {
        id_operador: integerOrNull(form.get("id_operador")),
        id_unidad: integerOrNull(form.get("id_unidad")),
        id_viaje: integerOrNull(form.get("id_viaje")),
        fecha_salida: normalizeDateTimeForApi(form.get("fecha_salida")),
        fecha_regreso: normalizeDateTimeForApi(form.get("fecha_regreso")),
        km_inicial: numberOrNull(form.get("km_inicial")),
        km_final: numberOrNull(form.get("km_final")),
        rendimiento_combustible: numberOrNull(form.get("rendimiento_combustible")),
      };
    }

    const TARIFA_VENTA_NOMBRE_DUPLICADO_MSG =
      "Este nombre de tarifa ya está en uso por otra tarifa activa. Usa otro nombre distintivo.";

    function normalizeTarifaVentaNombreKey(raw) {
      return String(raw || "").trim().toLowerCase();
    }

    function findActiveTarifaVentaNombreDuplicado(nombreRaw, excludeId) {
      const key = normalizeTarifaVentaNombreKey(nombreRaw);
      if (!key) {
        return null;
      }
      for (const t of state.tarifas || []) {
        if (!t.activo) {
          continue;
        }
        if (excludeId != null && Number(t.id) === Number(excludeId)) {
          continue;
        }
        if (normalizeTarifaVentaNombreKey(t.nombre_tarifa) === key) {
          return t;
        }
      }
      return null;
    }

    function refreshTarifaVentaNombreAviso(inputEl, avisoEl, submitBtn, excludeId) {
      if (!inputEl || !avisoEl) {
        return;
      }
      const dup = findActiveTarifaVentaNombreDuplicado(inputEl.value, excludeId);
      if (dup) {
        avisoEl.textContent = TARIFA_VENTA_NOMBRE_DUPLICADO_MSG;
        avisoEl.hidden = false;
        inputEl.setAttribute("aria-invalid", "true");
        if (submitBtn) {
          submitBtn.disabled = true;
        }
      } else {
        avisoEl.textContent = "";
        avisoEl.hidden = true;
        inputEl.removeAttribute("aria-invalid");
        if (submitBtn) {
          submitBtn.disabled = false;
        }
      }
    }

    function initTarifaVentaNombreUnico() {
      const tfNombre = document.getElementById("tarifa-form-nombre-tarifa");
      const tfAviso = document.getElementById("tarifa-form-nombre-aviso");
      const tfForm = document.getElementById("tarifa-form");
      const tfSubmit = tfForm ? tfForm.querySelector('button[type="submit"]') : null;
      if (tfNombre && tfAviso) {
        const runAlta = () => refreshTarifaVentaNombreAviso(tfNombre, tfAviso, tfSubmit, null);
        tfNombre.addEventListener("input", runAlta);
        tfNombre.addEventListener("change", runAlta);
      }
      const teNombre = document.getElementById("tarifa-edit-form-nombre-tarifa");
      const teAviso = document.getElementById("tarifa-edit-form-nombre-aviso");
      const teForm = document.getElementById("tarifa-edit-form");
      const teSubmit = teForm ? teForm.querySelector('button[type="submit"]') : null;
      if (teNombre && teAviso && teForm) {
        const runEdit = () => {
          const sid = teForm.elements.id && teForm.elements.id.value;
          const ex = sid ? Number(sid) : null;
          refreshTarifaVentaNombreAviso(
            teNombre,
            teAviso,
            teSubmit,
            Number.isFinite(ex) && ex > 0 ? ex : null,
          );
        };
        teNombre.addEventListener("input", runEdit);
        teNombre.addEventListener("change", runEdit);
      }
    }

    function buildTarifaFleteVentaPayload(form) {
      const pu = numberOrNull(form.get("porcentaje_utilidad"));
      const pr = numberOrNull(form.get("porcentaje_riesgo"));
      const pug = numberOrNull(form.get("porcentaje_urgencia"));
      const prv = numberOrNull(form.get("porcentaje_retorno_vacio"));
      const pce = numberOrNull(form.get("porcentaje_carga_especial"));
      return {
        nombre_tarifa: clean(form.get("nombre_tarifa")),
        tipo_operacion: clean(form.get("tipo_operacion")) || "subcontratado",
        ambito: clean(form.get("ambito")) || "federal",
        modalidad_cobro: clean(form.get("modalidad_cobro")) || "mixta",
        origen: clean(form.get("origen")),
        destino: clean(form.get("destino")),
        tipo_unidad: clean(form.get("tipo_unidad")),
        tipo_carga: clean(form.get("tipo_carga")),
        tarifa_base: numberOrNull(form.get("tarifa_base")),
        tarifa_km: numberOrNull(form.get("tarifa_km")) ?? 0,
        tarifa_kg: numberOrNull(form.get("tarifa_kg")) ?? 0,
        tarifa_tonelada: numberOrNull(form.get("tarifa_tonelada")) ?? 0,
        tarifa_hora: numberOrNull(form.get("tarifa_hora")) ?? 0,
        tarifa_dia: numberOrNull(form.get("tarifa_dia")) ?? 0,
        recargo_minimo: numberOrNull(form.get("recargo_minimo")) ?? 0,
        porcentaje_utilidad: pu != null ? pu : 0.2,
        porcentaje_riesgo: pr != null ? pr : 0,
        porcentaje_urgencia: pug != null ? pug : 0,
        porcentaje_retorno_vacio: prv != null ? prv : 0,
        porcentaje_carga_especial: pce != null ? pce : 0,
        moneda: clean(form.get("moneda")) || "MXN",
        activo: form.get("activo") === "on",
        vigencia_inicio: normalizeDateOnlyForApi(form.get("vigencia_inicio")),
        vigencia_fin: normalizeDateOnlyForApi(form.get("vigencia_fin")),
      };
    }

    function buildFacturaPayload(form) {
      return {
        serie: clean(form.get("serie")),
        cliente_id: integerOrNull(form.get("cliente_id")),
        flete_id: integerOrNull(form.get("flete_id")),
        orden_servicio_id: integerOrNull(form.get("orden_servicio_id")),
        fecha_emision: normalizeDateOnlyForApi(form.get("fecha_emision")),
        fecha_vencimiento: normalizeDateOnlyForApi(form.get("fecha_vencimiento")),
        concepto: clean(form.get("concepto")),
        referencia: clean(form.get("referencia")),
        moneda: clean(form.get("moneda")) || "MXN",
        subtotal: numberOrNull(form.get("subtotal")),
        iva_pct: numberOrNull(form.get("iva_pct")) ?? 0.16,
        iva_monto: numberOrNull(form.get("iva_monto")),
        retencion_monto: numberOrNull(form.get("retencion_monto")) ?? 0,
        total: numberOrNull(form.get("total")),
        saldo_pendiente: numberOrNull(form.get("saldo_pendiente")),
        forma_pago: clean(form.get("forma_pago")),
        metodo_pago: clean(form.get("metodo_pago")),
        uso_cfdi: clean(form.get("uso_cfdi")),
        estatus: clean(form.get("estatus")) || "borrador",
        timbrada: form.get("timbrada") === "on",
        observaciones: clean(form.get("observaciones")),
      };
    }

    function buildTarifaCompraPayload(form) {
      const activoRaw = form.get("activo");
      return {
        transportista_id: integerOrNull(form.get("transportista_id")),
        tipo_transportista: clean(form.get("tipo_transportista")) || "subcontratado",
        nombre_tarifa: clean(form.get("nombre_tarifa")),
        ambito: clean(form.get("ambito")) || "federal",
        modalidad_cobro: clean(form.get("modalidad_cobro")) || "mixta",
        origen: clean(form.get("origen")),
        destino: clean(form.get("destino")),
        tipo_unidad: clean(form.get("tipo_unidad")),
        tipo_carga: clean(form.get("tipo_carga")),
        tarifa_base: numberOrNull(form.get("tarifa_base")),
        tarifa_km: numberOrNull(form.get("tarifa_km")) ?? 0,
        tarifa_kg: numberOrNull(form.get("tarifa_kg")) ?? 0,
        tarifa_tonelada: numberOrNull(form.get("tarifa_tonelada")) ?? 0,
        tarifa_hora: numberOrNull(form.get("tarifa_hora")) ?? 0,
        tarifa_dia: numberOrNull(form.get("tarifa_dia")) ?? 0,
        recargo_minimo: numberOrNull(form.get("recargo_minimo")) ?? 0,
        dias_credito: integerOrNull(form.get("dias_credito")) ?? 0,
        moneda: clean(form.get("moneda")) || "MXN",
        activo: activoRaw === "on" || activoRaw === "true",
        vigencia_inicio: normalizeDateOnlyForApi(form.get("vigencia_inicio")),
        vigencia_fin: normalizeDateOnlyForApi(form.get("vigencia_fin")),
        observaciones: clean(form.get("observaciones")),
      };
    }

    function buildDespachoPayload(form) {
      return {
        id_flete: integerOrNull(form.get("id_flete")),
        salida_programada: normalizeDateTimeForApi(form.get("salida_programada")),
        estatus: clean(form.get("estatus")),
        observaciones_transito: clean(form.get("observaciones_transito")),
        motivo_cancelacion: clean(form.get("motivo_cancelacion")),
      };
    }

    function buildClienteContactoPayload(form) {
      return {
        cliente_id: integerOrNull(form.get("cliente_id")),
        nombre: clean(form.get("nombre")),
        area: clean(form.get("area")),
        puesto: clean(form.get("puesto")),
        telefono: clean(form.get("telefono")),
        extension: clean(form.get("extension")),
        celular: clean(form.get("celular")),
        email: clean(form.get("email")),
        principal: form.get("principal") === "on",
        activo: form.get("activo") === "on",
      };
    }

    function clienteContactoCaptureToFormData() {
      const fd = new FormData();
      fd.append("cliente_id", document.getElementById("cliente-contacto-cliente").value);
      fd.append("nombre", document.getElementById("cliente-contacto-nombre").value);
      fd.append("area", document.getElementById("cliente-contacto-area").value);
      fd.append("puesto", document.getElementById("cliente-contacto-puesto").value);
      fd.append("email", document.getElementById("cliente-contacto-email").value);
      fd.append("telefono", document.getElementById("cliente-contacto-telefono").value);
      fd.append("extension", document.getElementById("cliente-contacto-extension").value);
      fd.append("celular", document.getElementById("cliente-contacto-celular").value);
      if (document.getElementById("cliente-contacto-principal").checked) {
        fd.append("principal", "on");
      }
      if (document.getElementById("cliente-contacto-activo").checked) {
        fd.append("activo", "on");
      }
      return fd;
    }

    function validateClienteContactoCapture() {
      const cliente = document.getElementById("cliente-contacto-cliente");
      const nombre = document.getElementById("cliente-contacto-nombre");
      const email = document.getElementById("cliente-contacto-email");
      if (!cliente.value) {
        setMessage("cliente-contacto-message", "Selecciona un cliente.", "error");
        cliente.focus();
        return false;
      }
      if (!nombre.value.trim()) {
        setMessage("cliente-contacto-message", "Captura el nombre del contacto.", "error");
        nombre.focus();
        return false;
      }
      if (email.value && typeof email.checkValidity === "function" && !email.checkValidity()) {
        setMessage("cliente-contacto-message", "Revisa el formato del email.", "error");
        email.focus();
        return false;
      }
      return true;
    }

    function buildClienteDomicilioPayload(form) {
      return {
        cliente_id: integerOrNull(form.get("cliente_id")),
        tipo_domicilio: clean(form.get("tipo_domicilio")),
        nombre_sede: clean(form.get("nombre_sede")),
        direccion_completa: clean(form.get("direccion_completa")),
        municipio: clean(form.get("municipio")),
        estado: clean(form.get("estado")),
        codigo_postal: clean(form.get("codigo_postal")),
        horario_carga: clean(form.get("horario_carga")),
        horario_descarga: clean(form.get("horario_descarga")),
        instrucciones_acceso: clean(form.get("instrucciones_acceso")),
        activo: form.get("activo") === "on",
      };
    }

    function normBusquedaText(s) {
      return String(s || "").toLowerCase().trim();
    }

    function busquedaWordCandidates(fields) {
      const words = [];
      for (const f of fields) {
        const txt = normBusquedaText(f);
        if (!txt) {
          continue;
        }
        words.push(txt);
        txt.split(/[\s/.,\-_|]+/).forEach((chunk) => {
          if (chunk) {
            words.push(chunk);
          }
        });
      }
      return words;
    }

    function matchesBusqueda(query, fields, modo) {
      const q = normBusquedaText(query);
      if (!q) {
        return true;
      }
      const flat = fields.map((f) => normBusquedaText(f));
      const haystack = flat.join(" ");
      if (modo === "todas_palabras") {
        const tokens = q.split(/\s+/).filter(Boolean);
        if (!tokens.length) {
          return true;
        }
        return tokens.every((t) => haystack.includes(t));
      }
      if (modo === "prefijo_palabras") {
        const tokens = q.split(/\s+/).filter(Boolean);
        if (!tokens.length) {
          return true;
        }
        const words = busquedaWordCandidates(fields);
        return tokens.every((tok) => words.some((w) => w.startsWith(tok)));
      }
      return flat.some((x) => x.includes(q)) || haystack.includes(q);
    }

    function escapeDatalistValue(value) {
      return String(value).replace(/&/g, "&amp;").replace(/"/g, "&quot;");
    }

    function updateBusquedaDatalist(inputId, datalistId, allItems, labelFn, getFields) {
      const input = document.getElementById(inputId);
      const dl = document.getElementById(datalistId);
      if (!input || !dl) {
        return;
      }
      const modo = uiState.buscarModo || "contiene";
      const qRaw = (input.value || "").trim();
      let ranked = allItems.filter((item) =>
        matchesBusqueda(qRaw, getFields(item), modo),
      );
      if (!qRaw) {
        ranked = allItems.slice();
      }
      const seen = new Set();
      const parts = [];
      for (const item of ranked) {
        const lab = labelFn(item);
        if (!lab || seen.has(lab)) {
          continue;
        }
        seen.add(lab);
        parts.push(`<option value="${escapeDatalistValue(lab)}"></option>`);
        if (parts.length >= 18) {
          break;
        }
      }
      dl.innerHTML = parts.join("");
    }

    const BUSQUEDA_DL_BY_INPUT = {
      "cliente-filter-buscar": {
        datalistId: "cliente-filter-buscar-dl",
        getItems: () => state.clientes,
        label: (c) => c.razon_social || c.nombre_comercial || `Cliente ${c.id}`,
        fields: (c) => [c.razon_social, c.nombre_comercial, c.rfc],
      },
      "transportista-filter-buscar": {
        datalistId: "transportista-filter-buscar-dl",
        getItems: () => state.transportistas,
        label: (t) => t.nombre || t.nombre_comercial || `Transportista ${t.id}`,
        fields: (t) => [t.nombre, t.nombre_comercial, t.rfc],
      },
      "viaje-filter-buscar": {
        datalistId: "viaje-filter-buscar-dl",
        getItems: () => state.viajes,
        label: (v) => v.codigo_viaje || `Viaje ${v.id}`,
        fields: (v) => [v.codigo_viaje || "", v.origen || "", v.destino || "", String(v.id ?? "")],
      },
      "flete-filter-buscar": {
        datalistId: "flete-filter-buscar-dl",
        getItems: () => state.fletes,
        label: (x) => x.codigo_flete || `Flete ${x.id}`,
        fields: (x) => {
          const cliente = x.cliente?.razon_social || x.cliente?.nombre_comercial || "";
          const transp = x.transportista?.nombre || x.transportista?.nombre_comercial || "";
          return [String(x.id ?? ""), x.codigo_flete || "", cliente, transp, x.estado || ""];
        },
      },
      "factura-filter-buscar": {
        datalistId: "factura-filter-buscar-dl",
        getItems: () => state.facturas,
        label: (x) => x.folio || `Factura ${x.id}`,
        fields: (x) => [x.folio || "", x.concepto || "", x.referencia || "", String(x.id ?? "")],
      },
      "tarifa-venta-filter-buscar": {
        datalistId: "tarifa-venta-filter-buscar-dl",
        getItems: () => state.tarifas,
        label: (x) => x.nombre_tarifa || `Tarifa ${x.id}`,
        fields: (x) => [
          String(x.id ?? ""),
          x.nombre_tarifa || "",
          x.origen || "",
          x.destino || "",
          x.tipo_unidad || "",
          x.tipo_carga || "",
          x.tipo_operacion || "",
          String(x.ambito || ""),
          String(x.modalidad_cobro || ""),
        ],
      },
      "tarifa-compra-filter-buscar": {
        datalistId: "tarifa-compra-filter-buscar-dl",
        getItems: () => state.tarifasCompra,
        label: (x) => {
          const tn = state.transportistas.find((t) => Number(t.id) === Number(x.transportista_id))?.nombre || "";
          return x.nombre_tarifa || tn || `Tarifa compra ${x.id}`;
        },
        fields: (x) => {
          const tn = state.transportistas.find((t) => Number(t.id) === Number(x.transportista_id))?.nombre || "";
          return [
            x.nombre_tarifa || "",
            x.origen || "",
            x.destino || "",
            x.tipo_unidad || "",
            tn,
            String(x.id ?? ""),
          ];
        },
      },
      "gasto-filter-buscar": {
        datalistId: "gasto-filter-buscar-dl",
        getItems: () => state.gastos,
        label: (x) => x.referencia || x.tipo_gasto || `Gasto ${x.id}`,
        fields: (x) => [
          String(x.id ?? ""),
          String(x.flete_id ?? ""),
          x.tipo_gasto || "",
          x.referencia || "",
          x.descripcion || "",
          String(x.monto ?? ""),
        ],
      },
      "operador-filter-buscar": {
        datalistId: "operador-filter-buscar-dl",
        getItems: () => state.operadores,
        label: (x) =>
          [x.nombre, x.apellido_paterno, x.apellido_materno].filter(Boolean).join(" ").trim() ||
          `Operador ${x.id_operador}`,
        fields: (x) => {
          const transp = state.transportistas.find((t) => t.id === x.transportista_id)?.nombre || "";
          return [
            String(x.id_operador ?? ""),
            x.nombre || "",
            x.apellido_paterno || "",
            x.apellido_materno || "",
            x.curp || "",
            x.telefono_principal || "",
            x.certificaciones || "",
            transp,
          ];
        },
      },
      "unidad-filter-buscar": {
        datalistId: "unidad-filter-buscar-dl",
        getItems: () => state.unidades,
        label: (x) => x.economico || `Unidad ${x.id_unidad}`,
        fields: (x) => {
          const transp = state.transportistas.find((t) => t.id === x.transportista_id)?.nombre || "";
          return [String(x.id_unidad ?? ""), x.economico || "", x.placas || "", x.descripcion || "", transp];
        },
      },
      "asignacion-filter-buscar": {
        datalistId: "asignacion-filter-buscar-dl",
        getItems: () => state.asignaciones,
        label: (x) => x.unidad?.economico || `Asignacion ${x.id_asignacion}`,
        fields: (x) => {
          const nom = `${x.operador?.nombre || ""} ${x.operador?.apellido_paterno || ""} ${x.operador?.apellido_materno || ""}`;
          const ec = x.unidad?.economico || "";
          const cv = x.viaje?.codigo_viaje || "";
          return [String(x.id_asignacion), nom, ec, cv];
        },
      },
      "despacho-filter-buscar": {
        datalistId: "despacho-filter-buscar-dl",
        getItems: () => state.despachos,
        label: (x) => x.flete?.codigo_flete || `Despacho ${x.id_despacho}`,
        fields: (x) => {
          const cf = x.flete?.codigo_flete || "";
          const cv = x.asignacion?.viaje?.codigo_viaje || "";
          return [String(x.id_despacho), x.estatus || "", cf, cv];
        },
      },
    };

    function refreshBusquedaDatalist(inputId) {
      const cfg = BUSQUEDA_DL_BY_INPUT[inputId];
      if (!cfg) {
        return;
      }
      updateBusquedaDatalist(inputId, cfg.datalistId, cfg.getItems(), cfg.label, cfg.fields);
    }

    function refreshAllBusquedaDatalists() {
      Object.keys(BUSQUEDA_DL_BY_INPUT).forEach((id) => refreshBusquedaDatalist(id));
    }

    function refreshAllConsultaTables() {
      renderClientes();
      renderTransportistas();
      renderViajes();
      renderFletes();
      renderOrdenesServicio();
      renderFacturas();
      renderTarifas();
      renderTarifasCompra();
      renderGastos();
      renderOperadores();
      renderUnidades();
      renderAsignaciones();
      renderDespachos();
      refreshAllBusquedaDatalists();
    }

    function filteredClientes() {
      const buscar = uiState.clienteFilters.buscar.trim();
      const activo = uiState.clienteFilters.activo;
      const modo = uiState.buscarModo || "contiene";
      return state.clientes.filter((item) => {
        if (
          buscar &&
          !matchesBusqueda(buscar, [item.razon_social, item.nombre_comercial, item.rfc], modo)
        ) {
          return false;
        }
        if (activo === "true" && !item.activo) {
          return false;
        }
        if (activo === "false" && item.activo) {
          return false;
        }
        return true;
      });
    }

    function filteredFletes() {
      const buscar = (uiState.fleteFilters.buscar || "").trim();
      const modo = uiState.buscarModo || "contiene";
      return state.fletes.filter((item) => {
        if (buscar) {
          const cliente = item.cliente?.razon_social || item.cliente?.nombre_comercial || "";
          const transp = item.transportista?.nombre || item.transportista?.nombre_comercial || "";
          const viajeCod = item.viaje?.codigo_viaje || "";
          if (
            !matchesBusqueda(
              buscar,
              [
                String(item.id ?? ""),
                item.codigo_flete || "",
                cliente,
                transp,
                item.estado || "",
                viajeCod,
              ],
              modo,
            )
          ) {
            return false;
          }
        }
        if (uiState.fleteFilters.estado && item.estado !== uiState.fleteFilters.estado) {
          return false;
        }
        if (uiState.fleteFilters.cliente_id && String(item.cliente_id) !== uiState.fleteFilters.cliente_id) {
          return false;
        }
        if (uiState.fleteFilters.transportista_id && String(item.transportista_id) !== uiState.fleteFilters.transportista_id) {
          return false;
        }
        return true;
      });
    }

    function filteredTarifasVenta() {
      const buscar = (uiState.tarifaVentaFilters.buscar || "").trim();
      const modo = uiState.buscarModo || "contiene";
      return state.tarifas.filter((item) => {
        if (!buscar) {
          return true;
        }
        return matchesBusqueda(
          buscar,
          [
            String(item.id ?? ""),
            item.nombre_tarifa || "",
            item.origen || "",
            item.destino || "",
            item.tipo_unidad || "",
            item.tipo_carga || "",
            item.tipo_operacion || "",
            String(item.ambito || ""),
            String(item.modalidad_cobro || ""),
          ],
          modo,
        );
      });
    }

    function filteredGastos() {
      const buscar = (uiState.gastoFilters.buscar || "").trim();
      const modo = uiState.buscarModo || "contiene";
      return state.gastos.filter((item) => {
        if (!buscar) {
          return true;
        }
        return matchesBusqueda(
          buscar,
          [
            String(item.id ?? ""),
            String(item.flete_id ?? ""),
            item.tipo_gasto || "",
            item.referencia || "",
            item.descripcion || "",
            String(item.monto ?? ""),
          ],
          modo,
        );
      });
    }

    function filteredOperadores() {
      const buscar = (uiState.operadorFilters.buscar || "").trim();
      const modo = uiState.buscarModo || "contiene";
      return state.operadores.filter((item) => {
        if (!buscar) {
          return true;
        }
        const transp = state.transportistas.find((t) => t.id === item.transportista_id)?.nombre || "";
        return matchesBusqueda(
          buscar,
          [
            String(item.id_operador ?? ""),
            item.nombre || "",
            item.apellido_paterno || "",
            item.apellido_materno || "",
            item.curp || "",
            item.telefono_principal || "",
            item.certificaciones || "",
            transp,
          ],
          modo,
        );
      });
    }

    function filteredUnidades() {
      const buscar = (uiState.unidadFilters.buscar || "").trim();
      const modo = uiState.buscarModo || "contiene";
      const ft = uiState.unidadFilters.tipo_propiedad || "";
      const fe = uiState.unidadFilters.estatus_documental || "";
      const fa = uiState.unidadFilters.activo || "";
      return state.unidades.filter((item) => {
        if (ft && (item.tipo_propiedad || "") !== ft) {
          return false;
        }
        if (fe && (item.estatus_documental || "") !== fe) {
          return false;
        }
        if (fa !== "" && String(Boolean(item.activo)) !== fa) {
          return false;
        }
        if (!buscar) {
          return true;
        }
        const transp =
          state.transportistas.find((t) => String(t.id) === String(item.transportista_id))?.nombre || "";
        const tipoP = item.tipo_propiedad || "";
        const estDoc = item.estatus_documental || "";
        return matchesBusqueda(
          buscar,
          [
            String(item.id_unidad ?? ""),
            item.economico || "",
            item.placas || "",
            item.descripcion || "",
            transp,
            tipoP,
            estDoc,
          ],
          modo,
        );
      });
    }

    function filteredTransportistas() {
      const buscar = uiState.transportistaFilters.buscar.trim();
      const modo = uiState.buscarModo || "contiene";
      return state.transportistas.filter((item) => {
        if (buscar && !matchesBusqueda(buscar, [item.nombre, item.nombre_comercial, item.rfc], modo)) {
          return false;
        }
        if (
          uiState.transportistaFilters.estatus &&
          (item.estatus || (item.activo ? "activo" : "inactivo")) !== uiState.transportistaFilters.estatus
        ) {
          return false;
        }
        if (
          uiState.transportistaFilters.tipo_transportista &&
          item.tipo_transportista !== uiState.transportistaFilters.tipo_transportista
        ) {
          return false;
        }
        return true;
      });
    }

    function filteredViajes() {
      const buscar = uiState.viajeFilters.buscar.trim();
      const modo = uiState.buscarModo || "contiene";
      return state.viajes.filter((item) => {
        if (
          buscar &&
          !matchesBusqueda(buscar, [item.codigo_viaje, item.origen, item.destino, String(item.id ?? "")], modo)
        ) {
          return false;
        }
        if (uiState.viajeFilters.estado && item.estado !== uiState.viajeFilters.estado) {
          return false;
        }
        return true;
      });
    }

    function filteredFacturas() {
      const buscar = uiState.facturaFilters.buscar.trim();
      const modo = uiState.buscarModo || "contiene";
      return state.facturas.filter((item) => {
        if (
          buscar &&
          !matchesBusqueda(buscar, [item.folio, item.concepto, item.referencia, String(item.id ?? "")], modo)
        ) {
          return false;
        }
        if (
          uiState.facturaFilters.cliente_id &&
          String(item.cliente_id) !== uiState.facturaFilters.cliente_id
        ) {
          return false;
        }
        if (uiState.facturaFilters.estatus && item.estatus !== uiState.facturaFilters.estatus) {
          return false;
        }
        return true;
      });
    }

    function filteredTarifasCompra() {
      const buscar = uiState.tarifaCompraFilters.buscar.trim();
      const modo = uiState.buscarModo || "contiene";
      return state.tarifasCompra.filter((item) => {
        const transpNombre =
          state.transportistas.find((t) => Number(t.id) === Number(item.transportista_id))?.nombre || "";
        if (
          buscar &&
          !matchesBusqueda(
            buscar,
            [item.nombre_tarifa, item.origen, item.destino, item.tipo_unidad, transpNombre, String(item.id ?? "")],
            modo,
          )
        ) {
          return false;
        }
        if (
          uiState.tarifaCompraFilters.transportista_id &&
          String(item.transportista_id) !== uiState.tarifaCompraFilters.transportista_id
        ) {
          return false;
        }
        if (
          uiState.tarifaCompraFilters.activo &&
          String(Boolean(item.activo)) !== uiState.tarifaCompraFilters.activo
        ) {
          return false;
        }
        return true;
      });
    }

    function filteredAsignaciones() {
      const buscar = (uiState.asignacionFilters.buscar || "").trim();
      const modo = uiState.buscarModo || "contiene";
      return state.asignaciones.filter((item) => {
        if (buscar) {
          const nom = `${item.operador?.nombre || ""} ${item.operador?.apellido_paterno || ""} ${item.operador?.apellido_materno || ""}`;
          const ec = item.unidad?.economico || "";
          const cv = item.viaje?.codigo_viaje || "";
          if (!matchesBusqueda(buscar, [String(item.id_asignacion), nom, ec, cv], modo)) {
            return false;
          }
        }
        if (
          uiState.asignacionFilters.id_operador &&
          String(item.id_operador) !== uiState.asignacionFilters.id_operador
        ) {
          return false;
        }
        if (
          uiState.asignacionFilters.id_unidad &&
          String(item.id_unidad) !== uiState.asignacionFilters.id_unidad
        ) {
          return false;
        }
        if (
          uiState.asignacionFilters.id_viaje &&
          String(item.id_viaje) !== uiState.asignacionFilters.id_viaje
        ) {
          return false;
        }
        return true;
      });
    }

    function filteredDespachos() {
      const buscar = (uiState.despachoFilters.buscar || "").trim();
      const modo = uiState.buscarModo || "contiene";
      return state.despachos.filter((item) => {
        if (buscar) {
          const cf = item.flete?.codigo_flete || "";
          const cv = item.asignacion?.viaje?.codigo_viaje || "";
          if (!matchesBusqueda(buscar, [String(item.id_despacho), item.estatus || "", cf, cv], modo)) {
            return false;
          }
        }
        if (uiState.despachoFilters.estatus && item.estatus !== uiState.despachoFilters.estatus) {
          return false;
        }
        if (uiState.despachoFilters.id_asignacion && String(item.id_asignacion) !== uiState.despachoFilters.id_asignacion) {
          return false;
        }
        if (uiState.despachoFilters.id_flete && String(item.id_flete || "") !== uiState.despachoFilters.id_flete) {
          return false;
        }
        return true;
      });
    }

    function buildFletePayload(form) {
      return {
        codigo_flete: clean(form.get("codigo_flete")),
        cliente_id: integerOrNull(form.get("cliente_id")),
        transportista_id: integerOrNull(form.get("transportista_id")),
        viaje_id: integerOrNull(form.get("viaje_id")),
        tipo_operacion: clean(form.get("tipo_operacion")) || "subcontratado",
        tipo_unidad: clean(form.get("tipo_unidad")),
        tipo_carga: clean(form.get("tipo_carga")),
        descripcion_carga: clean(form.get("descripcion_carga")),
        peso_kg: numberOrNull(form.get("peso_kg")),
        volumen_m3: numberOrNull(form.get("volumen_m3")),
        numero_bultos: integerOrNull(form.get("numero_bultos")),
        distancia_km: numberOrNull(form.get("distancia_km")),
        monto_estimado: numberOrNull(form.get("monto_estimado")),
        precio_venta: numberOrNull(form.get("monto_estimado")),
        costo_transporte_estimado: numberOrNull(form.get("costo_transporte_estimado")),
        costo_transporte_real: numberOrNull(form.get("costo_transporte_real")),
        margen_estimado: numberOrNull(form.get("margen_estimado")),
        metodo_calculo: clean(form.get("metodo_calculo")) || "manual",
        moneda: clean(form.get("moneda")) || "MXN",
        estado: clean(form.get("estado")) || "cotizado",
        notas: clean(form.get("notas")),
      };
    }

    function buildOperadorPayload(form) {
      return {
        transportista_id: integerOrNull(form.get("transportista_id")),
        tipo_contratacion: clean(form.get("tipo_contratacion")),
        licencia: clean(form.get("licencia")),
        tipo_licencia: clean(form.get("tipo_licencia")),
        vigencia_licencia: normalizeDateOnlyForApi(form.get("vigencia_licencia")),
        estatus_documental: clean(form.get("estatus_documental")),
        nombre: clean(form.get("nombre")),
        apellido_paterno: clean(form.get("apellido_paterno")),
        apellido_materno: clean(form.get("apellido_materno")),
        fecha_nacimiento: normalizeDateOnlyForApi(form.get("fecha_nacimiento")),
        curp: clean(form.get("curp")),
        rfc: clean(form.get("rfc")),
        nss: clean(form.get("nss")),
        estado_civil: clean(form.get("estado_civil")),
        tipo_sangre: clean(form.get("tipo_sangre")),
        fotografia: clean(form.get("fotografia")),
        telefono_principal: clean(form.get("telefono_principal")),
        telefono_emergencia: clean(form.get("telefono_emergencia")),
        nombre_contacto_emergencia: clean(form.get("nombre_contacto_emergencia")),
        direccion: clean(form.get("direccion")),
        colonia: clean(form.get("colonia")),
        municipio: clean(form.get("municipio")),
        estado_geografico: clean(form.get("estado_geografico")),
        codigo_postal: clean(form.get("codigo_postal")),
        correo_electronico: clean(form.get("correo_electronico")),
        anios_experiencia: integerOrNull(form.get("anios_experiencia")),
        tipos_unidad_manejadas: clean(form.get("tipos_unidad_manejadas"))
          ? clean(form.get("tipos_unidad_manejadas"))
              .split(",")
              .map((item) => item.trim())
              .filter(Boolean)
          : null,
        rutas_conocidas: clean(form.get("rutas_conocidas")),
        tipos_carga_experiencia: clean(form.get("tipos_carga_experiencia"))
          ? clean(form.get("tipos_carga_experiencia"))
              .split(",")
              .map((item) => item.trim())
              .filter(Boolean)
          : null,
        certificaciones: clean(form.get("certificaciones")),
        ultima_revision_medica: normalizeDateOnlyForApi(form.get("ultima_revision_medica")),
        resultado_apto: form.get("resultado_apto") === "on" ? true : null,
        restricciones_medicas: clean(form.get("restricciones_medicas")),
        proxima_revision_medica: normalizeDateOnlyForApi(form.get("proxima_revision_medica")),
        puntualidad: numberOrNull(form.get("puntualidad")),
        consumo_diesel_promedio: numberOrNull(form.get("consumo_diesel_promedio")),
        consumo_gasolina_promedio: numberOrNull(form.get("consumo_gasolina_promedio")),
        incidencias_desempeno: clean(form.get("incidencias_desempeno")),
        calificacion_general: numberOrNull(form.get("calificacion_general")),
        comentarios_desempeno: clean(form.get("comentarios_desempeno")),
      };
    }

    function operadorCsvFromApi(value) {
      if (value == null || value === undefined) {
        return "";
      }
      if (Array.isArray(value)) {
        return value.map((x) => String(x).trim()).filter(Boolean).join(", ");
      }
      return String(value).trim();
    }

    function buildUnidadPayload(formData) {
      return {
        transportista_id: integerOrNull(formData.get("transportista_id")),
        economico: clean(formData.get("economico")),
        placas: clean(formData.get("placas")),
        tipo_propiedad: clean(formData.get("tipo_propiedad")),
        estatus_documental: clean(formData.get("estatus_documental")),
        descripcion: clean(formData.get("descripcion")),
        detalle: clean(formData.get("detalle")),
        activo: formData.get("activo") === "on",
        vigencia_permiso_sct: normalizeDateOnlyForApi(formData.get("vigencia_permiso_sct")),
        vigencia_seguro: normalizeDateOnlyForApi(formData.get("vigencia_seguro")),
      };
    }

    function updateFleteMargenPctHint(formSelector) {
      const ventaField = document.querySelector(`${formSelector} [name="monto_estimado"]`);
      const margenInput = document.querySelector(`${formSelector} [name="margen_estimado"]`);
      const pctHintId =
        formSelector === "#flete-edit-form" ? "flete-edit-margen-pct-hint" : "flete-margen-pct-hint-new";
      const pctHint = document.getElementById(pctHintId);
      if (!ventaField || !margenInput || !pctHint) {
        return;
      }
      const venta = numberOrNull(ventaField.value);
      const margenNum = numberOrNull(margenInput.value);
      if (venta !== null && venta > 0 && margenNum !== null) {
        const pct = (margenNum / venta) * 100;
        pctHint.textContent = `Margen estimado sobre venta: ${formatLocaleDecimal(pct, 2, 2)} %`;
      } else {
        pctHint.textContent = "";
      }
    }

    function refreshMarginForForm(formSelector) {
      const ventaField = document.querySelector(`${formSelector} [name="monto_estimado"]`);
      const costoField = document.querySelector(`${formSelector} [name="costo_transporte_estimado"]`);
      const margenInput = document.querySelector(`${formSelector} [name="margen_estimado"]`);
      if (!ventaField || !costoField || !margenInput) {
        return;
      }
      const venta = numberOrNull(ventaField.value);
      const costo = numberOrNull(costoField.value);
      if (!margenInput) {
        return;
      }
      if (venta !== null && costo !== null) {
        margenInput.value = formatMoneyInputFromEl(venta - costo, margenInput);
      } else {
        margenInput.value = "";
      }
      updateFleteMargenPctHint(formSelector);
    }

    /** Enter en inputs/selects pasa al siguiente campo (no envia el formulario). */
    function wireEnterAvanzaCampo(formSelector) {
      const form = document.querySelector(formSelector);
      if (!form) {
        return;
      }
      form.addEventListener("keydown", (e) => {
        if (e.key !== "Enter") {
          return;
        }
        if (e.target.tagName === "TEXTAREA") {
          return;
        }
        if (e.target.closest && e.target.closest("button")) {
          return;
        }
        const t = e.target.tagName;
        if (t !== "INPUT" && t !== "SELECT") {
          return;
        }
        if (t === "INPUT" && (e.target.type === "submit" || e.target.type === "button")) {
          return;
        }
        e.preventDefault();
        const focusables = Array.from(
          form.querySelectorAll(
            'input:not([type="hidden"]):not([disabled]), select:not([disabled]), textarea:not([disabled])',
          ),
        ).filter((el) => el.offsetParent !== null);
        const idx = focusables.indexOf(e.target);
        if (idx >= 0 && idx < focusables.length - 1) {
          focusables[idx + 1].focus();
        }
      });
    }

    /** Igual que en el backend: si el flete no trae km, usar kilometros_estimados del viaje. */
    function resolveDistanciaKmForQuote(payload, viaje) {
      if (payload.distancia_km !== null && payload.distancia_km !== undefined) {
        return payload.distancia_km;
      }
      const km = viaje && viaje.kilometros_estimados;
      if (km === null || km === undefined || km === "") {
        return null;
      }
      const n = typeof km === "number" ? km : parseLocaleNumber(String(km));
      return n !== null && Number.isFinite(n) ? n : null;
    }

    /** Viaje del catalogo en memoria (API /viajes). Normaliza ID para evitar fallo 1 vs "1". */
    function findViajeForFleteQuote(payload) {
      const raw = payload.viaje_id;
      if (raw === null || raw === undefined || raw === "") {
        throw new Error("Selecciona un viaje en la lista (origen y destino salen del viaje).");
      }
      const n = Number(raw);
      if (!Number.isFinite(n) || n < 1) {
        throw new Error("El viaje seleccionado no es valido. Vuelve a elegirlo en la lista.");
      }
      const viaje = state.viajes.find((item) => Number(item.id) === n);
      if (viaje) {
        return viaje;
      }
      if (!state.viajes.length) {
        throw new Error(
          "No hay viajes cargados en pantalla. Actualiza la pagina (F5) o abre el modulo Viajes y espera a que cargue el listado.",
        );
      }
      throw new Error(
        "No se encontro el viaje en el catalogo. Vuelve a elegir el viaje en el selector o actualiza la pagina.",
      );
    }

    function initFleteCotizador() {
      const ventaButton = document.getElementById("flete-cotizar-btn");
      const compraButton = document.getElementById("flete-cotizar-compra-btn");
      const editVentaButton = document.getElementById("edit-flete-cotizar-venta-btn");
      const editCompraButton = document.getElementById("edit-flete-cotizar-compra-btn");
      if (!ventaButton && !compraButton && !editVentaButton && !editCompraButton) {
        return;
      }

      const costoInput = document.querySelector('#flete-form [name="costo_transporte_estimado"]');
      const ventaInput = document.querySelector('#flete-form [name="monto_estimado"]');
      const editCostoInput = document.querySelector('#flete-edit-form [name="costo_transporte_estimado"]');
      const editVentaInput = document.querySelector('#flete-edit-form [name="monto_estimado"]');

      if (costoInput) {
        costoInput.addEventListener("input", () => refreshMarginForForm("#flete-form"));
      }
      if (ventaInput) {
        ventaInput.addEventListener("input", () => refreshMarginForForm("#flete-form"));
      }
      if (editCostoInput) {
        editCostoInput.addEventListener("input", () => refreshMarginForForm("#flete-edit-form"));
      }
      if (editVentaInput) {
        editVentaInput.addEventListener("input", () => refreshMarginForForm("#flete-edit-form"));
      }
      const margenNewInput = document.querySelector('#flete-form [name="margen_estimado"]');
      const margenEditInput = document.querySelector('#flete-edit-form [name="margen_estimado"]');
      if (margenNewInput) {
        margenNewInput.addEventListener("input", () => updateFleteMargenPctHint("#flete-form"));
      }
      if (margenEditInput) {
        margenEditInput.addEventListener("input", () => updateFleteMargenPctHint("#flete-edit-form"));
      }

      async function quoteVenta(formSelector, detailId, messageId, options = {}) {
        if (!options.silent) {
          clearMessage(messageId);
        }
        const formElement = document.querySelector(formSelector);
        const detail = document.getElementById(detailId);
        try {
          const payload = buildFletePayload(new FormData(formElement));
          const viaje = findViajeForFleteQuote(payload);
          if (!payload.tipo_unidad) {
            throw new Error("Escribe el tipo de unidad antes de cotizar venta.");
          }
          const distanciaKm = resolveDistanciaKmForQuote(payload, viaje);
          if (distanciaKm === null) {
            throw new Error(
              "Captura la distancia en km en el flete o define kilometros estimados en el viaje.",
            );
          }
          if (payload.peso_kg === null) {
            throw new Error("Captura el peso en kg antes de cotizar venta.");
          }

          const quote = await api("/fletes/cotizar", {
            method: "POST",
            body: JSON.stringify({
              cliente_id: payload.cliente_id,
              tipo_operacion: payload.tipo_operacion || "subcontratado",
              origen: viaje.origen,
              destino: viaje.destino,
              tipo_unidad: payload.tipo_unidad,
              tipo_carga: payload.tipo_carga,
              distancia_km: distanciaKm,
              peso_kg: payload.peso_kg,
              recargos: 0,
            }),
          });

          const ventaEl = document.querySelector(`${formSelector} [name="monto_estimado"]`);
          if (!ventaEl) {
            throw new Error("No se encontro el campo Precio venta en el formulario.");
          }
          const distInput = document.querySelector(`${formSelector} [name="distancia_km"]`);
          if (
            distInput &&
            (!String(distInput.value || "").trim() || payload.distancia_km === null) &&
            distanciaKm !== null
          ) {
            distInput.value = htmlNumberInputValue(distanciaKm);
          }
          ventaEl.value = formatMoneyInputFromEl(Number(quote.precio_venta_sugerido), ventaEl);
          document.querySelector(`${formSelector} [name="moneda"]`).value = quote.moneda;
          document.querySelector(`${formSelector} [name="metodo_calculo"]`).value = "tarifa";
          refreshMarginForForm(formSelector);
          const advVenta =
            quote.advertencias && quote.advertencias.length
              ? ` Advertencias: ${quote.advertencias.join(" | ")}`
              : "";
          detail.textContent = `Tarifa venta: ${quote.nombre_tarifa}. ${quote.detalle_calculo}${advVenta}`;
          if (!options.silent) {
            setMessage(
              messageId,
              `Venta sugerida: ${formatLocaleDecimal(Number(quote.precio_venta_sugerido), 2, 2)} ${quote.moneda}`,
              "ok",
            );
          }
          return true;
        } catch (error) {
          if (!options.silent) {
            detail.textContent = "No se pudo cotizar automaticamente la venta.";
            setMessage(messageId, error.message, "error");
          }
          return false;
        }
      }

      async function quoteCompra(formSelector, detailId, messageId, options = {}) {
        if (!options.silent) {
          clearMessage(messageId);
        }
        const formElement = document.querySelector(formSelector);
        const detail = document.getElementById(detailId);
        try {
          const payload = buildFletePayload(new FormData(formElement));
          const viaje = findViajeForFleteQuote(payload);
          if (!payload.transportista_id) {
            throw new Error("Selecciona el transportista antes de cotizar compra.");
          }
          if (!payload.tipo_unidad) {
            throw new Error("Escribe el tipo de unidad antes de cotizar compra.");
          }
          const distanciaKm = resolveDistanciaKmForQuote(payload, viaje);
          if (distanciaKm === null) {
            throw new Error(
              "Captura la distancia en km en el flete o define kilometros estimados en el viaje.",
            );
          }
          if (payload.peso_kg === null) {
            throw new Error("Captura el peso en kg antes de cotizar compra.");
          }

          const quote = await api("/fletes/cotizar-compra", {
            method: "POST",
            body: JSON.stringify({
              transportista_id: payload.transportista_id,
              origen: viaje.origen,
              destino: viaje.destino,
              tipo_unidad: payload.tipo_unidad,
              tipo_carga: payload.tipo_carga,
              distancia_km: distanciaKm,
              peso_kg: payload.peso_kg,
              recargos: 0,
            }),
          });

          const compraEl = document.querySelector(`${formSelector} [name="costo_transporte_estimado"]`);
          if (!compraEl) {
            throw new Error("No se encontro el campo Costo estimado en el formulario.");
          }
          const distInput = document.querySelector(`${formSelector} [name="distancia_km"]`);
          if (
            distInput &&
            (!String(distInput.value || "").trim() || payload.distancia_km === null) &&
            distanciaKm !== null
          ) {
            distInput.value = htmlNumberInputValue(distanciaKm);
          }
          compraEl.value = formatMoneyInputFromEl(Number(quote.costo_compra_sugerido), compraEl);
          if (!document.querySelector(`${formSelector} [name="moneda"]`).value) {
            document.querySelector(`${formSelector} [name="moneda"]`).value = quote.moneda;
          }
          refreshMarginForForm(formSelector);
          const advCompra =
            quote.advertencias && quote.advertencias.length
              ? ` Advertencias: ${quote.advertencias.join(" | ")}`
              : "";
          detail.textContent = `Tarifa compra: ${quote.nombre_tarifa}. ${quote.detalle_calculo}. Credito: ${quote.dias_credito} dias.${advCompra}`;
          if (!options.silent) {
            setMessage(
              messageId,
              `Compra sugerida: ${formatLocaleDecimal(Number(quote.costo_compra_sugerido), 2, 2)} ${quote.moneda}`,
              "ok",
            );
          }
          return true;
        } catch (error) {
          if (!options.silent) {
            detail.textContent = "No se pudo cotizar automaticamente la compra.";
            setMessage(messageId, error.message, "error");
          }
          return false;
        }
      }

      const autoQuoteTimers = {};

      function scheduleAutoQuote(formSelector, ventaDetailId, compraDetailId, messageId) {
        const formElement = document.querySelector(formSelector);
        if (!formElement) {
          return;
        }
        const payload = buildFletePayload(new FormData(formElement));
        if (payload.metodo_calculo !== "tarifa") {
          return;
        }
        let viajeAq = null;
        try {
          viajeAq = findViajeForFleteQuote(payload);
        } catch (_e) {
          return;
        }
        const distanciaAq = resolveDistanciaKmForQuote(payload, viajeAq);
        if (!payload.viaje_id || !payload.tipo_unidad || distanciaAq === null || payload.peso_kg === null) {
          return;
        }

        window.clearTimeout(autoQuoteTimers[formSelector]);
        autoQuoteTimers[formSelector] = window.setTimeout(async () => {
          await quoteVenta(formSelector, ventaDetailId, messageId, { silent: true });
          if (payload.transportista_id) {
            await quoteCompra(formSelector, compraDetailId, messageId, { silent: true });
          }
        }, 350);
      }

      function attachAutoQuote(formSelector, ventaDetailId, compraDetailId, messageId) {
        const formElement = document.querySelector(formSelector);
        if (!formElement) {
          return;
        }
        const watchedNames = [
          "cliente_id",
          "transportista_id",
          "viaje_id",
          "tipo_unidad",
          "tipo_carga",
          "distancia_km",
          "peso_kg",
          "metodo_calculo",
        ];
        for (const name of watchedNames) {
          const input = formElement.querySelector(`[name="${name}"]`);
          if (!input) {
            continue;
          }
          const eventName = input.tagName === "SELECT" ? "change" : "input";
          input.addEventListener(eventName, () => {
            scheduleAutoQuote(formSelector, ventaDetailId, compraDetailId, messageId);
          });
          if (eventName !== "change") {
            input.addEventListener("change", () => {
              scheduleAutoQuote(formSelector, ventaDetailId, compraDetailId, messageId);
            });
          }
        }
      }

      if (ventaButton) {
        ventaButton.addEventListener("click", () => quoteVenta("#flete-form", "flete-cotizacion-detalle", "flete-message"));
      }
      if (compraButton) {
        compraButton.addEventListener("click", () => quoteCompra("#flete-form", "flete-cotizacion-compra-detalle", "flete-message"));
      }
      if (editVentaButton) {
        editVentaButton.addEventListener("click", () => quoteVenta("#flete-edit-form", "edit-flete-cotizacion-detalle", "flete-edit-message"));
      }
      if (editCompraButton) {
        editCompraButton.addEventListener("click", () => quoteCompra("#flete-edit-form", "edit-flete-cotizacion-compra-detalle", "flete-edit-message"));
      }

      attachAutoQuote("#flete-form", "flete-cotizacion-detalle", "flete-cotizacion-compra-detalle", "flete-message");
      attachAutoQuote("#flete-edit-form", "edit-flete-cotizacion-detalle", "edit-flete-cotizacion-compra-detalle", "flete-edit-message");
    }

    function initFacturaModule() {
      const today = new Date().toISOString().slice(0, 10);
      const facturaForm = document.getElementById("factura-form");
      if (facturaForm && !facturaForm.elements.fecha_emision.value) {
        facturaForm.elements.fecha_emision.value = today;
      }

      if (!window.__facturaClienteFleteSyncBound) {
        window.__facturaClienteFleteSyncBound = true;
        const fc = document.getElementById("factura-cliente");
        const ff = document.getElementById("factura-flete");
        if (fc && ff) {
          fc.addEventListener("change", () => {
            const prevFlete = integerOrNull(ff.value);
            fillFacturaFleteSelectFiltered(fc.value);
            if (
              prevFlete != null &&
              [...ff.options].some((o) => o.value === String(prevFlete))
            ) {
              ff.value = String(prevFlete);
            }
          });
          ff.addEventListener("change", () => {
            const fid = integerOrNull(ff.value);
            if (!fid) {
              return;
            }
            const f = state.fletes.find((x) => x.id === fid);
            if (f && fc) {
              fc.value = String(f.cliente_id);
              fillFacturaFleteSelectFiltered(fc.value);
              ff.value = String(fid);
            }
          });
        }
      }

      const watchedSelectors = [
        '#factura-form [name="subtotal"]',
        '#factura-form [name="iva_pct"]',
        '#factura-form [name="retencion_monto"]',
        '#factura-edit-form [name="subtotal"]',
        '#factura-edit-form [name="iva_pct"]',
        '#factura-edit-form [name="retencion_monto"]',
      ];
      for (const selector of watchedSelectors) {
        const input = document.querySelector(selector);
        if (!input) {
          continue;
        }
        const formSelector = selector.startsWith("#factura-edit-form") ? "#factura-edit-form" : "#factura-form";
        input.addEventListener("input", () => recalculateFacturaForm(formSelector));
      }

      const autoFillButton = document.getElementById("factura-desde-flete-btn");
      if (autoFillButton) {
        autoFillButton.addEventListener("click", () => {
          clearMessage("factura-message");
          try {
            fillFacturaFromFlete("#factura-form");
            setMessage("factura-message", "Factura autollenada desde el flete.", "ok");
          } catch (error) {
            setMessage("factura-message", error.message, "error");
          }
        });
      }

      const previewFleteBtn = document.getElementById("factura-preview-flete-btn");
      if (previewFleteBtn) {
        previewFleteBtn.addEventListener("click", async () => {
          clearMessage("factura-message");
          const fleteId = integerOrNull(new FormData(document.getElementById("factura-form")).get("flete_id"));
          if (!fleteId) {
            setMessage("factura-message", "Selecciona un flete en el formulario.", "error");
            return;
          }
          try {
            const data = await api(`/facturas/preview-desde-flete/${fleteId}`);
            const fmtN = (v) =>
              v === null || v === undefined ? "—" : formatLocaleDecimal(Number(v), 2, 2);
            const linea1 = `Precio en flete: ${fmtN(data.subtotal_desde_flete)} → IVA ${fmtN(data.iva_monto)} → Total ${fmtN(data.total)} (${data.moneda}).`;
            const linea2 =
              data.subtotal_desde_tarifa_recalculado != null
                ? `Tarifa vigente «${data.nombre_tarifa || "?"}»: ${fmtN(data.subtotal_desde_tarifa_recalculado)} → total ${fmtN(data.total_si_precio_tarifa)}.`
                : `Tarifa automática: ${data.observaciones_sistema}`;
            setMessage("factura-message", `${linea1} ${linea2}`, "ok");
          } catch (error) {
            setMessage("factura-message", error.message, "error");
          }
        });
      }

      const generarAutoBtn = document.getElementById("factura-generar-auto-btn");
      if (generarAutoBtn) {
        generarAutoBtn.addEventListener("click", async () => {
          clearMessage("factura-message");
          const fleteId = integerOrNull(new FormData(document.getElementById("factura-form")).get("flete_id"));
          if (!fleteId) {
            setMessage("factura-message", "Selecciona un flete en el formulario.", "error");
            return;
          }
          const usarTarifa = document.getElementById("factura-gen-usar-tarifa")?.checked || false;
          try {
            const today = new Date().toISOString().slice(0, 10);
            await api("/facturas/generar-desde-flete", {
              method: "POST",
              body: JSON.stringify({
                flete_id: fleteId,
                fecha_emision: today,
                estatus: "emitida",
                usar_precio_tarifa_recalculado: usarTarifa,
              }),
            });
            setMessage("factura-message", "Factura generada. Actualizando datos…", "ok");
            await refreshData();
            setGenericSubpage("factura", "facturaSubpage", "consulta", "consulta");
          } catch (error) {
            setMessage("factura-message", error.message, "error");
          }
        });
      }

      const facturaOsFolioAplicar = document.getElementById("factura-os-folio-aplicar");
      if (facturaOsFolioAplicar) {
        facturaOsFolioAplicar.addEventListener("click", () => {
          aplicarFolioOrdenServicioAFactura("factura-message", "factura-os-folio-buscar", "factura-form-orden-servicio-id");
        });
      }
      const editFacturaOsFolioAplicar = document.getElementById("edit-factura-os-folio-aplicar");
      if (editFacturaOsFolioAplicar) {
        editFacturaOsFolioAplicar.addEventListener("click", () => {
          aplicarFolioOrdenServicioAFactura("factura-edit-message", "edit-factura-os-folio-buscar", "edit-factura-form-orden-servicio-id");
        });
      }
    }

    /** Paginas permitidas por rol (JWT). Sin JWT = API key: acceso completo al menu. admin/direccion/consulta = todo el menu. */
    const ROLE_PAGE_SET = {
      operaciones: new Set([
        "inicio",
        "transportistas",
        "viajes",
        "fletes",
        "operadores",
        "unidades",
        "asignaciones",
        "gastos",
        "despachos",
        "bajas-danos",
        "seguimiento",
      ]),
      contabilidad: new Set([
        "inicio",
        "clientes",
        "transportistas",
        "viajes",
        "fletes",
        "facturas",
        "gastos",
        "tarifas",
        "tarifas-compra",
        "bajas-danos",
      ]),
      ventas: new Set([
        "inicio",
        "clientes",
        "transportistas",
        "viajes",
        "fletes",
        "tarifas",
        "tarifas-compra",
        "facturas",
      ]),
    };

    function sifeCanAccessPage(pageId) {
      if (pageId === "inicio") {
        return true;
      }
      if (pageId === "direccion" && !sessionStorage.getItem("sife_access_token")) {
        return false;
      }
      if (!pageMeta[pageId]) {
        return false;
      }
      if (pageId === "usuarios-admin") {
        if (!sessionStorage.getItem("sife_access_token")) {
          return true;
        }
        const r = (window.__SIFE_ROLE_NAME__ || "").trim().toLowerCase();
        return r === "admin" || r === "direccion";
      }
      if (pageId === "audit-logs") {
        if (!sessionStorage.getItem("sife_access_token")) {
          return false;
        }
        const r = (window.__SIFE_ROLE_NAME__ || "").trim().toLowerCase();
        return r === "admin" || r === "direccion";
      }
      if (!sessionStorage.getItem("sife_access_token")) {
        return true;
      }
      const role = (window.__SIFE_ROLE_NAME__ || "").trim().toLowerCase();
      // Si el servidor entrega JWT sin rol visible, no bloqueamos la UI:
      // el backend RBAC sigue protegiendo operaciones sensibles.
      if (!role) {
        return true;
      }
      if (role === "admin" || role === "direccion" || role === "consulta") {
        return true;
      }
      const allowed = ROLE_PAGE_SET[role];
      if (!allowed) {
        return false;
      }
      return allowed.has(pageId);
    }

    function applyRoleToSidebar() {
      const hasJwt = !!sessionStorage.getItem("sife_access_token");
      const role = (window.__SIFE_ROLE_NAME__ || "").trim().toLowerCase();
      const showAll = !hasJwt || !role || role === "admin" || role === "direccion" || role === "consulta";
      for (const btn of document.querySelectorAll("button.nav-button[data-page]")) {
        const p = btn.dataset.page;
        if (!p) {
          continue;
        }
        let ok = showAll || ROLE_PAGE_SET[role]?.has(p) || p === "inicio";
        if (p === "direccion" && !hasJwt) {
          ok = false;
        }
        if (p === "audit-logs" && !hasJwt) {
          ok = false;
        }
        const restrict = (btn.getAttribute("data-restrict-roles") || "").trim();
        if (restrict && hasJwt) {
          const allowed = restrict.split(",").map((s) => s.trim().toLowerCase()).filter(Boolean);
          if (allowed.length && !allowed.includes(role)) {
            ok = false;
          }
        }
        btn.style.display = ok ? "" : "none";
      }
      syncUsuariosAdminPanels();
      syncOrdenServicioEditVisibility();
    }

    function syncOrdenServicioEditVisibility() {
      const hasJwt = !!sessionStorage.getItem("sife_access_token");
      const role = (window.__SIFE_ROLE_NAME__ || "").trim().toLowerCase();
      const hideEditors = hasJwt && role === "consulta";
      for (const el of document.querySelectorAll("[data-orden-servicio-editor]")) {
        el.style.display = hideEditors ? "none" : "";
      }
    }

    function setPage(page) {
      const raw = pageMeta[page] ? page : "inicio";
      const target = sifeCanAccessPage(raw) ? raw : "inicio";
      for (const section of document.querySelectorAll(".page")) {
        section.classList.toggle("active", section.id === `page-${target}`);
      }
      for (const button of document.querySelectorAll(".nav-button[data-page]")) {
        button.classList.toggle("active", button.dataset.page === target);
      }
      document.getElementById("page-title").textContent = pageMeta[target][0];
      document.getElementById("page-description").textContent = pageMeta[target][1];
      window.location.hash = target;
      if (target === "fletes" && typeof populateSelects === "function") {
        populateSelects();
      }
      if (
        target === "unidades" &&
        state.catalogLoaded &&
        Array.isArray(state.unidades) &&
        state.unidades.length === 0
      ) {
        void refreshData().catch((e) => {
          setMessage("unidad-consulta-message", e.message || "No se pudo recargar el catalogo.", "error");
        });
      }
      if (target === "usuarios-admin") {
        void refreshUsuariosAdminTable();
      }
      if (target === "direccion") {
        void refreshDireccionDashboard();
      }
      if (target === "bajas-danos") {
        void refreshBajasDanosList();
      }
      if (target === "audit-logs") {
        void refreshAuditLogs();
      }
    }

    function renderAuditLogs(items) {
      const box = document.getElementById("audit-logs-list");
      if (!box) return;
      if (!items || items.length === 0) {
        box.innerHTML = '<div class="hint">Sin registros para los filtros seleccionados.</div>';
        return;
      }
      const rows = items
        .map(
          (it) => `
            <tr>
              <td>${Number(it.id || 0)}</td>
              <td>${escapeHtml(it.created_at || "")}</td>
              <td>${escapeHtml(it.entity || "")}</td>
              <td>${escapeHtml(it.entity_id || "")}</td>
              <td>${escapeHtml(it.action || "")}</td>
              <td>${escapeHtml(it.actor_type || "")}</td>
              <td>${escapeHtml(it.actor_username || "")}</td>
              <td>${escapeHtml(it.source_method || "")}</td>
              <td>${escapeHtml(it.source_path || "")}</td>
            </tr>
          `
        )
        .join("");
      box.innerHTML = `
        <table>
          <thead>
            <tr>
              <th>ID</th><th>Fecha</th><th>Entidad</th><th>Entity ID</th><th>Acción</th><th>Actor tipo</th><th>Actor</th><th>Método</th><th>Ruta</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      `;
    }

    async function refreshAuditLogs() {
      const form = document.getElementById("audit-logs-form");
      if (!form) return;
      const fd = new FormData(form);
      const q = new URLSearchParams();
      const put = (k, v) => {
        const t = String(v || "").trim();
        if (t) q.set(k, t);
      };
      put("entity", fd.get("entity"));
      put("entity_id", fd.get("entity_id"));
      put("action", fd.get("action"));
      put("actor_username", fd.get("actor_username"));
      put("skip", fd.get("skip") || "0");
      put("limit", fd.get("limit") || "50");
      clearMessage("audit-message");
      const summary = document.getElementById("audit-summary");
      try {
        const data = await api(`/audit-logs?${q.toString()}`);
        renderAuditLogs(data?.items || []);
        if (summary) {
          summary.textContent = `Total: ${Number(data?.total || 0)} registros (skip ${Number(
            data?.skip || 0
          )}, limit ${Number(data?.limit || 0)}).`;
        }
        setMessage("audit-message", "Consulta de auditoría completada.", "ok");
      } catch (error) {
        if (summary) summary.textContent = "Sin consulta.";
        renderAuditLogs([]);
        setMessage("audit-message", error?.message || "No se pudo consultar auditoría.", "error");
      }
    }


    function initNavigation() {
      const sidebar = document.querySelector("aside.sidebar");
      if (sidebar) {
        sidebar.addEventListener("click", (event) => {
          const btn = event.target && event.target.closest
            ? event.target.closest("button.nav-button[data-page]")
            : null;
          if (!btn) return;
          event.preventDefault();
          setPage(btn.dataset.page);
        });
      }
      window.addEventListener("hashchange", () => {
        const h = window.location.hash.replace(/^#/, "").split("&")[0];
        if (h && pageMeta[h]) {
          setPage(h);
        }
      });
      const initialHash = window.location.hash.replace(/^#/, "").split("&")[0];
      setPage(initialHash && pageMeta[initialHash] ? initialHash : "inicio");
      window.sifeSetPage = setPage;
    }

    function getAuthHeaders() {
      const token = sessionStorage.getItem("sife_access_token");
      if (token) {
        return { Authorization: "Bearer " + token };
      }
      return { "X-API-Key": API_KEY };
    }

    async function api(path, options = {}) {
      const headers = {
        "Accept": "application/json",
        ...getAuthHeaders(),
        ...(options.body ? {"Content-Type": "application/json"} : {}),
        ...(options.headers || {}),
      };

      const response = await fetch(`${API_BASE}${path}`, {
        method: options.method || "GET",
        headers,
        body: options.body,
      });

      if (!response.ok) {
        let detail = `HTTP ${response.status}`;
        const raw = await response.text();
        try {
          const payload = raw ? JSON.parse(raw) : {};
          if (typeof payload.detail === "string") {
            detail = payload.detail;
          } else if (Array.isArray(payload.detail)) {
            detail = payload.detail.map((item) => item.msg || JSON.stringify(item)).join(" | ");
          } else if (
            payload.detail &&
            typeof payload.detail === "object" &&
            payload.detail.tipo === "cumplimiento_documental"
          ) {
            const b = (payload.detail.bloqueos || []).join("\\n• ");
            const a = (payload.detail.advertencias || []).join("\\n• ");
            detail =
              (payload.detail.mensaje || "Validación documental.") +
              (b ? "\\n\\nPendientes:\\n• " + b : "") +
              (a ? "\\n\\nAdvertencias:\\n• " + a : "");
          } else if (payload.detail !== undefined) {
            detail = JSON.stringify(payload.detail);
          } else if (raw) {
            detail = raw;
          }
        } catch (_parseError) {
          if (raw) {
            detail = raw;
          }
        }
        throw new Error(detail);
      }

      if (response.status === 204) {
        return null;
      }

      return response.json();
    }

    async function apiDownload(path, filenameFallback) {
      const response = await fetch(`${API_BASE}${path}`, {
        method: "GET",
        headers: {
          Accept: "text/csv,application/json",
          ...getAuthHeaders(),
        },
      });
      if (!response.ok) {
        const raw = await response.text();
        throw new Error(raw || `HTTP ${response.status}`);
      }
      const blob = await response.blob();
      const cd = response.headers.get("content-disposition") || "";
      const m = cd.match(/filename=\"?([^\";]+)\"?/i);
      const filename = m && m[1] ? m[1] : filenameFallback;
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    }

    function syncUsuariosAdminPanels() {
      const hasJwt = !!sessionStorage.getItem("sife_access_token");
      const r = (window.__SIFE_ROLE_NAME__ || "").trim().toLowerCase();
      const selfCard = document.getElementById("usuarios-self-pass-card");
      const adminCard = document.getElementById("usuarios-admin-card");
      if (selfCard) {
        selfCard.style.display = hasJwt ? "" : "none";
      }
      if (adminCard) {
        adminCard.style.display = !hasJwt || r === "admin" || r === "direccion" ? "" : "none";
      }
    }

    async function refreshUsuariosAdminTable() {
      const tbody = document.getElementById("usuarios-admin-tbody");
      const msg = document.getElementById("usuarios-admin-msg");
      const adminCard = document.getElementById("usuarios-admin-card");
      if (!tbody || !adminCard || adminCard.style.display === "none") {
        return;
      }
      msg.textContent = "";
      msg.style.color = "";
      try {
        const rows = await api("/usuarios");
        const roles = await api("/usuarios/roles");
        const actor = (window.__SIFE_ROLE_NAME__ || "").trim().toLowerCase();
        const hasJwt = !!sessionStorage.getItem("sife_access_token");
        const canAssignAdmin = !hasJwt || actor === "admin";
        tbody.replaceChildren();
        for (const u of rows) {
          const tr = document.createElement("tr");
          tr.dataset.userId = String(u.id);
          const tdId = document.createElement("td");
          tdId.style.padding = "6px";
          tdId.textContent = String(u.id);
          const tdUser = document.createElement("td");
          tdUser.style.padding = "6px";
          tdUser.textContent = u.username;
          const tdRole = document.createElement("td");
          tdRole.style.padding = "6px";
          const sel = document.createElement("select");
          sel.className = "usuarios-role-sel";
          sel.dataset.userId = String(u.id);
          for (const ro of roles) {
            if (!canAssignAdmin && (ro.name || "").toLowerCase() === "admin") {
              continue;
            }
            const o = document.createElement("option");
            o.value = ro.name;
            o.textContent = ro.name;
            if ((ro.name || "") === u.role_name) {
              o.selected = true;
            }
            sel.appendChild(o);
          }
          tdRole.appendChild(sel);
          const tdAct = document.createElement("td");
          tdAct.style.padding = "6px";
          const cb = document.createElement("input");
          cb.type = "checkbox";
          cb.className = "usuarios-active-cb";
          cb.dataset.userId = String(u.id);
          cb.checked = !!u.is_active;
          tdAct.appendChild(cb);
          const tdBtn = document.createElement("td");
          tdBtn.style.padding = "6px";
          const b = document.createElement("button");
          b.type = "button";
          b.className = "secondary-button usuarios-pass";
          b.dataset.userId = String(u.id);
          b.textContent = "Nueva clave";
          tdBtn.appendChild(b);
          tr.appendChild(tdId);
          tr.appendChild(tdUser);
          tr.appendChild(tdRole);
          tr.appendChild(tdAct);
          tr.appendChild(tdBtn);
          tbody.appendChild(tr);
        }
      } catch (e) {
        msg.textContent = e && e.message ? e.message : "Error al cargar usuarios.";
        msg.style.color = "#b91c1c";
      }
    }

    async function loadUsuariosCreateRoleSelect() {
      const sel = document.getElementById("usuarios-create-role");
      if (!sel) {
        return;
      }
      sel.replaceChildren();
      try {
        const roles = await api("/usuarios/roles");
        const actor = (window.__SIFE_ROLE_NAME__ || "").trim().toLowerCase();
        const hasJwt = !!sessionStorage.getItem("sife_access_token");
        const canAssignAdmin = !hasJwt || actor === "admin";
        for (const r of roles) {
          if (!canAssignAdmin && (r.name || "").toLowerCase() === "admin") {
            continue;
          }
          const o = document.createElement("option");
          o.value = r.name;
          o.textContent = r.name;
          sel.appendChild(o);
        }
      } catch (_e) {}
    }

    function initUsuariosAdminModule() {
      syncUsuariosAdminPanels();
      const selfForm = document.getElementById("usuarios-self-pass-form");
      const selfMsg = document.getElementById("usuarios-self-pass-msg");
      if (selfForm) {
        selfForm.addEventListener("submit", async (e) => {
          e.preventDefault();
          const fd = new FormData(selfForm);
          if (fd.get("new1") !== fd.get("new2")) {
            selfMsg.textContent = "Las contraseñas nuevas no coinciden.";
            selfMsg.style.color = "#b91c1c";
            return;
          }
          try {
            await api("/auth/change-password", {
              method: "POST",
              body: JSON.stringify({
                current_password: fd.get("current") || "",
                new_password: fd.get("new1") || "",
              }),
            });
            selfMsg.textContent = "Contraseña actualizada.";
            selfMsg.style.color = "#0f766e";
            selfForm.reset();
          } catch (err) {
            selfMsg.textContent = err.message || "Error";
            selfMsg.style.color = "#b91c1c";
          }
        });
      }
      const createForm = document.getElementById("usuarios-create-form");
      const adminMsg = document.getElementById("usuarios-admin-msg");
      if (createForm) {
        createForm.addEventListener("submit", async (e) => {
          e.preventDefault();
          const fd = new FormData(createForm);
          const payload = {
            username: (fd.get("username") || "").trim(),
            password: fd.get("password") || "",
            role_name: (fd.get("role_name") || "").trim(),
            email: (fd.get("email") || "").trim() || null,
            full_name: (fd.get("full_name") || "").trim() || null,
          };
          try {
            await api("/usuarios", { method: "POST", body: JSON.stringify(payload) });
            adminMsg.textContent = "Usuario creado.";
            adminMsg.style.color = "#0f766e";
            createForm.reset();
            await loadUsuariosCreateRoleSelect();
            await refreshUsuariosAdminTable();
          } catch (err) {
            adminMsg.textContent = err.message || "Error";
            adminMsg.style.color = "#b91c1c";
          }
        });
      }
      const tbody = document.getElementById("usuarios-admin-tbody");
      if (tbody) {
        tbody.addEventListener("change", async (ev) => {
          const t = ev.target;
          if (t.classList.contains("usuarios-role-sel")) {
            const id = parseInt(t.dataset.userId, 10);
            try {
              await api(`/usuarios/${id}`, {
                method: "PATCH",
                body: JSON.stringify({ role_name: t.value }),
              });
            } catch (err) {
              window.alert(err.message || "Error");
              void refreshUsuariosAdminTable();
            }
          }
          if (t.classList.contains("usuarios-active-cb")) {
            const id = parseInt(t.dataset.userId, 10);
            try {
              await api(`/usuarios/${id}`, {
                method: "PATCH",
                body: JSON.stringify({ is_active: t.checked }),
              });
            } catch (err) {
              window.alert(err.message || "Error");
              t.checked = !t.checked;
            }
          }
        });
        tbody.addEventListener("click", async (ev) => {
          const btn = ev.target.closest(".usuarios-pass");
          if (!btn) {
            return;
          }
          const id = parseInt(btn.dataset.userId, 10);
          const np = window.prompt("Nueva contraseña para este usuario:");
          if (!np) {
            return;
          }
          try {
            await api(`/usuarios/${id}/password`, {
              method: "POST",
              body: JSON.stringify({ new_password: np }),
            });
            if (adminMsg) {
              adminMsg.textContent = "Contraseña actualizada para id " + id + ".";
              adminMsg.style.color = "#0f766e";
            }
          } catch (err) {
            window.alert(err.message || "Error");
          }
        });
      }
      void loadUsuariosCreateRoleSelect();
    }

    function initAuditLogsModule() {
      const form = document.getElementById("audit-logs-form");
      if (!form || form.dataset.bound === "true") return;
      form.dataset.bound = "true";
      const clearBtn = document.getElementById("audit-clear-btn");
      form.addEventListener("submit", (event) => {
        event.preventDefault();
        void refreshAuditLogs();
      });
      if (clearBtn && clearBtn.dataset.bound !== "true") {
        clearBtn.dataset.bound = "true";
        clearBtn.addEventListener("click", () => {
          form.reset();
          const skip = document.getElementById("audit-skip");
          const limit = document.getElementById("audit-limit");
          if (skip) skip.value = "0";
          if (limit) limit.value = "50";
          const summary = document.getElementById("audit-summary");
          if (summary) summary.textContent = "Sin consulta.";
          renderAuditLogs([]);
          clearMessage("audit-message");
        });
      }
    }

    async function initAuthBar() {
      const hint = document.getElementById("auth-hint");
      const loginLink = document.getElementById("auth-login-link");
      const logoutBtn = document.getElementById("auth-logout-btn");
      const apiKeyNote = document.getElementById("auth-apikey-note");
      if (!hint || !loginLink || !logoutBtn) return;
      function setApiKeyNoteVisible(show) {
        if (apiKeyNote) apiKeyNote.style.display = show ? "inline" : "none";
      }
      logoutBtn.addEventListener("click", () => {
        sessionStorage.removeItem("sife_access_token");
        window.__SIFE_ROLE_NAME__ = "";
        window.location.replace("/login?next=/ui&logged_out=1");
      });
      const token = sessionStorage.getItem("sife_access_token");
      window.__SIFE_ROLE_NAME__ = "";
      if (!token) {
        hint.textContent = "Sin sesión JWT. Pulse Iniciar sesión o siga con API key del servidor.";
        loginLink.style.display = "";
        logoutBtn.style.display = "none";
        setApiKeyNoteVisible(true);
        applyRoleToSidebar();
        return;
      }
      try {
        const r = await fetch(`${API_BASE}/auth/me`, {
          headers: { Accept: "application/json", ...getAuthHeaders() },
        });
        if (!r.ok) {
          sessionStorage.removeItem("sife_access_token");
          window.__SIFE_ROLE_NAME__ = "";
          hint.textContent = "Sesión JWT no válida. Pulse Iniciar sesión de nuevo.";
          loginLink.style.display = "";
          logoutBtn.style.display = "none";
          setApiKeyNoteVisible(true);
          applyRoleToSidebar();
          return;
        }
        const me = await r.json();
        window.__SIFE_ROLE_NAME__ = me.role_name || "";
        const roleLabel = (me.role_name || "").trim().toLowerCase();
        if (!roleLabel) {
          hint.textContent =
            "Sesión: " +
            me.username +
            " (sin rol). Menú completo en UI; permisos finales se validan en servidor.";
        } else {
          const menuNote =
            roleLabel !== "admin" &&
            roleLabel !== "direccion" &&
            roleLabel !== "consulta"
              ? " Menú acotado a su rol."
              : "";
          hint.textContent = "Sesión: " + me.username + " (" + me.role_name + ")." + menuNote;
        }
        loginLink.style.display = "none";
        logoutBtn.style.display = "inline-block";
        setApiKeyNoteVisible(false);
        applyRoleToSidebar();
      } catch (_e) {
        window.__SIFE_ROLE_NAME__ = "";
        hint.textContent = "No se pudo validar JWT. Pulse Iniciar sesión.";
        loginLink.style.display = "";
        logoutBtn.style.display = "none";
        setApiKeyNoteVisible(true);
        applyRoleToSidebar();
      }
    }

    const SELECT_CLASS = {
      cliente: { tag: "Cliente", title: "Catalogo comercial: clientes (razon social, RFC)." },
      transportista: { tag: "Transportista", title: "Catalogo de proveedores de transporte." },
      viaje: { tag: "Viaje", title: "Planes de ruta (codigo, origen, destino)." },
      flete: { tag: "Flete", title: "Servicios de flete vinculados a cliente y viaje." },
      operador: { tag: "Operador", title: "Choferes dados de alta para operacion." },
      unidad: { tag: "Unidad", title: "Vehiculos (economico, placas) por transportista." },
      asignacion: { tag: "Asignacion", title: "Combinacion operador + unidad + viaje." },
      despacho: { tag: "Despacho", title: "Salidas programadas ligadas a asignacion y flete." },
    };

    function escapeSelectAttr(value) {
      return String(value)
        .replace(/&/g, "&amp;")
        .replace(/"/g, "&quot;");
    }

    function escapeSelectText(value) {
      return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
    }

    function fillSelect(selectId, items, getValue, getLabel, options = {}) {
      const select = document.getElementById(selectId);
      if (!select) {
        return;
      }

      const current = select.value;
      const includeEmpty = options.includeEmpty ?? true;
      const emptyLabel = options.emptyLabel || "Selecciona...";
      const classKey = options.classKey || null;
      const meta = classKey && SELECT_CLASS[classKey] ? SELECT_CLASS[classKey] : null;
      const prefix = meta ? `${meta.tag} · ` : "";

      if (meta) {
        select.title = meta.title;
        select.dataset.catalog = classKey;
      } else {
        select.removeAttribute("title");
        select.removeAttribute("data-catalog");
      }

      const html = [];

      if (includeEmpty) {
        html.push(`<option value="">${escapeSelectText(emptyLabel)}</option>`);
      }

      for (const item of items) {
        const value = getValue(item);
        const label = prefix + getLabel(item);
        html.push(`<option value="${escapeSelectAttr(value)}">${escapeSelectText(label)}</option>`);
      }

      select.innerHTML = html.join("");
      if (current && [...select.options].some((option) => option.value === current)) {
        select.value = current;
      }
    }

    /** Inserta opcion PATCH flete_id/viaje_id/despacho_id = null (valor interno __clear__). */
    function addOrdenServicioVinculoClearOption(selectId) {
      const sel = document.getElementById(selectId);
      if (!sel || sel.options.length === 0) {
        return;
      }
      if ([...sel.options].some((o) => o.value === "__clear__")) {
        return;
      }
      const opt = document.createElement("option");
      opt.value = "__clear__";
      opt.textContent = "Quitar vínculo";
      const first = sel.options[0];
      sel.insertBefore(opt, first.nextSibling);
    }

    function fillClienteContactoEditSelect(filterText, selectedClienteId) {
      const selectId = "cliente-contacto-edit-cliente";
      const select = document.getElementById(selectId);
      if (!select) {
        return;
      }
      const q = (filterText || "").trim().toLowerCase();
      let items = state.clientes;
      if (q) {
        items = state.clientes.filter((c) => {
          const blob = [c.razon_social, c.nombre_comercial, c.rfc, String(c.id)]
            .filter(Boolean)
            .join(" ")
            .toLowerCase();
          return blob.includes(q);
        });
      }
      const ensureId =
        selectedClienteId != null && selectedClienteId !== ""
          ? String(selectedClienteId)
          : select.value || "";
      if (q && ensureId && !items.some((c) => String(c.id) === ensureId)) {
        const missing = state.clientes.find((c) => String(c.id) === ensureId);
        if (missing) {
          items = [missing, ...items];
        }
      }
      if (!state.clientes.length) {
        select.innerHTML = '<option value="">Sin clientes en catalogo</option>';
        select.disabled = true;
        return;
      }
      if (items.length === 0) {
        select.innerHTML = '<option value="">Sin coincidencias</option>';
        select.disabled = true;
        return;
      }
      select.disabled = false;
      fillSelect(selectId, items, (item) => item.id, (item) => `${item.id} - ${item.razon_social}`, { includeEmpty: false, classKey: "cliente" });
      if (ensureId && [...select.options].some((option) => option.value === ensureId)) {
        select.value = ensureId;
      }
    }

    function fillClienteDomicilioSelect(filterText, selectedClienteId) {
      const selectId = "cliente-domicilio-cliente";
      const select = document.getElementById(selectId);
      if (!select) {
        return;
      }
      const q = (filterText || "").trim().toLowerCase();
      let items = state.clientes;
      if (q) {
        items = state.clientes.filter((c) => {
          const blob = [c.razon_social, c.nombre_comercial, c.rfc, String(c.id)]
            .filter(Boolean)
            .join(" ")
            .toLowerCase();
          return blob.includes(q);
        });
      }
      const ensureId =
        selectedClienteId != null && selectedClienteId !== ""
          ? String(selectedClienteId)
          : select.value || "";
      if (q && ensureId && !items.some((c) => String(c.id) === ensureId)) {
        const missing = state.clientes.find((c) => String(c.id) === ensureId);
        if (missing) {
          items = [missing, ...items];
        }
      }
      if (!state.clientes.length) {
        select.innerHTML = '<option value="">Sin clientes en catalogo</option>';
        select.disabled = true;
        return;
      }
      if (items.length === 0) {
        select.innerHTML = '<option value="">Sin coincidencias</option>';
        select.disabled = true;
        return;
      }
      select.disabled = false;
      fillSelect(selectId, items, (item) => item.id, (item) => `${item.id} - ${item.razon_social}`, {
        includeEmpty: true,
        emptyLabel: "Selecciona cliente",
        classKey: "cliente",
      });
      if (ensureId && [...select.options].some((option) => option.value === ensureId)) {
        select.value = ensureId;
      }
    }

    function renderStats() {
      const metrics = [
        ["Clientes", state.clientes.length],
        ["Transportistas", state.transportistas.length],
        ["Viajes", state.viajes.length],
        ["Fletes", state.fletes.length],
        ["Facturas", state.facturas.length],
        ["Gastos", state.gastos.length],
        ["Tarifas", state.tarifas.length],
        ["Tarifas compra", state.tarifasCompra.length],
        ["Operadores", state.operadores.length],
        ["Unidades", state.unidades.length],
        ["Asignaciones", state.asignaciones.length],
        ["Despachos", state.despachos.length],
        ["Ordenes servicio", state.ordenesServicio.length],
      ];

      document.getElementById("stats").innerHTML = metrics.map(([label, value]) => `
        <div class="stat">
          <strong>${value}</strong>
          <div>${label}</div>
        </div>
      `).join("");
    }

    function renderClientes() {
      const items = filteredClientes();
      const rows = items.map((item) => `
        <tr>
          <td>${item.id}</td>
          <td>${item.razon_social}</td>
          <td>${item.nombre_comercial || "-"}</td>
          <td>${item.tipo_cliente || "-"}</td>
          <td>${item.rfc || "-"}</td>
          <td>${item.contactos?.length || 0}</td>
          <td>${item.domicilios?.length || 0}</td>
          <td><span class="pill">${item.activo ? "activo" : "inactivo"}</span></td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startClienteEdit(${item.id})">Editar</button>
            </div>
          </td>
        </tr>
      `).join("");

      document.getElementById("clientes-table").innerHTML = `
        <table>
          <thead><tr><th>ID</th><th>Razon social</th><th>Nombre comercial</th><th>Tipo</th><th>RFC</th><th>Contactos</th><th>Domicilios</th><th>Estatus</th><th>Acciones</th></tr></thead>
          <tbody>${rows || '<tr><td colspan="9">Sin clientes con ese filtro.</td></tr>'}</tbody>
        </table>
      `;
    }

    function getClienteBySelect(selectId) {
      const value = document.getElementById(selectId)?.value || "";
      if (!value) {
        return null;
      }
      return state.clientes.find((item) => String(item.id) === value) || null;
    }

    function clienteModuleSummaryText(cliente) {
      if (!cliente) {
        return "Selecciona un cliente para continuar.";
      }
      return `Cliente ${cliente.id} - ${cliente.razon_social}. Comercial: ${cliente.nombre_comercial || "-"}. RFC: ${cliente.rfc || "-"}. Contactos: ${cliente.contactos?.length || 0}. Domicilios: ${cliente.domicilios?.length || 0}.`;
    }

    function syncClienteModuleSummaries() {
      const contactoCliente = getClienteBySelect("cliente-contacto-cliente");
      const domicilioCliente = getClienteBySelect("cliente-domicilio-cliente");
      const condicionCliente = getClienteBySelect("cliente-condicion-cliente");
      const contactoNode = document.getElementById("cliente-contacto-summary");
      const domicilioNode = document.getElementById("cliente-domicilio-summary");
      const condicionNode = document.getElementById("cliente-condicion-selected-summary");
      if (contactoNode) {
        contactoNode.textContent = clienteModuleSummaryText(contactoCliente);
      }
      if (domicilioNode) {
        domicilioNode.textContent = clienteModuleSummaryText(domicilioCliente);
      }
      if (condicionNode) {
        condicionNode.textContent = clienteModuleSummaryText(condicionCliente);
      }
    }

    function syncClienteModuleSelection(sourceSelectId) {
      cancelClienteContactoEdit();
      const source = document.getElementById(sourceSelectId);
      const value = source?.value || "";
      if (value) {
        for (const selectId of [
          "cliente-contacto-cliente",
          "cliente-domicilio-cliente",
          "cliente-condicion-cliente",
        ]) {
          const select = document.getElementById(selectId);
          if (select) {
            select.value = value;
          }
        }
      }
      const domicilioBuscarEl = document.getElementById("cliente-domicilio-buscar");
      const domicilioSelectEl = document.getElementById("cliente-domicilio-cliente");
      if (domicilioBuscarEl && domicilioSelectEl) {
        fillClienteDomicilioSelect(domicilioBuscarEl.value, value || domicilioSelectEl.value || null);
      }
      if (sourceSelectId === "cliente-contacto-cliente") {
        setClienteSubpage("contactos");
      } else if (sourceSelectId === "cliente-domicilio-cliente") {
        setClienteSubpage("domicilios");
      } else if (sourceSelectId === "cliente-condicion-cliente") {
        setClienteSubpage("condiciones");
      }
      syncClienteModuleSummaries();
      renderClienteContactos();
      flushClienteDomiciliosForSelectedClient(value);
      syncClienteCondicionForm();
    }

    function syncTransportistaModuleSelection(sourceSelectId) {
      cancelTransportistaContactoEdit();
      const source = document.getElementById(sourceSelectId);
      const value = source?.value || "";
      if (value) {
        for (const selectId of [
          "transportista-contacto-transportista",
          "transportista-documento-transportista",
        ]) {
          const select = document.getElementById(selectId);
          if (select) {
            select.value = value;
          }
        }
      }
      if (sourceSelectId === "transportista-contacto-transportista") {
        setTransportistaSubpage("contactos");
      } else if (sourceSelectId === "transportista-documento-transportista") {
        setTransportistaSubpage("documentos");
      }
      renderTransportistaContactos();
      renderTransportistaDocumentos();
    }

    async function refreshClienteDomiciliosFromApi(clienteId) {
      const id = typeof clienteId === "number" ? clienteId : parseInt(clienteId, 10);
      if (!Number.isFinite(id) || id <= 0) {
        return;
      }
      try {
        const res = await api(`/clientes/${id}/domicilios`);
        const idx = state.clientes.findIndex((c) => Number(c.id) === Number(id));
        if (idx >= 0) {
          state.clientes[idx].domicilios = res.items;
        }
      } catch (e) {
        /* dejar datos en memoria */
      }
    }

    function flushClienteDomiciliosForSelectedClient(selectedValue) {
      void (async () => {
        const v = selectedValue != null ? String(selectedValue).trim() : "";
        if (v) {
          await refreshClienteDomiciliosFromApi(parseInt(v, 10));
        }
        renderClienteDomicilios();
      })();
    }

    function renderClienteContactos() {
      const cliente = getClienteBySelect("cliente-contacto-cliente");
      syncClienteModuleSummaries();
      if (!cliente) {
        document.getElementById("cliente-contactos-table").innerHTML = '<div class="hint">Selecciona un cliente para ver sus contactos.</div>';
        return;
      }
      const rows = (cliente.contactos || []).map((item) => `
        <tr>
          <td>${item.nombre}</td>
          <td>${item.area || "-"}</td>
          <td>${item.puesto || "-"}</td>
          <td>${item.email || "-"}</td>
          <td>${item.telefono || item.celular || "-"}</td>
          <td>${item.principal ? '<span class="pill">principal</span>' : '-'}</td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startClienteContactoEdit(${cliente.id}, ${item.id})">Editar</button>
              <button type="button" class="secondary-button small-button" onclick="deleteClienteContacto(${cliente.id}, ${item.id})">Eliminar</button>
            </div>
          </td>
        </tr>
      `).join("");
      document.getElementById("cliente-contactos-table").innerHTML = `
        <table>
          <thead><tr><th>Nombre</th><th>Area</th><th>Puesto</th><th>Email</th><th>Telefono</th><th>Principal</th><th>Acciones</th></tr></thead>
          <tbody>${rows || '<tr><td colspan="7">Sin contactos para este cliente.</td></tr>'}</tbody>
        </table>
      `;
    }

    function renderClienteDomicilios() {
      const cliente = getClienteBySelect("cliente-domicilio-cliente");
      syncClienteModuleSummaries();
      if (!cliente) {
        document.getElementById("cliente-domicilios-table").innerHTML = '<div class="hint">Selecciona un cliente para ver sus domicilios.</div>';
        return;
      }
      const rows = (cliente.domicilios || []).map((item) => `
        <tr>
          <td>${item.tipo_domicilio}</td>
          <td>${item.nombre_sede}</td>
          <td>${item.municipio || "-"}</td>
          <td>${item.estado || "-"}</td>
          <td>${item.horario_carga || "-"}</td>
          <td>${item.horario_descarga || "-"}</td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startClienteDomicilioEdit(${cliente.id}, ${item.id})">Editar</button>
              <button type="button" class="secondary-button small-button" onclick="deleteClienteDomicilio(${cliente.id}, ${item.id})">Eliminar</button>
            </div>
          </td>
        </tr>
      `).join("");
      document.getElementById("cliente-domicilios-table").innerHTML = `
        <table>
          <thead><tr><th>Tipo</th><th>Sede</th><th>Municipio</th><th>Estado</th><th>Horario carga</th><th>Horario descarga</th><th>Acciones</th></tr></thead>
          <tbody>${rows || '<tr><td colspan="7">Sin domicilios para este cliente.</td></tr>'}</tbody>
        </table>
      `;
    }

    function renderClienteCondicion() {
      const cliente = getClienteBySelect("cliente-condicion-cliente");
      const node = document.getElementById("cliente-condicion-summary");
      syncClienteModuleSummaries();
      if (!cliente) {
        node.textContent = "Selecciona un cliente para ver o capturar sus condiciones comerciales.";
        return;
      }
      const condicion = cliente.condicion_comercial;
      if (!condicion) {
        node.textContent = "Este cliente aun no tiene condiciones comerciales registradas.";
        return;
      }
      const limFmt =
        condicion.limite_credito === null || condicion.limite_credito === undefined
          ? "0.00"
          : formatLocaleDecimal(Number(condicion.limite_credito), 2, 2);
      node.textContent = `Credito: ${condicion.dias_credito ?? 0} dias. Limite: ${limFmt} ${condicion.moneda_preferida}. Forma pago: ${condicion.forma_pago || "-"}.`;
    }

    function syncClienteCondicionForm() {
      const form = document.getElementById("cliente-condicion-form");
      const cliente = getClienteBySelect("cliente-condicion-cliente");
      if (!form) {
        return;
      }
      syncClienteModuleSummaries();
      if (!cliente) {
        form.reset();
        form.elements.moneda_preferida.value = "MXN";
        renderClienteCondicion();
        return;
      }
      const condicion = cliente.condicion_comercial;
      form.elements.cliente_id.value = String(cliente.id);
      form.elements.dias_credito.value =
        condicion == null ? "" : integerStringForNumberInput(condicion.dias_credito);
      form.elements.limite_credito.value =
        condicion == null ? "" : moneyFieldFromApi(condicion.limite_credito, 2, 2);
      form.elements.moneda_preferida.value = condicion?.moneda_preferida || "MXN";
      form.elements.forma_pago.value = condicion?.forma_pago || "";
      form.elements.uso_cfdi.value = condicion?.uso_cfdi || "";
      form.elements.requiere_oc.checked = Boolean(condicion?.requiere_oc);
      form.elements.requiere_cita.checked = Boolean(condicion?.requiere_cita);
      form.elements.bloqueado_credito.checked = Boolean(condicion?.bloqueado_credito);
      form.elements.observaciones_credito.value = condicion?.observaciones_credito || "";
      applyMoneyFormatToForm(form);
      renderClienteCondicion();
    }

    function startClienteContactoEdit(clienteId, contactoId) {
      const cliente = state.clientes.find((item) => item.id === clienteId);
      const contacto = cliente?.contactos?.find((item) => item.id === contactoId);
      if (!cliente || !contacto) {
        return;
      }
      uiState.editing.clienteContactoId = contactoId;
      setClienteSubpage("contactos");
      const buscar = document.getElementById("cliente-contacto-edit-buscar");
      if (buscar) {
        buscar.value = "";
      }
      const form = document.getElementById("cliente-contacto-edit-form");
      form.elements.id.value = contacto.id;
      document.getElementById("cliente-contacto-path-cliente").value = String(clienteId);
      fillClienteContactoEditSelect("", cliente.id);
      form.elements.nombre.value = contacto.nombre || "";
      form.elements.area.value = contacto.area || "";
      form.elements.puesto.value = contacto.puesto || "";
      form.elements.email.value = contacto.email || "";
      form.elements.telefono.value = contacto.telefono || "";
      form.elements.extension.value = contacto.extension || "";
      form.elements.celular.value = contacto.celular || "";
      form.elements.principal.checked = Boolean(contacto.principal);
      form.elements.activo.checked = Boolean(contacto.activo);
      showPanel("cliente-contacto-edit-panel");
      clearMessage("cliente-contacto-edit-message");
    }

    function cancelClienteContactoEdit() {
      uiState.editing.clienteContactoId = null;
      const buscar = document.getElementById("cliente-contacto-edit-buscar");
      if (buscar) {
        buscar.value = "";
      }
      document.getElementById("cliente-contacto-edit-form").reset();
      hidePanel("cliente-contacto-edit-panel", "cliente-contacto-edit-message");
    }

    async function deleteClienteContacto(clienteId, contactoId) {
      if (!window.confirm("¿Eliminar este contacto del cliente?")) {
        return;
      }
      clearMessage("cliente-contacto-message");
      try {
        await api(`/clientes/${clienteId}/contactos/${contactoId}`, { method: "DELETE" });
        if (uiState.editing.clienteContactoId === contactoId) {
          cancelClienteContactoEdit();
        }
        setMessage("cliente-contacto-message", "Contacto eliminado.", "ok");
        await refreshData();
        document.getElementById("cliente-contacto-cliente").value = String(clienteId);
        renderClienteContactos();
      } catch (error) {
        setMessage("cliente-contacto-message", error.message, "error");
      }
    }

    async function startClienteDomicilioEdit(clienteId, domicilioId) {
      const cliente = state.clientes.find((item) => item.id === clienteId);
      if (!cliente) {
        return;
      }
      uiState.editing.clienteDomicilioId = domicilioId;
      let domicilio = cliente.domicilios?.find((item) => item.id === domicilioId) || null;
      try {
        const res = await api(`/clientes/${clienteId}/domicilios`);
        const fresh = res.items.find((item) => item.id === domicilioId);
        if (fresh) {
          domicilio = fresh;
        }
      } catch (e) {
        /* usar domicilio en memoria si el listado falla */
      }
      if (!domicilio) {
        uiState.editing.clienteDomicilioId = null;
        return;
      }
      const form = document.getElementById("cliente-domicilio-edit-form");
      const setText = (name, value) => {
        const el = form.querySelector(`[name="${name}"]`);
        if (el && "value" in el) {
          el.value = value == null ? "" : String(value);
        }
      };
      setText("id", domicilio.id);
      setText("cliente_id", cliente.id);
      setText("cliente_label", `${cliente.id} - ${cliente.razon_social}`);
      setText("tipo_domicilio", domicilio.tipo_domicilio);
      setText("nombre_sede", domicilio.nombre_sede);
      setText("direccion_completa", domicilio.direccion_completa);
      setText("municipio", domicilio.municipio);
      setText("estado", domicilio.estado);
      setText("codigo_postal", domicilio.codigo_postal);
      setText("horario_carga", domicilio.horario_carga);
      setText("horario_descarga", domicilio.horario_descarga);
      setText("instrucciones_acceso", domicilio.instrucciones_acceso);
      const activoEl = form.querySelector('[name="activo"]');
      if (activoEl) {
        activoEl.checked = Boolean(domicilio.activo);
      }
      showPanel("cliente-domicilio-edit-panel");
      clearMessage("cliente-domicilio-edit-message");
      const panel = document.getElementById("cliente-domicilio-edit-panel");
      if (panel && typeof panel.scrollIntoView === "function") {
        panel.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
    }

    function cancelClienteDomicilioEdit() {
      uiState.editing.clienteDomicilioId = null;
      document.getElementById("cliente-domicilio-edit-form").reset();
      hidePanel("cliente-domicilio-edit-panel", "cliente-domicilio-edit-message");
    }

    async function deleteClienteDomicilio(clienteId, domicilioId) {
      if (!window.confirm("¿Eliminar este domicilio del cliente?")) {
        return;
      }
      clearMessage("cliente-domicilio-message");
      try {
        await api(`/clientes/${clienteId}/domicilios/${domicilioId}`, { method: "DELETE" });
        if (uiState.editing.clienteDomicilioId === domicilioId) {
          cancelClienteDomicilioEdit();
        }
        setMessage("cliente-domicilio-message", "Domicilio eliminado.", "ok");
        await refreshData();
        document.getElementById("cliente-domicilio-cliente").value = String(clienteId);
        flushClienteDomiciliosForSelectedClient(String(clienteId));
      } catch (error) {
        setMessage("cliente-domicilio-message", error.message, "error");
      }
    }

    function renderTransportistas() {
      const items = filteredTransportistas();
      const rows = items.map((item) => `
        <tr>
          <td>${item.id}</td>
          <td>${item.nombre_razon_social || item.nombre}</td>
          <td>${item.nombre_comercial || "-"}</td>
          <td>${item.tipo_transportista || "-"}</td>
          <td>${item.rfc || "-"}</td>
          <td>${item.contactos?.length || 0}</td>
          <td>${item.documentos?.length || 0}</td>
          <td><span class="pill">${item.estatus || (item.activo ? "activo" : "inactivo")}</span></td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startTransportistaEdit(${item.id})">Editar</button>
            </div>
          </td>
        </tr>
      `).join("");

      document.getElementById("transportistas-table").innerHTML = `
        <table>
          <thead><tr><th>ID</th><th>Razon social</th><th>Nombre comercial</th><th>Tipo</th><th>RFC</th><th>Contactos</th><th>Documentos</th><th>Estatus</th><th>Acciones</th></tr></thead>
          <tbody>${rows || '<tr><td colspan="9">Sin transportistas con ese filtro.</td></tr>'}</tbody>
        </table>
      `;
    }

    function getTransportistaBySelect(selectId) {
      const value = document.getElementById(selectId)?.value || "";
      if (!value) {
        return null;
      }
      return state.transportistas.find((item) => String(item.id) === value) || null;
    }

    function renderTransportistaContactos() {
      const transportista = getTransportistaBySelect("transportista-contacto-transportista");
      if (!transportista) {
        document.getElementById("transportista-contactos-table").innerHTML = '<div class="hint">Selecciona un transportista para ver sus contactos.</div>';
        return;
      }
      const rows = (transportista.contactos || []).map((item) => `
        <tr>
          <td>${item.nombre}</td>
          <td>${item.area || "-"}</td>
          <td>${item.puesto || "-"}</td>
          <td>${item.email || "-"}</td>
          <td>${item.telefono || item.celular || "-"}</td>
          <td>${item.principal ? '<span class="pill">principal</span>' : '-'}</td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startTransportistaContactoEdit(${transportista.id}, ${item.id})">Editar</button>
              <button type="button" class="secondary-button small-button" onclick="deleteTransportistaContacto(${transportista.id}, ${item.id})">Eliminar</button>
            </div>
          </td>
        </tr>
      `).join("");
      document.getElementById("transportista-contactos-table").innerHTML = `
        <table>
          <thead><tr><th>Nombre</th><th>Area</th><th>Puesto</th><th>Email</th><th>Telefono</th><th>Principal</th><th>Acciones</th></tr></thead>
          <tbody>${rows || '<tr><td colspan="7">Sin contactos para este transportista.</td></tr>'}</tbody>
        </table>
      `;
    }

    function renderTransportistaDocumentos() {
      const transportista = getTransportistaBySelect("transportista-documento-transportista");
      if (!transportista) {
        document.getElementById("transportista-documentos-table").innerHTML = '<div class="hint">Selecciona un transportista para ver sus documentos.</div>';
        return;
      }
      const rows = (transportista.documentos || []).map((item) => `
        <tr>
          <td>${item.tipo_documento}</td>
          <td>${item.numero_documento || "-"}</td>
          <td>${item.fecha_vencimiento || "-"}</td>
          <td><span class="pill">${item.estatus}</span></td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startTransportistaDocumentoEdit(${transportista.id}, ${item.id})">Editar</button>
              <button type="button" class="secondary-button small-button" onclick="deleteTransportistaDocumento(${transportista.id}, ${item.id})">Eliminar</button>
            </div>
          </td>
        </tr>
      `).join("");
      document.getElementById("transportista-documentos-table").innerHTML = `
        <table>
          <thead><tr><th>Tipo</th><th>Numero</th><th>Vencimiento</th><th>Estatus</th><th>Acciones</th></tr></thead>
          <tbody>${rows || '<tr><td colspan="5">Sin documentos para este transportista.</td></tr>'}</tbody>
        </table>
      `;
    }

    function renderViajes() {
      const items = filteredViajes();
      const rows = items.map((item) => `
        <tr>
          <td>${item.id}</td>
          <td>${item.codigo_viaje}</td>
          <td>${item.origen} -> ${item.destino}</td>
          <td><span class="pill">${item.estado}</span></td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startViajeEdit(${item.id})">Editar</button>
            </div>
          </td>
        </tr>
      `).join("");

      document.getElementById("viajes-table").innerHTML = `
        <table>
          <thead><tr><th>ID</th><th>Codigo</th><th>Ruta</th><th>Estado</th><th>Acciones</th></tr></thead>
          <tbody>${rows || '<tr><td colspan="5">Sin viajes con ese filtro.</td></tr>'}</tbody>
        </table>
      `;
    }

    function renderFacturas() {
      const items = filteredFacturas();
      const rows = items.map((item) => `
        <tr>
          <td>${item.folio}</td>
          <td>${item.cliente?.razon_social || item.cliente_id}</td>
          <td>${item.concepto}</td>
          <td class="table-money">${fmtMoneyList(item.subtotal)}</td>
          <td class="table-money">${fmtMoneyList(item.total)}</td>
          <td class="table-money">${fmtMoneyList(item.saldo_pendiente)}</td>
          <td><span class="pill">${item.estatus}</span></td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startFacturaEdit(${item.id})">Editar</button>
            </div>
          </td>
        </tr>
      `).join("");

      const emptyMsg =
        state.facturas.length === 0
          ? "Aún no hay facturas. Use la subopción <strong>Nueva factura</strong> o el script <code>scripts/demo_flujo_factura.py</code>."
          : "Sin facturas con ese filtro. Pruebe Limpiar o ajuste búsqueda, cliente o estatus.";

      document.getElementById("facturas-table").innerHTML = `
        <table>
          <thead><tr><th>Folio</th><th>Cliente</th><th>Concepto</th><th>Subtotal</th><th>Total</th><th>Saldo</th><th>Estatus</th><th>Acciones</th></tr></thead>
          <tbody>${rows || `<tr><td colspan="8">${emptyMsg}</td></tr>`}</tbody>
        </table>
      `;
    }

    function renderFletes() {
      const items = filteredFletes();
      const rows = items.map((item) => `
        <tr>
          <td>${item.id}</td>
          <td>${item.codigo_flete}</td>
          <td>${item.tipo_operacion || "-"}</td>
          <td>${item.cliente?.razon_social || item.cliente_id}</td>
          <td>${item.transportista?.nombre || item.transportista_id}</td>
          <td class="table-money">${fmtMoneyList(item.precio_venta ?? item.monto_estimado)}</td>
          <td class="table-money">${fmtMoneyList(item.margen_estimado)}</td>
          <td class="table-money">${fmtPctList(item.margen_estimado_pct)}</td>
          <td class="table-money">${fmtMoneyList(item.costo_transporte_real)}</td>
          <td class="table-money">${fmtMoneyList(item.margen_real)}</td>
          <td><span class="pill">${item.estado}</span></td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startFleteEdit(${item.id})">Editar</button>
            </div>
          </td>
        </tr>
      `).join("");

      document.getElementById("fletes-table").innerHTML = `
        <table>
          <thead><tr><th>ID</th><th>Codigo</th><th>Tipo</th><th>Cliente</th><th>Transportista</th><th>Venta</th><th>Margen est.</th><th>Margen est. % s/ venta</th><th>Costo real</th><th>Margen real</th><th>Estado</th><th>Acciones</th></tr></thead>
          <tbody>${rows || '<tr><td colspan="12">Sin fletes con ese filtro.</td></tr>'}</tbody>
        </table>
      `;
    }

    function filteredOrdenesServicio() {
      const buscar = (uiState.ordenServicioFilters.buscar || "").trim();
      const modo = uiState.buscarModo || "contiene";
      return (state.ordenesServicio || []).filter((item) => {
        if (buscar) {
          const cotFol = item.cotizacion?.folio || "";
          const fleteCod = item.flete?.codigo_flete || "";
          const viajeCod = item.viaje?.codigo_viaje || "";
          if (
            !matchesBusqueda(
              buscar,
              [
                String(item.id ?? ""),
                item.folio || "",
                item.cliente?.razon_social || "",
                item.origen || "",
                item.destino || "",
                item.estatus || "",
                cotFol,
                fleteCod,
                viajeCod,
              ],
              modo,
            )
          ) {
            return false;
          }
        }
        if (uiState.ordenServicioFilters.cliente_id && String(item.cliente_id) !== uiState.ordenServicioFilters.cliente_id) {
          return false;
        }
        if (uiState.ordenServicioFilters.estatus && item.estatus !== uiState.ordenServicioFilters.estatus) {
          return false;
        }
        return true;
      });
    }

    function fmtIsoShort(iso) {
      if (!iso) {
        return "—";
      }
      const s = String(iso);
      if (s.length >= 16) {
        return s.slice(0, 16).replace("T", " ");
      }
      return s;
    }

    function renderOrdenServicioDetailBody(o) {
      const lines = [
        `Folio: ${o.folio}`,
        `ID: ${o.id}   Estatus: ${o.estatus}`,
        `Cliente: ${o.cliente?.razon_social || o.cliente_id}`,
        `Origen → Destino: ${o.origen} → ${o.destino}`,
        `Unidad / Carga: ${o.tipo_unidad || "—"} / ${o.tipo_carga || "—"}`,
        `Peso kg: ${o.peso_kg != null ? o.peso_kg : "—"}   Distancia km: ${o.distancia_km != null ? o.distancia_km : "—"}`,
        `Precio comprometido: ${fmtMoneyList(o.precio_comprometido)} ${o.moneda || "MXN"}`,
        `Fecha solicitud: ${fmtIsoShort(o.fecha_solicitud)}`,
        `Fecha programada: ${fmtIsoShort(o.fecha_programada)}`,
        `Cotizacion: ${o.cotizacion ? o.cotizacion.folio + " (id " + o.cotizacion.id + ")" : "—"}`,
        `Flete: ${o.flete ? o.flete.codigo_flete + " (id " + o.flete.id + ")" : "—"}`,
        `Viaje: ${o.viaje ? o.viaje.codigo_viaje + " (id " + o.viaje.id + ")" : "—"}`,
        `Despacho: ${o.despacho ? "id " + o.despacho.id_despacho + " (" + o.despacho.estatus + ")" : "—"}`,
        `Observaciones: ${o.observaciones || "—"}`,
      ];
      return lines.join(String.fromCharCode(10));
    }

    function buildOrdenServicioDesdeCotizacionPayload(form) {
      const cotizacion_id = integerOrNull(form.get("cotizacion_id"));
      if (cotizacion_id === null || cotizacion_id < 1) {
        throw new Error("Indique un ID de cotizacion valido.");
      }
      return {
        cotizacion_id,
        fecha_programada: normalizeDateTimeForApi(form.get("fecha_programada")),
        observaciones: clean(form.get("observaciones")),
      };
    }

    function buildOrdenServicioNuevaPayload(form) {
      const cliente_id = integerOrNull(form.get("cliente_id"));
      if (cliente_id === null || cliente_id < 1) {
        throw new Error("Seleccione un cliente.");
      }
      const origen = clean(form.get("origen"));
      const destino = clean(form.get("destino"));
      const tipo_unidad = clean(form.get("tipo_unidad"));
      if (!origen || !destino || !tipo_unidad) {
        throw new Error("Complete origen, destino y tipo de unidad.");
      }
      const peso_kg = numberOrNull(form.get("peso_kg"));
      if (peso_kg === null || peso_kg < 0) {
        throw new Error("Indique peso kg valido.");
      }
      const precio_comprometido = numberOrNull(form.get("precio_comprometido"));
      if (precio_comprometido === null || precio_comprometido < 0) {
        throw new Error("Indique precio comprometido valido.");
      }
      const payload = {
        cliente_id,
        moneda: (clean(form.get("moneda")) || "MXN").toUpperCase(),
        origen,
        destino,
        tipo_unidad,
        tipo_carga: clean(form.get("tipo_carga")),
        peso_kg,
        precio_comprometido,
        fecha_programada: normalizeDateTimeForApi(form.get("fecha_programada")),
        observaciones: clean(form.get("observaciones")),
      };
      const cot = integerOrNull(form.get("cotizacion_id"));
      if (cot != null) {
        payload.cotizacion_id = cot;
      }
      const flete_id = integerOrNull(form.get("flete_id"));
      if (flete_id != null) {
        payload.flete_id = flete_id;
      }
      const viaje_id = integerOrNull(form.get("viaje_id"));
      if (viaje_id != null) {
        payload.viaje_id = viaje_id;
      }
      const despacho_id = integerOrNull(form.get("despacho_id"));
      if (despacho_id != null) {
        payload.despacho_id = despacho_id;
      }
      const distancia_km = numberOrNull(form.get("distancia_km"));
      if (distancia_km != null) {
        payload.distancia_km = distancia_km;
      }
      return payload;
    }

    function buildOrdenServicioDatosPayload(form) {
      const origen = clean(form.get("origen"));
      const destino = clean(form.get("destino"));
      const tipo_unidad = clean(form.get("tipo_unidad"));
      if (!origen || !destino || !tipo_unidad) {
        throw new Error("Complete origen, destino y tipo de unidad.");
      }
      const peso_kg = numberOrNull(form.get("peso_kg"));
      if (peso_kg === null || peso_kg < 0) {
        throw new Error("Indique peso kg valido.");
      }
      const precio_comprometido = numberOrNull(form.get("precio_comprometido"));
      if (precio_comprometido === null || precio_comprometido < 0) {
        throw new Error("Indique precio comprometido valido.");
      }
      return {
        origen,
        destino,
        tipo_unidad,
        tipo_carga: clean(form.get("tipo_carga")),
        peso_kg,
        distancia_km: numberOrNull(form.get("distancia_km")),
        precio_comprometido,
        moneda: (clean(form.get("moneda")) || "MXN").toUpperCase(),
        fecha_programada: normalizeDateTimeForApi(form.get("fecha_programada")),
        observaciones: clean(form.get("observaciones")),
      };
    }

    function applyOrdenServicioDetailToPanel(o) {
      if (!o) {
        return;
      }
      const hid = document.getElementById("orden-servicio-detail-id");
      if (hid) {
        hid.value = String(o.id);
      }
      const body = document.getElementById("orden-servicio-detail-body");
      if (body) {
        body.textContent = renderOrdenServicioDetailBody(o);
      }
      const estSel = document.getElementById("orden-servicio-estatus-select");
      if (estSel) {
        estSel.value = o.estatus || "borrador";
      }
      const setSelectIfOption = (selectId, rawId) => {
        const sel = document.getElementById(selectId);
        if (!sel) {
          return;
        }
        const v = rawId != null && rawId !== "" ? String(rawId) : "";
        if (v && [...sel.options].some((opt) => opt.value === v)) {
          sel.value = v;
        } else {
          sel.value = "";
        }
      };
      setSelectIfOption("orden-servicio-edit-flete", o.flete_id);
      setSelectIfOption("orden-servicio-edit-viaje", o.viaje_id);
      setSelectIfOption("orden-servicio-edit-despacho", o.despacho_id);
      const datosForm = document.getElementById("orden-servicio-datos-form");
      if (datosForm) {
        const origenEl = datosForm.querySelector('[name="origen"]');
        const destinoEl = datosForm.querySelector('[name="destino"]');
        const tipoUnidadEl = datosForm.querySelector('[name="tipo_unidad"]');
        const tipoCargaEl = datosForm.querySelector('[name="tipo_carga"]');
        const pesoEl = datosForm.querySelector('[name="peso_kg"]');
        const distEl = datosForm.querySelector('[name="distancia_km"]');
        const precioEl = datosForm.querySelector('[name="precio_comprometido"]');
        const monedaEl = datosForm.querySelector('[name="moneda"]');
        const fechaEl = datosForm.querySelector('[name="fecha_programada"]');
        const obsEl = datosForm.querySelector('[name="observaciones"]');
        if (origenEl) {
          origenEl.value = o.origen != null ? String(o.origen) : "";
        }
        if (destinoEl) {
          destinoEl.value = o.destino != null ? String(o.destino) : "";
        }
        if (tipoUnidadEl) {
          tipoUnidadEl.value = o.tipo_unidad != null ? String(o.tipo_unidad) : "";
        }
        if (tipoCargaEl) {
          tipoCargaEl.value = o.tipo_carga != null ? String(o.tipo_carga) : "";
        }
        if (pesoEl) {
          pesoEl.value = htmlNumberInputValue(o.peso_kg);
        }
        if (distEl) {
          distEl.value = htmlNumberInputValue(o.distancia_km);
        }
        if (precioEl) {
          precioEl.value = htmlNumberInputValue(o.precio_comprometido);
        }
        if (monedaEl) {
          monedaEl.value = o.moneda != null ? String(o.moneda) : "MXN";
        }
        if (fechaEl) {
          fechaEl.value = toDateTimeLocal(o.fecha_programada);
        }
        if (obsEl) {
          obsEl.value = o.observaciones != null ? String(o.observaciones) : "";
        }
      }
      clearMessage("orden-servicio-estatus-msg");
      clearMessage("orden-servicio-datos-msg");
      clearMessage("orden-servicio-vinculos-msg");
      clearMessage("orden-servicio-delete-msg");
    }

    async function showOrdenServicioDetail(ordenId, opts) {
      const skipFetch = opts && opts.skipFetch === true;
      const id = Number(ordenId);
      if (!Number.isFinite(id) || id < 1) {
        return;
      }
      const body = document.getElementById("orden-servicio-detail-body");
      const panel = document.getElementById("orden-servicio-detail-panel");
      let o = state.ordenesServicio.find((row) => Number(row.id) === id);
      if (!skipFetch) {
        if (body) {
          body.textContent = "Cargando detalle…";
        }
        if (panel) {
          panel.classList.remove("hidden");
          panel.setAttribute("aria-hidden", "false");
        }
        try {
          const fresh = await api(`/ordenes-servicio/${id}`);
          const idx = state.ordenesServicio.findIndex((row) => Number(row.id) === id);
          if (idx >= 0) {
            state.ordenesServicio[idx] = fresh;
          } else {
            state.ordenesServicio.push(fresh);
          }
          o = fresh;
          renderOrdenesServicio();
        } catch (err) {
          if (!o) {
            if (body) {
              body.textContent = err && err.message ? err.message : "No se pudo cargar la orden.";
            }
            if (panel) {
              panel.classList.remove("hidden");
              panel.setAttribute("aria-hidden", "false");
            }
            return;
          }
        }
      } else if (!o) {
        o = state.ordenesServicio.find((row) => Number(row.id) === id);
      }
      if (!o) {
        if (body) {
          body.textContent = "Orden no encontrada.";
        }
        return;
      }
      applyOrdenServicioDetailToPanel(o);
      if (panel) {
        panel.classList.remove("hidden");
        panel.setAttribute("aria-hidden", "false");
        if (!skipFetch) {
          panel.scrollIntoView({ behavior: "smooth", block: "nearest" });
        }
      }
    }

    function hideOrdenServicioDetail() {
      hidePanel("orden-servicio-detail-panel", null);
    }

    async function deleteOrdenServicioSeleccionada() {
      clearMessage("orden-servicio-delete-msg");
      const hid = document.getElementById("orden-servicio-detail-id");
      const id = hid && hid.value ? integerOrNull(hid.value) : null;
      if (id === null || id < 1) {
        return;
      }
      const o = state.ordenesServicio.find((row) => Number(row.id) === id);
      const folio = o && o.folio ? String(o.folio) : String(id);
      if (
        !window.confirm(
          `¿Eliminar la orden de servicio ${folio} (ID ${id})? Esta accion no se puede deshacer. Si hay registros que dependan de ella, el servidor rechazara el borrado.`,
        )
      ) {
        return;
      }
      try {
        await api(`/ordenes-servicio/${id}`, { method: "DELETE" });
        hideOrdenServicioDetail();
        await refreshData();
      } catch (err) {
        setMessage("orden-servicio-delete-msg", err.message, "error");
      }
    }

    /** Tras refreshData: actualiza texto y selects del detalle solo si el usuario sigue viendo esa orden. */
    function refreshOrdenServicioDetailIfOpen(ordenId) {
      const panel = document.getElementById("orden-servicio-detail-panel");
      const hid = document.getElementById("orden-servicio-detail-id");
      if (!panel || panel.classList.contains("hidden")) {
        return;
      }
      if (!hid || String(hid.value) !== String(ordenId)) {
        return;
      }
      void showOrdenServicioDetail(ordenId, { skipFetch: true });
    }

    function renderOrdenesServicio() {
      const hasJwt = !!sessionStorage.getItem("sife_access_token");
      const role = (window.__SIFE_ROLE_NAME__ || "").trim().toLowerCase();
      const canManageOrdenServicio = !(hasJwt && role === "consulta");
      const detailButtonLabel = canManageOrdenServicio ? "Gestionar" : "Ver detalle";
      const items = filteredOrdenesServicio();
      const rows = items
        .map(
          (item) => `
        <tr>
          <td>${item.id}</td>
          <td>${item.folio}</td>
          <td>${item.cliente?.razon_social || item.cliente_id}</td>
          <td><span class="pill">${item.estatus}</span></td>
          <td>${item.cotizacion?.folio || "—"}</td>
          <td>${item.flete?.codigo_flete || "—"}</td>
          <td>${fmtIsoShort(item.fecha_programada)}</td>
          <td class="table-money">${fmtMoneyList(item.precio_comprometido)}</td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="showOrdenServicioDetail(${item.id})">${detailButtonLabel}</button>
            </div>
          </td>
        </tr>
      `,
        )
        .join("");
      const emptyMsg =
        (state.ordenesServicio || []).length === 0
          ? "No hay ordenes de servicio. Cree una con las tarjetas superiores (desde cotizacion o manual), por API en /docs (tag ordenes-servicio) o con el script de demo."
          : "Sin ordenes con ese filtro. Pruebe Limpiar o ajuste criterios.";
      const tableEl = document.getElementById("ordenes-servicio-table");
      if (!tableEl) {
        return;
      }
      tableEl.innerHTML = `
        <table>
          <thead><tr><th>ID</th><th>Folio</th><th>Cliente</th><th>Estatus</th><th>Cotizacion</th><th>Flete</th><th>Fecha prog.</th><th>Precio comp.</th><th>Acciones</th></tr></thead>
          <tbody>${rows || `<tr><td colspan="9">${emptyMsg}</td></tr>`}</tbody>
        </table>
      `;
    }

    function aplicarFolioOrdenServicioAFactura(messageId, folioInputId, ordenIdInputId) {
      clearMessage(messageId);
      const folioEl = document.getElementById(folioInputId);
      const idEl = document.getElementById(ordenIdInputId);
      const raw = folioEl && folioEl.value ? folioEl.value.trim() : "";
      if (!idEl) {
        return;
      }
      if (!raw) {
        setMessage(messageId, "Escriba un folio de orden de servicio.", "error");
        return;
      }
      const list = state.ordenesServicio || [];
      const low = raw.toLowerCase();
      const exact = list.find((o) => String(o.folio).toLowerCase() === low);
      const loose = exact || list.find((o) => String(o.folio).toLowerCase().includes(low));
      if (!loose) {
        setMessage(
          messageId,
          "No se encontro orden con ese folio. Actualice la pagina (F5) o verifique en Fletes > Ordenes de servicio.",
          "error",
        );
        return;
      }
      idEl.value = String(loose.id);
      setMessage(messageId, `Orden ${loose.folio} (ID ${loose.id}) aplicada.`, "ok");
    }

    function renderGastos() {
      const items = filteredGastos();
      const rows = items.map((item) => `
        <tr>
          <td>${item.id}</td>
          <td>${item.flete_id}</td>
          <td title="${item.tipo_gasto}">${labelGastoCategoria(item.tipo_gasto)}</td>
          <td class="table-money">${fmtMoneyList(item.monto)}</td>
          <td>${item.fecha_gasto}</td>
          <td>${item.referencia || "-"}</td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startGastoEdit(${item.id})">Editar</button>
              <button type="button" class="secondary-button small-button" onclick="deleteGasto(${item.id})">Eliminar</button>
            </div>
          </td>
        </tr>
      `).join("");

      document.getElementById("gastos-table").innerHTML = `
        <table>
          <thead><tr><th>ID</th><th>Flete</th><th>Categoría</th><th>Monto</th><th>Fecha</th><th>Referencia</th><th>Acciones</th></tr></thead>
          <tbody>${rows || '<tr><td colspan="7">Sin gastos con ese filtro.</td></tr>'}</tbody>
        </table>
      `;
    }

    function renderTarifas() {
      const items = filteredTarifasVenta();
      const rows = items.map((item) => `
        <tr>
          <td>${item.id}</td>
          <td>${item.nombre_tarifa}</td>
          <td>${item.tipo_operacion || "subcontratado"}</td>
          <td>${item.ambito || "—"}</td>
          <td>${item.modalidad_cobro || "—"}</td>
          <td>${item.origen} -> ${item.destino}</td>
          <td>${item.tipo_unidad}</td>
          <td class="table-money">${fmtMoneyList(item.tarifa_base)}</td>
          <td class="table-money">${fmtTarifaList(item.tarifa_km, 4)}</td>
          <td><span class="pill">${item.activo ? "activa" : "inactiva"}</span></td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startTarifaFleteEdit(${item.id})">Editar</button>
            </div>
          </td>
        </tr>
      `).join("");

      document.getElementById("tarifas-table").innerHTML = `
        <table>
          <thead><tr><th>ID</th><th>Nombre</th><th>Tipo op.</th><th>Ambito</th><th>Modalidad</th><th>Ruta</th><th>Unidad</th><th>Base</th><th>Km</th><th>Estatus</th><th>Acciones</th></tr></thead>
          <tbody>${rows || '<tr><td colspan="11">Sin tarifas con ese filtro.</td></tr>'}</tbody>
        </table>
      `;
    }

    function renderTarifasCompra() {
      const items = filteredTarifasCompra();
      const rows = items.map((item) => `
        <tr>
          <td>${item.id}</td>
          <td>${state.transportistas.find((t) => t.id === item.transportista_id)?.nombre || item.transportista_id}</td>
          <td>${item.tipo_transportista || "subcontratado"}</td>
          <td>${item.nombre_tarifa}</td>
          <td>${item.origen} -> ${item.destino}</td>
          <td>${item.tipo_unidad}</td>
          <td class="table-money">${fmtMoneyList(item.tarifa_base)}</td>
          <td>${item.dias_credito ?? 0}</td>
          <td><span class="pill">${item.activo ? "activa" : "inactiva"}</span></td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startTarifaCompraEdit(${item.id})">Editar</button>
              <button type="button" class="secondary-button small-button" onclick="deleteTarifaCompra(${item.id})">Eliminar</button>
            </div>
          </td>
        </tr>
      `).join("");

      document.getElementById("tarifas-compra-table").innerHTML = `
        <table>
          <thead><tr><th>ID</th><th>Transportista</th><th>Tipo</th><th>Nombre</th><th>Ruta</th><th>Unidad</th><th>Base</th><th>Credito</th><th>Estatus</th><th>Acciones</th></tr></thead>
          <tbody>${rows || '<tr><td colspan="10">Sin tarifas de compra con ese filtro.</td></tr>'}</tbody>
        </table>
      `;
    }

    function escapeHtml(text) {
      return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
    }

    function fmtUnidadDateCell(value) {
      if (value == null || value === "") {
        return "—";
      }
      const s = typeof value === "string" ? value.slice(0, 10) : String(value);
      return s || "—";
    }

    function unidadDescripcionCorta(text) {
      const raw = (text || "").trim();
      if (!raw) {
        return "—";
      }
      const shown = raw.length > 64 ? `${raw.slice(0, 61)}…` : raw;
      return escapeHtml(shown);
    }

    function operadorCertificacionesCorta(text) {
      const s = (text || "").trim();
      if (!s) {
        return "—";
      }
      const raw = s.length > 56 ? `${s.slice(0, 53)}…` : s;
      return escapeHtml(raw);
    }

    function renderOperadores() {
      const items = filteredOperadores();
      const rows = items.map((item) => {
        const cert = (item.certificaciones || "").trim();
        const titleAttr = cert ? ` title="${escapeHtml(cert)}"` : "";
        return `
        <tr>
          <td>${item.id_operador}</td>
          <td>${item.nombre} ${item.apellido_paterno}</td>
          <td>${state.transportistas.find((t) => t.id === item.transportista_id)?.nombre || item.transportista_id || "-"}</td>
          <td>${item.curp}</td>
          <td>${item.telefono_principal || "-"}</td>
          <td${titleAttr}>${operadorCertificacionesCorta(item.certificaciones)}</td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startOperadorEdit(${item.id_operador})">Editar</button>
            </div>
          </td>
        </tr>
      `;
      }).join("");

      document.getElementById("operadores-table").innerHTML = `
        <table>
          <thead><tr><th>ID</th><th>Nombre</th><th>Transportista</th><th>CURP</th><th>Telefono</th><th>Certificaciones</th><th>Acciones</th></tr></thead>
          <tbody>${rows || '<tr><td colspan="7">Sin operadores con ese filtro.</td></tr>'}</tbody>
        </table>
      `;
    }

    function renderUnidades() {
      const totalUnidades = state.unidades.length;
      const items = filteredUnidades();
      const rows = items
        .map((item) => {
          const transp =
            state.transportistas.find((t) => String(t.id) === String(item.transportista_id))?.nombre ||
            item.transportista_id ||
            "—";
          const tipoP = (item.tipo_propiedad || "").trim() || "—";
          const estDoc = (item.estatus_documental || "").trim() || "—";
          return `
        <tr>
          <td>${item.id_unidad}</td>
          <td>${escapeHtml(item.economico || "")}</td>
          <td>${escapeHtml(String(transp))}</td>
          <td>${escapeHtml(item.placas || "—")}</td>
          <td>${escapeHtml(tipoP)}</td>
          <td>${escapeHtml(estDoc)}</td>
          <td>${unidadDescripcionCorta(item.descripcion)}</td>
          <td><span class="pill">${item.activo ? "activa" : "inactiva"}</span></td>
          <td>${fmtUnidadDateCell(item.vigencia_permiso_sct)}</td>
          <td>${fmtUnidadDateCell(item.vigencia_seguro)}</td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startUnidadEdit(${item.id_unidad})">Editar</button>
              <button type="button" class="secondary-button small-button" onclick="deleteUnidad(${item.id_unidad})">Eliminar</button>
            </div>
          </td>
        </tr>
      `;
        })
        .join("");

      let emptyHint = "";
      if (!rows) {
        if (!state.catalogLoaded) {
          emptyHint =
            '<tr><td colspan="11">Cargando catalogo… Si no aparece nada en unos segundos, actualice la pagina (F5) o revise el mensaje de error en la parte superior.</td></tr>';
        } else if (unidadesEndpointFailed()) {
          emptyHint =
            '<tr><td colspan="11"><strong>No se pudo cargar el listado de unidades</strong> (fallo de red, API o servidor). Esto <strong>no</strong> significa necesariamente que no haya datos en MySQL. Revise el aviso amarillo arriba, la API key en <code>.env</code>, que MySQL este en marcha y pulse <strong>Recargar catalogo</strong>. Pruebe tambien <a href="/docs">/docs</a> → <code>GET /api/v1/unidades</code>.</td></tr>';
        } else if (totalUnidades === 0) {
          emptyHint =
            '<tr><td colspan="11"><strong>Situacion normal si aun no dio de alta vehiculos:</strong> en la base configurada (<code>MYSQL_DB</code> en <code>.env</code>, suele ser <code>sife_mxn</code>) la tabla <code>unidades</code> tiene 0 filas. Use <strong>Nueva unidad</strong> (economico obligatorio) o ejecute <code>python scripts/seed_unidad_ejemplo.py</code> si ya tiene transportista. Si <em>creyó</em> tener datos, confirme que el servidor usa el mismo <code>.env</code> que la base de datos que inspecciona en MySQL.</td></tr>';
        } else {
          emptyHint =
            '<tr><td colspan="11">Ninguna fila coincide con el filtro actual. Vacie el buscador, deje <strong>Todos</strong> en los tres listados y pulse <strong>Limpiar filtros</strong> (restablece el modo de busqueda a <strong>Contiene</strong>). Si aun asi no aparece, use <strong>Recargar catalogo</strong>.</td></tr>';
        }
      }

      document.getElementById("unidades-table").innerHTML = `
        <table>
          <thead><tr><th>ID</th><th>Economico</th><th>Transportista</th><th>Placas</th><th>Tipo prop.</th><th>Estatus doc.</th><th>Descripcion</th><th>Activo</th><th>Vig. SCT</th><th>Vig. seguro</th><th>Acciones</th></tr></thead>
          <tbody>${rows || emptyHint}</tbody>
        </table>
      `;
    }

    function renderAsignaciones() {
      const items = filteredAsignaciones();
      const rows = items.map((item) => `
        <tr>
          <td>${item.id_asignacion}</td>
          <td>${item.operador?.nombre || ""} ${item.operador?.apellido_paterno || ""}</td>
          <td>${item.unidad?.economico || item.id_unidad}</td>
          <td>${item.viaje?.codigo_viaje || item.id_viaje}</td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startAsignacionEdit(${item.id_asignacion})">Editar</button>
            </div>
          </td>
        </tr>
      `).join("");

      document.getElementById("asignaciones-table").innerHTML = `
        <table>
          <thead><tr><th>ID</th><th>Operador</th><th>Unidad</th><th>Viaje</th><th>Acciones</th></tr></thead>
          <tbody>${rows || '<tr><td colspan="5">Sin asignaciones con ese filtro.</td></tr>'}</tbody>
        </table>
      `;
    }

    function renderDespachos() {
      const items = filteredDespachos();
      const rows = items.map((item) => `
        <tr>
          <td>${item.id_despacho}</td>
          <td>${item.asignacion?.viaje?.codigo_viaje || item.id_asignacion}</td>
          <td>${item.flete?.codigo_flete || "-"}</td>
          <td><span class="pill">${item.estatus}</span></td>
          <td>${item.eventos?.length || 0}</td>
          <td>
            <div class="row-actions">
              <button type="button" class="secondary-button small-button" onclick="startDespachoEdit(${item.id_despacho})">Editar</button>
            </div>
          </td>
        </tr>
      `).join("");

      document.getElementById("despachos-table").innerHTML = `
        <table>
          <thead><tr><th>ID</th><th>Viaje</th><th>Flete</th><th>Estatus</th><th>Eventos</th><th>Acciones</th></tr></thead>
          <tbody>${rows || '<tr><td colspan="6">Sin despachos con ese filtro.</td></tr>'}</tbody>
        </table>
      `;
    }

    function hidePanel(panelId, messageId) {
      const el = document.getElementById(panelId);
      if (el) {
        el.classList.add("hidden");
        el.setAttribute("aria-hidden", "true");
      }
      if (messageId) {
        clearMessage(messageId);
      }
    }

    function showPanel(panelId) {
      const el = document.getElementById(panelId);
      if (el) {
        el.classList.remove("hidden");
        el.setAttribute("aria-hidden", "false");
      }
    }

    function getPrimarySaveButton(formElement) {
      const fid = formElement.getAttribute("id");
      if (fid === "cliente-contacto-form") {
        return document.getElementById("cliente-contacto-guardar");
      }
      if (fid === "cliente-contacto-edit-form") {
        return document.getElementById("cliente-contacto-edit-guardar");
      }
      if (fid) {
        const linked = document.querySelector(`button[form="${fid}"][data-primary-action='save']`);
        if (linked) {
          return linked;
        }
      }
      return (
        formElement.querySelector('button[type="submit"]') ||
        formElement.querySelector("button[data-primary-action='save']") ||
        null
      );
    }

    function getSequentialFields(formElement) {
      return [...formElement.querySelectorAll("input, select, textarea, button")]
        .filter((field) => {
          if (field.disabled) {
            return false;
          }
          if (field.type === "hidden") {
            return false;
          }
          if (field.tagName === "BUTTON" && field.type === "button") {
            return false;
          }
          return true;
        });
    }

    function focusNextSequentialField(formElement, fromField) {
      if (!formElement || !fromField) {
        return;
      }
      const fields = getSequentialFields(formElement);
      const index = fields.indexOf(fromField);
      if (index === -1) {
        return;
      }
      const nextField = fields[index + 1];
      if (nextField && typeof nextField.focus === "function") {
        nextField.focus();
        if (nextField.select && nextField.tagName === "INPUT") {
          const t = (nextField.type || "").toLowerCase();
          if (t !== "checkbox" && t !== "radio" && t !== "file") {
            nextField.select();
          }
        }
        return;
      }
      // Evita que Enter en el ultimo campo enfoque/active "Guardar",
      // porque puede disparar submits no intencionales y dar sensacion de congelamiento.
    }

    function wireImplicitSubmitGuard(formId) {
      const form = document.getElementById(formId);
      if (!form || form.dataset.implicitSubmitGuard === "true") {
        return;
      }
      form.dataset.implicitSubmitGuard = "true";
      form.addEventListener(
        "submit",
        (event) => {
          const saveBtn = getPrimarySaveButton(form);
          if (!saveBtn) {
            return;
          }
          if (event.submitter === saveBtn) {
            return;
          }
          event.preventDefault();
          event.stopImmediatePropagation();
          const active = document.activeElement;
          if (form.contains(active) && active !== saveBtn) {
            focusNextSequentialField(form, active);
          }
        },
        true
      );
    }

    function enableEnterToNextField(formId) {
      const formElement = document.getElementById(formId);
      if (!formElement || formElement.dataset.enterNavInstalled === "true") {
        return;
      }
      formElement.dataset.enterNavInstalled = "true";
      const onEnterNavKeydown = (event) => {
        if (event.defaultPrevented || event.isComposing || event.repeat) {
          return;
        }
        const isEnter =
          event.key === "Enter" ||
          event.code === "Enter" ||
          event.code === "NumpadEnter" ||
          event.keyCode === 13;
        if (!isEnter) {
          return;
        }
        const target = event.target;
        if (!(target instanceof HTMLElement)) {
          return;
        }
        const tagName = target.tagName;
        if (!["INPUT", "SELECT", "TEXTAREA"].includes(tagName)) {
          return;
        }
        if (tagName === "INPUT") {
          const inputType = (target.type || "").toLowerCase();
          if (inputType === "submit" || inputType === "button" || inputType === "file" || inputType === "hidden") {
            return;
          }
        }
        if (tagName === "TEXTAREA") {
          return;
        }
        if (!formElement.contains(target)) {
          return;
        }
        event.preventDefault();
        event.stopPropagation();
        focusNextSequentialField(formElement, target);
      };
      formElement.addEventListener("keydown", onEnterNavKeydown, true);
    }

    const CLIENTE_CONTACTO_ENTER_ORDER = [
      "cliente-contacto-cliente",
      "cliente-contacto-nombre",
      "cliente-contacto-area",
      "cliente-contacto-puesto",
      "cliente-contacto-email",
      "cliente-contacto-telefono",
      "cliente-contacto-extension",
      "cliente-contacto-celular",
      "cliente-contacto-principal",
      "cliente-contacto-activo",
    ];

    function wireClienteContactoEnterNavigation() {
      const form = document.getElementById("cliente-contacto-form");
      if (!form || window.__sifeClienteContactoEnterNav) {
        return;
      }
      window.__sifeClienteContactoEnterNav = true;
      const saveId = "cliente-contacto-guardar";
      const onEnter = (event) => {
        if (event.defaultPrevented || event.isComposing || event.repeat) {
          return;
        }
        const isEnter =
          event.key === "Enter" ||
          event.code === "Enter" ||
          event.code === "NumpadEnter" ||
          event.keyCode === 13;
        if (!isEnter) {
          return;
        }
        const rawTarget = event.target;
        if (!(rawTarget instanceof HTMLElement)) {
          return;
        }
        if (!form || !form.contains(rawTarget)) {
          return;
        }
        const target = rawTarget.tagName === "INPUT" || rawTarget.tagName === "SELECT" || rawTarget.tagName === "TEXTAREA"
          ? rawTarget
          : null;
        if (!target) {
          return;
        }
        if (target.tagName === "INPUT") {
          const ty = (target.type || "").toLowerCase();
          if (ty === "submit" || ty === "button" || ty === "file" || ty === "hidden") {
            return;
          }
        }
        if (target.tagName === "TEXTAREA") {
          return;
        }
        if (target.id === saveId) {
          return;
        }
        if (!CLIENTE_CONTACTO_ENTER_ORDER.includes(target.id)) {
          return;
        }
        event.preventDefault();
        event.stopPropagation();
        event.stopImmediatePropagation();
        const idx = CLIENTE_CONTACTO_ENTER_ORDER.indexOf(target.id);
        for (let step = idx + 1; step < CLIENTE_CONTACTO_ENTER_ORDER.length; step += 1) {
          const next = document.getElementById(CLIENTE_CONTACTO_ENTER_ORDER[step]);
          if (next && !next.disabled) {
            next.focus();
            if (next.select && next.tagName === "INPUT") {
              const t = (next.type || "").toLowerCase();
              if (!["checkbox", "radio", "file"].includes(t)) {
                next.select();
              }
            }
            return;
          }
        }
        const saveBtn = document.getElementById(saveId);
        if (saveBtn && typeof saveBtn.focus === "function") {
          saveBtn.focus();
        }
      };
      // Limita la captura de Enter al formulario de contactos del cliente.
      // Evita interferencia global con otros formularios/paneles al navegar con teclado.
      form.addEventListener("keydown", onEnter, true);
      form.addEventListener("keypress", (event) => {
        const isEnter = event.key === "Enter" || event.keyCode === 13;
        if (!isEnter) {
          return;
        }
        const t = event.target;
        if (!(t instanceof HTMLElement) || !form || !form.contains(t)) {
          return;
        }
        if (t.id === saveId) {
          return;
        }
        if (t.tagName === "INPUT" || t.tagName === "SELECT") {
          const ty = t.tagName === "INPUT" ? (t.type || "").toLowerCase() : "";
          if (ty === "submit" || ty === "button" || ty === "hidden" || ty === "file") {
            return;
          }
          if (CLIENTE_CONTACTO_ENTER_ORDER.includes(t.id)) {
            event.preventDefault();
            event.stopImmediatePropagation();
          }
        }
      }, true);
    }

    function openSingleClienteFromFilter() {
      const items = filteredClientes();
      if (items.length !== 1) {
        return false;
      }
      startClienteEdit(items[0].id);
      return true;
    }

    function openSingleTransportistaFromFilter() {
      const items = filteredTransportistas();
      if (items.length !== 1) {
        return false;
      }
      startTransportistaEdit(items[0].id);
      return true;
    }

    function setClienteSubpage(tab) {
      const target = tab || "alta";
      uiState.clienteSubpage = target;
      if (target !== "contactos") {
        cancelClienteContactoEdit();
      }
      for (const button of document.querySelectorAll("[data-cliente-tab]")) {
        button.classList.toggle("active", button.dataset.clienteTab === target);
      }
      for (const panel of document.querySelectorAll("[data-cliente-tab-panel]")) {
        panel.classList.toggle("hidden", panel.dataset.clienteTabPanel !== target);
      }
      if (target === "manual") {
        const manualScroll = document.querySelector("[data-manual-scroll='clientes']");
        if (manualScroll) {
          manualScroll.scrollTop = 0;
        }
      }
    }

    function setTransportistaSubpage(tab) {
      const target = tab || "consulta";
      uiState.transportistaSubpage = target;
      if (target !== "contactos") {
        cancelTransportistaContactoEdit();
      }
      for (const button of document.querySelectorAll("[data-transportista-tab]")) {
        button.classList.toggle("active", button.dataset.transportistaTab === target);
      }
      for (const panel of document.querySelectorAll("[data-transportista-tab-panel]")) {
        panel.classList.toggle("hidden", panel.dataset.transportistaTabPanel !== target);
      }
      if (target === "manual") {
        const manualScroll = document.querySelector("[data-manual-scroll='transportistas']");
        if (manualScroll) {
          manualScroll.scrollTop = 0;
        }
      }
    }

    function setGenericSubpage(prefix, stateKey, defaultTab, tab) {
      const target = tab || defaultTab;
      uiState[stateKey] = target;
      for (const button of document.querySelectorAll(`[data-${prefix}-tab]`)) {
        const btnTab = button.getAttribute(`data-${prefix}-tab`);
        button.classList.toggle("active", btnTab === target);
      }
      for (const panel of document.querySelectorAll(`[data-${prefix}-tab-panel]`)) {
        const panelTab = panel.getAttribute(`data-${prefix}-tab-panel`);
        panel.classList.toggle("hidden", panelTab !== target);
      }
      if (target === "manual") {
        const manualScroll = document.querySelector(`[data-manual-scroll="${prefix}"]`);
        if (manualScroll) {
          manualScroll.scrollTop = 0;
        }
      }
      if (prefix === "flete" && target === "alta" && typeof populateSelects === "function") {
        populateSelects();
      }
      if (prefix === "tarifa" && target === "alta") {
        const tfa = document.getElementById("tarifa-form");
        if (tfa && typeof applyMoneyFormatToForm === "function") {
          applyMoneyFormatToForm(tfa);
        }
      }
      if (prefix === "tarifa-compra" && target === "alta") {
        const tcf = document.getElementById("tarifa-compra-form");
        if (tcf && typeof applyMoneyFormatToForm === "function") {
          applyMoneyFormatToForm(tcf);
        }
      }
      if (prefix === "flete" && target === "ordenes-servicio" && typeof renderOrdenesServicio === "function") {
        renderOrdenesServicio();
      }
      if (prefix === "operador" && target !== "consulta") {
        cancelOperadorEdit();
      }
      if (prefix === "unidad" && target !== "consulta") {
        cancelUnidadEdit();
      }
      if (prefix === "despacho" && target !== "consulta") {
        cancelDespachoEdit();
      }
    }

    function initCrudSubpageModules() {
      const modules = [
        { prefix: "viaje", stateKey: "viajeSubpage", defaultTab: "consulta" },
        { prefix: "flete", stateKey: "fleteSubpage", defaultTab: "consulta" },
        { prefix: "factura", stateKey: "facturaSubpage", defaultTab: "consulta" },
        { prefix: "tarifa", stateKey: "tarifaSubpage", defaultTab: "consulta" },
        { prefix: "tarifa-compra", stateKey: "tarifaCompraSubpage", defaultTab: "consulta" },
        { prefix: "operador", stateKey: "operadorSubpage", defaultTab: "consulta" },
        { prefix: "unidad", stateKey: "unidadSubpage", defaultTab: "consulta" },
        { prefix: "gasto", stateKey: "gastoSubpage", defaultTab: "consulta" },
        { prefix: "asignacion", stateKey: "asignacionSubpage", defaultTab: "consulta" },
        { prefix: "despacho", stateKey: "despachoSubpage", defaultTab: "consulta" },
        { prefix: "seguimiento", stateKey: "seguimientoSubpage", defaultTab: "salida" },
      ];
      for (const { prefix, stateKey, defaultTab } of modules) {
        for (const button of document.querySelectorAll(`[data-${prefix}-tab]`)) {
          button.addEventListener("click", () => {
            const tab = button.getAttribute(`data-${prefix}-tab`);
            setGenericSubpage(prefix, stateKey, defaultTab, tab);
          });
        }
        const manualToc = document.getElementById(`manual-${prefix}-toc`);
        if (manualToc) {
          manualToc.addEventListener("click", (event) => {
            const link = event.target.closest(`a[href^='#manual-${prefix}-']`);
            if (!link) {
              return;
            }
            event.preventDefault();
            const id = link.getAttribute("href").slice(1);
            const targetEl = document.getElementById(id);
            if (targetEl) {
              targetEl.scrollIntoView({ behavior: "smooth", block: "start" });
            }
          });
        }
        const openManualBtn = document.getElementById(`${prefix}-open-manual-btn`);
        if (openManualBtn) {
          openManualBtn.addEventListener("click", () => {
            setGenericSubpage(prefix, stateKey, defaultTab, "manual");
          });
        }
        setGenericSubpage(prefix, stateKey, defaultTab, uiState[stateKey]);
      }
    }

    function startClienteEdit(clienteId) {
      const item = state.clientes.find((row) => row.id === clienteId);
      if (!item) {
        return;
      }
      uiState.editing.clienteId = clienteId;
      const form = document.getElementById("cliente-edit-form");
      form.elements.id.value = item.id;
      form.elements.razon_social.value = item.razon_social || "";
      form.elements.nombre_comercial.value = item.nombre_comercial || "";
      form.elements.tipo_cliente.value = item.tipo_cliente || "mixto";
      form.elements.rfc.value = item.rfc || "";
      form.elements.sector.value = item.sector || "";
      form.elements.origen_prospecto.value = item.origen_prospecto || "";
      form.elements.email.value = item.email || "";
      form.elements.telefono.value = item.telefono || "";
      form.elements.direccion.value = item.domicilio_fiscal || item.direccion || "";
      form.elements.sitio_web.value = item.sitio_web || "";
      form.elements.notas_operativas.value = item.notas_operativas || "";
      form.elements.notas_comerciales.value = item.notas_comerciales || "";
      form.elements.activo.checked = Boolean(item.activo);
      setClienteSubpage("consulta");
      showPanel("cliente-edit-panel");
      clearMessage("cliente-edit-message");
      document.getElementById("cliente-edit-panel").scrollIntoView({ behavior: "smooth", block: "start" });
    }

    function cancelClienteEdit() {
      uiState.editing.clienteId = null;
      document.getElementById("cliente-edit-form").reset();
      hidePanel("cliente-edit-panel", "cliente-edit-message");
    }

    function startTransportistaEdit(transportistaId) {
      const item = state.transportistas.find((row) => row.id === transportistaId);
      if (!item) {
        return;
      }
      uiState.editing.transportistaId = transportistaId;
      const form = document.getElementById("transportista-edit-form");
      form.elements.id.value = item.id;
      form.elements.nombre.value = item.nombre || "";
      form.elements.nombre_comercial.value = item.nombre_comercial || "";
      form.elements.tipo_transportista.value = item.tipo_transportista || "subcontratado";
      form.elements.tipo_persona.value = item.tipo_persona || "moral";
      form.elements.estatus.value = item.estatus || "activo";
      form.elements.rfc.value = item.rfc || "";
      form.elements.curp.value = item.curp || "";
      form.elements.regimen_fiscal.value = item.regimen_fiscal || "";
      form.elements.fecha_alta.value = toDateInputValue(item.fecha_alta);
      form.elements.nivel_confianza.value = item.nivel_confianza || "medio";
      form.elements.prioridad_asignacion.value = integerStringForNumberInput(item.prioridad_asignacion);
      form.elements.contacto.value = item.contacto || "";
      form.elements.telefono.value = item.telefono || item.telefono_general || "";
      form.elements.email.value = item.email || item.email_general || "";
      form.elements.sitio_web.value = item.sitio_web || "";
      form.elements.codigo_postal.value = item.codigo_postal || "";
      form.elements.ciudad.value = item.ciudad || "";
      form.elements.estado.value = item.estado || "";
      form.elements.pais.value = item.pais || "";
      form.elements.direccion_fiscal.value = item.direccion_fiscal || "";
      form.elements.direccion_operativa.value = item.direccion_operativa || "";
      form.elements.notas_operativas.value = item.notas_operativas || item.notas || "";
      form.elements.notas_comerciales.value = item.notas_comerciales || "";
      form.elements.blacklist.checked = Boolean(item.blacklist);
      form.elements.activo.checked = Boolean(item.activo);
      setTransportistaSubpage("consulta");
      showPanel("transportista-edit-panel");
      clearMessage("transportista-edit-message");
      const editPanel = document.getElementById("transportista-edit-panel");
      if (editPanel) {
        editPanel.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    }

    function cancelTransportistaEdit() {
      uiState.editing.transportistaId = null;
      document.getElementById("transportista-edit-form").reset();
      hidePanel("transportista-edit-panel", "transportista-edit-message");
    }

    function cancelOperadorEdit() {
      uiState.editing.operadorId = null;
      const form = document.getElementById("operador-edit-form");
      if (form) {
        form.reset();
        applyMoneyFormatToForm(form);
      }
      hidePanel("operador-edit-panel", "operador-edit-message");
    }

    function cancelUnidadEdit() {
      uiState.editing.unidadId = null;
      const form = document.getElementById("unidad-edit-form");
      if (form) {
        form.reset();
      }
      hidePanel("unidad-edit-panel", "unidad-edit-message");
    }

    function startUnidadEdit(id) {
      const uid = Number(id);
      const item = state.unidades.find((row) => Number(row.id_unidad) === uid);
      if (!item) {
        setMessage(
          "unidad-consulta-message",
          "No se encontro esa unidad en el catalogo cargado (memoria). Pulse Recargar catalogo; si tiene mas de 500 unidades en el servidor, el panel solo muestra las primeras 500 por economico.",
          "error",
        );
        return;
      }
      uiState.editing.unidadId = item.id_unidad;
      fillSelect("edit-unidad-transportista", state.transportistas, (t) => t.id, (t) => `${t.id} - ${t.nombre}`, {
        includeEmpty: true,
        emptyLabel: "Sin transportista",
        classKey: "transportista",
      });
      const form = document.getElementById("unidad-edit-form");
      const idEl = document.getElementById("unidad-edit-form-id");
      if (idEl) {
        idEl.value = String(item.id_unidad);
      }
      form.elements.transportista_id.value = item.transportista_id != null ? String(item.transportista_id) : "";
      form.elements.tipo_propiedad.value = item.tipo_propiedad || "";
      form.elements.estatus_documental.value = item.estatus_documental || "";
      form.elements.economico.value = item.economico || "";
      form.elements.placas.value = item.placas || "";
      form.elements.descripcion.value = item.descripcion || "";
      form.elements.detalle.value = item.detalle || "";
      form.elements.vigencia_permiso_sct.value = toDateInputValue(item.vigencia_permiso_sct);
      form.elements.vigencia_seguro.value = toDateInputValue(item.vigencia_seguro);
      form.elements.activo.checked = item.activo === true;
      setGenericSubpage("unidad", "unidadSubpage", "consulta", "consulta");
      showPanel("unidad-edit-panel");
      clearMessage("unidad-edit-message");
      const panel = document.getElementById("unidad-edit-panel");
      if (panel) {
        panel.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    }

    async function deleteUnidad(idUnidad) {
      const uid = Number(idUnidad);
      if (!Number.isFinite(uid) || uid < 1) {
        return;
      }
      if (
        !window.confirm(
          "¿Eliminar esta unidad? La accion no se puede deshacer. Si existen asignaciones que la usen, el servidor rechazara el borrado.",
        )
      ) {
        return;
      }
      clearMessage("unidad-consulta-message");
      try {
        await api(`/unidades/${uid}`, { method: "DELETE" });
        if (uiState.editing.unidadId != null && Number(uiState.editing.unidadId) === uid) {
          cancelUnidadEdit();
        }
        setMessage("unidad-consulta-message", "Unidad eliminada.", "ok");
        await refreshData();
      } catch (error) {
        setMessage("unidad-consulta-message", error.message, "error");
      }
    }

    function startOperadorEdit(operadorId) {
      const oid = Number(operadorId);
      const item = state.operadores.find((row) => Number(row.id_operador) === oid);
      if (!item) {
        return;
      }
      uiState.editing.operadorId = item.id_operador;
      const form = document.getElementById("operador-edit-form");
      const idEl = document.getElementById("operador-edit-form-id");
      if (idEl) {
        idEl.value = String(item.id_operador);
      }
      form.elements.transportista_id.value = item.transportista_id != null ? String(item.transportista_id) : "";
      form.elements.tipo_contratacion.value = item.tipo_contratacion || "";
      form.elements.licencia.value = item.licencia || "";
      form.elements.tipo_licencia.value = item.tipo_licencia || "";
      form.elements.vigencia_licencia.value = toDateInputValue(item.vigencia_licencia);
      form.elements.estatus_documental.value = item.estatus_documental || "";
      form.elements.nombre.value = item.nombre || "";
      form.elements.apellido_paterno.value = item.apellido_paterno || "";
      form.elements.apellido_materno.value = item.apellido_materno || "";
      form.elements.fecha_nacimiento.value = toDateInputValue(item.fecha_nacimiento);
      form.elements.curp.value = item.curp || "";
      form.elements.rfc.value = item.rfc || "";
      form.elements.nss.value = item.nss || "";
      form.elements.estado_civil.value = item.estado_civil || "soltero";
      form.elements.tipo_sangre.value = item.tipo_sangre || "O+";
      form.elements.fotografia.value = item.fotografia || "";
      form.elements.telefono_principal.value = item.telefono_principal || "";
      form.elements.telefono_emergencia.value = item.telefono_emergencia || "";
      form.elements.nombre_contacto_emergencia.value = item.nombre_contacto_emergencia || "";
      form.elements.correo_electronico.value = item.correo_electronico || "";
      form.elements.direccion.value = item.direccion || "";
      form.elements.colonia.value = item.colonia || "";
      form.elements.municipio.value = item.municipio || "";
      form.elements.estado_geografico.value = item.estado_geografico || "";
      form.elements.codigo_postal.value = item.codigo_postal || "";
      form.elements.anios_experiencia.value = optionalNonNegativeIntString(item.anios_experiencia);
      form.elements.tipos_unidad_manejadas.value = operadorCsvFromApi(item.tipos_unidad_manejadas);
      form.elements.tipos_carga_experiencia.value = operadorCsvFromApi(item.tipos_carga_experiencia);
      form.elements.rutas_conocidas.value = item.rutas_conocidas || "";
      form.elements.certificaciones.value = item.certificaciones || "";
      form.elements.ultima_revision_medica.value = toDateInputValue(item.ultima_revision_medica);
      form.elements.proxima_revision_medica.value = toDateInputValue(item.proxima_revision_medica);
      form.elements.resultado_apto.checked = item.resultado_apto === true;
      form.elements.restricciones_medicas.value = item.restricciones_medicas || "";
      form.elements.puntualidad.value = item.puntualidad != null && item.puntualidad !== "" ? String(item.puntualidad) : "";
      form.elements.consumo_diesel_promedio.value =
        item.consumo_diesel_promedio != null && item.consumo_diesel_promedio !== ""
          ? String(item.consumo_diesel_promedio)
          : "";
      form.elements.consumo_gasolina_promedio.value =
        item.consumo_gasolina_promedio != null && item.consumo_gasolina_promedio !== ""
          ? String(item.consumo_gasolina_promedio)
          : "";
      form.elements.calificacion_general.value =
        item.calificacion_general != null && item.calificacion_general !== "" ? String(item.calificacion_general) : "";
      form.elements.incidencias_desempeno.value = item.incidencias_desempeno || "";
      form.elements.comentarios_desempeno.value = item.comentarios_desempeno || "";
      applyMoneyFormatToForm(form);
      setGenericSubpage("operador", "operadorSubpage", "consulta", "consulta");
      showPanel("operador-edit-panel");
      clearMessage("operador-edit-message");
      const panel = document.getElementById("operador-edit-panel");
      if (panel) {
        panel.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    }

    function startTransportistaContactoEdit(transportistaId, contactoId) {
      const transportista = state.transportistas.find((item) => item.id === transportistaId);
      const contacto = transportista?.contactos?.find((item) => item.id === contactoId);
      if (!transportista || !contacto) {
        return;
      }
      uiState.editing.transportistaContactoId = contactoId;
      const form = document.getElementById("transportista-contacto-edit-form");
      form.elements.id.value = contacto.id;
      form.elements.transportista_id.value = transportista.id;
      form.elements.transportista_label.value = `${transportista.id} - ${transportista.nombre}`;
      form.elements.nombre.value = contacto.nombre || "";
      form.elements.area.value = contacto.area || "";
      form.elements.puesto.value = contacto.puesto || "";
      form.elements.email.value = contacto.email || "";
      form.elements.telefono.value = contacto.telefono || "";
      form.elements.extension.value = contacto.extension || "";
      form.elements.celular.value = contacto.celular || "";
      form.elements.principal.checked = Boolean(contacto.principal);
      form.elements.activo.checked = Boolean(contacto.activo);
      setTransportistaSubpage("contactos");
      showPanel("transportista-contacto-edit-panel");
      clearMessage("transportista-contacto-edit-message");
    }

    function cancelTransportistaContactoEdit() {
      uiState.editing.transportistaContactoId = null;
      document.getElementById("transportista-contacto-edit-form").reset();
      hidePanel("transportista-contacto-edit-panel", "transportista-contacto-edit-message");
    }

    async function deleteTransportistaContacto(transportistaId, contactoId) {
      if (!window.confirm("¿Eliminar este contacto del transportista?")) {
        return;
      }
      clearMessage("transportista-contacto-message");
      try {
        await api(`/transportistas/${transportistaId}/contactos/${contactoId}`, { method: "DELETE" });
        if (uiState.editing.transportistaContactoId === contactoId) {
          cancelTransportistaContactoEdit();
        }
        setMessage("transportista-contacto-message", "Contacto eliminado.", "ok");
        await refreshData();
        document.getElementById("transportista-contacto-transportista").value = String(transportistaId);
        syncTransportistaModuleSelection("transportista-contacto-transportista");
      } catch (error) {
        setMessage("transportista-contacto-message", error.message, "error");
      }
    }

    function startTransportistaDocumentoEdit(transportistaId, documentoId) {
      const transportista = state.transportistas.find((item) => item.id === transportistaId);
      const documento = transportista?.documentos?.find((item) => item.id === documentoId);
      if (!transportista || !documento) {
        return;
      }
      uiState.editing.transportistaDocumentoId = documentoId;
      const form = document.getElementById("transportista-documento-edit-form");
      form.elements.id.value = documento.id;
      form.elements.transportista_id.value = transportista.id;
      form.elements.transportista_label.value = `${transportista.id} - ${transportista.nombre}`;
      form.elements.tipo_documento.value = documento.tipo_documento || "otro";
      form.elements.numero_documento.value = documento.numero_documento || "";
      form.elements.fecha_emision.value = toDateInputValue(documento.fecha_emision);
      form.elements.fecha_vencimiento.value = toDateInputValue(documento.fecha_vencimiento);
      form.elements.archivo_url.value = documento.archivo_url || "";
      form.elements.estatus.value = documento.estatus || "pendiente";
      form.elements.observaciones.value = documento.observaciones || "";
      setTransportistaSubpage("documentos");
      showPanel("transportista-documento-edit-panel");
      clearMessage("transportista-documento-edit-message");
    }

    function cancelTransportistaDocumentoEdit() {
      uiState.editing.transportistaDocumentoId = null;
      document.getElementById("transportista-documento-edit-form").reset();
      hidePanel("transportista-documento-edit-panel", "transportista-documento-edit-message");
    }

    async function deleteTransportistaDocumento(transportistaId, documentoId) {
      if (!window.confirm("¿Eliminar este documento del transportista?")) {
        return;
      }
      clearMessage("transportista-documento-message");
      try {
        await api(`/transportistas/${transportistaId}/documentos/${documentoId}`, { method: "DELETE" });
        if (uiState.editing.transportistaDocumentoId === documentoId) {
          cancelTransportistaDocumentoEdit();
        }
        setMessage("transportista-documento-message", "Documento eliminado.", "ok");
        await refreshData();
        document.getElementById("transportista-documento-transportista").value = String(transportistaId);
        syncTransportistaModuleSelection("transportista-documento-transportista");
      } catch (error) {
        setMessage("transportista-documento-message", error.message, "error");
      }
    }

    function startViajeEdit(viajeId) {
      const item = state.viajes.find((row) => row.id === viajeId);
      if (!item) {
        return;
      }
      uiState.editing.viajeId = viajeId;
      const form = document.getElementById("viaje-edit-form");
      form.elements.id.value = item.id;
      form.elements.codigo_viaje.value = item.codigo_viaje || "";
      form.elements.descripcion.value = item.descripcion || "";
      form.elements.origen.value = item.origen || "";
      form.elements.destino.value = item.destino || "";
      form.elements.fecha_salida.value = toDateTimeLocal(item.fecha_salida);
      form.elements.fecha_llegada_estimada.value = toDateTimeLocal(item.fecha_llegada_estimada);
      form.elements.fecha_llegada_real.value = toDateTimeLocal(item.fecha_llegada_real);
      form.elements.estado.value = item.estado || "planificado";
      form.elements.kilometros_estimados.value = htmlNumberInputValue(item.kilometros_estimados);
      form.elements.notas.value = item.notas || "";
      setGenericSubpage("viaje", "viajeSubpage", "consulta", "consulta");
      showPanel("viaje-edit-panel");
      clearMessage("viaje-edit-message");
    }

    function cancelViajeEdit() {
      uiState.editing.viajeId = null;
      document.getElementById("viaje-edit-form").reset();
      hidePanel("viaje-edit-panel", "viaje-edit-message");
    }

    function recalculateFacturaForm(formSelector) {
      const subtotalInput = document.querySelector(`${formSelector} [name="subtotal"]`);
      const ivaPctInput = document.querySelector(`${formSelector} [name="iva_pct"]`);
      const ivaMontoInput = document.querySelector(`${formSelector} [name="iva_monto"]`);
      const retencionInput = document.querySelector(`${formSelector} [name="retencion_monto"]`);
      const totalInput = document.querySelector(`${formSelector} [name="total"]`);
      const saldoInput = document.querySelector(`${formSelector} [name="saldo_pendiente"]`);
      if (!subtotalInput || !ivaPctInput || !ivaMontoInput || !retencionInput || !totalInput || !saldoInput) {
        return;
      }
      const subtotal = numberOrNull(subtotalInput.value);
      const ivaPct = numberOrNull(ivaPctInput.value);
      const retencion = numberOrNull(retencionInput.value) ?? 0;
      if (subtotal === null || ivaPct === null) {
        return;
      }
      const ivaMonto = subtotal * ivaPct;
      const total = subtotal + ivaMonto - retencion;
      ivaMontoInput.value = formatMoneyInputFromEl(ivaMonto, ivaMontoInput);
      totalInput.value = formatMoneyInputFromEl(total, totalInput);
      if (parseLocaleNumber(saldoInput.value) === null || String(saldoInput.value).trim() === "") {
        saldoInput.value = formatMoneyInputFromEl(total, saldoInput);
      }
    }

    function fillFacturaFleteSelectFiltered(clienteIdStr) {
      const raw = clienteIdStr != null ? String(clienteIdStr).trim() : "";
      const cid = raw === "" ? null : Number(raw);
      let items = Array.isArray(state.fletes) ? state.fletes : [];
      if (cid != null && Number.isFinite(cid)) {
        items = items.filter((f) => Number(f.cliente_id) === cid);
      }
      const emptyLabel =
        cid != null && Number.isFinite(cid)
          ? items.length
            ? "Selecciona flete"
            : "Sin fletes para este cliente"
          : "Sin flete";
      fillSelect("factura-flete", items, (item) => item.id, (item) => `${item.id} - ${item.codigo_flete}`, {
        includeEmpty: true,
        emptyLabel,
        classKey: "flete",
      });
    }

    function fillFacturaFromFlete(formSelector) {
      const form = document.querySelector(formSelector);
      const fleteId = integerOrNull(form.querySelector('[name="flete_id"]').value);
      if (!fleteId) {
        throw new Error("Selecciona primero un flete.");
      }
      const flete = state.fletes.find((item) => item.id === fleteId);
      if (!flete) {
        throw new Error("Flete no encontrado en memoria.");
      }
      form.querySelector('[name="cliente_id"]').value = String(flete.cliente_id);
      form.querySelector('[name="concepto"]').value = `Servicio de flete ${flete.codigo_flete}`;
      form.querySelector('[name="referencia"]').value = flete.codigo_flete || "";
      form.querySelector('[name="moneda"]').value = flete.moneda || "MXN";
      const subtotalEl = form.querySelector('[name="subtotal"]');
      subtotalEl.value = formatMoneyInputFromEl(
        Number(flete.precio_venta ?? flete.monto_estimado ?? 0),
        subtotalEl,
      );
      if (form.querySelector('[name="orden_servicio_id"]') && !form.querySelector('[name="orden_servicio_id"]').value) {
        form.querySelector('[name="orden_servicio_id"]').value = "";
      }
      recalculateFacturaForm(formSelector);
    }

    function startFacturaEdit(facturaId) {
      const item = state.facturas.find((row) => row.id === facturaId);
      if (!item) {
        return;
      }
      uiState.editing.facturaId = facturaId;
      const form = document.getElementById("factura-edit-form");
      form.elements.id.value = item.id;
      form.elements.serie.value = item.serie || "";
      form.elements.cliente_id.value = String(item.cliente_id || "");
      form.elements.flete_id.value = item.flete_id ? String(item.flete_id) : "";
      form.elements.orden_servicio_id.value = item.orden_servicio_id ? String(item.orden_servicio_id) : "";
      form.elements.fecha_emision.value = toDateInputValue(item.fecha_emision);
      form.elements.fecha_vencimiento.value = toDateInputValue(item.fecha_vencimiento);
      form.elements.concepto.value = item.concepto || "";
      form.elements.referencia.value = item.referencia || "";
      form.elements.moneda.value = item.moneda || "MXN";
      form.elements.subtotal.value = item.subtotal ?? "";
      form.elements.iva_pct.value = htmlNumberInputValue(item.iva_pct != null ? item.iva_pct : 0.16);
      form.elements.iva_monto.value = item.iva_monto ?? "";
      form.elements.retencion_monto.value = item.retencion_monto ?? 0;
      form.elements.total.value = item.total ?? "";
      form.elements.saldo_pendiente.value = item.saldo_pendiente ?? "";
      form.elements.forma_pago.value = item.forma_pago || "";
      form.elements.metodo_pago.value = item.metodo_pago || "";
      form.elements.uso_cfdi.value = item.uso_cfdi || "";
      form.elements.estatus.value = item.estatus || "borrador";
      form.elements.timbrada.checked = Boolean(item.timbrada);
      form.elements.observaciones.value = item.observaciones || "";
      applyMoneyFormatToForm(form);
      setGenericSubpage("factura", "facturaSubpage", "consulta", "consulta");
      showPanel("factura-edit-panel");
      clearMessage("factura-edit-message");
    }

    function cancelFacturaEdit() {
      uiState.editing.facturaId = null;
      document.getElementById("factura-edit-form").reset();
      hidePanel("factura-edit-panel", "factura-edit-message");
    }

    function startTarifaCompraEdit(tarifaId) {
      const tid = Number(tarifaId);
      if (!Number.isFinite(tid) || tid < 1) {
        return;
      }
      const item = state.tarifasCompra.find((row) => Number(row.id) === tid);
      if (!item) {
        return;
      }
      uiState.editing.tarifaCompraId = tid;
      lastTarifaCompraEditId = tid;
      try {
        window.__SIFE_tarifaCompraEditId = tid;
      } catch (_e) {
        /* ignore */
      }
      const form = document.getElementById("tarifa-compra-edit-form");
      const sid = String(item.id);
      form._sifeTarifaCompraId = tid;
      setTarifaCompraEditIdStorage(sid);
      form.setAttribute("data-tarifa-compra-id", sid);
      const idInput = document.getElementById("tarifa-compra-edit-record-id");
      if (idInput) {
        idInput.value = sid;
        idInput.defaultValue = sid;
      }
      const saveBtn = document.getElementById("tarifa-compra-edit-save");
      if (saveBtn) {
        saveBtn.setAttribute("data-tarifa-compra-record-id", sid);
      }
      form.elements.transportista_id.value = String(item.transportista_id || "");
      form.elements.nombre_tarifa.value = item.nombre_tarifa || "";
      form.elements.tipo_transportista.value = item.tipo_transportista || "subcontratado";
      form.elements.ambito.value = item.ambito || "federal";
      form.elements.modalidad_cobro.value = item.modalidad_cobro || "mixta";
      form.elements.origen.value = item.origen || "";
      form.elements.destino.value = item.destino || "";
      form.elements.tipo_unidad.value = item.tipo_unidad || "";
      form.elements.tipo_carga.value = item.tipo_carga || "";
      form.elements.tarifa_base.value = item.tarifa_base ?? "";
      form.elements.tarifa_km.value = item.tarifa_km ?? "";
      form.elements.tarifa_kg.value = item.tarifa_kg ?? "";
      form.elements.tarifa_tonelada.value = item.tarifa_tonelada ?? "";
      form.elements.tarifa_hora.value = item.tarifa_hora ?? "";
      form.elements.tarifa_dia.value = item.tarifa_dia ?? "";
      form.elements.recargo_minimo.value = item.recargo_minimo ?? "";
      form.elements.dias_credito.value =
        item.dias_credito != null && item.dias_credito !== "" ? String(item.dias_credito) : "";
      form.elements.moneda.value = item.moneda || "MXN";
      form.elements.activo.checked = Boolean(item.activo);
      form.elements.vigencia_inicio.value = toDateInputValue(item.vigencia_inicio);
      form.elements.vigencia_fin.value = toDateInputValue(item.vigencia_fin);
      form.elements.observaciones.value = item.observaciones || "";
      applyMoneyFormatToForm(form);
      for (const name of ["tarifa_km", "tarifa_kg", "tarifa_tonelada"]) {
        const el = form.querySelector(`input.field-money[name="${name}"]`);
        if (!el) {
          continue;
        }
        const p = parseLocaleNumber(el.value);
        el.value = p === null ? "" : formatMoneyInputFromEl(p, el);
      }
      setGenericSubpage("tarifa-compra", "tarifaCompraSubpage", "consulta", "consulta");
      showPanel("tarifa-compra-edit-panel");
      clearMessage("tarifa-compra-edit-message");
    }

    function cancelTarifaCompraEdit() {
      uiState.editing.tarifaCompraId = null;
      lastTarifaCompraEditId = null;
      try {
        window.__SIFE_tarifaCompraEditId = null;
      } catch (_e) {
        /* ignore */
      }
      const form = document.getElementById("tarifa-compra-edit-form");
      try {
        delete form._sifeTarifaCompraId;
      } catch (_e) {
        form._sifeTarifaCompraId = null;
      }
      setTarifaCompraEditIdStorage(null);
      form.removeAttribute("data-tarifa-compra-id");
      const idInput = document.getElementById("tarifa-compra-edit-record-id");
      if (idInput) {
        idInput.value = "";
        idInput.defaultValue = "";
      }
      const saveBtn = document.getElementById("tarifa-compra-edit-save");
      if (saveBtn) {
        saveBtn.removeAttribute("data-tarifa-compra-record-id");
      }
      form.reset();
      hidePanel("tarifa-compra-edit-panel", "tarifa-compra-edit-message");
    }

    function tarifaFleteDateInput(value) {
      return toDateInputValue(value);
    }

    function setEnumSelectSafe(selectEl, rawValue, allowed, fallback) {
      if (!selectEl) {
        return;
      }
      const s = rawValue != null && String(rawValue).trim() !== "" ? String(rawValue).trim().toLowerCase() : "";
      const pick = allowed.includes(s) ? s : fallback;
      selectEl.value = pick;
    }

    async function startTarifaFleteEdit(tarifaId) {
      const tid = Number(tarifaId);
      if (!Number.isFinite(tid) || tid < 1) {
        setMessage("tarifa-message", "ID de tarifa no valido.", "error");
        return;
      }
      let item = state.tarifas.find((row) => Number(row.id) === tid);
      try {
        item = await api(`/tarifas-flete/${tid}`);
      } catch (_err) {
        if (!item) {
          setMessage(
            "tarifa-message",
            "No se pudo cargar la tarifa desde el servidor. Actualice la pagina (F5) e intente de nuevo.",
            "error",
          );
          return;
        }
      }
      if (!item) {
        setMessage("tarifa-message", "No se encontro la tarifa en el listado cargado. Pulse F5.", "error");
        return;
      }
      uiState.editing.tarifaFleteId = item.id;
      const form = document.getElementById("tarifa-edit-form");
      form.elements.id.value = item.id;
      form.elements.nombre_tarifa.value = item.nombre_tarifa || "";
      form.elements.moneda.value = item.moneda || "MXN";
      form.elements.tipo_operacion.value = item.tipo_operacion || "subcontratado";
      if (form.elements.ambito) {
        setEnumSelectSafe(form.elements.ambito, item.ambito, ["local", "estatal", "federal"], "federal");
      }
      if (form.elements.modalidad_cobro) {
        setEnumSelectSafe(
          form.elements.modalidad_cobro,
          item.modalidad_cobro,
          ["mixta", "por_viaje", "por_km", "por_tonelada", "por_hora", "por_dia"],
          "mixta",
        );
      }
      form.elements.origen.value = item.origen || "";
      form.elements.destino.value = item.destino || "";
      form.elements.tipo_unidad.value = item.tipo_unidad || "";
      form.elements.tipo_carga.value = item.tipo_carga || "";
      form.elements.tarifa_base.value = item.tarifa_base ?? "";
      form.elements.tarifa_km.value = item.tarifa_km ?? "";
      form.elements.tarifa_kg.value = item.tarifa_kg ?? "";
      if (form.elements.tarifa_tonelada) {
        form.elements.tarifa_tonelada.value = item.tarifa_tonelada ?? "";
      }
      if (form.elements.tarifa_hora) {
        form.elements.tarifa_hora.value = item.tarifa_hora ?? "";
      }
      if (form.elements.tarifa_dia) {
        form.elements.tarifa_dia.value = item.tarifa_dia ?? "";
      }
      if (form.elements.porcentaje_utilidad) {
        form.elements.porcentaje_utilidad.value = item.porcentaje_utilidad ?? "";
      }
      if (form.elements.porcentaje_riesgo) {
        form.elements.porcentaje_riesgo.value = item.porcentaje_riesgo ?? "";
      }
      if (form.elements.porcentaje_urgencia) {
        form.elements.porcentaje_urgencia.value = item.porcentaje_urgencia ?? "";
      }
      if (form.elements.porcentaje_retorno_vacio) {
        form.elements.porcentaje_retorno_vacio.value = item.porcentaje_retorno_vacio ?? "";
      }
      if (form.elements.porcentaje_carga_especial) {
        form.elements.porcentaje_carga_especial.value = item.porcentaje_carga_especial ?? "";
      }
      form.elements.recargo_minimo.value = item.recargo_minimo ?? "";
      form.elements.vigencia_inicio.value = tarifaFleteDateInput(item.vigencia_inicio);
      form.elements.vigencia_fin.value = tarifaFleteDateInput(item.vigencia_fin);
      form.elements.activo.checked = Boolean(item.activo);
      applyMoneyFormatToForm(form);
      for (const name of ["tarifa_km", "tarifa_kg", "tarifa_tonelada"]) {
        const el = form.querySelector(`input.field-money[name="${name}"]`);
        if (!el) {
          continue;
        }
        const p = parseLocaleNumber(el.value);
        el.value = p === null ? "" : formatMoneyInputFromEl(p, el);
      }
      setGenericSubpage("tarifa", "tarifaSubpage", "consulta", "consulta");
      showPanel("tarifa-edit-panel");
      clearMessage("tarifa-edit-message");
      const teNombre = document.getElementById("tarifa-edit-form-nombre-tarifa");
      const teAviso = document.getElementById("tarifa-edit-form-nombre-aviso");
      const teSubmit = form.querySelector('button[type="submit"]');
      refreshTarifaVentaNombreAviso(teNombre, teAviso, teSubmit, item.id);
      document.getElementById("tarifa-edit-panel").scrollIntoView({ behavior: "smooth", block: "nearest" });
    }

    function cancelTarifaFleteEdit() {
      uiState.editing.tarifaFleteId = null;
      document.getElementById("tarifa-edit-form").reset();
      const teAviso = document.getElementById("tarifa-edit-form-nombre-aviso");
      if (teAviso) {
        teAviso.textContent = "";
        teAviso.hidden = true;
      }
      hidePanel("tarifa-edit-panel", "tarifa-edit-message");
    }

    async function deleteTarifaCompra(tarifaId) {
      if (!window.confirm("¿Eliminar esta tarifa de compra?")) {
        return;
      }
      clearMessage("tarifa-compra-message");
      try {
        await api(`/tarifas-compra-transportista/${tarifaId}`, { method: "DELETE" });
        if (Number(uiState.editing.tarifaCompraId) === Number(tarifaId)) {
          cancelTarifaCompraEdit();
        }
        setMessage("tarifa-compra-message", "Tarifa de compra eliminada.", "ok");
        await refreshData();
      } catch (error) {
        setMessage("tarifa-compra-message", error.message, "error");
      }
    }

    function startAsignacionEdit(asignacionId) {
      const item = state.asignaciones.find((row) => row.id_asignacion === asignacionId);
      if (!item) {
        return;
      }
      uiState.editing.asignacionId = asignacionId;
      const form = document.getElementById("asignacion-edit-form");
      form.elements.id_asignacion.value = item.id_asignacion;
      form.elements.id_operador.value = String(item.id_operador || "");
      form.elements.id_unidad.value = String(item.id_unidad || "");
      form.elements.id_viaje.value = String(item.id_viaje || "");
      form.elements.fecha_salida.value = toDateTimeLocal(item.fecha_salida);
      form.elements.fecha_regreso.value = toDateTimeLocal(item.fecha_regreso);
      form.elements.km_inicial.value = htmlNumberInputValue(item.km_inicial);
      form.elements.km_final.value = htmlNumberInputValue(item.km_final);
      form.elements.rendimiento_combustible.value = htmlNumberInputValue(item.rendimiento_combustible);
      setGenericSubpage("asignacion", "asignacionSubpage", "consulta", "consulta");
      showPanel("asignacion-edit-panel");
      clearMessage("asignacion-edit-message");
    }

    function cancelAsignacionEdit() {
      uiState.editing.asignacionId = null;
      document.getElementById("asignacion-edit-form").reset();
      hidePanel("asignacion-edit-panel", "asignacion-edit-message");
    }

    function startFleteEdit(fleteId) {
      const fid = Number(fleteId);
      const item = state.fletes.find((row) => Number(row.id) === fid);
      if (!item) {
        return;
      }
      uiState.editing.fleteId = item.id;
      const form = document.getElementById("flete-edit-form");
      const idPk = document.getElementById("flete-edit-form-record-id");
      if (idPk) {
        idPk.value = String(item.id);
      }
      if (form) {
        form.dataset.sifeEditingFleteId = String(item.id);
      }
      form.elements.codigo_flete.value = item.codigo_flete || "";
      form.elements.estado.value = item.estado || "cotizado";
      form.elements.tipo_operacion.value = item.tipo_operacion || "subcontratado";
      form.elements.metodo_calculo.value = item.metodo_calculo || "manual";
      form.elements.moneda.value = item.moneda || "MXN";
      form.elements.cliente_id.value = String(item.cliente_id || "");
      form.elements.transportista_id.value = String(item.transportista_id || "");
      form.elements.viaje_id.value = item.viaje_id ? String(item.viaje_id) : "";
      form.elements.tipo_unidad.value = item.tipo_unidad || "";
      form.elements.tipo_carga.value = item.tipo_carga || "";
      form.elements.descripcion_carga.value = item.descripcion_carga || "";
      form.elements.peso_kg.value = htmlNumberInputValue(item.peso_kg);
      form.elements.volumen_m3.value = htmlNumberInputValue(item.volumen_m3);
      form.elements.numero_bultos.value = optionalNonNegativeIntString(item.numero_bultos);
      form.elements.distancia_km.value = htmlNumberInputValue(item.distancia_km);
      form.elements.monto_estimado.value = item.precio_venta ?? item.monto_estimado ?? "";
      form.elements.costo_transporte_estimado.value = item.costo_transporte_estimado ?? "";
      form.elements.costo_transporte_real.value = item.costo_transporte_real ?? "";
      form.elements.margen_estimado.value = item.margen_estimado ?? "";
      form.elements.notas.value = item.notas || "";
      applyMoneyFormatToForm(form);
      refreshMarginForForm("#flete-edit-form");
      setGenericSubpage("flete", "fleteSubpage", "consulta", "consulta");
      showPanel("flete-edit-panel");
      clearMessage("flete-edit-message");
    }

    function cancelFleteEdit() {
      uiState.editing.fleteId = null;
      const form = document.getElementById("flete-edit-form");
      if (form) {
        delete form.dataset.sifeEditingFleteId;
        form.reset();
      }
      hidePanel("flete-edit-panel", "flete-edit-message");
    }

    function startGastoEdit(gastoId) {
      const item = state.gastos.find((row) => row.id === gastoId);
      if (!item) {
        return;
      }
      const valid = Object.keys(GASTO_CATEGORIA_LABELS);
      uiState.editing.gastoId = gastoId;
      const form = document.getElementById("gasto-edit-form");
      form.elements.id.value = item.id;
      form.elements.flete_id.value = String(item.flete_id);
      form.elements.tipo_gasto.value = valid.includes(item.tipo_gasto) ? item.tipo_gasto : "otros";
      form.elements.monto.value = item.monto ?? "";
      form.elements.fecha_gasto.value = toDateInputValue(item.fecha_gasto);
      form.elements.referencia.value = item.referencia || "";
      form.elements.comprobante.value = item.comprobante || "";
      form.elements.descripcion.value = item.descripcion || "";
      applyMoneyFormatToForm(form);
      setGenericSubpage("gasto", "gastoSubpage", "consulta", "consulta");
      showPanel("gasto-edit-panel");
      clearMessage("gasto-edit-message");
    }

    function cancelGastoEdit() {
      uiState.editing.gastoId = null;
      document.getElementById("gasto-edit-form").reset();
      hidePanel("gasto-edit-panel", "gasto-edit-message");
    }

    async function deleteGasto(gastoId) {
      if (
        !window.confirm(
          "¿Eliminar este gasto de viaje? Se recalculará el costo real y el margen del flete.",
        )
      ) {
        return;
      }
      clearMessage("gasto-list-message");
      try {
        await api(`/gastos-viaje/${gastoId}`, { method: "DELETE" });
        if (uiState.editing.gastoId === gastoId) {
          cancelGastoEdit();
        }
        setMessage("gasto-list-message", "Gasto eliminado.", "ok");
        await refreshData();
      } catch (error) {
        setMessage("gasto-list-message", error.message, "error");
      }
    }

    function startDespachoEdit(despachoId) {
      const did = Number(despachoId);
      if (!Number.isFinite(did) || did < 1) {
        return;
      }
      const item = state.despachos.find((row) => Number(row.id_despacho) === did);
      if (!item) {
        return;
      }
      uiState.editing.despachoId = item.id_despacho;
      const form = document.getElementById("despacho-edit-form");
      if (!form) {
        return;
      }
      form.dataset.sifeEditingDespachoId = String(item.id_despacho);
      const idEl = document.getElementById("despacho-edit-form-id");
      if (idEl) {
        idEl.value = String(item.id_despacho);
      }
      form.elements.asignacion_label.value = `${item.id_asignacion} - ${item.asignacion?.viaje?.codigo_viaje || "sin viaje"}`;
      form.elements.id_flete.value = item.id_flete ? String(item.id_flete) : "";
      form.elements.estatus.value = item.estatus || "programado";
      form.elements.salida_programada.value = toDateTimeLocal(item.salida_programada);
      form.elements.observaciones_transito.value = item.observaciones_transito || "";
      form.elements.motivo_cancelacion.value = item.motivo_cancelacion || "";
      setGenericSubpage("despacho", "despachoSubpage", "consulta", "consulta");
      showPanel("despacho-edit-panel");
      clearMessage("despacho-edit-message");
    }

    function cancelDespachoEdit() {
      uiState.editing.despachoId = null;
      const form = document.getElementById("despacho-edit-form");
      if (form) {
        delete form.dataset.sifeEditingDespachoId;
        form.reset();
      }
      hidePanel("despacho-edit-panel", "despacho-edit-message");
    }

    function populateSelects() {
      fillSelect("flete-cliente", state.clientes, (item) => item.id, (item) => `${item.id} - ${item.razon_social}`, { includeEmpty: false, classKey: "cliente" });
      fillSelect("flete-transportista", state.transportistas, (item) => item.id, (item) => `${item.id} - ${item.nombre}`, { includeEmpty: false, classKey: "transportista" });
      fillSelect("flete-viaje", state.viajes, (item) => item.id, (item) => `${item.id} - ${item.codigo_viaje}`, { includeEmpty: true, emptyLabel: "Sin viaje", classKey: "viaje" });
      fillSelect("factura-cliente", state.clientes, (item) => item.id, (item) => `${item.id} - ${item.razon_social}`, { includeEmpty: false, classKey: "cliente" });
      fillSelect("factura-filter-cliente", state.clientes, (item) => item.id, (item) => `${item.id} - ${item.razon_social}`, { includeEmpty: true, emptyLabel: "Todos", classKey: "cliente" });
      fillSelect("orden-servicio-filter-cliente", state.clientes, (item) => item.id, (item) => `${item.id} - ${item.razon_social}`, { includeEmpty: true, emptyLabel: "Todos", classKey: "cliente" });
      fillSelect("edit-factura-cliente", state.clientes, (item) => item.id, (item) => `${item.id} - ${item.razon_social}`, { includeEmpty: false, classKey: "cliente" });
      fillSelect("factura-flete", state.fletes, (item) => item.id, (item) => `${item.id} - ${item.codigo_flete}`, { includeEmpty: true, emptyLabel: "Sin flete", classKey: "flete" });
      fillSelect("edit-factura-flete", state.fletes, (item) => item.id, (item) => `${item.id} - ${item.codigo_flete}`, { includeEmpty: true, emptyLabel: "Sin flete", classKey: "flete" });
      fillSelect("gasto-flete", state.fletes, (item) => item.id, (item) => `${item.id} - ${item.codigo_flete}`, { includeEmpty: false, classKey: "flete" });
      fillSelect("edit-gasto-flete", state.fletes, (item) => item.id, (item) => `${item.id} - ${item.codigo_flete}`, { includeEmpty: false, classKey: "flete" });
      fillSelect("gasto-control-flete", state.fletes, (item) => item.id, (item) => `${item.id} - ${item.codigo_flete}`, { includeEmpty: false, classKey: "flete" });
      fillSelect("cliente-contacto-cliente", state.clientes, (item) => item.id, (item) => `${item.id} - ${item.razon_social}`, { includeEmpty: true, emptyLabel: "Selecciona cliente", classKey: "cliente" });
      fillClienteContactoEditSelect("", null);
      const domBuscar = document.getElementById("cliente-domicilio-buscar");
      fillClienteDomicilioSelect(domBuscar ? domBuscar.value : "", document.getElementById("cliente-domicilio-cliente")?.value ?? null);
      fillSelect("cliente-condicion-cliente", state.clientes, (item) => item.id, (item) => `${item.id} - ${item.razon_social}`, { includeEmpty: true, emptyLabel: "Selecciona cliente", classKey: "cliente" });
      fillSelect("transportista-contacto-transportista", state.transportistas, (item) => item.id, (item) => `${item.id} - ${item.nombre}`, { includeEmpty: false, classKey: "transportista" });
      fillSelect("transportista-documento-transportista", state.transportistas, (item) => item.id, (item) => `${item.id} - ${item.nombre}`, { includeEmpty: false, classKey: "transportista" });
      fillSelect("tarifa-compra-transportista", state.transportistas, (item) => item.id, (item) => `${item.id} - ${item.nombre}`, { includeEmpty: false });
      fillSelect("tarifa-compra-filter-transportista", state.transportistas, (item) => item.id, (item) => `${item.id} - ${item.nombre}`, { includeEmpty: true, emptyLabel: "Todos", classKey: "transportista" });
      fillSelect("edit-tarifa-compra-transportista", state.transportistas, (item) => item.id, (item) => `${item.id} - ${item.nombre}`, { includeEmpty: false });
      fillSelect("operador-transportista", state.transportistas, (item) => item.id, (item) => `${item.id} - ${item.nombre}`, { includeEmpty: true, emptyLabel: "Sin transportista", classKey: "transportista" });
      fillSelect("edit-operador-transportista", state.transportistas, (item) => item.id, (item) => `${item.id} - ${item.nombre}`, { includeEmpty: true, emptyLabel: "Sin transportista", classKey: "transportista" });
      fillSelect("unidad-transportista", state.transportistas, (item) => item.id, (item) => `${item.id} - ${item.nombre}`, { includeEmpty: true, emptyLabel: "Sin transportista", classKey: "transportista" });
      fillSelect("edit-unidad-transportista", state.transportistas, (item) => item.id, (item) => `${item.id} - ${item.nombre}`, { includeEmpty: true, emptyLabel: "Sin transportista", classKey: "transportista" });
      fillSelect("asignacion-filter-operador", state.operadores, (item) => item.id_operador, (item) => `${item.id_operador} - ${item.nombre} ${item.apellido_paterno}`, { includeEmpty: true, emptyLabel: "Todos", classKey: "operador" });
      fillSelect("asignacion-filter-unidad", state.unidades, (item) => item.id_unidad, (item) => `${item.id_unidad} - ${item.economico}`, { includeEmpty: true, emptyLabel: "Todas", classKey: "unidad" });
      fillSelect("asignacion-filter-viaje", state.viajes, (item) => item.id, (item) => `${item.id} - ${item.codigo_viaje}`, { includeEmpty: true, emptyLabel: "Todos", classKey: "viaje" });
      fillSelect("flete-filter-cliente", state.clientes, (item) => item.id, (item) => `${item.id} - ${item.razon_social}`, { includeEmpty: true, emptyLabel: "Todos", classKey: "cliente" });
      fillSelect("flete-filter-transportista", state.transportistas, (item) => item.id, (item) => `${item.id} - ${item.nombre}`, { includeEmpty: true, emptyLabel: "Todos", classKey: "transportista" });
      fillSelect("edit-flete-cliente", state.clientes, (item) => item.id, (item) => `${item.id} - ${item.razon_social}`, { includeEmpty: false, classKey: "cliente" });
      fillSelect("edit-flete-transportista", state.transportistas, (item) => item.id, (item) => `${item.id} - ${item.nombre}`, { includeEmpty: false, classKey: "transportista" });
      fillSelect("edit-flete-viaje", state.viajes, (item) => item.id, (item) => `${item.id} - ${item.codigo_viaje}`, { includeEmpty: true, emptyLabel: "Sin viaje", classKey: "viaje" });

      fillSelect("asignacion-operador", state.operadores, (item) => item.id_operador, (item) => `${item.id_operador} - ${item.nombre} ${item.apellido_paterno}`, { includeEmpty: false, classKey: "operador" });
      fillSelect("asignacion-unidad", state.unidades, (item) => item.id_unidad, (item) => `${item.id_unidad} - ${item.economico}`, { includeEmpty: false, classKey: "unidad" });
      fillSelect("asignacion-viaje", state.viajes, (item) => item.id, (item) => `${item.id} - ${item.codigo_viaje}`, { includeEmpty: false, classKey: "viaje" });
      fillSelect("edit-asignacion-operador", state.operadores, (item) => item.id_operador, (item) => `${item.id_operador} - ${item.nombre} ${item.apellido_paterno}`, { includeEmpty: false, classKey: "operador" });
      fillSelect("edit-asignacion-unidad", state.unidades, (item) => item.id_unidad, (item) => `${item.id_unidad} - ${item.economico}`, { includeEmpty: false, classKey: "unidad" });
      fillSelect("edit-asignacion-viaje", state.viajes, (item) => item.id, (item) => `${item.id} - ${item.codigo_viaje}`, { includeEmpty: false, classKey: "viaje" });

      fillSelect("despacho-asignacion", state.asignaciones, (item) => item.id_asignacion, (item) => {
        const operador = item.operador ? `${item.operador.nombre} ${item.operador.apellido_paterno}` : `Operador ${item.id_operador}`;
        const unidad = item.unidad?.economico || `Unidad ${item.id_unidad}`;
        const viaje = item.viaje?.codigo_viaje || `Viaje ${item.id_viaje}`;
        return `${item.id_asignacion} - ${viaje} / ${operador} / ${unidad}`;
      }, { includeEmpty: false, classKey: "asignacion" });
      fillSelect("despacho-flete", state.fletes, (item) => item.id, (item) => `${item.id} - ${item.codigo_flete}`, { includeEmpty: true, emptyLabel: "Sin flete", classKey: "flete" });
      fillSelect("despacho-filter-asignacion", state.asignaciones, (item) => item.id_asignacion, (item) => {
        const viaje = item.viaje?.codigo_viaje || `Viaje ${item.id_viaje}`;
        return `${item.id_asignacion} - ${viaje}`;
      }, { includeEmpty: true, emptyLabel: "Todas", classKey: "asignacion" });
      fillSelect("despacho-filter-flete", state.fletes, (item) => item.id, (item) => `${item.id} - ${item.codigo_flete}`, { includeEmpty: true, emptyLabel: "Todos", classKey: "flete" });
      fillSelect("edit-despacho-flete", state.fletes, (item) => item.id, (item) => `${item.id} - ${item.codigo_flete}`, { includeEmpty: true, emptyLabel: "Sin flete", classKey: "flete" });

      const despachoLabel = (item) => `${item.id_despacho} - ${item.estatus} - ${item.asignacion?.viaje?.codigo_viaje || "sin viaje"}`;
      fillSelect("orden-servicio-nueva-cliente", state.clientes, (item) => item.id, (item) => `${item.id} - ${item.razon_social}`, { includeEmpty: false, classKey: "cliente" });
      fillSelect("orden-servicio-nueva-flete", state.fletes, (item) => item.id, (item) => `${item.id} - ${item.codigo_flete}`, { includeEmpty: true, emptyLabel: "Sin flete", classKey: "flete" });
      fillSelect("orden-servicio-nueva-viaje", state.viajes, (item) => item.id, (item) => `${item.id} - ${item.codigo_viaje}`, { includeEmpty: true, emptyLabel: "Sin viaje", classKey: "viaje" });
      fillSelect("orden-servicio-nueva-despacho", state.despachos, (item) => item.id_despacho, despachoLabel, { includeEmpty: true, emptyLabel: "Sin despacho", classKey: "despacho" });
      fillSelect("orden-servicio-edit-flete", state.fletes, (item) => item.id, (item) => `${item.id} - ${item.codigo_flete}`, { includeEmpty: true, emptyLabel: "Sin cambiar", classKey: "flete" });
      fillSelect("orden-servicio-edit-viaje", state.viajes, (item) => item.id, (item) => `${item.id} - ${item.codigo_viaje}`, { includeEmpty: true, emptyLabel: "Sin cambiar", classKey: "viaje" });
      fillSelect("orden-servicio-edit-despacho", state.despachos, (item) => item.id_despacho, despachoLabel, { includeEmpty: true, emptyLabel: "Sin cambiar", classKey: "despacho" });
      addOrdenServicioVinculoClearOption("orden-servicio-edit-flete");
      addOrdenServicioVinculoClearOption("orden-servicio-edit-viaje");
      addOrdenServicioVinculoClearOption("orden-servicio-edit-despacho");
      fillSelect("salida-despacho", state.despachos, (item) => item.id_despacho, despachoLabel, { includeEmpty: false, classKey: "despacho" });
      fillSelect("evento-despacho", state.despachos, (item) => item.id_despacho, despachoLabel, { includeEmpty: false, classKey: "despacho" });
      fillSelect("entrega-despacho", state.despachos, (item) => item.id_despacho, despachoLabel, { includeEmpty: false, classKey: "despacho" });
      fillSelect("cierre-despacho", state.despachos, (item) => item.id_despacho, despachoLabel, { includeEmpty: false, classKey: "despacho" });
      fillSelect("cancelacion-despacho", state.despachos, (item) => item.id_despacho, despachoLabel, { includeEmpty: false, classKey: "despacho" });

      const elFacturaCliente = document.getElementById("factura-cliente");
      if (elFacturaCliente && elFacturaCliente.value) {
        fillFacturaFleteSelectFiltered(elFacturaCliente.value);
      }

      if (!window.__tarifaCompraTipoSyncBound) {
        window.__tarifaCompraTipoSyncBound = true;
        document.addEventListener("change", (e) => {
          if (e.target.id !== "tarifa-compra-transportista" && e.target.id !== "edit-tarifa-compra-transportista") {
            return;
          }
          const t = state.transportistas.find((x) => String(x.id) === String(e.target.value));
          if (!t || !t.tipo_transportista) {
            return;
          }
          if (e.target.id === "tarifa-compra-transportista") {
            const tipoEl = document.getElementById("tarifa-compra-tipo-transportista");
            if (tipoEl) {
              tipoEl.value = t.tipo_transportista;
            }
          } else {
            const tipoEdit = document.getElementById("edit-tarifa-compra-tipo-transportista");
            if (tipoEdit) {
              tipoEdit.value = t.tipo_transportista;
            }
          }
        });
      }
    }

    function unidadesEndpointFailed() {
      return (state.catalogRefreshErrors || []).some((e) => String(e).startsWith("Unidades:"));
    }

    function updateCatalogRefreshBanner() {
      const el = document.getElementById("catalog-refresh-banner");
      if (!el) {
        return;
      }
      const errs = state.catalogRefreshErrors || [];
      if (errs.length === 0) {
        el.innerHTML = "";
        el.hidden = true;
        return;
      }
      const li = errs.map((e) => `<li>${escapeHtml(e)}</li>`).join("");
      el.hidden = false;
      el.innerHTML =
        "<strong>Carga parcial del catalogo</strong>Algunos listados no se pudieron cargar; el resto del panel puede mostrarse con normalidad. Revise la API key en <code>.env</code>, que Uvicorn este en marcha y que MySQL acepte conexiones. Reintente con F5 o con <strong>Recargar catalogo</strong> en el modulo afectado." +
        `<ul>${li}</ul>`;
    }

    async function refreshData() {
      const pickItems = (res) => (Array.isArray(res?.items) ? res.items : []);

      const catalogFetches = [
        { label: "Clientes", stateKey: "clientes", path: "/clientes?limit=500" },
        { label: "Transportistas", stateKey: "transportistas", path: "/transportistas?limit=500" },
        { label: "Viajes", stateKey: "viajes", path: "/viajes?limit=500" },
        { label: "Fletes", stateKey: "fletes", path: "/fletes?limit=500" },
        { label: "Facturas", stateKey: "facturas", path: "/facturas?limit=500" },
        { label: "Gastos viaje", stateKey: "gastos", path: "/gastos-viaje?limit=500" },
        { label: "Tarifas venta", stateKey: "tarifas", path: "/tarifas-flete?limit=500" },
        { label: "Tarifas compra", stateKey: "tarifasCompra", path: "/tarifas-compra-transportista?limit=500" },
        { label: "Operadores", stateKey: "operadores", path: "/operadores?limit=500" },
        { label: "Unidades", stateKey: "unidades", path: "/unidades?limit=500" },
        { label: "Asignaciones", stateKey: "asignaciones", path: "/asignaciones?limit=500" },
        { label: "Despachos", stateKey: "despachos", path: "/despachos?limit=500" },
        { label: "Ordenes servicio", stateKey: "ordenesServicio", path: "/ordenes-servicio?limit=500" },
      ];

      state.catalogRefreshErrors = [];
      const settled = await Promise.allSettled(catalogFetches.map((f) => api(f.path)));

      settled.forEach((result, i) => {
        const f = catalogFetches[i];
        if (result.status === "fulfilled") {
          const val = result.value;
          if (f.stateKey === "unidades") {
            state.unidades = pickItems(val);
            state.unidadesTotalServidor =
              typeof val?.total === "number" ? val.total : state.unidades.length;
          } else {
            state[f.stateKey] = pickItems(val);
          }
        } else {
          const msg =
            result.reason && result.reason.message ? result.reason.message : String(result.reason);
          state.catalogRefreshErrors.push(`${f.label}: ${msg}`);
        }
      });

      state.catalogLoaded = true;
      updateCatalogRefreshBanner();

      renderStats();
      renderClientes();
      renderTransportistas();
      renderTransportistaContactos();
      renderTransportistaDocumentos();
      renderViajes();
      renderFletes();
      renderOrdenesServicio();
      renderFacturas();
      renderGastos();
      renderTarifas();
      renderTarifasCompra();
      renderOperadores();
      renderUnidades();
      renderAsignaciones();
      renderDespachos();
      populateSelects();
      refreshAllBusquedaDatalists();
      renderClienteContactos();
      flushClienteDomiciliosForSelectedClient(document.getElementById("cliente-domicilio-cliente")?.value || "");
      syncClienteCondicionForm();
      resyncFleteEditPkAfterRefresh();
      resyncDespachoEditPkAfterRefresh();
    }

    function createdEntitySuffix(data) {
      if (!data || typeof data !== "object") {
        return "";
      }
      const parts = [];
      if (data.id != null) {
        parts.push("ID " + data.id);
      }
      if (data.id_unidad != null) {
        parts.push("ID unidad " + data.id_unidad);
      }
      if (data.id_operador != null) {
        parts.push("ID operador " + data.id_operador);
      }
      if (data.id_asignacion != null) {
        parts.push("ID asignacion " + data.id_asignacion);
      }
      if (data.id_despacho != null) {
        parts.push("ID despacho " + data.id_despacho);
      }
      if (data.folio != null) {
        parts.push("folio " + data.folio);
      }
      if (parts.length === 0) {
        return "";
      }
      return " — " + parts.join(", ") + ".";
    }

    function attachSubmit(formId, messageId, builder, requestFactory, successText) {
      document.getElementById(formId).addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage(messageId);
        const form = event.currentTarget;
        try {
          const payload = builder(new FormData(form));
          const data = await requestFactory(payload);
          form.reset();
          applyMoneyFormatToForm(form);
          setMessage(messageId, successText + createdEntitySuffix(data), "ok");
          await refreshData();
        } catch (error) {
          setMessage(messageId, error.message, "error");
        }
      });
    }

    function initForms() {
      enableEnterToNextField("cliente-form");
      enableEnterToNextField("cliente-edit-form");
      wireClienteContactoEnterNavigation();
      enableEnterToNextField("cliente-contacto-edit-form");
      enableEnterToNextField("cliente-domicilio-form");
      enableEnterToNextField("cliente-domicilio-edit-form");
      enableEnterToNextField("transportista-form");
      enableEnterToNextField("transportista-edit-form");
      enableEnterToNextField("tarifa-form");
      enableEnterToNextField("tarifa-edit-form");
      enableEnterToNextField("tarifa-compra-form");
      enableEnterToNextField("tarifa-compra-edit-form");
      wireImplicitSubmitGuard("tarifa-form");
      wireImplicitSubmitGuard("tarifa-edit-form");
      wireImplicitSubmitGuard("tarifa-compra-form");
      wireImplicitSubmitGuard("tarifa-compra-edit-form");
      enableEnterToNextField("cliente-condicion-form");
      wireImplicitSubmitGuard("cliente-condicion-form");
      enableEnterToNextField("viaje-form");
      wireImplicitSubmitGuard("viaje-form");
      enableEnterToNextField("factura-form");
      wireImplicitSubmitGuard("factura-form");
      enableEnterToNextField("flete-form");
      wireImplicitSubmitGuard("flete-form");
      wireImplicitSubmitGuard("flete-edit-form");
      enableEnterToNextField("gasto-form");
      wireImplicitSubmitGuard("gasto-form");
      enableEnterToNextField("gasto-edit-form");
      wireImplicitSubmitGuard("gasto-edit-form");
      enableEnterToNextField("transportista-contacto-form");
      wireImplicitSubmitGuard("transportista-contacto-form");
      enableEnterToNextField("transportista-documento-form");
      wireImplicitSubmitGuard("transportista-documento-form");
      enableEnterToNextField("transportista-documento-edit-form");
      wireImplicitSubmitGuard("transportista-documento-edit-form");
      enableEnterToNextField("operador-form");
      wireImplicitSubmitGuard("operador-form");
      enableEnterToNextField("operador-edit-form");
      wireImplicitSubmitGuard("operador-edit-form");
      enableEnterToNextField("unidad-form");
      wireImplicitSubmitGuard("unidad-form");
      enableEnterToNextField("unidad-edit-form");
      wireImplicitSubmitGuard("unidad-edit-form");
      enableEnterToNextField("asignacion-form");
      wireImplicitSubmitGuard("asignacion-form");
      enableEnterToNextField("despacho-form");
      wireImplicitSubmitGuard("despacho-form");
      enableEnterToNextField("orden-servicio-desde-cotizacion-form");
      wireImplicitSubmitGuard("orden-servicio-desde-cotizacion-form");
      enableEnterToNextField("orden-servicio-nueva-form");
      wireImplicitSubmitGuard("orden-servicio-nueva-form");
      enableEnterToNextField("orden-servicio-estatus-form");
      wireImplicitSubmitGuard("orden-servicio-estatus-form");
      enableEnterToNextField("orden-servicio-datos-form");
      wireImplicitSubmitGuard("orden-servicio-datos-form");
      enableEnterToNextField("orden-servicio-vinculos-form");
      wireImplicitSubmitGuard("orden-servicio-vinculos-form");
      enableEnterToNextField("salida-form");
      wireImplicitSubmitGuard("salida-form");
      enableEnterToNextField("evento-form");
      wireImplicitSubmitGuard("evento-form");
      enableEnterToNextField("entrega-form");
      wireImplicitSubmitGuard("entrega-form");
      enableEnterToNextField("cierre-form");
      wireImplicitSubmitGuard("cierre-form");
      enableEnterToNextField("cancelacion-form");
      wireImplicitSubmitGuard("cancelacion-form");
      wireImplicitSubmitGuard("cliente-form");
      wireImplicitSubmitGuard("cliente-edit-form");
      wireImplicitSubmitGuard("transportista-form");
      attachSubmit("cliente-form", "cliente-message", (form) => buildClientePayload(form), (payload) => api("/clientes", { method: "POST", body: JSON.stringify(payload) }), "Cliente guardado.");

      document.getElementById("cliente-contacto-cancel-clear").addEventListener("click", () => {
        cancelClienteContactoEdit();
        clearCaptureFormFields("cliente-contacto-form");
        document.getElementById("cliente-contacto-activo").checked = true;
        clearMessage("cliente-contacto-message");
        syncClienteModuleSummaries();
        renderClienteContactos();
      });
      document.getElementById("cliente-contacto-guardar").addEventListener("click", async () => {
        clearMessage("cliente-contacto-message");
        if (!validateClienteContactoCapture()) {
          return;
        }
        try {
          const payload = buildClienteContactoPayload(clienteContactoCaptureToFormData());
          const created = await api(`/clientes/${payload.cliente_id}/contactos`, {
            method: "POST",
            body: JSON.stringify({
              nombre: payload.nombre,
              area: payload.area,
              puesto: payload.puesto,
              telefono: payload.telefono,
              extension: payload.extension,
              celular: payload.celular,
              email: payload.email,
              principal: payload.principal,
              activo: payload.activo,
            }),
          });
          const selected = String(payload.cliente_id);
          clearCaptureFormFields("cliente-contacto-form");
          document.getElementById("cliente-contacto-activo").checked = true;
          setMessage(
            "cliente-contacto-message",
            "Contacto guardado." + createdEntitySuffix(created),
            "ok",
          );
          await refreshData();
          document.getElementById("cliente-contacto-cliente").value = selected;
          cancelClienteContactoEdit();
          renderClienteContactos();
        } catch (error) {
          setMessage("cliente-contacto-message", error.message, "error");
        }
      });

      document.getElementById("cliente-domicilio-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("cliente-domicilio-message");
        const form = event.currentTarget;
        try {
          const payload = buildClienteDomicilioPayload(new FormData(form));
          const createdDom = await api(`/clientes/${payload.cliente_id}/domicilios`, {
            method: "POST",
            body: JSON.stringify({
              tipo_domicilio: payload.tipo_domicilio,
              nombre_sede: payload.nombre_sede,
              direccion_completa: payload.direccion_completa,
              municipio: payload.municipio,
              estado: payload.estado,
              codigo_postal: payload.codigo_postal,
              horario_carga: payload.horario_carga,
              horario_descarga: payload.horario_descarga,
              instrucciones_acceso: payload.instrucciones_acceso,
              activo: payload.activo,
            }),
          });
          const selected = String(payload.cliente_id);
          form.reset();
          setMessage("cliente-domicilio-message", "Domicilio guardado." + createdEntitySuffix(createdDom), "ok");
          await refreshData();
          document.getElementById("cliente-domicilio-cliente").value = selected;
          flushClienteDomiciliosForSelectedClient(selected);
        } catch (error) {
          setMessage("cliente-domicilio-message", error.message, "error");
        }
      });

      attachSubmit("cliente-condicion-form", "cliente-condicion-message", (form) => ({
        cliente_id: integerOrNull(form.get("cliente_id")),
        dias_credito: integerOrNull(form.get("dias_credito")),
        limite_credito: numberOrNull(form.get("limite_credito")),
        moneda_preferida: clean(form.get("moneda_preferida")) || "MXN",
        forma_pago: clean(form.get("forma_pago")),
        uso_cfdi: clean(form.get("uso_cfdi")),
        requiere_oc: form.get("requiere_oc") === "on",
        requiere_cita: form.get("requiere_cita") === "on",
        bloqueado_credito: form.get("bloqueado_credito") === "on",
        observaciones_credito: clean(form.get("observaciones_credito")),
      }), async (payload) => {
        if (payload.cliente_id === null || payload.cliente_id < 1) {
          throw new Error("Selecciona un cliente en la lista antes de guardar condiciones comerciales.");
        }
        return api(`/clientes/${payload.cliente_id}/condiciones-comerciales`, {
          method: "PUT",
          body: JSON.stringify({
            dias_credito: payload.dias_credito,
            limite_credito: payload.limite_credito,
            moneda_preferida: payload.moneda_preferida,
            forma_pago: payload.forma_pago,
            uso_cfdi: payload.uso_cfdi,
            requiere_oc: payload.requiere_oc,
            requiere_cita: payload.requiere_cita,
            bloqueado_credito: payload.bloqueado_credito,
            observaciones_credito: payload.observaciones_credito,
          }),
        });
      }, "Condiciones comerciales guardadas.");

      attachSubmit("transportista-form", "transportista-message", (form) => buildTransportistaPayload(form), (payload) => api("/transportistas", { method: "POST", body: JSON.stringify(payload) }), "Transportista guardado.");

      document.getElementById("transportista-contacto-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("transportista-contacto-message");
        const form = event.currentTarget;
        try {
          const payload = buildTransportistaContactoPayload(new FormData(form));
          const createdTc = await api(`/transportistas/${payload.transportista_id}/contactos`, {
            method: "POST",
            body: JSON.stringify({
              nombre: payload.nombre,
              area: payload.area,
              puesto: payload.puesto,
              telefono: payload.telefono,
              extension: payload.extension,
              celular: payload.celular,
              email: payload.email,
              principal: payload.principal,
              activo: payload.activo,
            }),
          });
          const selected = String(payload.transportista_id);
          form.reset();
          setMessage("transportista-contacto-message", "Contacto guardado." + createdEntitySuffix(createdTc), "ok");
          await refreshData();
          document.getElementById("transportista-contacto-transportista").value = selected;
          syncTransportistaModuleSelection("transportista-contacto-transportista");
        } catch (error) {
          setMessage("transportista-contacto-message", error.message, "error");
        }
      });

      document.getElementById("transportista-documento-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("transportista-documento-message");
        const form = event.currentTarget;
        try {
          const payload = buildTransportistaDocumentoPayload(new FormData(form));
          const createdTd = await api(`/transportistas/${payload.transportista_id}/documentos`, {
            method: "POST",
            body: JSON.stringify({
              tipo_documento: payload.tipo_documento,
              numero_documento: payload.numero_documento,
              fecha_emision: payload.fecha_emision,
              fecha_vencimiento: payload.fecha_vencimiento,
              archivo_url: payload.archivo_url,
              estatus: payload.estatus,
              observaciones: payload.observaciones,
            }),
          });
          const selected = String(payload.transportista_id);
          form.reset();
          setMessage("transportista-documento-message", "Documento guardado." + createdEntitySuffix(createdTd), "ok");
          await refreshData();
          document.getElementById("transportista-documento-transportista").value = selected;
          syncTransportistaModuleSelection("transportista-documento-transportista");
        } catch (error) {
          setMessage("transportista-documento-message", error.message, "error");
        }
      });

      attachSubmit("viaje-form", "viaje-message", (form) => ({
        ...buildViajePayload(form),
        fecha_llegada_real: null,
      }), (payload) => api("/viajes", { method: "POST", body: JSON.stringify(payload) }), "Viaje guardado.");

      attachSubmit("factura-form", "factura-message", (form) => buildFacturaPayload(form), (payload) => api("/facturas", { method: "POST", body: JSON.stringify(payload) }), "Factura guardada.");

      attachSubmit("flete-form", "flete-message", (form) => buildFletePayload(form), (payload) => api("/fletes", { method: "POST", body: JSON.stringify(payload) }), "Flete guardado.");

      attachSubmit("gasto-form", "gasto-message", (form) => ({
        flete_id: integerOrNull(form.get("flete_id")),
        tipo_gasto: clean(form.get("tipo_gasto")),
        monto: numberOrNull(form.get("monto")),
        fecha_gasto: normalizeDateOnlyForApi(form.get("fecha_gasto")),
        descripcion: clean(form.get("descripcion")),
        referencia: clean(form.get("referencia")),
        comprobante: clean(form.get("comprobante")),
      }), (payload) => api("/gastos-viaje", { method: "POST", body: JSON.stringify(payload) }), "Gasto guardado.");

      document.getElementById("gasto-presupuesto-generar").addEventListener("click", async () => {
        const out = document.getElementById("gasto-control-output");
        const fid = document.getElementById("gasto-control-flete").value;
        if (!fid) {
          out.textContent = "Seleccione un flete.";
          return;
        }
        out.textContent = "Generando…";
        try {
          const data = await api(`/fletes/${fid}/presupuesto-gasto/generar`, {
            method: "POST",
            body: JSON.stringify({}),
          });
          out.textContent = JSON.stringify(data, null, 2);
          await refreshData();
        } catch (error) {
          out.textContent = error.message;
        }
      });
      document.getElementById("gasto-liquidacion-ver").addEventListener("click", async () => {
        const out = document.getElementById("gasto-control-output");
        const fid = document.getElementById("gasto-control-flete").value;
        if (!fid) {
          out.textContent = "Seleccione un flete.";
          return;
        }
        out.textContent = "Cargando…";
        try {
          const data = await api(`/fletes/${fid}/liquidacion-gastos`);
          out.textContent = JSON.stringify(data, null, 2);
        } catch (error) {
          out.textContent = error.message;
        }
      });

      document.getElementById("gasto-edit-cancel").addEventListener("click", cancelGastoEdit);
      document.getElementById("gasto-edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("gasto-edit-message");
        const formElement = event.currentTarget;
        try {
          const payload = {
            flete_id: integerOrNull(formElement.elements.flete_id.value),
            tipo_gasto: clean(formElement.elements.tipo_gasto.value),
            monto: numberOrNull(formElement.elements.monto.value),
            fecha_gasto: normalizeDateOnlyForApi(formElement.elements.fecha_gasto.value),
            descripcion: clean(formElement.elements.descripcion.value),
            referencia: clean(formElement.elements.referencia.value),
            comprobante: clean(formElement.elements.comprobante.value),
          };
          const id = requirePositiveIntOrThrow(formElement.elements.id.value, "Gasto");
          await api(`/gastos-viaje/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
          setMessage("gasto-edit-message", "Gasto actualizado.", "ok");
          cancelGastoEdit();
          await refreshData();
        } catch (error) {
          setMessage("gasto-edit-message", error.message, "error");
        }
      });

      attachSubmit(
        "tarifa-form",
        "tarifa-message",
        (form) => {
          const nombre = clean(new FormData(form).get("nombre_tarifa"));
          if (findActiveTarifaVentaNombreDuplicado(nombre, null)) {
            throw new Error(TARIFA_VENTA_NOMBRE_DUPLICADO_MSG);
          }
          return buildTarifaFleteVentaPayload(form);
        },
        (payload) => api("/tarifas-flete", { method: "POST", body: JSON.stringify(payload) }),
        "Tarifa guardada."
      );

      document.getElementById("tarifa-edit-cancel").addEventListener("click", cancelTarifaFleteEdit);
      document.getElementById("tarifa-edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("tarifa-edit-message");
        const formElement = event.currentTarget;
        try {
          const id = requirePositiveIntOrThrow(formElement.elements.id.value, "Tarifa de venta");
          const nombre = clean(formElement.elements.nombre_tarifa.value);
          if (findActiveTarifaVentaNombreDuplicado(nombre, id)) {
            throw new Error(TARIFA_VENTA_NOMBRE_DUPLICADO_MSG);
          }
          const payload = buildTarifaFleteVentaPayload(new FormData(formElement));
          await api(`/tarifas-flete/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
          setMessage("tarifa-edit-message", "Tarifa actualizada.", "ok");
          cancelTarifaFleteEdit();
          await refreshData();
        } catch (error) {
          setMessage("tarifa-edit-message", error.message, "error");
        }
      });

      attachSubmit("tarifa-compra-form", "tarifa-compra-message", (form) => buildTarifaCompraPayload(form), (payload) => api("/tarifas-compra-transportista", { method: "POST", body: JSON.stringify(payload) }), "Tarifa de compra guardada.");

      attachSubmit(
        "operador-form",
        "operador-message",
        (form) => buildOperadorPayload(form),
        (payload) => api("/operadores", { method: "POST", body: JSON.stringify(payload) }),
        "Operador guardado.",
      );

      document.getElementById("operador-edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("operador-edit-message");
        const form = event.currentTarget;
        try {
          const id = requirePositiveIntOrThrow(form.elements.id_operador.value, "Operador");
          const payload = buildOperadorPayload(new FormData(form));
          await api(`/operadores/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
          setMessage("operador-edit-message", "Operador actualizado.", "ok");
          cancelOperadorEdit();
          await refreshData();
        } catch (error) {
          setMessage("operador-edit-message", error.message, "error");
        }
      });
      document.getElementById("operador-edit-cancel").addEventListener("click", cancelOperadorEdit);

      attachSubmit(
        "unidad-form",
        "unidad-message",
        (formData) => buildUnidadPayload(formData),
        (payload) => api("/unidades", { method: "POST", body: JSON.stringify(payload) }),
        "Unidad guardada.",
      );

      document.getElementById("unidad-edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("unidad-edit-message");
        const form = event.currentTarget;
        try {
          const id = requirePositiveIntOrThrow(form.elements.id_unidad.value, "Unidad");
          const payload = buildUnidadPayload(new FormData(form));
          await api(`/unidades/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
          setMessage("unidad-edit-message", "Unidad actualizada.", "ok");
          cancelUnidadEdit();
          await refreshData();
        } catch (error) {
          setMessage("unidad-edit-message", error.message, "error");
        }
      });
      document.getElementById("unidad-edit-cancel").addEventListener("click", cancelUnidadEdit);

      attachSubmit("asignacion-form", "asignacion-message", (form) => buildAsignacionPayload(form), (payload) => api("/asignaciones", { method: "POST", body: JSON.stringify(payload) }), "Asignacion guardada.");

      attachSubmit("despacho-form", "despacho-message", (form) => ({
        id_asignacion: integerOrNull(form.get("id_asignacion")),
        id_flete: integerOrNull(form.get("id_flete")),
        salida_programada: normalizeDateTimeForApi(form.get("salida_programada")),
        observaciones_transito: clean(form.get("observaciones_transito")),
      }), (payload) => api("/despachos", { method: "POST", body: JSON.stringify(payload) }), "Despacho guardado.");

      attachSubmit(
        "orden-servicio-desde-cotizacion-form",
        "orden-servicio-desde-cot-msg",
        (form) => buildOrdenServicioDesdeCotizacionPayload(form),
        (payload) => api("/ordenes-servicio/desde-cotizacion", { method: "POST", body: JSON.stringify(payload) }),
        "Orden generada desde cotizacion.",
      );
      attachSubmit(
        "orden-servicio-nueva-form",
        "orden-servicio-nueva-msg",
        (form) => buildOrdenServicioNuevaPayload(form),
        (payload) => api("/ordenes-servicio", { method: "POST", body: JSON.stringify(payload) }),
        "Orden creada en borrador.",
      );

      const osEstatusForm = document.getElementById("orden-servicio-estatus-form");
      if (osEstatusForm) {
        osEstatusForm.addEventListener("submit", async (event) => {
          event.preventDefault();
          clearMessage("orden-servicio-estatus-msg");
          const hid = document.getElementById("orden-servicio-detail-id");
          const id = hid && hid.value ? integerOrNull(hid.value) : null;
          if (id === null || id < 1) {
            setMessage("orden-servicio-estatus-msg", "No hay orden seleccionada.", "error");
            return;
          }
          const fd = new FormData(osEstatusForm);
          const estatus = clean(fd.get("estatus"));
          if (!estatus) {
            setMessage("orden-servicio-estatus-msg", "Seleccione un estatus.", "error");
            return;
          }
          try {
            await api(`/ordenes-servicio/${id}/estatus`, {
              method: "POST",
              body: JSON.stringify({ estatus, observaciones: clean(fd.get("observaciones")) }),
            });
            setMessage("orden-servicio-estatus-msg", "Estatus actualizado.", "ok");
            const noteEl = osEstatusForm.querySelector('[name="observaciones"]');
            if (noteEl) {
              noteEl.value = "";
            }
            await refreshData();
            refreshOrdenServicioDetailIfOpen(id);
          } catch (error) {
            setMessage("orden-servicio-estatus-msg", error.message, "error");
          }
        });
      }

      const osDatosForm = document.getElementById("orden-servicio-datos-form");
      if (osDatosForm) {
        osDatosForm.addEventListener("submit", async (event) => {
          event.preventDefault();
          clearMessage("orden-servicio-datos-msg");
          const hid = document.getElementById("orden-servicio-detail-id");
          const id = hid && hid.value ? integerOrNull(hid.value) : null;
          if (id === null || id < 1) {
            setMessage("orden-servicio-datos-msg", "No hay orden seleccionada.", "error");
            return;
          }
          try {
            const fd = new FormData(osDatosForm);
            const payload = buildOrdenServicioDatosPayload(fd);
            await api(`/ordenes-servicio/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
            setMessage("orden-servicio-datos-msg", "Datos guardados.", "ok");
            await refreshData();
            refreshOrdenServicioDetailIfOpen(id);
          } catch (error) {
            setMessage("orden-servicio-datos-msg", error.message, "error");
          }
        });
      }

      const osVinculosForm = document.getElementById("orden-servicio-vinculos-form");
      if (osVinculosForm) {
        osVinculosForm.addEventListener("submit", async (event) => {
          event.preventDefault();
          clearMessage("orden-servicio-vinculos-msg");
          const hid = document.getElementById("orden-servicio-detail-id");
          const id = hid && hid.value ? integerOrNull(hid.value) : null;
          if (id === null || id < 1) {
            setMessage("orden-servicio-vinculos-msg", "No hay orden seleccionada.", "error");
            return;
          }
          const fd = new FormData(osVinculosForm);
          const payload = {};
          const parseVin = (field) => {
            const raw = fd.get(field);
            if (raw != null && String(raw) === "__clear__") {
              return { kind: "clear" };
            }
            const id = integerOrNull(raw);
            if (id != null) {
              return { kind: "set", id };
            }
            return { kind: "omit" };
          };
          const pf = parseVin("flete_id");
          if (pf.kind === "clear") {
            payload.flete_id = null;
          } else if (pf.kind === "set") {
            payload.flete_id = pf.id;
          }
          const pv = parseVin("viaje_id");
          if (pv.kind === "clear") {
            payload.viaje_id = null;
          } else if (pv.kind === "set") {
            payload.viaje_id = pv.id;
          }
          const pd = parseVin("despacho_id");
          if (pd.kind === "clear") {
            payload.despacho_id = null;
          } else if (pd.kind === "set") {
            payload.despacho_id = pd.id;
          }
          if (Object.keys(payload).length === 0) {
            setMessage("orden-servicio-vinculos-msg", "Seleccione al menos un vinculo a actualizar.", "error");
            return;
          }
          try {
            await api(`/ordenes-servicio/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
            setMessage("orden-servicio-vinculos-msg", "Vinculos actualizados.", "ok");
            await refreshData();
            refreshOrdenServicioDetailIfOpen(id);
          } catch (error) {
            setMessage("orden-servicio-vinculos-msg", error.message, "error");
          }
        });
      }

      document.getElementById("salida-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("salida-message");
        const form = event.currentTarget;
        try {
          const fd = new FormData(form);
          const payload = {
            id_despacho: integerOrNull(fd.get("id_despacho")),
            salida_real: normalizeDateTimeForApi(fd.get("salida_real")),
            km_salida: numberOrNull(fd.get("km_salida")),
            observaciones_salida: clean(fd.get("observaciones_salida")),
          };
          const omitir = fd.get("omitir_validacion_cumplimiento") === "on";
          const q = omitir ? "?omitir_validacion_cumplimiento=true" : "";
          const response = await fetch(`${API_BASE}/despachos/${payload.id_despacho}/salida${q}`, {
            method: "POST",
            headers: {
              "Accept": "application/json",
              "Content-Type": "application/json",
              ...getAuthHeaders(),
            },
            body: JSON.stringify({
              salida_real: payload.salida_real,
              km_salida: payload.km_salida,
              observaciones_salida: payload.observaciones_salida,
            }),
          });
          const data = await response.json().catch(() => ({}));
          if (!response.ok) {
            if (response.status === 422 && data.detail && data.detail.tipo === "cumplimiento_documental") {
              const bloqueos = (data.detail.bloqueos || []).join("\\n• ");
              const adv = (data.detail.advertencias || []).length
                ? "\\n\\nAdvertencias:\\n• " + (data.detail.advertencias || []).join("\\n• ")
                : "";
              setMessage(
                "salida-message",
                (data.detail.mensaje || "La validación documental no autoriza la salida.") +
                  (bloqueos ? "\\n\\nPendientes:\\n• " + bloqueos : "") +
                  adv +
                  "\\n\\nSi debe salir igual, marque la casilla de confirmación abajo y vuelva a guardar.",
                "error"
              );
              return;
            }
            let detail = `HTTP ${response.status}`;
            if (typeof data.detail === "string") {
              detail = data.detail;
            } else if (data.detail) {
              detail = JSON.stringify(data.detail);
            }
            throw new Error(detail);
          }
          form.reset();
          setMessage("salida-message", "Salida registrada.", "ok");
          await refreshData();
        } catch (error) {
          setMessage("salida-message", error.message, "error");
        }
      });

      attachSubmit("evento-form", "evento-message", (form) => ({
        id_despacho: integerOrNull(form.get("id_despacho")),
        tipo_evento: clean(form.get("tipo_evento")),
        fecha_evento: normalizeDateTimeForApi(form.get("fecha_evento")),
        ubicacion: clean(form.get("ubicacion")),
        descripcion: clean(form.get("descripcion")),
        latitud: numberOrNull(form.get("latitud")),
        longitud: numberOrNull(form.get("longitud")),
      }), (payload) => api(`/despachos/${payload.id_despacho}/eventos`, {
        method: "POST",
        body: JSON.stringify({
          tipo_evento: payload.tipo_evento,
          fecha_evento: payload.fecha_evento,
          ubicacion: payload.ubicacion,
          descripcion: payload.descripcion,
          latitud: payload.latitud,
          longitud: payload.longitud,
        }),
      }), "Evento guardado.");

      attachSubmit("entrega-form", "entrega-message", (form) => ({
        id_despacho: integerOrNull(form.get("id_despacho")),
        fecha_entrega: normalizeDateTimeForApi(form.get("fecha_entrega")),
        evidencia_entrega: clean(form.get("evidencia_entrega")),
        firma_recibe: clean(form.get("firma_recibe")),
        observaciones_entrega: clean(form.get("observaciones_entrega")),
      }), (payload) => api(`/despachos/${payload.id_despacho}/entrega`, {
        method: "POST",
        body: JSON.stringify({
          fecha_entrega: payload.fecha_entrega,
          evidencia_entrega: payload.evidencia_entrega,
          firma_recibe: payload.firma_recibe,
          observaciones_entrega: payload.observaciones_entrega,
        }),
      }), "Entrega registrada.");

      attachSubmit("cierre-form", "cierre-message", (form) => ({
        id_despacho: integerOrNull(form.get("id_despacho")),
        llegada_real: normalizeDateTimeForApi(form.get("llegada_real")),
        km_llegada: numberOrNull(form.get("km_llegada")),
        observaciones_cierre: clean(form.get("observaciones_cierre")),
      }), (payload) => api(`/despachos/${payload.id_despacho}/cerrar`, {
        method: "POST",
        body: JSON.stringify({
          llegada_real: payload.llegada_real,
          km_llegada: payload.km_llegada,
          observaciones_cierre: payload.observaciones_cierre,
        }),
      }), "Despacho cerrado.");

      attachSubmit("cancelacion-form", "cancelacion-message", (form) => ({
        id_despacho: integerOrNull(form.get("id_despacho")),
        motivo_cancelacion: clean(form.get("motivo_cancelacion")),
      }), (payload) => api(`/despachos/${payload.id_despacho}/cancelar`, {
        method: "POST",
        body: JSON.stringify({
          motivo_cancelacion: payload.motivo_cancelacion,
        }),
      }), "Despacho cancelado.");
    }

    function initFilters() {
      try {
        const m = sessionStorage.getItem("SIFE_buscar_modo");
        if (m === "contiene" || m === "prefijo_palabras" || m === "todas_palabras") {
          uiState.buscarModo = m;
        }
      } catch (_) {
        /* ignore */
      }
      document.querySelectorAll(".buscar-modo-sync").forEach((el) => {
        el.value = uiState.buscarModo;
      });
      document.addEventListener("change", (e) => {
        const t = e.target;
        if (!t || !t.classList.contains("buscar-modo-sync")) {
          return;
        }
        uiState.buscarModo = t.value;
        try {
          sessionStorage.setItem("SIFE_buscar_modo", t.value);
        } catch (_) {
          /* ignore */
        }
        document.querySelectorAll(".buscar-modo-sync").forEach((x) => {
          if (x !== t) {
            x.value = t.value;
          }
        });
        refreshAllConsultaTables();
      });

      const applyClienteFilter = () => {
        const formNode = document.getElementById("cliente-filter-form");
        const form = new FormData(formNode);
        uiState.clienteFilters.buscar = clean(form.get("buscar")) || "";
        uiState.clienteFilters.activo = clean(form.get("activo")) || "";
        renderClientes();
        refreshBusquedaDatalist("cliente-filter-buscar");
        openSingleClienteFromFilter();
      };

      document.getElementById("cliente-filter-form").addEventListener("submit", (event) => {
        event.preventDefault();
        applyClienteFilter();
      });
      document.getElementById("cliente-filter-buscar").addEventListener("input", () => {
        applyClienteFilter();
      });
      document.getElementById("cliente-filter-activo").addEventListener("change", () => {
        applyClienteFilter();
      });
      document.getElementById("cliente-filter-clear").addEventListener("click", () => {
        document.getElementById("cliente-filter-form").reset();
        uiState.clienteFilters = { buscar: "", activo: "" };
        renderClientes();
        cancelClienteEdit();
      });

      const applyFleteFilter = () => {
        const formNode = document.getElementById("flete-filter-form");
        const form = new FormData(formNode);
        uiState.fleteFilters.buscar = clean(form.get("buscar")) || "";
        uiState.fleteFilters.estado = clean(form.get("estado")) || "";
        uiState.fleteFilters.cliente_id = clean(form.get("cliente_id")) || "";
        uiState.fleteFilters.transportista_id = clean(form.get("transportista_id")) || "";
        renderFletes();
        refreshBusquedaDatalist("flete-filter-buscar");
      };
      document.getElementById("flete-filter-form").addEventListener("submit", (event) => {
        event.preventDefault();
        applyFleteFilter();
      });
      document.getElementById("flete-filter-buscar").addEventListener("input", () => {
        applyFleteFilter();
      });
      document.getElementById("flete-filter-clear").addEventListener("click", () => {
        document.getElementById("flete-filter-form").reset();
        uiState.fleteFilters = { buscar: "", estado: "", cliente_id: "", transportista_id: "" };
        renderFletes();
      });

      const applyDespachoFilter = () => {
        const formNode = document.getElementById("despacho-filter-form");
        const form = new FormData(formNode);
        uiState.despachoFilters.buscar = clean(form.get("buscar")) || "";
        uiState.despachoFilters.estatus = clean(form.get("estatus")) || "";
        uiState.despachoFilters.id_asignacion = clean(form.get("id_asignacion")) || "";
        uiState.despachoFilters.id_flete = clean(form.get("id_flete")) || "";
        renderDespachos();
        refreshBusquedaDatalist("despacho-filter-buscar");
      };
      document.getElementById("despacho-filter-form").addEventListener("submit", (event) => {
        event.preventDefault();
        applyDespachoFilter();
      });
      document.getElementById("despacho-filter-buscar").addEventListener("input", () => {
        applyDespachoFilter();
      });
      document.getElementById("despacho-filter-clear").addEventListener("click", () => {
        document.getElementById("despacho-filter-form").reset();
        uiState.despachoFilters = { buscar: "", estatus: "", id_asignacion: "", id_flete: "" };
        renderDespachos();
        cancelDespachoEdit();
      });

      const applyTransportistaFilter = () => {
        const formNode = document.getElementById("transportista-filter-form");
        const form = new FormData(formNode);
        uiState.transportistaFilters.buscar = clean(form.get("buscar")) || "";
        uiState.transportistaFilters.estatus = clean(form.get("estatus")) || "";
        uiState.transportistaFilters.tipo_transportista = clean(form.get("tipo_transportista")) || "";
        renderTransportistas();
        refreshBusquedaDatalist("transportista-filter-buscar");
        openSingleTransportistaFromFilter();
      };

      document.getElementById("transportista-filter-form").addEventListener("submit", (event) => {
        event.preventDefault();
        applyTransportistaFilter();
      });
      document.getElementById("transportista-filter-buscar").addEventListener("input", () => {
        applyTransportistaFilter();
      });
      document.getElementById("transportista-filter-estatus").addEventListener("change", () => {
        applyTransportistaFilter();
      });
      document.getElementById("transportista-filter-tipo").addEventListener("change", () => {
        applyTransportistaFilter();
      });
      document.getElementById("transportista-filter-clear").addEventListener("click", () => {
        document.getElementById("transportista-filter-form").reset();
        uiState.transportistaFilters = { buscar: "", estatus: "", tipo_transportista: "" };
        renderTransportistas();
        cancelTransportistaEdit();
      });

      const applyViajeFilter = () => {
        const formNode = document.getElementById("viaje-filter-form");
        const form = new FormData(formNode);
        uiState.viajeFilters.buscar = clean(form.get("buscar")) || "";
        uiState.viajeFilters.estado = clean(form.get("estado")) || "";
        renderViajes();
        refreshBusquedaDatalist("viaje-filter-buscar");
      };
      document.getElementById("viaje-filter-form").addEventListener("submit", (event) => {
        event.preventDefault();
        applyViajeFilter();
      });
      document.getElementById("viaje-filter-buscar").addEventListener("input", () => {
        applyViajeFilter();
      });
      document.getElementById("viaje-filter-clear").addEventListener("click", () => {
        document.getElementById("viaje-filter-form").reset();
        uiState.viajeFilters = { buscar: "", estado: "" };
        renderViajes();
        cancelViajeEdit();
      });

      const applyFacturaFilter = () => {
        const formNode = document.getElementById("factura-filter-form");
        const form = new FormData(formNode);
        uiState.facturaFilters.buscar = clean(form.get("buscar")) || "";
        uiState.facturaFilters.cliente_id = clean(form.get("cliente_id")) || "";
        uiState.facturaFilters.estatus = clean(form.get("estatus")) || "";
        renderFacturas();
        refreshBusquedaDatalist("factura-filter-buscar");
      };
      document.getElementById("factura-filter-form").addEventListener("submit", (event) => {
        event.preventDefault();
        applyFacturaFilter();
      });
      document.getElementById("factura-filter-buscar").addEventListener("input", () => {
        applyFacturaFilter();
      });
      document.getElementById("factura-filter-cliente").addEventListener("change", () => {
        applyFacturaFilter();
      });
      document.getElementById("factura-filter-estatus").addEventListener("change", () => {
        applyFacturaFilter();
      });
      document.getElementById("factura-filter-clear").addEventListener("click", () => {
        document.getElementById("factura-filter-form").reset();
        uiState.facturaFilters = { buscar: "", cliente_id: "", estatus: "" };
        renderFacturas();
        cancelFacturaEdit();
      });

      const applyOrdenServicioFilter = () => {
        const formNode = document.getElementById("orden-servicio-filter-form");
        if (!formNode) {
          return;
        }
        const form = new FormData(formNode);
        uiState.ordenServicioFilters.buscar = clean(form.get("buscar")) || "";
        uiState.ordenServicioFilters.cliente_id = clean(form.get("cliente_id")) || "";
        uiState.ordenServicioFilters.estatus = clean(form.get("estatus")) || "";
        renderOrdenesServicio();
        hideOrdenServicioDetail();
      };
      const ordenServicioFilterForm = document.getElementById("orden-servicio-filter-form");
      if (ordenServicioFilterForm) {
        ordenServicioFilterForm.addEventListener("submit", (event) => {
          event.preventDefault();
          applyOrdenServicioFilter();
        });
        document.getElementById("orden-servicio-filter-buscar")?.addEventListener("input", () => {
          applyOrdenServicioFilter();
        });
        document.getElementById("orden-servicio-filter-cliente")?.addEventListener("change", () => {
          applyOrdenServicioFilter();
        });
        document.getElementById("orden-servicio-filter-estatus")?.addEventListener("change", () => {
          applyOrdenServicioFilter();
        });
        document.getElementById("orden-servicio-filter-clear")?.addEventListener("click", () => {
          ordenServicioFilterForm.reset();
          uiState.ordenServicioFilters = { buscar: "", cliente_id: "", estatus: "" };
          renderOrdenesServicio();
          hideOrdenServicioDetail();
        });
        document.getElementById("orden-servicio-detail-close")?.addEventListener("click", () => {
          hideOrdenServicioDetail();
        });
        document.getElementById("orden-servicio-delete-btn")?.addEventListener("click", () => {
          void deleteOrdenServicioSeleccionada();
        });
      }

      const applyTarifaCompraFilter = () => {
        const formNode = document.getElementById("tarifa-compra-filter-form");
        const form = new FormData(formNode);
        uiState.tarifaCompraFilters.buscar = clean(form.get("buscar")) || "";
        uiState.tarifaCompraFilters.transportista_id = clean(form.get("transportista_id")) || "";
        uiState.tarifaCompraFilters.activo = clean(form.get("activo")) || "";
        renderTarifasCompra();
        refreshBusquedaDatalist("tarifa-compra-filter-buscar");
      };
      document.getElementById("tarifa-compra-filter-form").addEventListener("submit", (event) => {
        event.preventDefault();
        applyTarifaCompraFilter();
      });
      document.getElementById("tarifa-compra-filter-buscar").addEventListener("input", () => {
        applyTarifaCompraFilter();
      });
      document.getElementById("tarifa-compra-filter-transportista").addEventListener("change", () => {
        applyTarifaCompraFilter();
      });
      document.getElementById("tarifa-compra-filter-activo").addEventListener("change", () => {
        applyTarifaCompraFilter();
      });
      document.getElementById("tarifa-compra-filter-clear").addEventListener("click", () => {
        document.getElementById("tarifa-compra-filter-form").reset();
        uiState.tarifaCompraFilters = { buscar: "", transportista_id: "", activo: "" };
        renderTarifasCompra();
        cancelTarifaCompraEdit();
      });

      const applyAsignacionFilter = () => {
        const formNode = document.getElementById("asignacion-filter-form");
        const form = new FormData(formNode);
        uiState.asignacionFilters.buscar = clean(form.get("buscar")) || "";
        uiState.asignacionFilters.id_operador = clean(form.get("id_operador")) || "";
        uiState.asignacionFilters.id_unidad = clean(form.get("id_unidad")) || "";
        uiState.asignacionFilters.id_viaje = clean(form.get("id_viaje")) || "";
        renderAsignaciones();
        refreshBusquedaDatalist("asignacion-filter-buscar");
      };
      document.getElementById("asignacion-filter-form").addEventListener("submit", (event) => {
        event.preventDefault();
        applyAsignacionFilter();
      });
      document.getElementById("asignacion-filter-buscar").addEventListener("input", () => {
        applyAsignacionFilter();
      });
      document.getElementById("asignacion-filter-clear").addEventListener("click", () => {
        document.getElementById("asignacion-filter-form").reset();
        uiState.asignacionFilters = { buscar: "", id_operador: "", id_unidad: "", id_viaje: "" };
        renderAsignaciones();
        cancelAsignacionEdit();
      });

      document.getElementById("tarifa-venta-filter-buscar").addEventListener("input", (event) => {
        uiState.tarifaVentaFilters.buscar = clean(event.target.value) || "";
        renderTarifas();
        refreshBusquedaDatalist("tarifa-venta-filter-buscar");
      });
      document.getElementById("gasto-filter-buscar").addEventListener("input", (event) => {
        uiState.gastoFilters.buscar = clean(event.target.value) || "";
        renderGastos();
        refreshBusquedaDatalist("gasto-filter-buscar");
      });
      document.getElementById("operador-filter-buscar").addEventListener("input", (event) => {
        uiState.operadorFilters.buscar = clean(event.target.value) || "";
        renderOperadores();
        refreshBusquedaDatalist("operador-filter-buscar");
      });
      document.getElementById("operador-filter-clear").addEventListener("click", () => {
        uiState.operadorFilters.buscar = "";
        const inp = document.getElementById("operador-filter-buscar");
        if (inp) {
          inp.value = "";
        }
        renderOperadores();
        refreshBusquedaDatalist("operador-filter-buscar");
      });
      document.getElementById("unidad-filter-buscar").addEventListener("input", (event) => {
        uiState.unidadFilters.buscar = clean(event.target.value) || "";
        renderUnidades();
        refreshBusquedaDatalist("unidad-filter-buscar");
      });
      document.getElementById("unidad-filter-tipo-propiedad").addEventListener("change", (event) => {
        uiState.unidadFilters.tipo_propiedad = clean(event.target.value) || "";
        renderUnidades();
      });
      document.getElementById("unidad-filter-estatus-doc").addEventListener("change", (event) => {
        uiState.unidadFilters.estatus_documental = clean(event.target.value) || "";
        renderUnidades();
      });
      document.getElementById("unidad-filter-activo").addEventListener("change", (event) => {
        uiState.unidadFilters.activo = clean(event.target.value) || "";
        renderUnidades();
      });
      document.getElementById("unidad-filter-clear").addEventListener("click", () => {
        uiState.unidadFilters = { buscar: "", tipo_propiedad: "", estatus_documental: "", activo: "" };
        uiState.buscarModo = "contiene";
        try {
          sessionStorage.setItem("SIFE_buscar_modo", "contiene");
        } catch (_) {
          /* ignore */
        }
        document.querySelectorAll(".buscar-modo-sync").forEach((el) => {
          el.value = "contiene";
        });
        const ub = document.getElementById("unidad-filter-buscar");
        if (ub) {
          ub.value = "";
        }
        document.getElementById("unidad-filter-tipo-propiedad").value = "";
        document.getElementById("unidad-filter-estatus-doc").value = "";
        document.getElementById("unidad-filter-activo").value = "";
        clearMessage("unidad-consulta-message");
        refreshAllConsultaTables();
        refreshBusquedaDatalist("unidad-filter-buscar");
      });
      document.getElementById("unidad-recargar-catalogo").addEventListener("click", async () => {
        clearMessage("unidad-consulta-message");
        try {
          await refreshData();
          const t = state.unidadesTotalServidor;
          const n = state.unidades.length;
          const uErr = unidadesEndpointFailed();
          let hint = "";
          if (uErr) {
            hint =
              " No se pudieron leer unidades desde la API (vea el aviso amarillo arriba). El total mostrado puede no ser fiable hasta que la peticion funcione.";
          } else if (t === 0) {
            hint =
              " No hay filas en la tabla unidades de MySQL en esta conexion: cree al menos una en Nueva unidad (economico obligatorio) o ejecute un script de demo si lo tiene.";
          }
          const tDisp = t == null ? "?" : t;
          setMessage(
            "unidad-consulta-message",
            `Catalogo actualizado: total en servidor = ${tDisp} (${n} cargadas en el panel, limite 500).` + hint,
            uErr ? "error" : "ok",
          );
        } catch (error) {
          setMessage("unidad-consulta-message", error.message || "No se pudo recargar el catalogo.", "error");
        }
      });
    }

    function initClienteModule() {
      const contactoSelect = document.getElementById("cliente-contacto-cliente");
      const domicilioSelect = document.getElementById("cliente-domicilio-cliente");
      const condicionSelect = document.getElementById("cliente-condicion-cliente");
      const clienteTabButtons = document.querySelectorAll("[data-cliente-tab]");

      for (const button of clienteTabButtons) {
        button.addEventListener("click", () => {
          setClienteSubpage(button.dataset.clienteTab);
        });
      }

      const manualToc = document.getElementById("manual-clientes-toc");
      if (manualToc) {
        manualToc.addEventListener("click", (event) => {
          const link = event.target.closest("a[href^='#manual-clientes-']");
          if (!link) {
            return;
          }
          event.preventDefault();
          const id = link.getAttribute("href").slice(1);
          const target = document.getElementById(id);
          if (target) {
            target.scrollIntoView({ behavior: "smooth", block: "start" });
          }
        });
      }

      const clienteOpenManualBtn = document.getElementById("cliente-open-manual-btn");
      if (clienteOpenManualBtn) {
        clienteOpenManualBtn.addEventListener("click", () => setClienteSubpage("manual"));
      }

      if (contactoSelect) {
        contactoSelect.addEventListener("change", () => syncClienteModuleSelection("cliente-contacto-cliente"));
      }
      if (domicilioSelect) {
        domicilioSelect.addEventListener("change", () => syncClienteModuleSelection("cliente-domicilio-cliente"));
      }
      const domicilioBuscar = document.getElementById("cliente-domicilio-buscar");
      if (domicilioBuscar) {
        domicilioBuscar.addEventListener("input", () => {
          const sel = document.getElementById("cliente-domicilio-cliente");
          fillClienteDomicilioSelect(domicilioBuscar.value, sel ? sel.value : null);
          syncClienteModuleSummaries();
          renderClienteDomicilios();
        });
      }
      if (condicionSelect) {
        condicionSelect.addEventListener("change", () => syncClienteModuleSelection("cliente-condicion-cliente"));
      }

      const clienteEditOpenContactos = document.getElementById("cliente-edit-open-contactos");
      if (clienteEditOpenContactos) {
        clienteEditOpenContactos.addEventListener("click", () => {
          const id = uiState.editing.clienteId;
          if (!id) {
            return;
          }
          const sel = document.getElementById("cliente-contacto-cliente");
          if (sel) {
            sel.value = String(id);
          }
          syncClienteModuleSelection("cliente-contacto-cliente");
          const contactoPanel = document.querySelector("[data-cliente-tab-panel='contactos']");
          if (contactoPanel) {
            contactoPanel.scrollIntoView({ behavior: "smooth", block: "start" });
          }
        });
      }

      const clienteEditOpenDomicilios = document.getElementById("cliente-edit-open-domicilios");
      if (clienteEditOpenDomicilios) {
        clienteEditOpenDomicilios.addEventListener("click", () => {
          const id = uiState.editing.clienteId;
          if (!id) {
            return;
          }
          const sel = document.getElementById("cliente-domicilio-cliente");
          if (sel) {
            sel.value = String(id);
          }
          syncClienteModuleSelection("cliente-domicilio-cliente");
          const domPanel = document.querySelector("[data-cliente-tab-panel='domicilios']");
          if (domPanel) {
            domPanel.scrollIntoView({ behavior: "smooth", block: "start" });
          }
        });
      }

      setClienteSubpage(uiState.clienteSubpage);
      syncClienteModuleSummaries();

      document.getElementById("cliente-contacto-edit-cancel").addEventListener("click", cancelClienteContactoEdit);
      const contactoEditBuscar = document.getElementById("cliente-contacto-edit-buscar");
      if (contactoEditBuscar) {
        contactoEditBuscar.addEventListener("input", () => {
          const sel = document.getElementById("cliente-contacto-edit-cliente");
          const cur = sel?.value || "";
          fillClienteContactoEditSelect(contactoEditBuscar.value, cur || null);
        });
      }
      document.getElementById("cliente-domicilio-edit-cancel").addEventListener("click", cancelClienteDomicilioEdit);

      const clienteContactoEditForm = document.getElementById("cliente-contacto-edit-form");
      clienteContactoEditForm.addEventListener("submit", (event) => event.preventDefault());
      document.getElementById("cliente-contacto-edit-guardar").addEventListener("click", async () => {
        clearMessage("cliente-contacto-edit-message");
        const form = clienteContactoEditForm;
        if (!form.reportValidity()) {
          return;
        }
        try {
          const contactoId = requirePositiveIntOrThrow(form.elements.id.value, "Contacto del cliente");
          const pathClienteId = requirePositiveIntOrThrow(
            document.getElementById("cliente-contacto-path-cliente").value,
            "Cliente",
          );
          const payload = buildClienteContactoPayload(new FormData(form));
          const patchBody = {
            nombre: payload.nombre,
            area: payload.area,
            puesto: payload.puesto,
            telefono: payload.telefono,
            extension: payload.extension,
            celular: payload.celular,
            email: payload.email,
            principal: payload.principal,
            activo: payload.activo,
          };
          if (payload.cliente_id !== pathClienteId) {
            patchBody.cliente_id = payload.cliente_id;
          }
          await api(`/clientes/${pathClienteId}/contactos/${contactoId}`, {
            method: "PATCH",
            body: JSON.stringify(patchBody),
          });
          setMessage("cliente-contacto-edit-message", "Contacto actualizado.", "ok");
          cancelClienteContactoEdit();
          await refreshData();
          document.getElementById("cliente-contacto-cliente").value = String(payload.cliente_id);
          renderClienteContactos();
        } catch (error) {
          setMessage("cliente-contacto-edit-message", error.message, "error");
        }
      });

      document.getElementById("cliente-domicilio-edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("cliente-domicilio-edit-message");
        const form = event.currentTarget;
        try {
          const domicilioId = requirePositiveIntOrThrow(form.elements.id.value, "Domicilio");
          const clienteId = requirePositiveIntOrThrow(form.elements.cliente_id.value, "Cliente");
          const payload = buildClienteDomicilioPayload(new FormData(form));
          await api(`/clientes/${clienteId}/domicilios/${domicilioId}`, {
            method: "PATCH",
            body: JSON.stringify({
              tipo_domicilio: payload.tipo_domicilio,
              nombre_sede: payload.nombre_sede,
              direccion_completa: payload.direccion_completa,
              municipio: payload.municipio,
              estado: payload.estado,
              codigo_postal: payload.codigo_postal,
              horario_carga: payload.horario_carga,
              horario_descarga: payload.horario_descarga,
              instrucciones_acceso: payload.instrucciones_acceso,
              activo: payload.activo,
            }),
          });
          setMessage("cliente-domicilio-edit-message", "Domicilio actualizado.", "ok");
          cancelClienteDomicilioEdit();
          await refreshData();
          document.getElementById("cliente-domicilio-cliente").value = String(clienteId);
          flushClienteDomiciliosForSelectedClient(String(clienteId));
        } catch (error) {
          setMessage("cliente-domicilio-edit-message", error.message, "error");
        }
      });
    }

    function initTransportistaModule() {
      const contactoSelect = document.getElementById("transportista-contacto-transportista");
      const documentoSelect = document.getElementById("transportista-documento-transportista");
      const transportistaTabButtons = document.querySelectorAll("[data-transportista-tab]");

      for (const button of transportistaTabButtons) {
        button.addEventListener("click", () => {
          setTransportistaSubpage(button.dataset.transportistaTab);
        });
      }

      const manualTransportistasToc = document.getElementById("manual-transportistas-toc");
      if (manualTransportistasToc) {
        manualTransportistasToc.addEventListener("click", (event) => {
          const link = event.target.closest("a[href^='#manual-transportistas-']");
          if (!link) {
            return;
          }
          event.preventDefault();
          const id = link.getAttribute("href").slice(1);
          const target = document.getElementById(id);
          if (target) {
            target.scrollIntoView({ behavior: "smooth", block: "start" });
          }
        });
      }

      const transportistaOpenManualBtn = document.getElementById("transportista-open-manual-btn");
      if (transportistaOpenManualBtn) {
        transportistaOpenManualBtn.addEventListener("click", () => setTransportistaSubpage("manual"));
      }

      if (contactoSelect) {
        contactoSelect.addEventListener("change", () => syncTransportistaModuleSelection("transportista-contacto-transportista"));
      }
      if (documentoSelect) {
        documentoSelect.addEventListener("change", () => syncTransportistaModuleSelection("transportista-documento-transportista"));
      }

      setTransportistaSubpage(uiState.transportistaSubpage);

      document.getElementById("transportista-edit-cancel").addEventListener("click", cancelTransportistaEdit);
      document.getElementById("transportista-contacto-edit-cancel").addEventListener("click", cancelTransportistaContactoEdit);
      document.getElementById("transportista-documento-edit-cancel").addEventListener("click", cancelTransportistaDocumentoEdit);

      document.getElementById("transportista-edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("transportista-edit-message");
        const form = event.currentTarget;
        try {
          const id = requirePositiveIntOrThrow(form.elements.id.value, "Transportista");
          const payload = buildTransportistaPayload(new FormData(form));
          await api(`/transportistas/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
          setMessage("transportista-edit-message", "Transportista actualizado.", "ok");
          cancelTransportistaEdit();
          await refreshData();
        } catch (error) {
          setMessage("transportista-edit-message", error.message, "error");
        }
      });

      document.getElementById("transportista-contacto-edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("transportista-contacto-edit-message");
        const form = event.currentTarget;
        try {
          const contactoId = requirePositiveIntOrThrow(form.elements.id.value, "Contacto del transportista");
          const transportistaId = requirePositiveIntOrThrow(form.elements.transportista_id.value, "Transportista");
          const payload = buildTransportistaContactoPayload(new FormData(form));
          await api(`/transportistas/${transportistaId}/contactos/${contactoId}`, {
            method: "PATCH",
            body: JSON.stringify({
              nombre: payload.nombre,
              area: payload.area,
              puesto: payload.puesto,
              telefono: payload.telefono,
              extension: payload.extension,
              celular: payload.celular,
              email: payload.email,
              principal: payload.principal,
              activo: payload.activo,
            }),
          });
          setMessage("transportista-contacto-edit-message", "Contacto actualizado.", "ok");
          cancelTransportistaContactoEdit();
          await refreshData();
          document.getElementById("transportista-contacto-transportista").value = String(transportistaId);
          syncTransportistaModuleSelection("transportista-contacto-transportista");
        } catch (error) {
          setMessage("transportista-contacto-edit-message", error.message, "error");
        }
      });

      document.getElementById("transportista-documento-edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("transportista-documento-edit-message");
        const form = event.currentTarget;
        try {
          const documentoId = requirePositiveIntOrThrow(form.elements.id.value, "Documento del transportista");
          const transportistaId = requirePositiveIntOrThrow(form.elements.transportista_id.value, "Transportista");
          const payload = buildTransportistaDocumentoPayload(new FormData(form));
          await api(`/transportistas/${transportistaId}/documentos/${documentoId}`, {
            method: "PATCH",
            body: JSON.stringify({
              tipo_documento: payload.tipo_documento,
              numero_documento: payload.numero_documento,
              fecha_emision: payload.fecha_emision,
              fecha_vencimiento: payload.fecha_vencimiento,
              archivo_url: payload.archivo_url,
              estatus: payload.estatus,
              observaciones: payload.observaciones,
            }),
          });
          setMessage("transportista-documento-edit-message", "Documento actualizado.", "ok");
          cancelTransportistaDocumentoEdit();
          await refreshData();
          document.getElementById("transportista-documento-transportista").value = String(transportistaId);
          syncTransportistaModuleSelection("transportista-documento-transportista");
        } catch (error) {
          setMessage("transportista-documento-edit-message", error.message, "error");
        }
      });
    }

    function initEditors() {
      document.getElementById("cliente-edit-cancel").addEventListener("click", cancelClienteEdit);
      document.getElementById("cliente-edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("cliente-edit-message");
        const formElement = event.currentTarget;
        try {
          const payload = buildClientePayload(new FormData(formElement));
          const id = requirePositiveIntOrThrow(formElement.elements.id.value, "Cliente");
          await api(`/clientes/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
          setMessage("cliente-edit-message", "Cliente actualizado.", "ok");
          cancelClienteEdit();
          await refreshData();
        } catch (error) {
          setMessage("cliente-edit-message", error.message, "error");
        }
      });

      document.getElementById("viaje-edit-cancel").addEventListener("click", cancelViajeEdit);
      document.getElementById("viaje-edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("viaje-edit-message");
        const formElement = event.currentTarget;
        try {
          const payload = buildViajePayload(new FormData(formElement));
          const id = requirePositiveIntOrThrow(formElement.elements.id.value, "Viaje");
          await api(`/viajes/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
          setMessage("viaje-edit-message", "Viaje actualizado.", "ok");
          cancelViajeEdit();
          await refreshData();
        } catch (error) {
          setMessage("viaje-edit-message", error.message, "error");
        }
      });

      document.getElementById("factura-edit-cancel").addEventListener("click", cancelFacturaEdit);
      document.getElementById("factura-edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("factura-edit-message");
        const formElement = event.currentTarget;
        try {
          const payload = buildFacturaPayload(new FormData(formElement));
          const id = requirePositiveIntOrThrow(formElement.elements.id.value, "Factura");
          await api(`/facturas/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
          setMessage("factura-edit-message", "Factura actualizada.", "ok");
          cancelFacturaEdit();
          await refreshData();
        } catch (error) {
          setMessage("factura-edit-message", error.message, "error");
        }
      });

      document.getElementById("tarifa-compra-edit-cancel").addEventListener("click", cancelTarifaCompraEdit);
      document.getElementById("tarifa-compra-edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("tarifa-compra-edit-message");
        const formElement = event.currentTarget;
        try {
          const fd = new FormData(formElement);
          const payload = buildTarifaCompraPayload(fd);
          const rawId = tarifaCompraEditIdForPatch(formElement);
          const id = requirePositiveIntOrThrow(rawId, "Tarifa de compra");
          await api(`/tarifas-compra-transportista/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
          setMessage("tarifa-compra-edit-message", "Tarifa de compra actualizada.", "ok");
          cancelTarifaCompraEdit();
          await refreshData();
        } catch (error) {
          setMessage("tarifa-compra-edit-message", error.message, "error");
        }
      });

      document.getElementById("flete-edit-cancel").addEventListener("click", cancelFleteEdit);
      document.getElementById("flete-edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("flete-edit-message");
        const formElement = event.currentTarget;
        try {
          const payload = buildFletePayload(new FormData(formElement));
          const idRaw = resolveFleteEditRecordId(formElement);
          const id = requirePositiveIntOrThrow(idRaw, "Flete");
          await api(`/fletes/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
          setMessage("flete-edit-message", "Flete actualizado.", "ok");
          cancelFleteEdit();
          await refreshData();
        } catch (error) {
          setMessage("flete-edit-message", error.message, "error");
        }
      });

      document.getElementById("asignacion-edit-cancel").addEventListener("click", cancelAsignacionEdit);
      document.getElementById("asignacion-edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("asignacion-edit-message");
        const formElement = event.currentTarget;
        try {
          const payload = buildAsignacionPayload(new FormData(formElement));
          const id = requirePositiveIntOrThrow(formElement.elements.id_asignacion.value, "Asignacion");
          await api(`/asignaciones/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
          setMessage("asignacion-edit-message", "Asignacion actualizada.", "ok");
          cancelAsignacionEdit();
          await refreshData();
        } catch (error) {
          setMessage("asignacion-edit-message", error.message, "error");
        }
      });

      document.getElementById("despacho-edit-cancel").addEventListener("click", cancelDespachoEdit);
      document.getElementById("despacho-edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        clearMessage("despacho-edit-message");
        const formElement = event.currentTarget;
        try {
          const payload = buildDespachoPayload(new FormData(formElement));
          const idCandidate = resolveDespachoEditRecordId(formElement);
          const id = requirePositiveIntIdOrThrow(idCandidate, "Despacho");
          await api(`/despachos/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
          setMessage("despacho-edit-message", "Despacho actualizado.", "ok");
          cancelDespachoEdit();
          await refreshData();
        } catch (error) {
          setMessage("despacho-edit-message", error.message, "error");
        }
      });
    }

    async function refreshBajasDanosList() {
      const box = document.getElementById("bajas-danos-tabla");
      if (!box) return;
      const tipoEl = document.getElementById("bajas-danos-filtro-tipo");
      const fleteEl = document.getElementById("bajas-danos-filtro-flete");
      const tipo = tipoEl ? String(tipoEl.value || "").trim() : "";
      const fleteRaw = fleteEl ? String(fleteEl.value || "").trim() : "";
      const q = new URLSearchParams({ skip: "0", limit: "100" });
      if (tipo) q.set("tipo", tipo);
      if (fleteRaw) q.set("flete_id", fleteRaw);
      clearMessage("bajas-danos-list-message");
      try {
        const data = await api(`/bajas-danos?${q.toString()}`);
        const items = Array.isArray(data?.items) ? data.items : [];
        if (!items.length) {
          box.innerHTML = '<div class="hint">Sin registros.</div>';
          return;
        }
        const rows = items
          .map(
            (it) => `
            <tr data-bd-id="${Number(it.id)}">
              <td>${Number(it.id)}</td>
              <td>${escapeHtml(String(it.tipo || ""))}</td>
              <td>${escapeHtml(String(it.titulo || ""))}</td>
              <td>${escapeHtml(String(it.fecha_evento || ""))}</td>
              <td>${it.flete_id != null ? Number(it.flete_id) : "—"}</td>
              <td>${it.id_unidad != null ? Number(it.id_unidad) : "—"}</td>
              <td>${it.id_operador != null ? Number(it.id_operador) : "—"}</td>
              <td>
                <select data-bd-estatus>
                  <option value="abierta" ${String(it.estatus) === "abierta" ? "selected" : ""}>Abierta</option>
                  <option value="en_seguimiento" ${String(it.estatus) === "en_seguimiento" ? "selected" : ""}>En seguimiento</option>
                  <option value="cerrada" ${String(it.estatus) === "cerrada" ? "selected" : ""}>Cerrada</option>
                </select>
              </td>
              <td><button type="button" class="secondary-button" data-bd-save>Guardar</button></td>
            </tr>`
          )
          .join("");
        box.innerHTML = `
          <table>
            <thead>
              <tr>
                <th>ID</th><th>Tipo</th><th>Título</th><th>Fecha</th><th>Flete</th><th>Unidad</th><th>Operador</th><th>Estatus</th><th></th>
              </tr>
            </thead>
            <tbody>${rows}</tbody>
          </table>`;
      } catch (error) {
        box.innerHTML = "";
        setMessage("bajas-danos-list-message", error?.message || "No se pudo cargar el listado.", "error");
      }
    }

    function initBajasDanosModule() {
      const form = document.getElementById("bajas-danos-form");
      const filtros = document.getElementById("bajas-danos-filtros");
      const refreshBtn = document.getElementById("bajas-danos-refresh-btn");
      const tabla = document.getElementById("bajas-danos-tabla");
      if (!form || !filtros) return;
      const fecha = form.elements.fecha_evento;
      if (fecha && !fecha.value) {
        const d = new Date();
        fecha.value = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
      }
      if (!form.dataset.bound) {
        form.dataset.bound = "true";
        filtros.dataset.bound = "true";
        form.addEventListener("submit", async (event) => {
          event.preventDefault();
          clearMessage("bajas-danos-form-message");
          const fd = new FormData(form);
          const titulo = String(fd.get("titulo") || "").trim();
          const tipo = String(fd.get("tipo") || "").trim();
          const fecha_evento = String(fd.get("fecha_evento") || "").trim();
          const detalleRaw = String(fd.get("detalle") || "").trim();
          const estatus = String(fd.get("estatus") || "abierta").trim();
          const fleteRaw = String(fd.get("flete_id") || "").trim();
          const unidadRaw = String(fd.get("id_unidad") || "").trim();
          const operRaw = String(fd.get("id_operador") || "").trim();
          const costoRaw = String(fd.get("costo_estimado") || "").trim();
          if (!titulo || !tipo || !fecha_evento) {
            setMessage("bajas-danos-form-message", "Complete tipo, fecha y título.", "error");
            return;
          }
          const payload = {
            tipo,
            titulo,
            fecha_evento,
            detalle: detalleRaw || null,
            estatus,
            flete_id: fleteRaw ? Number(fleteRaw) : null,
            id_unidad: unidadRaw ? Number(unidadRaw) : null,
            id_operador: operRaw ? Number(operRaw) : null,
            costo_estimado: costoRaw ? Number(costoRaw.replace(",", ".")) : null,
          };
          if (payload.flete_id != null && !Number.isFinite(payload.flete_id)) {
            setMessage("bajas-danos-form-message", "ID flete inválido.", "error");
            return;
          }
          try {
            await api("/bajas-danos", { method: "POST", body: JSON.stringify(payload) });
            setMessage("bajas-danos-form-message", "Registro guardado.", "ok");
            form.reset();
            if (fecha) {
              const d = new Date();
              fecha.value = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
            }
            await refreshBajasDanosList();
          } catch (error) {
            setMessage("bajas-danos-form-message", error?.message || "No se pudo guardar.", "error");
          }
        });
        filtros.addEventListener("submit", (event) => {
          event.preventDefault();
          void refreshBajasDanosList();
        });
      }
      if (refreshBtn && !refreshBtn.dataset.bound) {
        refreshBtn.dataset.bound = "true";
        refreshBtn.addEventListener("click", () => {
          void refreshBajasDanosList();
        });
      }
      if (tabla && !tabla.dataset.bound) {
        tabla.dataset.bound = "true";
        tabla.addEventListener("click", async (event) => {
          const btn = event.target.closest("[data-bd-save]");
          if (!btn) return;
          const tr = btn.closest("tr[data-bd-id]");
          if (!tr) return;
          const id = Number(tr.dataset.bdId);
          const estatus = tr.querySelector("[data-bd-estatus]")?.value || "abierta";
          clearMessage("bajas-danos-list-message");
          try {
            await api(`/bajas-danos/${id}`, { method: "PATCH", body: JSON.stringify({ estatus }) });
            setMessage("bajas-danos-list-message", `Registro #${id} actualizado.`, "ok");
            await refreshBajasDanosList();
          } catch (error) {
            setMessage("bajas-danos-list-message", error?.message || "No se pudo actualizar.", "error");
          }
        });
      }
    }

    async function fetchHealthIntoPanel() {
      const el = document.getElementById("health-conn-info");
      if (!el) {
        return;
      }
      try {
        const r = await fetch("/health", { headers: { Accept: "application/json" } });
        if (!r.ok) {
          throw new Error(`HTTP ${r.status}`);
        }
        const data = await r.json();
        const host = data.mysql_host != null ? String(data.mysql_host) : "?";
        const port = data.mysql_port != null ? String(data.mysql_port) : "?";
        const db = data.mysql_db != null ? String(data.mysql_db) : "?";
        el.innerHTML =
          "<strong>Base de datos (este proceso):</strong> <code>" +
          escapeHtml(db) +
          "</code> en <code>" +
          escapeHtml(host) +
          ":" +
          escapeHtml(port) +
          '</code>. Comparala con la base que abres en MySQL: si no coincide, el panel y el cliente SQL estan mirando otro servidor o base. JSON: <a href="/health">/health</a>.';
      } catch (e) {
        el.textContent =
          "No se pudo leer /health: " +
          (e && e.message ? e.message : "error") +
          ". Verifique que Uvicorn este en marcha.";
      }
    }

    async function boot() {
      const initErrors = [];
      async function runInitStep(name, fn) {
        try {
          await fn();
        } catch (error) {
          const msg = error && error.message ? error.message : String(error);
          initErrors.push(`${name}: ${msg}`);
          console.error(`[SIFE boot] ${name}`, error);
        }
      }

      await runInitStep("initAuthBar", () => initAuthBar());
      await runInitStep("initNavigation", () => initNavigation());
      await runInitStep("applyCaptureShellStyle", () => applyCaptureShellStyle());
      await runInitStep("installCaptureFormCancelButtons", () => installCaptureFormCancelButtons());
      await runInitStep("initForms", () => initForms());
      await runInitStep("wireMoneyInputs", () => wireMoneyInputs());
      await runInitStep("applyMoneyFormatToForm(all)", () => {
        for (const form of document.querySelectorAll("form")) {
          applyMoneyFormatToForm(form);
        }
      });
      await runInitStep("initClienteModule", () => initClienteModule());
      await runInitStep("initTransportistaModule", () => initTransportistaModule());
      await runInitStep("initCrudSubpageModules", () => initCrudSubpageModules());
      await runInitStep("initFacturaModule", () => initFacturaModule());
      await runInitStep("initFilters", () => initFilters());
      await runInitStep("initTarifaVentaNombreUnico", () => initTarifaVentaNombreUnico());
      await runInitStep("initUsuariosAdminModule", () => initUsuariosAdminModule());
      await runInitStep("initAuditLogsModule", () => initAuditLogsModule());
      await runInitStep("initEditors", () => initEditors());
      await runInitStep("initFleteCotizador", () => initFleteCotizador());
      await runInitStep("initDireccionModule", () => initDireccionModule());
      await runInitStep("initBajasDanosModule", () => initBajasDanosModule());
      await runInitStep("wireEnterAvanzaCampo(#flete-form)", () => wireEnterAvanzaCampo("#flete-form"));
      await runInitStep("wireEnterAvanzaCampo(#flete-edit-form)", () => wireEnterAvanzaCampo("#flete-edit-form"));
      await runInitStep("refreshData + fetchHealthIntoPanel", () => Promise.all([refreshData(), fetchHealthIntoPanel()]));

      if (initErrors.length) {
        document.body.insertAdjacentHTML(
          "afterbegin",
          `<div style="margin:16px;padding:12px;border:1px solid #fecaca;background:#fef2f2;color:#991b1b;border-radius:12px;">
            El panel cargo con incidencias. Revise la consola del navegador para detalle.
          </div>`
        );
      }
    }

    window.sifePanelBoot = boot;
  
