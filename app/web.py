from __future__ import annotations

import json
from html import escape
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from app.core.config import settings

router = APIRouter(include_in_schema=False)

_UI_TEMPLATE = """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>__PROJECT_NAME__ | Panel</title>
  <link rel="stylesheet" href="/static/panel/panel.css" />
</head>
<body>
  <noscript>
    <div style="margin:0;padding:14px 18px;background:#fef2f2;border-bottom:2px solid #fecaca;color:#991b1b;font-family:system-ui,sans-serif;">
      Este panel necesita <strong>JavaScript</strong> activado para cambiar de modulo. Activalo en el navegador y recarga.
      Puedes usar la API en <a href="/docs">/docs</a> mientras tanto.
    </div>
  </noscript>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <h1>__PROJECT_NAME__</h1>
        <p>Panel simple con menu lateral para trabajar un modulo a la vez.</p>
        <p class="sidebar-url-hint">Usa la URL <strong>/ui</strong> para este panel. El manual de cumplimiento es otra pagina.</p>
      </div>

      <div class="nav-group">
        <div class="nav-title">General</div>
        <button type="button" class="nav-button active" data-page="inicio">
          Inicio
          <small>Resumen rapido y accesos</small>
        </button>
      </div>

      <div class="nav-group">
        <div class="nav-title">Catalogos base</div>
        <button type="button" class="nav-button" data-page="clientes">
          Clientes
          <small>Alta y listado</small>
        </button>
        <button type="button" class="nav-button" data-page="transportistas">
          Transportistas
          <small>Proveedores de transporte</small>
        </button>
        <button type="button" class="nav-button" data-page="viajes">
          Viajes
          <small>Planeacion</small>
        </button>
        <button type="button" class="nav-button" data-page="operadores">
          Operadores
          <small>Choferes de transporte</small>
        </button>
        <button type="button" class="nav-button" data-page="unidades">
          Unidades
          <small>Vehiculos y economicos</small>
        </button>
      </div>

      <div class="nav-group">
        <div class="nav-title">Comercial y planeacion</div>
        <button type="button" class="nav-button" data-page="tarifas">
          Tarifa venta
          <small>Reglas de cotizacion</small>
        </button>
        <button type="button" class="nav-button" data-page="tarifas-compra">
          Tarifas compra
          <small>Compra negociada por transportista</small>
        </button>
        <button type="button" class="nav-button" data-page="fletes">
          Fletes
          <small>Cotizacion, venta y ordenes de servicio</small>
        </button>
      </div>

      <div class="nav-group">
        <div class="nav-title">Operacion</div>
        <button type="button" class="nav-button" data-page="asignaciones">
          Asignaciones
          <small>Operador + unidad + viaje</small>
        </button>
        <button type="button" class="nav-button" data-page="despachos">
          Despachos
          <small>Programacion operativa</small>
        </button>
        <button type="button" class="nav-button" data-page="bajas-danos">
          Bajas y daños
          <small>Incidentes operativos</small>
        </button>
        <a
          class="sidebar-manual-link"
          href="/manual/cumplimiento"
          target="_blank"
          rel="noopener"
        >
          Manual cumplimiento
          <small>Legal MX (imprimir PDF)</small>
        </a>
        <button type="button" class="nav-button" data-page="seguimiento">
          Seguimiento
          <small>Salida, entrega, cierre</small>
        </button>
      </div>

      <div class="nav-group">
        <div class="nav-title">Cierre economico</div>
        <button type="button" class="nav-button" data-page="gastos">
          Gastos viaje
          <small>Costos reales por flete</small>
        </button>
        <button type="button" class="nav-button" data-page="facturas">
          Facturas
          <small>Simulacion administrativa de cobro</small>
        </button>
      </div>

      <div class="nav-group">
        <div class="nav-title">Administracion</div>
        <button
          type="button"
          class="nav-button"
          data-page="direccion"
          data-restrict-roles="admin,direccion"
        >
          Dirección
          <small>Tablero ejecutivo KPI</small>
        </button>
        <button
          type="button"
          class="nav-button"
          data-page="usuarios-admin"
          data-restrict-roles="admin,direccion"
        >
          Usuarios
          <small>Roles, altas y contraseñas</small>
        </button>
        <button
          type="button"
          class="nav-button"
          data-page="audit-logs"
          data-restrict-roles="admin,direccion"
        >
          Auditoría
          <small>Trazabilidad de cambios</small>
        </button>
      </div>

      <div class="sidebar-note">
        Si algo avanzado no aparece aqui, puedes usar <a href="/docs" style="color:#fff;text-decoration:underline;">Swagger</a> como respaldo.
      </div>
    </aside>

    <main class="main">
      <div id="catalog-refresh-banner" class="catalog-refresh-banner" hidden></div>
      <div class="topbar">
        <div>
          <h2 id="page-title">Inicio</h2>
          <p id="page-description">Resumen del sistema y accesos a cada modulo sin mezclar pantallas.</p>
        </div>
        <div class="meta" id="auth-bar-wrap">
          <span id="auth-hint">Comprobando sesión…</span>
          <a href="/login?next=/ui" id="auth-login-link" style="margin-left:10px;">Iniciar sesión (JWT)</a>
          <button type="button" id="auth-logout-btn" class="secondary-button" style="margin-left:8px;display:none;">Cerrar sesión</button>
          <span id="auth-apikey-note" style="margin-left:12px;opacity:0.85;">| Sin JWT, el panel usa <code>API_KEY</code> del servidor.</span>
        </div>
      </div>

      <section class="banner">
        <div><strong>Modo guiado:</strong> solo se muestra un módulo; elija otro en el <strong>menú lateral</strong> (izquierda).</div>
      </section>

      <section class="page active" id="page-inicio">
        <div class="status-grid" id="stats"></div>
        <div class="grid">
          <article class="card">
            <h3>Como usarlo</h3>
            <ol class="summary-list">
              <li><strong>Catalogos base:</strong> clientes, transportistas, viajes, operadores y unidades.</li>
              <li><strong>Reglas comerciales:</strong> tarifas de venta y tarifas de compra antes de cotizar.</li>
              <li><strong>Venta y compromiso:</strong> fletes y luego <strong>Ordenes de servicio</strong> (subpestaña en Fletes).</li>
              <li><strong>Ejecucion:</strong> asignacion (operador + unidad + viaje), despacho y seguimiento (salida a cierre).</li>
              <li><strong>Cierre economico:</strong> gastos de viaje por flete y despues facturas administrativas.</li>
              <li><strong>Control de acceso:</strong> usuarios y roles en Administracion (solo admin/direccion).</li>
            </ol>
            <p class="hint" style="margin:10px 0 0 0;">Lo que no se guarda con el boton correspondiente <strong>no queda en el servidor</strong> (no hay borradores automaticos en el navegador). Guarde por pasos antes de cambiar de modulo o recargar.</p>
          </article>
          <article class="card">
            <h3>Estado actual</h3>
            <div class="hint">Este panel consume la misma API que ya validaste. Si algo falla, el mensaje del formulario te dira la razon.</div>
            <div id="health-conn-info" class="hint" style="margin-top:12px;">Leyendo conexion de datos desde <a href="/health">/health</a>…</div>
            <div class="meta" style="margin-top:10px;">Si necesitas consultar raw endpoints, tienes disponible <a href="/docs">/docs</a>.</div>
          </article>
          <article class="card">
            <h3>Documentación</h3>
            <div class="hint">Los manuales integrados están en cada módulo del menú lateral: pestaña <strong>Manual</strong> o botón <strong>Abrir manual</strong> (índice y visor en pantalla).</div>
          </article>
        </div>
      </section>

      <section class="page" id="page-clientes">
        <div class="card">
          <div class="module-subpage-head">
            <div>
              <h3>Subopciones de clientes</h3>
              <div class="hint">Trabaja una parte del cliente a la vez para evitar confusión.</div>
            </div>
            <button type="button" class="secondary-button open-manual-btn" id="cliente-open-manual-btn" title="Abrir el manual integrado">Abrir manual</button>
          </div>
          <div class="subpage-buttons" id="cliente-subpage-buttons">
            <button type="button" class="subpage-button active" data-cliente-tab="alta">Nuevo cliente</button>
            <button type="button" class="subpage-button" data-cliente-tab="consulta">Consultar y editar</button>
            <button type="button" class="subpage-button" data-cliente-tab="contactos">Contactos</button>
            <button type="button" class="subpage-button" data-cliente-tab="domicilios">Domicilios</button>
            <button type="button" class="subpage-button" data-cliente-tab="condiciones">Condiciones</button>
            <button type="button" class="subpage-button" data-cliente-tab="manual">Manual</button>
          </div>
        </div>
        <div class="grid">
          <article class="card" data-cliente-tab-panel="alta">
            <h3>Nuevo cliente</h3>
            <div class="hint">Ficha general del cliente para venta, operacion y facturacion.</div>
            <form id="cliente-form">
              <label>Razon social
                <input name="razon_social" required />
              </label>
              <div class="two-col">
                <label>Nombre comercial
                  <input name="nombre_comercial" />
                </label>
                <label>Tipo cliente
                  <select name="tipo_cliente">
                    <option value="embarcador">embarcador</option>
                    <option value="consignatario">consignatario</option>
                    <option value="pagador">pagador</option>
                    <option value="corporativo">corporativo</option>
                    <option value="mixto" selected>mixto</option>
                  </select>
                </label>
              </div>
              <div class="three-col">
                <label>RFC
                  <input name="rfc" />
                </label>
                <label>Sector
                  <input name="sector" />
                </label>
                <label>Origen prospecto
                  <input name="origen_prospecto" placeholder="referido, web, directo..." />
                </label>
              </div>
              <div class="three-col">
                <label>Email general
                  <input name="email" type="email" />
                </label>
                <label>Telefono general
                  <input name="telefono" />
                </label>
                <label>Sitio web
                  <input name="sitio_web" />
                </label>
              </div>
              <label>Domicilio fiscal
                <textarea name="direccion"></textarea>
              </label>
              <div class="two-col">
                <label>Notas operativas
                  <textarea name="notas_operativas"></textarea>
                </label>
                <label>Notas comerciales
                  <textarea name="notas_comerciales"></textarea>
                </label>
              </div>
              <label class="check-row">
                <input name="activo" type="checkbox" checked />
                Cliente activo
              </label>
              <button type="submit">Guardar cliente</button>
            </form>
            <div id="cliente-message" class="message"></div>
          </article>
          <article class="card hidden" data-cliente-tab-panel="consulta">
            <h3>Listado de clientes</h3>
            <div class="toolbar">
              <h4>Consultar clientes</h4>
              <div class="filtro-busqueda-modo hint">
                <label>Como buscar el texto
                  <select class="buscar-modo-sync" title="Mismo criterio en todos los listados del panel; se guarda en el navegador">
                    <option value="contiene">Contiene (flexible, recomendado)</option>
                    <option value="prefijo_palabras">Prefijos de palabra (ej. Ro coincide con Rodriguez)</option>
                    <option value="todas_palabras">Todas las palabras, en cualquier orden</option>
                  </select>
                </label>
              </div>
              <form id="cliente-filter-form">
                <div class="two-col">
                  <label>Buscar por razon social
                    <input id="cliente-filter-buscar" name="buscar" list="cliente-filter-buscar-dl" placeholder="Nombre, comercial o RFC" autocomplete="off" />
                  </label>
                  <label>Estatus
                    <select id="cliente-filter-activo" name="activo">
                      <option value="">Todos</option>
                      <option value="true">Activos</option>
                      <option value="false">Inactivos</option>
                    </select>
                  </label>
                </div>
                <datalist id="cliente-filter-buscar-dl"></datalist>
                <div class="toolbar-actions">
                  <button type="submit">Aplicar filtro</button>
                  <button type="button" id="cliente-filter-clear" class="secondary-button">Limpiar</button>
                </div>
              </form>
            </div>
            <div id="clientes-table"></div>
            <div id="cliente-edit-panel" class="toolbar hidden">
              <h4>Editar cliente</h4>
              <p class="hint">
                Horario de carga, horario de descarga e instrucciones de acceso <strong>no</strong> van aquí: son datos de cada
                <strong>domicilio operativo</strong> (carga, descarga, fiscal, etc.). Captúralos en la subopción
                <strong>Domicilios</strong> (barra superior de este módulo), eligiendo el cliente y luego <strong>Editar</strong> en la fila del domicilio.
              </p>
              <div class="toolbar-actions">
                <button type="button" id="cliente-edit-open-contactos" class="secondary-button">Ir a Contactos de este cliente</button>
                <button type="button" id="cliente-edit-open-domicilios" class="secondary-button">Ir a Domicilios de este cliente</button>
              </div>
              <form id="cliente-edit-form">
                <input name="id" type="hidden" />
                <label>Razon social
                  <input name="razon_social" required />
                </label>
                <div class="two-col">
                  <label>Nombre comercial
                    <input name="nombre_comercial" />
                  </label>
                  <label>Tipo cliente
                    <select name="tipo_cliente">
                      <option value="embarcador">embarcador</option>
                      <option value="consignatario">consignatario</option>
                      <option value="pagador">pagador</option>
                      <option value="corporativo">corporativo</option>
                      <option value="mixto">mixto</option>
                    </select>
                  </label>
                </div>
                <div class="three-col">
                  <label>RFC
                    <input name="rfc" />
                  </label>
                  <label>Sector
                    <input name="sector" />
                  </label>
                  <label>Origen prospecto
                    <input name="origen_prospecto" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Email general
                    <input name="email" type="email" />
                  </label>
                  <label>Telefono general
                    <input name="telefono" />
                  </label>
                  <label>Sitio web
                    <input name="sitio_web" />
                  </label>
                </div>
                <label>Domicilio fiscal
                  <textarea name="direccion"></textarea>
                </label>
                <div class="two-col">
                  <label>Notas operativas
                    <textarea name="notas_operativas"></textarea>
                  </label>
                  <label>Notas comerciales
                    <textarea name="notas_comerciales"></textarea>
                  </label>
                </div>
                <label class="check-row">
                  <input name="activo" type="checkbox" />
                  Cliente activo
                </label>
                <div class="toolbar-actions">
                  <button type="submit">Guardar cambios</button>
                  <button type="button" id="cliente-edit-cancel" class="secondary-button">Cancelar</button>
                </div>
              </form>
              <div id="cliente-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card hidden" data-cliente-tab-panel="contactos">
            <h3>Contactos del cliente</h3>
            <div class="hint">Registra contactos de trafico, facturacion, cobranza o almacen.</div>
            <div class="hint">Enter pasa al siguiente campo; al terminar, Enter con foco en Guardar contacto guarda.</div>
            <div class="hint">Los contactos ya guardados aparecen en la <strong>tabla de abajo</strong>. El bloque superior es solo para <strong>dar de alta</strong> un contacto nuevo (por eso los campos suelen ir vacíos).</div>
            <h4 class="capture-section-title">Nuevo contacto</h4>
            <div id="cliente-contacto-form" class="contacto-capture" role="group" aria-label="Nuevo contacto del cliente">
              <label>Cliente
                <select id="cliente-contacto-cliente" name="cliente_id" required></select>
              </label>
              <div id="cliente-contacto-summary" class="hint"></div>
              <div class="two-col">
                <label>Nombre
                  <input id="cliente-contacto-nombre" name="nombre" required autocomplete="off" />
                </label>
                <label>Area
                  <input id="cliente-contacto-area" name="area" placeholder="trafico, cobranza..." autocomplete="off" />
                </label>
              </div>
              <div class="two-col">
                <label>Puesto
                  <input id="cliente-contacto-puesto" name="puesto" autocomplete="off" />
                </label>
                <label>Email
                  <input id="cliente-contacto-email" name="email" type="email" autocomplete="off" />
                </label>
              </div>
              <div class="three-col">
                <label>Telefono
                  <input id="cliente-contacto-telefono" name="telefono" autocomplete="off" />
                </label>
                <label>Extension
                  <input id="cliente-contacto-extension" name="extension" autocomplete="off" />
                </label>
                <label>Celular
                  <input id="cliente-contacto-celular" name="celular" autocomplete="off" />
                </label>
              </div>
              <div class="two-col">
                <label class="check-row">
                  <input id="cliente-contacto-principal" name="principal" type="checkbox" />
                  Contacto principal
                </label>
                <label class="check-row">
                  <input id="cliente-contacto-activo" name="activo" type="checkbox" checked />
                  Contacto activo
                </label>
              </div>
            </div>
            <div class="toolbar-actions">
              <button type="button" id="cliente-contacto-guardar" data-primary-action="save">Guardar contacto</button>
              <button type="button" id="cliente-contacto-cancel-clear" class="secondary-button">Cancelar y limpiar</button>
            </div>
            <div id="cliente-contacto-message" class="message"></div>
            <div id="cliente-contactos-table" class="contacto-table-wrap"></div>
            <div id="cliente-contacto-edit-panel" class="toolbar hidden" aria-hidden="true">
              <h4>Editar contacto</h4>
              <p class="hint" style="margin:0 0 8px">Este bloque solo aparece al pulsar <strong>Editar</strong> en la tabla. No es un segundo alta: usa arriba <strong>Nuevo contacto</strong> para agregar.</p>
              <form id="cliente-contacto-edit-form" onsubmit="return false;">
                <input name="id" type="hidden" />
                <input type="hidden" id="cliente-contacto-path-cliente" />
                <label>Filtrar cliente (escribe para acortar la lista)
                  <input type="search" id="cliente-contacto-edit-buscar" placeholder="Razon social, nombre comercial o RFC" autocomplete="off" />
                </label>
                <label>Cliente
                  <select id="cliente-contacto-edit-cliente" name="cliente_id" required></select>
                </label>
                <div class="hint">Abre la lista o escribe arriba para filtrar. Si cambias de cliente y guardas, el contacto pasa a ese cliente.</div>
                <div class="two-col">
                  <label>Nombre
                    <input name="nombre" required />
                  </label>
                  <label>Area
                    <input name="area" />
                  </label>
                </div>
                <div class="two-col">
                  <label>Puesto
                    <input name="puesto" />
                  </label>
                  <label>Email
                    <input name="email" type="email" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Telefono
                    <input name="telefono" />
                  </label>
                  <label>Extension
                    <input name="extension" />
                  </label>
                  <label>Celular
                    <input name="celular" />
                  </label>
                </div>
                <div class="two-col">
                  <label class="check-row">
                    <input name="principal" type="checkbox" />
                    Contacto principal
                  </label>
                  <label class="check-row">
                    <input name="activo" type="checkbox" />
                    Contacto activo
                  </label>
                </div>
              </form>
              <div class="toolbar-actions">
                <button type="button" id="cliente-contacto-edit-guardar" data-primary-action="save">Guardar cambios</button>
                <button type="button" id="cliente-contacto-edit-cancel" class="secondary-button">Cancelar</button>
              </div>
              <div id="cliente-contacto-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card hidden" data-cliente-tab-panel="domicilios">
            <h3>Domicilios del cliente</h3>
            <div class="hint">Puntos de carga, descarga, fiscal o sedes del cliente. Aquí se capturan horarios de carga/descarga e instrucciones de acceso por cada domicilio. Para editarlos, elige el cliente y pulsa <strong>Editar</strong> en la tabla.</div>
            <form id="cliente-domicilio-form">
              <label>Filtrar cliente (escribe para acortar la lista)
                <input type="search" id="cliente-domicilio-buscar" placeholder="Razon social, nombre comercial o RFC" autocomplete="off" />
              </label>
              <label>Cliente
                <select id="cliente-domicilio-cliente" name="cliente_id" required></select>
              </label>
              <div class="hint">El buscador acorta la lista; si no ves al cliente, borra el texto o cambia la busqueda.</div>
              <div id="cliente-domicilio-summary" class="hint"></div>
              <div class="two-col">
                <label>Tipo domicilio
                  <input name="tipo_domicilio" placeholder="fiscal, carga, descarga..." required />
                </label>
                <label>Nombre sede
                  <input name="nombre_sede" required />
                </label>
              </div>
              <label>Direccion completa
                <textarea name="direccion_completa" required></textarea>
              </label>
              <div class="three-col">
                <label>Municipio
                  <input name="municipio" />
                </label>
                <label>Estado
                  <input name="estado" />
                </label>
                <label>Codigo postal
                  <input name="codigo_postal" />
                </label>
              </div>
              <div class="two-col">
                <label>Horario carga
                  <input name="horario_carga" />
                </label>
                <label>Horario descarga
                  <input name="horario_descarga" />
                </label>
              </div>
              <label>Instrucciones acceso
                <textarea name="instrucciones_acceso"></textarea>
              </label>
              <label class="check-row">
                <input name="activo" type="checkbox" checked />
                Domicilio activo
              </label>
              <button type="submit">Guardar domicilio</button>
            </form>
            <div id="cliente-domicilio-message" class="message"></div>
            <div id="cliente-domicilios-table"></div>
            <div id="cliente-domicilio-edit-panel" class="toolbar hidden">
              <h4>Editar domicilio</h4>
              <form id="cliente-domicilio-edit-form">
                <input name="id" type="hidden" />
                <input name="cliente_id" type="hidden" />
                <label>Cliente
                  <input name="cliente_label" readonly />
                </label>
                <div class="two-col">
                  <label>Tipo domicilio
                    <input name="tipo_domicilio" required />
                  </label>
                  <label>Nombre sede
                    <input name="nombre_sede" required />
                  </label>
                </div>
                <label>Direccion completa
                  <textarea name="direccion_completa" required></textarea>
                </label>
                <div class="three-col">
                  <label>Municipio
                    <input name="municipio" />
                  </label>
                  <label>Estado
                    <input name="estado" />
                  </label>
                  <label>Codigo postal
                    <input name="codigo_postal" />
                  </label>
                </div>
                <div class="two-col">
                  <label>Horario carga
                    <input name="horario_carga" />
                  </label>
                  <label>Horario descarga
                    <input name="horario_descarga" />
                  </label>
                </div>
                <label>Instrucciones acceso
                  <textarea name="instrucciones_acceso"></textarea>
                </label>
                <label class="check-row">
                  <input name="activo" type="checkbox" />
                  Domicilio activo
                </label>
                <div class="toolbar-actions">
                  <button type="submit">Guardar cambios</button>
                  <button type="button" id="cliente-domicilio-edit-cancel" class="secondary-button">Cancelar</button>
                </div>
              </form>
              <div id="cliente-domicilio-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card hidden" data-cliente-tab-panel="condiciones">
            <h3>Condiciones comerciales</h3>
            <div class="hint">Credito, moneda y requisitos para facturacion u operacion.</div>
            <div class="hint">Enter en un campo pasa al siguiente; en observaciones Enter hace salto de linea. Guarde con el boton al final.</div>
            <form id="cliente-condicion-form">
              <label>Cliente
                <select id="cliente-condicion-cliente" name="cliente_id" required></select>
              </label>
              <div id="cliente-condicion-selected-summary" class="hint"></div>
              <div class="three-col">
                <label>Dias credito
                  <input name="dias_credito" type="number" min="0" step="1" inputmode="numeric" title="Solo numeros enteros (sin decimales)" />
                </label>
                <label>Limite credito
                  <input name="limite_credito" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                </label>
                <label>Moneda preferida
                  <input name="moneda_preferida" value="MXN" maxlength="3" />
                </label>
              </div>
              <div class="two-col">
                <label>Forma pago
                  <input name="forma_pago" placeholder="transferencia, PPD..." />
                </label>
                <label>Uso CFDI
                  <input name="uso_cfdi" placeholder="G03, S01..." />
                </label>
              </div>
              <div class="three-col">
                <label class="check-row">
                  <input name="requiere_oc" type="checkbox" />
                  Requiere OC
                </label>
                <label class="check-row">
                  <input name="requiere_cita" type="checkbox" />
                  Requiere cita
                </label>
                <label class="check-row">
                  <input name="bloqueado_credito" type="checkbox" />
                  Bloqueado por credito
                </label>
              </div>
              <label>Observaciones credito
                <textarea name="observaciones_credito"></textarea>
              </label>
              <button type="submit">Guardar condiciones</button>
            </form>
            <div id="cliente-condicion-message" class="message"></div>
            <div id="cliente-condicion-summary" class="hint"></div>
          </article>
          <article class="card hidden manual-doc manual-interface" data-cliente-tab-panel="manual">
            <div class="manual-interface-head">
              <h3>Manual del módulo Clientes</h3>
              <span class="manual-badge" title="Contenido completo en esta pantalla">Documentación en pantalla</span>
            </div>
            <div class="hint">Documento de apoyo integrado en la aplicación. La información se registra en el servidor a través de la API; el tono de esta guía es formal en el marco general y operativo en los procedimientos. Use el índice lateral para saltar entre secciones; el texto largo se desplaza dentro del panel derecho.</div>

            <div class="manual-interface-body">
              <nav class="manual-toc" id="manual-clientes-toc" aria-label="Índice del manual de clientes">
                <div class="manual-toc-title">Contenido</div>
                <a href="#manual-clientes-1">1. Objetivo del módulo</a>
                <a href="#manual-clientes-2">2. Subopciones</a>
                <a href="#manual-clientes-3">3. Nuevo cliente</a>
                <a href="#manual-clientes-4">4. Consultar y editar</a>
                <a href="#manual-clientes-5">5. Contactos</a>
                <a href="#manual-clientes-6">6. Domicilios</a>
                <a href="#manual-clientes-7">7. Condiciones comerciales</a>
                <a href="#manual-clientes-8">8. Ejemplos de texto</a>
                <a href="#manual-clientes-9">9. Preguntas frecuentes</a>
                <a href="#manual-clientes-10">10. Mensajes y errores</a>
                <a href="#manual-clientes-11">11. Referencia técnica</a>
              </nav>
              <div class="manual-scroll" data-manual-scroll="clientes" tabindex="0" role="region" aria-label="Texto del manual de clientes">
            <div class="manual-note">
              <strong>Secuencia operativa recomendada:</strong> (1) Registrar la ficha en <strong>Nuevo cliente</strong>. (2) Capturar <strong>Contactos</strong> y <strong>Domicilios</strong> según corresponda al negocio. (3) Registrar <strong>Condiciones</strong> comerciales. (4) Utilizar <strong>Consultar y editar</strong> para auditoría o correcciones puntuales de la ficha.
            </div>

            <h4 id="manual-clientes-1">1. Objetivo del módulo</h4>
            <p class="manual-p">El módulo tiene por finalidad centralizar la información maestra del cliente (incluidos roles tales como embarcador o pagador), así como los contactos de trabajo, los domicilios operativos y las condiciones de crédito y facturación. La división en subopciones permite mantener la captura estructurada y reducir errores de mezcla de datos.</p>

            <h4 id="manual-clientes-2">2. Subopciones (barra superior)</h4>
            <ul class="summary-list">
              <li><strong>Nuevo cliente:</strong> registro de la ficha general: razón social, tipo, RFC, datos corporativos, domicilio fiscal en texto libre y notas.</li>
              <li><strong>Consultar y editar:</strong> búsqueda, visualización tabular y edición del registro seleccionado.</li>
              <li><strong>Contactos:</strong> personas de contacto para tráfico, facturación, cobranza, almacén u otras áreas.</li>
              <li><strong>Domicilios:</strong> ubicaciones operativas con dirección, horarios e instrucciones de acceso.</li>
              <li><strong>Condiciones:</strong> plazos y límites de crédito, moneda, forma de pago, uso CFDI e indicadores de orden de compra, cita y bloqueo.</li>
              <li><strong>Manual:</strong> la presente guía.</li>
            </ul>
            <p class="manual-p"><strong>Sincronización entre pestañas:</strong> al modificar el cliente seleccionado en <strong>Contactos</strong>, <strong>Domicilios</strong> o <strong>Condiciones</strong>, la aplicación replica la misma selección en los selectores de las otras dos subopciones, de modo que pueda continuar el trabajo sobre un mismo cliente sin volver a elegirlo manualmente.</p>

            <h4 id="manual-clientes-3">3. Nuevo cliente</h4>
            <p class="manual-p">El único campo obligatorio es <strong>Razón social</strong>. Se recomienda completar el resto de acuerdo con las políticas internas de ventas, operaciones y facturación.</p>
            <h5>Descripción de campos</h5>
            <ul class="summary-list">
              <li><strong>Nombre comercial:</strong> denominación habitual en operación o en documentos no fiscales.</li>
              <li><strong>Tipo cliente:</strong> clasificación operativa (embarcador, consignatario, pagador, corporativo, mixto). Valor predeterminado: mixto.</li>
              <li><strong>RFC, sector, origen prospecto:</strong> identificación fiscal y, en su caso, seguimiento del origen del prospecto.</li>
              <li><strong>Correo electrónico, teléfono y sitio web (generales):</strong> datos a nivel empresa; no sustituyen el detalle de personas de contacto en la subopción Contactos.</li>
              <li><strong>Domicilio fiscal:</strong> texto para fines de facturación; las ubicaciones operativas múltiples se registran en Domicilios.</li>
              <li><strong>Notas operativas y comerciales:</strong> información interna acordada para operación o fuerza de ventas.</li>
              <li><strong>Cliente activo:</strong> si se desactiva, el registro podrá excluirse por filtro de inactivos y dejará de considerarse en los flujos habituales.</li>
            </ul>
            <p class="manual-p"><strong>Procedimiento:</strong> capture la información y pulse <strong>Guardar cliente</strong>. Verifique el mensaje inmediatamente debajo del formulario: confirmará el resultado o mostrará la causa de rechazo devuelta por el servidor.</p>

            <h4 id="manual-clientes-4">4. Consultar y editar</h4>
            <p class="manual-p">El criterio de búsqueda aplica sobre <strong>razón social</strong>, <strong>nombre comercial</strong> y <strong>RFC</strong>, sin distinción de mayúsculas. El resultado se recalcula de forma automática al escribir en el campo de búsqueda y al cambiar <strong>Estatus</strong> (Todos, Activos, Inactivos). El control <strong>Aplicar filtro</strong> ejecuta la misma actualización para quien prefiera validar el criterio mediante un envío explícito.</p>
            <ul class="summary-list">
              <li><strong>Coincidencia única:</strong> si el filtro deja un solo registro, el panel <strong>Editar cliente</strong> se abre de forma automática con dicho cliente.</li>
              <li><strong>Tabla de resultados:</strong> columnas ID, razón social, nombre comercial, tipo, RFC, conteo de contactos y domicilios, estatus y acción <strong>Editar</strong>.</li>
              <li><strong>Limpiar:</strong> restablece filtros, muestra el universo completo y cierra el panel de edición si estaba visible.</li>
              <li><strong>Edición:</strong> los campos son análogos al alta; confirme con <strong>Guardar cambios</strong> o descarte con <strong>Cancelar</strong>.</li>
            </ul>

            <h4 id="manual-clientes-5">5. Contactos del cliente</h4>
            <p class="manual-p">Bajo el selector aparece un <strong>resumen</strong> del cliente (identificador, razón social, nombre comercial, RFC y conteos). Utilícelo como verificación previa antes de capturar o modificar contactos.</p>
            <ol class="summary-list">
              <li>Seleccione el <strong>Cliente</strong>. El campo <strong>Nombre</strong> del contacto es obligatorio; el resto de campos son opcionales pero se suelen completar para trazabilidad.</li>
              <li>Marque <strong>Contacto principal</strong> y <strong>Contacto activo</strong> conforme a la política de su organización.</li>
              <li>Teclado: la tecla <strong>Enter</strong> avanza al siguiente campo; con el foco en <strong>Guardar contacto</strong>, Enter envía la captura.</li>
              <li><strong>Cancelar y limpiar</strong> descarta la captura en curso sin persistir datos.</li>
              <li>En la grilla, <strong>Editar</strong> abre el panel inferior. Mediante <strong>Filtrar cliente</strong> puede acotar el listado; si modifica el cliente y guarda, el contacto queda <strong>reasignado</strong> al cliente indicado (corrección de error o cambio de cuenta).</li>
              <li><strong>Eliminar</strong> solicita confirmación antes de borrar el registro.</li>
            </ol>

            <h4 id="manual-clientes-6">6. Domicilios</h4>
            <p class="manual-p">Obligatorios: <strong>Cliente</strong>, <strong>Tipo domicilio</strong>, <strong>Nombre sede</strong> y <strong>Dirección completa</strong>. El tipo debe reflejar el uso operativo (por ejemplo fiscal, carga, descarga).</p>
            <ul class="summary-list">
              <li><strong>Municipio, estado, código postal:</strong> completar según requerimientos de reportes o de instructivos de ruta.</li>
              <li><strong>Horarios de carga y descarga:</strong> ventanas acordadas contractualmente o operativamente.</li>
              <li><strong>Instrucciones de acceso:</strong> requisitos de seguridad, citas en caseta, muelle asignado, contacto en planta, EPP, etc.</li>
              <li><strong>Domicilio activo:</strong> desmarcar cuando el punto deje de estar vigente.</li>
              <li><strong>Edición desde la tabla:</strong> el cliente se muestra en solo lectura; ajuste los demás campos y guarde o cancele.</li>
              <li><strong>Eliminar:</strong> requiere confirmación.</li>
            </ul>

            <h4 id="manual-clientes-7">7. Condiciones comerciales</h4>
            <ul class="summary-list">
              <li><strong>Días de crédito y límite de crédito:</strong> valores numéricos no negativos; el límite admite decimales.</li>
              <li><strong>Moneda preferida:</strong> convención habitual de tres caracteres (el formulario sugiere MXN).</li>
              <li><strong>Forma de pago y uso CFDI:</strong> texto libre alineado a catálogos internos y a criterio fiscal; véase la sección 8.</li>
              <li><strong>Requiere OC, Requiere cita, Bloqueado por crédito:</strong> indicadores para operación y cobranza; su efecto en otros módulos depende de las reglas que defina la empresa.</li>
              <li><strong>Observaciones de crédito:</strong> acuerdos especiales, garantías o seguimiento de incidencias.</li>
              <li>Pulse <strong>Guardar condiciones</strong> para persistir la configuración del cliente seleccionado.</li>
            </ul>

            <h4 id="manual-clientes-8">8. Ejemplos de texto (referencia operativa)</h4>
            <p class="manual-p">Los campos citados admiten texto libre. Para uniformar criterios, puede adoptar las convenciones corporativas y, en su defecto, tomar como referencia los ejemplos siguientes, habituales en el entorno fiscal mexicano.</p>
            <h5>Tipo de domicilio</h5>
            <ul class="summary-list">
              <li><strong>Fiscal:</strong> alineado a datos de facturación y RFC.</li>
              <li><strong>Carga o recolección:</strong> origen de mercancía o punto de retiro.</li>
              <li><strong>Descarga o entrega:</strong> destino o muelle de descarga.</li>
              <li><strong>Oficinas o corporativo:</strong> sede administrativa sin movimiento de carga.</li>
              <li><strong>Almacén o cross-dock:</strong> consolidación o transbordo.</li>
            </ul>
            <p class="manual-p">En <strong>Nombre sede</strong> se recomienda una etiqueta breve y única, por ejemplo: Planta Querétaro, CEDIS Guadalajara, Oficinas Ciudad de México.</p>
            <h5>Forma de pago</h5>
            <ul class="summary-list">
              <li>Referencias frecuentes: transferencia electrónica; <strong>PPD</strong> (pago en parcialidades o diferido); <strong>PUE</strong> (pago en una exhibición); cheque nominativo.</li>
              <li>Si aplica complemento de recepción de pagos, el texto debe ser coherente con contabilidad y con los requerimientos del SAT.</li>
            </ul>
            <h5>Uso CFDI</h5>
            <ul class="summary-list">
              <li>Ejemplos de claves de uso frecuentes: <strong>G03</strong> (gastos en general), <strong>G01</strong> (adquisición de mercancías), <strong>I04</strong> (equipo de transporte), <strong>P01</strong> (por definir, cuando aplique), <strong>S01</strong> (sin efectos fiscales, según normativa aplicable).</li>
              <li>La vigencia y el sentido exacto de cada clave deben validarse con el área fiscal y con los catálogos actualizados del SAT.</li>
            </ul>

            <h4 id="manual-clientes-9">9. Preguntas frecuentes</h4>
            <h5>No aparece el cliente en Contactos o Domicilios</h5>
            <p class="manual-p">Verifique que el alta se haya guardado correctamente en <strong>Nuevo cliente</strong> y que el estatus sea coherente con sus filtros (por ejemplo, activo). Si el registro es reciente, recargue la vista o vuelva a entrar al módulo para forzar la actualización del catálogo en pantalla.</p>
            <h5>Relación entre el domicilio fiscal del alta y los registros en Domicilios</h5>
            <p class="manual-p">No son equivalentes por definición. El domicilio fiscal en la ficha general es un campo de texto para facturación; la subopción <strong>Domicilios</strong> permite uno o varios puntos operativos con nombre de sede y detalle estructurado.</p>
            <h5>Uso del indicador «Bloqueado por crédito»</h5>
            <p class="manual-p">Registra una restricción de crédito visible para ventas y operación. La forma en que dicho bloqueo se traduzca en otros procesos (por ejemplo viajes o facturación) depende de las políticas internas de la organización.</p>
            <h5>Reasignación de un contacto a otro cliente</h5>
            <p class="manual-p">Procedimiento: abra <strong>Editar contacto</strong>, seleccione el cliente destino en el listado (use el filtro si el catálogo es extenso) y ejecute <strong>Guardar cambios</strong>. El contacto quedará asociado al nuevo cliente.</p>
            <h5>Apertura automática del panel de edición al filtrar</h5>
            <p class="manual-p">Cuando el criterio de búsqueda produce exactamente un resultado, el sistema abre <strong>Editar cliente</strong> de forma automática. Si existen varias coincidencias, deberá pulsar <strong>Editar</strong> en la fila correspondiente.</p>

            <h4 id="manual-clientes-10">10. Mensajes y errores</h4>
            <p class="manual-p">Los mensajes bajo cada formulario reproducen la respuesta del servidor (operación exitosa, validación de datos o reglas de negocio). Si las tablas permanecen vacías de forma inesperada, verifique la conectividad y el estado del servicio de API.</p>

            <h4 id="manual-clientes-11">11. Referencia técnica</h4>
            <p class="manual-p">Para consultar rutas, esquemas JSON y pruebas interactivas, utilice la documentación Swagger en <a href="/docs">/docs</a>.</p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="page" id="page-transportistas">
        <div class="card">
          <div class="module-subpage-head">
            <div>
              <h3>Subopciones de transportistas</h3>
              <div class="hint">Trabaja una parte del transportista a la vez para evitar confusión.</div>
            </div>
            <button type="button" class="secondary-button open-manual-btn" id="transportista-open-manual-btn" title="Abrir el manual integrado">Abrir manual</button>
          </div>
          <div class="subpage-buttons" id="transportista-subpage-buttons">
            <button type="button" class="subpage-button" data-transportista-tab="alta">Nuevo transportista</button>
            <button type="button" class="subpage-button active" data-transportista-tab="consulta">Consultar y editar</button>
            <button type="button" class="subpage-button" data-transportista-tab="contactos">Contactos</button>
            <button type="button" class="subpage-button" data-transportista-tab="documentos">Documentos</button>
            <button type="button" class="subpage-button" data-transportista-tab="manual">Manual</button>
          </div>
        </div>
        <div class="grid">
          <article class="card hidden" data-transportista-tab-panel="alta">
            <h3>Nuevo transportista</h3>
            <div class="hint">Maestro del proveedor de transporte con datos fiscales, operativos y comerciales.</div>
            <form id="transportista-form">
              <div class="two-col">
                <label>Razon social
                  <input name="nombre" required />
                </label>
                <label>Nombre comercial
                  <input name="nombre_comercial" />
                </label>
              </div>
              <div class="three-col">
                <label>Tipo transportista
                  <select name="tipo_transportista">
                    <option value="propio">propio</option>
                    <option value="subcontratado" selected>subcontratado</option>
                    <option value="fletero">fletero</option>
                    <option value="aliado">aliado</option>
                  </select>
                </label>
                <label>Tipo persona
                  <select name="tipo_persona">
                    <option value="fisica">fisica</option>
                    <option value="moral" selected>moral</option>
                  </select>
                </label>
                <label>Estatus
                  <select name="estatus">
                    <option value="activo" selected>activo</option>
                    <option value="inactivo">inactivo</option>
                    <option value="bloqueado">bloqueado</option>
                  </select>
                </label>
              </div>
              <div class="three-col">
                <label>RFC
                  <input name="rfc" />
                </label>
                <label>CURP
                  <input name="curp" />
                </label>
                <label>Regimen fiscal
                  <input name="regimen_fiscal" />
                </label>
              </div>
              <div class="three-col">
                <label>Fecha alta
                  <input name="fecha_alta" type="date" />
                </label>
                <label>Nivel confianza
                  <select name="nivel_confianza">
                    <option value="alto">alto</option>
                    <option value="medio" selected>medio</option>
                    <option value="bajo">bajo</option>
                  </select>
                </label>
                <label>Prioridad asignacion
                  <input name="prioridad_asignacion" type="number" min="0" step="1" inputmode="numeric" value="0" title="Solo numeros enteros" />
                </label>
              </div>
              <div class="two-col">
                <label>Contacto principal
                  <input name="contacto" />
                </label>
                <label>Telefono general
                  <input name="telefono" />
                </label>
              </div>
              <div class="three-col">
                <label>Email general
                  <input name="email" type="email" />
                </label>
                <label>Sitio web
                  <input name="sitio_web" />
                </label>
                <label>Codigo postal
                  <input name="codigo_postal" />
                </label>
              </div>
              <div class="three-col">
                <label>Ciudad
                  <input name="ciudad" />
                </label>
                <label>Estado
                  <input name="estado" />
                </label>
                <label>Pais
                  <input name="pais" value="Mexico" />
                </label>
              </div>
              <label>Direccion fiscal
                <textarea name="direccion_fiscal"></textarea>
              </label>
              <label>Direccion operativa
                <textarea name="direccion_operativa"></textarea>
              </label>
              <div class="two-col">
                <label>Notas operativas
                  <textarea name="notas_operativas"></textarea>
                </label>
                <label>Notas comerciales
                  <textarea name="notas_comerciales"></textarea>
                </label>
              </div>
              <div class="two-col">
                <label class="check-row">
                  <input name="blacklist" type="checkbox" />
                  En blacklist
                </label>
                <label class="check-row">
                  <input name="activo" type="checkbox" checked />
                  Transportista activo
                </label>
              </div>
              <button type="submit">Guardar transportista</button>
            </form>
            <div id="transportista-message" class="message"></div>
          </article>
          <article class="card" data-transportista-tab-panel="consulta">
            <h3>Listado de transportistas</h3>
            <div class="toolbar">
              <h4>Consultar transportistas</h4>
              <div class="filtro-busqueda-modo hint">
                <label>Como buscar el texto
                  <select class="buscar-modo-sync" title="Mismo criterio en todos los listados del panel; se guarda en el navegador">
                    <option value="contiene">Contiene (flexible, recomendado)</option>
                    <option value="prefijo_palabras">Prefijos de palabra (ej. Ro coincide con Rodriguez)</option>
                    <option value="todas_palabras">Todas las palabras, en cualquier orden</option>
                  </select>
                </label>
              </div>
              <form id="transportista-filter-form">
                <div class="two-col">
                  <label>Buscar por razon social
                    <input id="transportista-filter-buscar" name="buscar" list="transportista-filter-buscar-dl" placeholder="Nombre, comercial o RFC" autocomplete="off" />
                  </label>
                  <label>Estatus
                    <select id="transportista-filter-estatus" name="estatus">
                      <option value="">Todos</option>
                      <option value="activo">activo</option>
                      <option value="inactivo">inactivo</option>
                      <option value="bloqueado">bloqueado</option>
                    </select>
                  </label>
                </div>
                <div class="two-col">
                  <label>Tipo transportista
                    <select id="transportista-filter-tipo" name="tipo_transportista">
                      <option value="">Todos</option>
                      <option value="propio">propio</option>
                      <option value="subcontratado">subcontratado</option>
                      <option value="fletero">fletero</option>
                      <option value="aliado">aliado</option>
                    </select>
                  </label>
                </div>
                <datalist id="transportista-filter-buscar-dl"></datalist>
                <div class="toolbar-actions">
                  <button type="submit">Aplicar filtro</button>
                  <button type="button" id="transportista-filter-clear" class="secondary-button">Limpiar</button>
                </div>
              </form>
            </div>
            <div id="transportistas-table"></div>
            <div id="transportista-edit-panel" class="toolbar hidden">
              <h4>Editar transportista</h4>
              <form id="transportista-edit-form">
                <input name="id" type="hidden" />
                <div class="two-col">
                  <label>Razon social
                    <input name="nombre" required />
                  </label>
                  <label>Nombre comercial
                    <input name="nombre_comercial" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Tipo transportista
                    <select name="tipo_transportista">
                      <option value="propio">propio</option>
                      <option value="subcontratado">subcontratado</option>
                      <option value="fletero">fletero</option>
                      <option value="aliado">aliado</option>
                    </select>
                  </label>
                  <label>Tipo persona
                    <select name="tipo_persona">
                      <option value="fisica">fisica</option>
                      <option value="moral">moral</option>
                    </select>
                  </label>
                  <label>Estatus
                    <select name="estatus">
                      <option value="activo">activo</option>
                      <option value="inactivo">inactivo</option>
                      <option value="bloqueado">bloqueado</option>
                    </select>
                  </label>
                </div>
                <div class="three-col">
                  <label>RFC
                    <input name="rfc" />
                  </label>
                  <label>CURP
                    <input name="curp" />
                  </label>
                  <label>Regimen fiscal
                    <input name="regimen_fiscal" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Fecha alta
                    <input name="fecha_alta" type="date" />
                  </label>
                  <label>Nivel confianza
                    <select name="nivel_confianza">
                      <option value="alto">alto</option>
                      <option value="medio">medio</option>
                      <option value="bajo">bajo</option>
                    </select>
                  </label>
                  <label>Prioridad asignacion
                    <input name="prioridad_asignacion" type="number" min="0" step="1" inputmode="numeric" title="Solo numeros enteros" />
                  </label>
                </div>
                <div class="two-col">
                  <label>Contacto principal
                    <input name="contacto" />
                  </label>
                  <label>Telefono general
                    <input name="telefono" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Email general
                    <input name="email" type="email" />
                  </label>
                  <label>Sitio web
                    <input name="sitio_web" />
                  </label>
                  <label>Codigo postal
                    <input name="codigo_postal" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Ciudad
                    <input name="ciudad" />
                  </label>
                  <label>Estado
                    <input name="estado" />
                  </label>
                  <label>Pais
                    <input name="pais" />
                  </label>
                </div>
                <label>Direccion fiscal
                  <textarea name="direccion_fiscal"></textarea>
                </label>
                <label>Direccion operativa
                  <textarea name="direccion_operativa"></textarea>
                </label>
                <div class="two-col">
                  <label>Notas operativas
                    <textarea name="notas_operativas"></textarea>
                  </label>
                  <label>Notas comerciales
                    <textarea name="notas_comerciales"></textarea>
                  </label>
                </div>
                <div class="two-col">
                  <label class="check-row">
                    <input name="blacklist" type="checkbox" />
                    En blacklist
                  </label>
                  <label class="check-row">
                    <input name="activo" type="checkbox" />
                    Transportista activo
                  </label>
                </div>
                <div class="toolbar-actions">
                  <button type="submit">Guardar cambios</button>
                  <button type="button" id="transportista-edit-cancel" class="secondary-button">Cancelar</button>
                </div>
              </form>
              <div id="transportista-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card hidden" data-transportista-tab-panel="contactos">
            <h3>Contactos del transportista</h3>
            <div class="hint">Captura trafico, administracion, cobranza o mantenimiento.</div>
            <h4 class="capture-section-title">Nuevo contacto</h4>
            <form id="transportista-contacto-form">
              <label>Transportista
                <select id="transportista-contacto-transportista" name="transportista_id" required></select>
              </label>
              <div class="two-col">
                <label>Nombre
                  <input name="nombre" required />
                </label>
                <label>Area
                  <input name="area" />
                </label>
              </div>
              <div class="two-col">
                <label>Puesto
                  <input name="puesto" />
                </label>
                <label>Email
                  <input name="email" type="email" />
                </label>
              </div>
              <div class="three-col">
                <label>Telefono
                  <input name="telefono" />
                </label>
                <label>Extension
                  <input name="extension" />
                </label>
                <label>Celular
                  <input name="celular" />
                </label>
              </div>
              <div class="two-col">
                <label class="check-row">
                  <input name="principal" type="checkbox" />
                  Contacto principal
                </label>
                <label class="check-row">
                  <input name="activo" type="checkbox" checked />
                  Contacto activo
                </label>
              </div>
              <button type="submit">Guardar contacto</button>
            </form>
            <div id="transportista-contacto-message" class="message"></div>
            <div id="transportista-contactos-table" class="contacto-table-wrap"></div>
            <div id="transportista-contacto-edit-panel" class="toolbar hidden" aria-hidden="true">
              <h4>Editar contacto</h4>
              <p class="hint" style="margin:0 0 8px">Solo aparece al pulsar <strong>Editar</strong> en la tabla. Para altas use <strong>Nuevo contacto</strong> arriba.</p>
              <form id="transportista-contacto-edit-form">
                <input name="id" type="hidden" />
                <input name="transportista_id" type="hidden" />
                <label>Transportista
                  <input name="transportista_label" readonly />
                </label>
                <div class="two-col">
                  <label>Nombre
                    <input name="nombre" required />
                  </label>
                  <label>Area
                    <input name="area" />
                  </label>
                </div>
                <div class="two-col">
                  <label>Puesto
                    <input name="puesto" />
                  </label>
                  <label>Email
                    <input name="email" type="email" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Telefono
                    <input name="telefono" />
                  </label>
                  <label>Extension
                    <input name="extension" />
                  </label>
                  <label>Celular
                    <input name="celular" />
                  </label>
                </div>
                <div class="two-col">
                  <label class="check-row">
                    <input name="principal" type="checkbox" />
                    Contacto principal
                  </label>
                  <label class="check-row">
                    <input name="activo" type="checkbox" />
                    Contacto activo
                  </label>
                </div>
                <div class="toolbar-actions">
                  <button type="submit">Guardar cambios</button>
                  <button type="button" id="transportista-contacto-edit-cancel" class="secondary-button">Cancelar</button>
                </div>
              </form>
              <div id="transportista-contacto-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card hidden" data-transportista-tab-panel="documentos">
            <h3>Documentos del transportista</h3>
            <div class="hint">Control de vigencias para operacion y cumplimiento.</div>
            <form id="transportista-documento-form">
              <label>Transportista
                <select id="transportista-documento-transportista" name="transportista_id" required></select>
              </label>
              <div class="three-col">
                <label>Tipo documento
                  <select name="tipo_documento">
                    <option value="permiso_sct">permiso_sct</option>
                    <option value="constancia_fiscal">constancia_fiscal</option>
                    <option value="seguro_rc">seguro_rc</option>
                    <option value="poliza_carga">poliza_carga</option>
                    <option value="tarjeta_circulacion">tarjeta_circulacion</option>
                    <option value="licencia_operador">licencia_operador</option>
                    <option value="ine">ine</option>
                    <option value="comprobante_domicilio">comprobante_domicilio</option>
                    <option value="contrato">contrato</option>
                    <option value="otro">otro</option>
                  </select>
                </label>
                <label>Numero documento
                  <input name="numero_documento" />
                </label>
                <label>Estatus
                  <select name="estatus">
                    <option value="vigente">vigente</option>
                    <option value="vencido">vencido</option>
                    <option value="pendiente" selected>pendiente</option>
                  </select>
                </label>
              </div>
              <div class="three-col">
                <label>Fecha emision
                  <input name="fecha_emision" type="date" />
                </label>
                <label>Fecha vencimiento
                  <input name="fecha_vencimiento" type="date" />
                </label>
                <label>Archivo URL
                  <input name="archivo_url" />
                </label>
              </div>
              <label>Observaciones
                <textarea name="observaciones"></textarea>
              </label>
              <button type="submit">Guardar documento</button>
            </form>
            <div id="transportista-documento-message" class="message"></div>
            <div id="transportista-documentos-table"></div>
            <div id="transportista-documento-edit-panel" class="toolbar hidden">
              <h4>Editar documento de transportista</h4>
              <form id="transportista-documento-edit-form">
                <input name="id" type="hidden" />
                <input name="transportista_id" type="hidden" />
                <label>Transportista
                  <input name="transportista_label" readonly />
                </label>
                <div class="three-col">
                  <label>Tipo documento
                    <select name="tipo_documento">
                      <option value="permiso_sct">permiso_sct</option>
                      <option value="constancia_fiscal">constancia_fiscal</option>
                      <option value="seguro_rc">seguro_rc</option>
                      <option value="poliza_carga">poliza_carga</option>
                      <option value="tarjeta_circulacion">tarjeta_circulacion</option>
                      <option value="licencia_operador">licencia_operador</option>
                      <option value="ine">ine</option>
                      <option value="comprobante_domicilio">comprobante_domicilio</option>
                      <option value="contrato">contrato</option>
                      <option value="otro">otro</option>
                    </select>
                  </label>
                  <label>Numero documento
                    <input name="numero_documento" />
                  </label>
                  <label>Estatus
                    <select name="estatus">
                      <option value="vigente">vigente</option>
                      <option value="vencido">vencido</option>
                      <option value="pendiente">pendiente</option>
                    </select>
                  </label>
                </div>
                <div class="three-col">
                  <label>Fecha emision
                    <input name="fecha_emision" type="date" />
                  </label>
                  <label>Fecha vencimiento
                    <input name="fecha_vencimiento" type="date" />
                  </label>
                  <label>Archivo URL
                    <input name="archivo_url" />
                  </label>
                </div>
                <label>Observaciones
                  <textarea name="observaciones"></textarea>
                </label>
                <div class="toolbar-actions">
                  <button type="submit">Guardar cambios</button>
                  <button type="button" id="transportista-documento-edit-cancel" class="secondary-button">Cancelar</button>
                </div>
              </form>
              <div id="transportista-documento-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card hidden manual-doc manual-interface" data-transportista-tab-panel="manual">
            <div class="manual-interface-head">
              <h3>Manual del módulo Transportistas</h3>
              <span class="manual-badge" title="Contenido completo en esta pantalla">Documentación en pantalla</span>
            </div>
            <div class="hint">Guía integrada en la aplicación. El registro persiste en el servidor vía API. Enfoque formal en el marco del módulo y operativo en procedimientos e indicaciones de captura.</div>

            <div class="manual-interface-body">
              <nav class="manual-toc" id="manual-transportistas-toc" aria-label="Índice del manual de transportistas">
                <div class="manual-toc-title">Contenido</div>
                <a href="#manual-transportistas-1">1. Objetivo del módulo</a>
                <a href="#manual-transportistas-2">2. Subopciones</a>
                <a href="#manual-transportistas-3">3. Nuevo transportista</a>
                <a href="#manual-transportistas-4">4. Consultar y editar</a>
                <a href="#manual-transportistas-5">5. Contactos</a>
                <a href="#manual-transportistas-6">6. Documentos</a>
                <a href="#manual-transportistas-7">7. Ejemplos de captura</a>
                <a href="#manual-transportistas-8">8. Preguntas frecuentes</a>
                <a href="#manual-transportistas-9">9. Mensajes y errores</a>
                <a href="#manual-transportistas-10">10. Referencia técnica</a>
              </nav>
              <div class="manual-scroll" data-manual-scroll="transportistas" tabindex="0" role="region" aria-label="Texto del manual de transportistas">
            <div class="manual-note">
              <strong>Secuencia operativa recomendada:</strong> (1) Registrar el maestro en <strong>Nuevo transportista</strong>. (2) Capturar <strong>Contactos</strong> operativos. (3) Registrar <strong>Documentos</strong> y vigencias. (4) Utilizar <strong>Consultar y editar</strong> para mantenimiento del catálogo.
            </div>

            <h4 id="manual-transportistas-1">1. Objetivo del módulo</h4>
            <p class="manual-p">Centralizar el expediente de cada proveedor de transporte (flota propia, subcontratado, fletero o aliado), sus personas de contacto y el control documental para operación y cumplimiento. La separación en subopciones evita mezclar datos maestros, personas y expedientes.</p>

            <h4 id="manual-transportistas-2">2. Subopciones (barra superior)</h4>
            <ul class="summary-list">
              <li><strong>Nuevo transportista:</strong> alta del maestro con datos fiscales, tipo de figura, estatus, direcciones y notas.</li>
              <li><strong>Consultar y editar:</strong> filtros, tabla resumida y edición del registro seleccionado.</li>
              <li><strong>Contactos:</strong> personas de tráfico, administración, cobranza o mantenimiento asociadas al transportista.</li>
              <li><strong>Documentos:</strong> tipos de documento, números, fechas, estatus de vigencia y referencia a archivo (URL).</li>
              <li><strong>Manual:</strong> la presente guía.</li>
            </ul>
            <p class="manual-p"><strong>Sincronización entre pestañas:</strong> al cambiar el transportista en el selector de <strong>Contactos</strong> o <strong>Documentos</strong>, la aplicación replica la misma selección en el otro selector para continuar sobre el mismo proveedor.</p>

            <h4 id="manual-transportistas-3">3. Nuevo transportista</h4>
            <p class="manual-p">El campo obligatorio es <strong>Razón social</strong> (etiqueta &quot;Razon social&quot; en pantalla). El resto refuerza clasificación operativa, fiscal y de riesgo.</p>
            <h5>Descripción de campos relevantes</h5>
            <ul class="summary-list">
              <li><strong>Tipo transportista:</strong> propio, subcontratado, fletero o aliado (predeterminado: subcontratado).</li>
              <li><strong>Tipo persona y estatus:</strong> física o moral; estatus operativo activo, inactivo o bloqueado.</li>
              <li><strong>RFC, CURP, régimen fiscal:</strong> identificación fiscal conforme a políticas internas.</li>
              <li><strong>Fecha alta, nivel de confianza, prioridad de asignación:</strong> trazabilidad y orden sugerido en asignaciones.</li>
              <li><strong>Contacto principal y teléfono general, email, sitio web:</strong> datos corporativos; el detalle por persona va en Contactos.</li>
              <li><strong>Código postal, ciudad, estado, país:</strong> ubicación; el país puede venir precargado (por ejemplo México).</li>
              <li><strong>Dirección fiscal y dirección operativa:</strong> domicilio para facturación y, en su caso, base operativa.</li>
              <li><strong>Notas operativas y comerciales:</strong> acuerdos internos o restricciones.</li>
              <li><strong>En blacklist / Transportista activo:</strong> restricción de uso y vigencia en catálogo.</li>
            </ul>
            <p class="manual-p"><strong>Procedimiento:</strong> complete la información y pulse <strong>Guardar transportista</strong>. Verifique el mensaje bajo el formulario para confirmación o causa de error.</p>

            <h4 id="manual-transportistas-4">4. Consultar y editar</h4>
            <p class="manual-p">La búsqueda aplica sobre <strong>razón social</strong> (campo nombre), <strong>nombre comercial</strong> y <strong>RFC</strong>, sin distinguir mayúsculas. El listado se actualiza al escribir y al modificar <strong>Estatus</strong> o <strong>Tipo transportista</strong>. <strong>Aplicar filtro</strong> ejecuta la misma actualización de forma explícita.</p>
            <ul class="summary-list">
              <li><strong>Coincidencia única:</strong> si el filtro deja un solo registro, el panel <strong>Editar transportista</strong> se abre automáticamente.</li>
              <li><strong>Tabla:</strong> ID, razón social, nombre comercial, tipo, RFC, conteos de contactos y documentos, estatus y <strong>Editar</strong>.</li>
              <li><strong>Limpiar:</strong> restablece filtros, muestra el universo de registros y cierra el panel de edición si estaba abierto.</li>
              <li><strong>Edición:</strong> análoga al alta; confirme con <strong>Guardar cambios</strong> o cancele.</li>
            </ul>

            <h4 id="manual-transportistas-5">5. Contactos del transportista</h4>
            <p class="manual-p">Seleccione <strong>Transportista</strong> y capture el contacto. <strong>Nombre</strong> es obligatorio; área, puesto, medios de contacto y banderas de principal/activo son opcionales pero recomendables.</p>
            <ul class="summary-list">
              <li>El envío del formulario de alta sigue el flujo estándar del panel (botón <strong>Guardar contacto</strong>).</li>
              <li>En la tabla, <strong>Editar</strong> abre el panel inferior; el transportista se muestra en solo lectura.</li>
              <li><strong>Eliminar</strong> solicita confirmación antes de borrar el contacto.</li>
            </ul>

            <h4 id="manual-transportistas-6">6. Documentos del transportista</h4>
            <p class="manual-p">Permite llevar un inventario de permisos, pólizas, identificaciones y anexos con fechas y estatus de vigencia. <strong>Archivo URL</strong> almacena una referencia (ruta o enlace) al documento digitalizado según su política de archivos.</p>
            <ul class="summary-list">
              <li><strong>Tipo documento:</strong> valores predefinidos (por ejemplo permiso SCT, constancia fiscal, seguro RC, póliza de carga, tarjeta de circulación, contrato, otro).</li>
              <li><strong>Número, fechas de emisión y vencimiento, estatus</strong> (vigente, vencido, pendiente).</li>
              <li><strong>Observaciones:</strong> notas de auditoría o condiciones especiales.</li>
              <li>Edición y <strong>Eliminar</strong> desde la tabla, con confirmación en eliminación.</li>
            </ul>

            <h4 id="manual-transportistas-7">7. Ejemplos de captura (referencia operativa)</h4>
            <p class="manual-p">Use las convenciones corporativas; los ejemplos siguientes homogeneizan criterios habituales en transporte en México.</p>
            <h5>Tipo de documento</h5>
            <ul class="summary-list">
              <li><strong>permiso_sct:</strong> autorización federal de operación.</li>
              <li><strong>seguro_rc, poliza_carga:</strong> coberturas de responsabilidad civil y de mercancía.</li>
              <li><strong>constancia_fiscal:</strong> situación fiscal o constancia de situación.</li>
              <li><strong>tarjeta_circulacion, licencia_operador:</strong> unidad u operador según aplique.</li>
              <li><strong>contrato, otro:</strong> acuerdos marco o documentación miscelánea.</li>
            </ul>
            <h5>Estatus del documento</h5>
            <ul class="summary-list">
              <li><strong>vigente:</strong> dentro de periodo útil para operar.</li>
              <li><strong>vencido:</strong> requiere renovación antes de usar en operación.</li>
              <li><strong>pendiente:</strong> en trámite o sin validar.</li>
            </ul>

            <h4 id="manual-transportistas-8">8. Preguntas frecuentes</h4>
            <h5>No aparece el transportista en Contactos o Documentos</h5>
            <p class="manual-p">Verifique que el alta se haya guardado en <strong>Nuevo transportista</strong> y que los filtros de consulta no excluyan el estatus del registro. Recargue la vista si acaba de crear el maestro.</p>
            <h5>Diferencia entre dirección fiscal y operativa</h5>
            <p class="manual-p">La <strong>dirección fiscal</strong> se orienta a facturación y datos ante autoridad; la <strong>operativa</strong> describe la base o patio de operaciones si difiere del domicilio fiscal.</p>
            <h5>Uso de «En blacklist»</h5>
            <p class="manual-p">Marca al proveedor como no elegible para nuevas operaciones según la política interna; el efecto en asignaciones o compras depende de las reglas de su organización.</p>
            <h5>Apertura automática del panel al filtrar</h5>
            <p class="manual-p">Si el criterio produce exactamente un resultado, se abre <strong>Editar transportista</strong> automáticamente; con varias filas deberá pulsar <strong>Editar</strong> en la fila deseada.</p>
            <h5>Checklist al salir a ruta (cumplimiento)</h5>
            <p class="manual-p">La validación al registrar salida en <strong>Seguimiento</strong> puede exigir documentación del transportista (p. ej. <strong>seguro RC</strong> vigente en <strong>Documentos</strong>) y datos fiscales/CP completos según su configuración. Mantenga expediente y vigencias actualizados.</p>

            <h4 id="manual-transportistas-9">9. Mensajes y errores</h4>
            <p class="manual-p">Los mensajes bajo cada formulario reflejan la respuesta del servidor. Si las tablas no se poblan, compruebe conectividad y disponibilidad de la API.</p>

            <h4 id="manual-transportistas-10">10. Referencia técnica</h4>
            <p class="manual-p">Para rutas REST, esquemas y pruebas, utilice <a href="/docs">/docs</a> (Swagger).</p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="page" id="page-viajes">
        <div class="card">
          <div class="module-subpage-head">
            <div>
              <h3>Subopciones de viajes</h3>
              <div class="hint">Trabaja una parte a la vez para evitar confusión.</div>
            </div>
            <button type="button" class="secondary-button open-manual-btn" id="viaje-open-manual-btn" title="Abrir el manual integrado">Abrir manual</button>
          </div>
          <div class="subpage-buttons">
            <button type="button" class="subpage-button" data-viaje-tab="alta">Nuevo viaje</button>
            <button type="button" class="subpage-button active" data-viaje-tab="consulta">Consultar y editar</button>
            <button type="button" class="subpage-button" data-viaje-tab="manual">Manual</button>
          </div>
        </div>
        <div class="split">
          <article class="card hidden" data-viaje-tab-panel="alta">
            <h3>Nuevo viaje</h3>
            <div class="hint">Planeacion del trayecto con origen, destino y estado.</div>
            <form id="viaje-form">
              <div class="two-col">
                <label>Codigo
                  <input name="codigo_viaje" required />
                </label>
                <label>Estado
                  <select name="estado">
                    <option value="planificado">planificado</option>
                    <option value="en_ruta">en_ruta</option>
                    <option value="completado">completado</option>
                    <option value="cancelado">cancelado</option>
                  </select>
                </label>
              </div>
              <label>Descripcion
                <input name="descripcion" />
              </label>
              <div class="two-col">
                <label>Origen
                  <input name="origen" required />
                </label>
                <label>Destino
                  <input name="destino" required />
                </label>
              </div>
              <div class="two-col">
                <label>Fecha salida
                  <input name="fecha_salida" type="datetime-local" required title="Use el selector; el valor debe ser fecha y hora validas" />
                </label>
                <label>Llegada estimada
                  <input name="fecha_llegada_estimada" type="datetime-local" title="Opcional. Formato fecha y hora local" />
                </label>
              </div>
              <p class="hint" style="margin:0;font-size:12px;">Si el navegador marca el campo como invalido, elija fecha y hora con el calendario o borre y vuelva a capturar.</p>
              <div class="two-col">
                <label>Kilometros estimados
                  <input
                    name="kilometros_estimados"
                    type="number"
                    step="0.01"
                    min="0"
                    inputmode="decimal"
                    autocomplete="off"
                    title="Numero en km (ej. 350 o 350.5). Punto como decimal; se usa en cotizacion de fletes."
                  />
                </label>
                <label>Notas
                  <input name="notas" />
                </label>
              </div>
              <button type="submit">Guardar viaje</button>
            </form>
            <div id="viaje-message" class="message"></div>
          </article>
          <article class="card" data-viaje-tab-panel="consulta">
            <h3>Listado de viajes</h3>
            <div class="toolbar">
              <h4>Consultar viajes</h4>
              <div class="filtro-busqueda-modo hint">
                <label>Como buscar el texto
                  <select class="buscar-modo-sync" title="Mismo criterio en todos los listados del panel; se guarda en el navegador">
                    <option value="contiene">Contiene (flexible, recomendado)</option>
                    <option value="prefijo_palabras">Prefijos de palabra (ej. Ro coincide con Rodriguez)</option>
                    <option value="todas_palabras">Todas las palabras, en cualquier orden</option>
                  </select>
                </label>
              </div>
              <form id="viaje-filter-form">
                <div class="two-col">
                  <label>Buscar
                    <input id="viaje-filter-buscar" name="buscar" type="search" list="viaje-filter-buscar-dl" placeholder="Codigo, origen o destino" autocomplete="off" />
                  </label>
                  <label>Estado
                    <select name="estado">
                      <option value="">Todos</option>
                      <option value="planificado">planificado</option>
                      <option value="en_ruta">en_ruta</option>
                      <option value="completado">completado</option>
                      <option value="cancelado">cancelado</option>
                    </select>
                  </label>
                </div>
                <datalist id="viaje-filter-buscar-dl"></datalist>
                <div class="toolbar-actions">
                  <button type="submit">Aplicar filtro</button>
                  <button type="button" id="viaje-filter-clear" class="secondary-button">Limpiar</button>
                </div>
              </form>
            </div>
            <div id="viajes-table"></div>
            <div id="viaje-edit-panel" class="toolbar hidden">
              <h4>Editar viaje</h4>
              <form id="viaje-edit-form">
                <input name="id" type="hidden" />
                <div class="two-col">
                  <label>Codigo
                    <input name="codigo_viaje" required />
                  </label>
                  <label>Estado
                    <select name="estado">
                      <option value="planificado">planificado</option>
                      <option value="en_ruta">en_ruta</option>
                      <option value="completado">completado</option>
                      <option value="cancelado">cancelado</option>
                    </select>
                  </label>
                </div>
                <label>Descripcion
                  <input name="descripcion" />
                </label>
                <div class="two-col">
                  <label>Origen
                    <input name="origen" required />
                  </label>
                  <label>Destino
                    <input name="destino" required />
                  </label>
                </div>
                <div class="two-col">
                  <label>Fecha salida
                    <input name="fecha_salida" type="datetime-local" required title="Use el selector; fecha y hora validas" />
                  </label>
                  <label>Llegada estimada
                    <input name="fecha_llegada_estimada" type="datetime-local" title="Opcional" />
                  </label>
                </div>
                <div class="two-col">
                  <label>Llegada real
                    <input name="fecha_llegada_real" type="datetime-local" title="Opcional" />
                  </label>
                  <label>Kilometros estimados
                    <input
                      name="kilometros_estimados"
                      type="number"
                      step="0.01"
                      min="0"
                      inputmode="decimal"
                      autocomplete="off"
                      title="Numero en km; se usa en formulas de cotizacion"
                    />
                  </label>
                </div>
                <p class="hint" style="margin:0;font-size:12px;">Al editar, las fechas se cargan desde el servidor en formato compatible con este control. Si aparece error, borre el campo y elija de nuevo con el calendario.</p>
                <label>Notas
                  <input name="notas" />
                </label>
                <div class="toolbar-actions">
                  <button type="submit">Guardar cambios</button>
                  <button type="button" id="viaje-edit-cancel" class="secondary-button">Cancelar</button>
                </div>
              </form>
              <div id="viaje-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card hidden manual-doc manual-interface" data-viaje-tab-panel="manual">
            <div class="manual-interface-head">
              <h3>Manual del módulo Viajes</h3>
              <span class="manual-badge">Documentación en pantalla</span>
            </div>
            <div class="hint">Guía del catálogo de viajes: planeación de trayecto, estados y consulta. Los datos se guardan vía API.</div>
            <div class="manual-interface-body">
              <nav class="manual-toc" id="manual-viaje-toc" aria-label="Índice del manual de viajes">
                <div class="manual-toc-title">Contenido</div>
                <a href="#manual-viaje-1">1. Objetivo</a>
                <a href="#manual-viaje-2">2. Subopciones</a>
                <a href="#manual-viaje-3">3. Nuevo viaje</a>
                <a href="#manual-viaje-4">4. Consultar y editar</a>
                <a href="#manual-viaje-5">5. Estados y seguimiento</a>
                <a href="#manual-viaje-6">6. Preguntas frecuentes</a>
                <a href="#manual-viaje-7">7. Mensajes y errores</a>
                <a href="#manual-viaje-8">8. Referencia técnica</a>
              </nav>
              <div class="manual-scroll" data-manual-scroll="viaje" tabindex="0" role="region" aria-label="Texto del manual de viajes">
            <div class="manual-note"><strong>Secuencia sugerida:</strong> registre el viaje en <strong>Nuevo viaje</strong> y utilice <strong>Consultar y editar</strong> para filtros y correcciones.</div>
            <h4 id="manual-viaje-1">1. Objetivo del módulo</h4>
            <p class="manual-p">Definir cada trayecto (código, origen, destino, fechas, kilómetros estimados y estado) como base para fletes, asignaciones y despachos.</p>
            <h4 id="manual-viaje-2">2. Subopciones</h4>
            <ul class="summary-list">
              <li><strong>Nuevo viaje:</strong> alta del registro.</li>
              <li><strong>Consultar y editar:</strong> filtro, tabla y panel de edición.</li>
              <li><strong>Manual:</strong> esta guía.</li>
            </ul>
            <h4 id="manual-viaje-3">3. Nuevo viaje</h4>
            <p class="manual-p">Capture código, estado (planificado, en ruta, completado, cancelado), descripción, origen y destino, fechas de salida y llegada estimada, kilómetros estimados y notas. Pulse <strong>Guardar viaje</strong> y verifique el mensaje bajo el formulario.</p>
            <h4 id="manual-viaje-4">4. Consultar y editar</h4>
            <p class="manual-p">Filtre por texto (código, origen o destino) y por estado. <strong>Aplicar filtro</strong> y <strong>Limpiar</strong> ajustan la vista. En la tabla use <strong>Editar</strong> para abrir el panel; puede actualizar fechas reales de llegada y demás campos.</p>
            <h4 id="manual-viaje-5">5. Estados y seguimiento</h4>
            <p class="manual-p">El estado del viaje se actualiza aquí o en flujos posteriores (fletes, seguimiento). Mantenga coherencia con la operación real.</p>
            <h4 id="manual-viaje-6">6. Preguntas frecuentes</h4>
            <p class="manual-p"><strong>¿No aparece en listados?</strong> Compruebe filtros y que el alta se haya guardado. <strong>¿No puedo elegir el viaje en otro módulo?</strong> Verifique que exista en catálogo y que el estado permita el vínculo.</p>
            <h4 id="manual-viaje-7">7. Mensajes y errores</h4>
            <p class="manual-p">Los avisos bajo el formulario provienen del servidor. Si la tabla no carga, revise conexión y API.</p>
            <h4 id="manual-viaje-8">8. Referencia técnica</h4>
            <p class="manual-p">Endpoints y esquemas en <a href="/docs">/docs</a>.</p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="page" id="page-fletes">
        <div class="card">
          <div class="module-subpage-head">
            <div>
              <h3>Subopciones de fletes</h3>
              <div class="hint">Trabaja una parte a la vez para evitar confusión.</div>
            </div>
            <button type="button" class="secondary-button open-manual-btn" id="flete-open-manual-btn" title="Abrir el manual integrado">Abrir manual</button>
          </div>
          <div class="subpage-buttons">
            <button type="button" class="subpage-button" data-flete-tab="alta">Nuevo flete</button>
            <button type="button" class="subpage-button active" data-flete-tab="consulta">Consultar y editar</button>
            <button type="button" class="subpage-button" data-flete-tab="ordenes-servicio">Ordenes de servicio</button>
            <button type="button" class="subpage-button" data-flete-tab="manual">Manual</button>
          </div>
        </div>
        <div class="split">
          <article class="card hidden" data-flete-tab-panel="alta">
            <h3>Nuevo flete</h3>
            <div class="hint">Conecta cliente, transportista y viaje. Si no ves opciones, primero crea catalogos.</div>
            <form id="flete-form">
              <div class="two-col">
                <label>Codigo flete
                  <input name="codigo_flete" required />
                </label>
                <label>Estado
                  <select name="estado">
                    <option value="cotizado">cotizado</option>
                    <option value="confirmado">confirmado</option>
                    <option value="asignado">asignado</option>
                    <option value="en_transito">en_transito</option>
                    <option value="entregado">entregado</option>
                    <option value="cancelado">cancelado</option>
                  </select>
                </label>
              </div>
              <div class="three-col">
                <label>Tipo operacion
                  <select name="tipo_operacion">
                    <option value="propio">propio</option>
                    <option value="subcontratado" selected>subcontratado</option>
                    <option value="fletero">fletero</option>
                    <option value="aliado">aliado</option>
                  </select>
                </label>
                <label>Metodo calculo
                  <select name="metodo_calculo">
                    <option value="manual" selected>manual</option>
                    <option value="tarifa">tarifa</option>
                    <option value="motor">motor</option>
                  </select>
                </label>
                <label>Moneda
                  <input name="moneda" value="MXN" maxlength="3" />
                </label>
              </div>
              <div class="three-col">
                <label>Cliente
                  <select id="flete-cliente" name="cliente_id" required></select>
                </label>
                <label>Transportista
                  <select id="flete-transportista" name="transportista_id" required></select>
                </label>
                <label>Viaje
                  <select id="flete-viaje" name="viaje_id"></select>
                </label>
              </div>
              <div class="two-col">
                <label>Tipo unidad
                  <input name="tipo_unidad" placeholder="torton, tractocamion..." />
                </label>
                <label>Tipo carga
                  <input name="tipo_carga" placeholder="seca, refrigerada..." />
                </label>
              </div>
              <label>Descripcion de carga
                <input name="descripcion_carga" />
              </label>
              <div class="three-col">
                <label>Peso kg
                  <input name="peso_kg" type="number" step="0.001" min="0" required />
                </label>
                <label>Volumen m3
                  <input name="volumen_m3" type="number" step="0.001" min="0" />
                </label>
                <label>Numero bultos
                  <input name="numero_bultos" type="number" min="0" step="1" inputmode="numeric" title="Cantidad entera de bultos" />
                </label>
              </div>
              <div class="three-col">
                <label>Distancia km
                  <input name="distancia_km" type="number" step="0.01" min="0" />
                </label>
                <label>Precio venta
                  <input name="monto_estimado" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" required />
                </label>
                <label>Costo estimado
                  <input name="costo_transporte_estimado" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                </label>
              </div>
              <div class="two-col">
                <label>Costo real
                  <input name="costo_transporte_real" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                </label>
                <label>Margen estimado
                  <input name="margen_estimado" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                </label>
              </div>
              <div class="hint" id="flete-margen-pct-hint-new"></div>
              <div class="two-col">
                <button type="button" id="flete-cotizar-btn">Cotizar venta</button>
                <button type="button" id="flete-cotizar-compra-btn">Cotizar compra</button>
              </div>
              <div class="two-col">
                <div class="hint" id="flete-cotizacion-detalle">
                  Usa el viaje seleccionado para tomar origen y destino, buscar una tarifa activa y sugerir el precio de venta.
                </div>
                <div class="hint" id="flete-cotizacion-compra-detalle">
                  Usa el transportista elegido para sugerir el costo de compra estimado.
                </div>
              </div>
              <label>Notas
                <textarea name="notas"></textarea>
              </label>
              <button type="submit">Guardar flete</button>
            </form>
            <div id="flete-message" class="message"></div>
          </article>
          <article class="card" data-flete-tab-panel="consulta">
            <h3>Listado de fletes</h3>
            <div class="toolbar">
              <h4>Consultar fletes</h4>
              <div class="filtro-busqueda-modo hint">
                <label>Como buscar el texto
                  <select class="buscar-modo-sync" title="Mismo criterio en todos los listados del panel; se guarda en el navegador">
                    <option value="contiene">Contiene (flexible, recomendado)</option>
                    <option value="prefijo_palabras">Prefijos de palabra (ej. Ro coincide con Rodriguez)</option>
                    <option value="todas_palabras">Todas las palabras, en cualquier orden</option>
                  </select>
                </label>
              </div>
              <form id="flete-filter-form">
                <div class="two-col">
                  <label class="span-2">Buscar rapido
                    <input id="flete-filter-buscar" name="buscar" type="search" list="flete-filter-buscar-dl" placeholder="Codigo flete, cliente, transportista o ID" autocomplete="off" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Estado
                    <select id="flete-filter-estado" name="estado">
                      <option value="">Todos</option>
                      <option value="cotizado">cotizado</option>
                      <option value="confirmado">confirmado</option>
                      <option value="asignado">asignado</option>
                      <option value="en_transito">en_transito</option>
                      <option value="entregado">entregado</option>
                      <option value="cancelado">cancelado</option>
                    </select>
                  </label>
                  <label>Cliente
                    <select id="flete-filter-cliente" name="cliente_id"></select>
                  </label>
                  <label>Transportista
                    <select id="flete-filter-transportista" name="transportista_id"></select>
                  </label>
                </div>
                <datalist id="flete-filter-buscar-dl"></datalist>
                <div class="toolbar-actions">
                  <button type="submit">Aplicar filtro</button>
                  <button type="button" id="flete-filter-clear" class="secondary-button">Limpiar</button>
                </div>
              </form>
            </div>
            <div id="fletes-table"></div>
            <div id="flete-edit-panel" class="toolbar hidden">
              <h4>Editar flete</h4>
              <form id="flete-edit-form">
                <input id="flete-edit-form-record-id" name="id" type="hidden" autocomplete="off" />
                <div class="two-col">
                  <label>Codigo flete
                    <input name="codigo_flete" required />
                  </label>
                  <label>Estado
                    <select name="estado">
                      <option value="cotizado">cotizado</option>
                      <option value="confirmado">confirmado</option>
                      <option value="asignado">asignado</option>
                      <option value="en_transito">en_transito</option>
                      <option value="entregado">entregado</option>
                      <option value="cancelado">cancelado</option>
                    </select>
                  </label>
                </div>
                <div class="three-col">
                  <label>Tipo operacion
                    <select name="tipo_operacion">
                      <option value="propio">propio</option>
                      <option value="subcontratado">subcontratado</option>
                      <option value="fletero">fletero</option>
                      <option value="aliado">aliado</option>
                    </select>
                  </label>
                  <label>Metodo calculo
                    <select name="metodo_calculo">
                      <option value="manual">manual</option>
                      <option value="tarifa">tarifa</option>
                      <option value="motor">motor</option>
                    </select>
                  </label>
                  <label>Moneda
                    <input name="moneda" maxlength="3" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Cliente
                    <select id="edit-flete-cliente" name="cliente_id" required></select>
                  </label>
                  <label>Transportista
                    <select id="edit-flete-transportista" name="transportista_id" required></select>
                  </label>
                  <label>Viaje
                    <select id="edit-flete-viaje" name="viaje_id"></select>
                  </label>
                </div>
                <div class="two-col">
                  <label>Tipo unidad
                    <input name="tipo_unidad" />
                  </label>
                  <label>Tipo carga
                    <input name="tipo_carga" />
                  </label>
                </div>
                <label>Descripcion de carga
                  <input name="descripcion_carga" />
                </label>
                <div class="three-col">
                  <label>Peso kg
                    <input name="peso_kg" type="number" step="0.001" min="0" />
                  </label>
                  <label>Volumen m3
                    <input name="volumen_m3" type="number" step="0.001" min="0" />
                  </label>
                  <label>Numero bultos
                    <input name="numero_bultos" type="number" min="0" step="1" inputmode="numeric" title="Cantidad entera de bultos" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Distancia km
                    <input name="distancia_km" type="number" step="0.01" min="0" />
                  </label>
                  <label>Precio venta
                    <input name="monto_estimado" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                  </label>
                  <label>Costo estimado
                    <input name="costo_transporte_estimado" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                  </label>
                </div>
                <div class="two-col">
                  <label>Costo real
                    <input name="costo_transporte_real" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                  </label>
                  <label>Margen estimado
                    <input name="margen_estimado" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                  </label>
                </div>
                <div class="hint" id="flete-edit-margen-pct-hint"></div>
                <div class="two-col">
                  <button type="button" id="edit-flete-cotizar-venta-btn">Cotizar venta</button>
                  <button type="button" id="edit-flete-cotizar-compra-btn">Cotizar compra</button>
                </div>
                <div class="two-col">
                  <div class="hint" id="edit-flete-cotizacion-detalle">
                    Recalcula el precio de venta sugerido desde la tarifa comercial.
                  </div>
                  <div class="hint" id="edit-flete-cotizacion-compra-detalle">
                    Recalcula el costo estimado desde la tarifa de compra del transportista.
                  </div>
                </div>
                <label>Notas
                  <textarea name="notas"></textarea>
                </label>
                <div class="toolbar-actions">
                  <button type="submit">Guardar cambios</button>
                  <button type="button" id="flete-edit-cancel" class="secondary-button">Cancelar</button>
                </div>
              </form>
              <div id="flete-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card hidden" data-flete-tab-panel="ordenes-servicio">
            <h3>Ordenes de servicio</h3>
            <div class="hint">Compromiso entre cotizacion aceptada y ejecucion (flete, viaje, despacho). Alta manual, generacion desde cotizacion <strong>aceptada</strong>, cambio de estatus y vínculos operativos desde esta pestaña (rol <strong>consulta</strong>: solo lectura).</div>
            <div class="grid" data-orden-servicio-editor style="margin-bottom: 18px">
              <article class="card" style="margin: 0">
                <h4>Desde cotizacion aceptada</h4>
                <p class="hint" style="font-size: 13px">La cotizacion debe estar en estatus <code>aceptada</code> o <code>convertida</code>.</p>
                <form id="orden-servicio-desde-cotizacion-form">
                  <label>ID cotizacion
                    <input name="cotizacion_id" type="number" min="1" required />
                  </label>
                  <label>Fecha programada (opcional)
                    <input name="fecha_programada" type="datetime-local" />
                  </label>
                  <label>Observaciones
                    <textarea name="observaciones" rows="2"></textarea>
                  </label>
                  <button type="submit">Generar orden</button>
                </form>
                <div id="orden-servicio-desde-cot-msg" class="message" role="status"></div>
              </article>
              <article class="card" style="margin: 0">
                <h4>Nueva orden (manual)</h4>
                <p class="hint" style="font-size: 13px">Se crea en <strong>borrador</strong>; use <strong>Cambiar estatus</strong> en el detalle para avanzar el flujo.</p>
                <form id="orden-servicio-nueva-form">
                  <div class="two-col">
                    <label>Cliente
                      <select id="orden-servicio-nueva-cliente" name="cliente_id" required></select>
                    </label>
                    <label>Moneda
                      <input name="moneda" type="text" value="MXN" maxlength="3" />
                    </label>
                    <label>ID cotizacion (opcional)
                      <input name="cotizacion_id" type="number" min="1" />
                    </label>
                    <label>ID flete (opcional)
                      <select id="orden-servicio-nueva-flete" name="flete_id"></select>
                    </label>
                    <label>ID viaje (opcional)
                      <select id="orden-servicio-nueva-viaje" name="viaje_id"></select>
                    </label>
                    <label>ID despacho (opcional)
                      <select id="orden-servicio-nueva-despacho" name="despacho_id"></select>
                    </label>
                  </div>
                  <div class="two-col">
                    <label>Origen
                      <input name="origen" required maxlength="255" />
                    </label>
                    <label>Destino
                      <input name="destino" required maxlength="255" />
                    </label>
                    <label>Tipo unidad
                      <input name="tipo_unidad" required maxlength="64" placeholder="ej. tractocamion" />
                    </label>
                    <label>Tipo carga
                      <input name="tipo_carga" maxlength="64" />
                    </label>
                    <label>Peso kg
                      <input name="peso_kg" type="number" step="0.001" min="0" required />
                    </label>
                    <label>Distancia km (opcional)
                      <input name="distancia_km" type="number" step="0.01" min="0" />
                    </label>
                    <label>Precio comprometido
                      <input name="precio_comprometido" type="number" step="0.01" min="0" required />
                    </label>
                    <label>Fecha programada (opcional)
                      <input name="fecha_programada" type="datetime-local" />
                    </label>
                  </div>
                  <label>Observaciones
                    <textarea name="observaciones" rows="2"></textarea>
                  </label>
                  <button type="submit">Crear borrador</button>
                </form>
                <div id="orden-servicio-nueva-msg" class="message" role="status"></div>
              </article>
            </div>
            <div class="toolbar">
              <h4>Filtrar</h4>
              <form id="orden-servicio-filter-form">
                <div class="three-col">
                  <label>Buscar
                    <input id="orden-servicio-filter-buscar" name="buscar" type="search" placeholder="Folio, origen, destino, codigo flete" autocomplete="off" />
                  </label>
                  <label>Cliente
                    <select id="orden-servicio-filter-cliente" name="cliente_id">
                      <option value="">Todos</option>
                    </select>
                  </label>
                  <label>Estatus
                    <select id="orden-servicio-filter-estatus" name="estatus">
                      <option value="">Todos</option>
                      <option value="borrador">borrador</option>
                      <option value="confirmada">confirmada</option>
                      <option value="programada">programada</option>
                      <option value="en_ejecucion">en_ejecucion</option>
                      <option value="cerrada">cerrada</option>
                      <option value="cancelada">cancelada</option>
                    </select>
                  </label>
                </div>
                <div class="toolbar-actions">
                  <button type="submit">Aplicar filtro</button>
                  <button type="button" id="orden-servicio-filter-clear" class="secondary-button">Limpiar</button>
                </div>
              </form>
            </div>
            <div id="ordenes-servicio-table"></div>
            <div id="orden-servicio-detail-panel" class="toolbar hidden" aria-hidden="true">
              <h4>Detalle de orden de servicio</h4>
              <input type="hidden" id="orden-servicio-detail-id" value="" />
              <div id="orden-servicio-detail-body" class="hint" style="white-space:pre-wrap;font-size:13px;line-height:1.5;"></div>
              <div data-orden-servicio-editor class="card" style="margin-top:12px;padding:12px;background:rgba(0,0,0,0.15)">
                <h4 style="margin-top:0">Cambiar estatus</h4>
                <form id="orden-servicio-estatus-form">
                  <div class="three-col">
                    <label>Estatus
                      <select id="orden-servicio-estatus-select" name="estatus" required>
                        <option value="borrador">borrador</option>
                        <option value="confirmada">confirmada</option>
                        <option value="programada">programada</option>
                        <option value="en_ejecucion">en_ejecucion</option>
                        <option value="cerrada">cerrada</option>
                        <option value="cancelada">cancelada</option>
                      </select>
                    </label>
                    <label style="grid-column: span 2">Nota (opcional)
                      <input name="observaciones" type="text" placeholder="Motivo o comentario del cambio" />
                    </label>
                  </div>
                  <button type="submit">Aplicar estatus</button>
                </form>
                <div id="orden-servicio-estatus-msg" class="message" role="status"></div>
                <h4>Datos del compromiso</h4>
                <p class="hint" style="font-size:12px">Ruta, carga, peso, precio, moneda, fecha programada y observaciones de la orden (PATCH <code>OrdenServicioUpdate</code>).</p>
                <form id="orden-servicio-datos-form">
                  <div class="two-col">
                    <label>Origen
                      <input name="origen" required maxlength="255" autocomplete="off" />
                    </label>
                    <label>Destino
                      <input name="destino" required maxlength="255" autocomplete="off" />
                    </label>
                    <label>Tipo unidad
                      <input name="tipo_unidad" required maxlength="64" autocomplete="off" />
                    </label>
                    <label>Tipo carga
                      <input name="tipo_carga" maxlength="64" autocomplete="off" />
                    </label>
                    <label>Peso kg
                      <input name="peso_kg" type="number" step="0.001" min="0" required />
                    </label>
                    <label>Distancia km
                      <input name="distancia_km" type="number" step="0.01" min="0" />
                    </label>
                    <label>Precio comprometido
                      <input name="precio_comprometido" type="number" step="0.01" min="0" required />
                    </label>
                    <label>Moneda
                      <input name="moneda" type="text" maxlength="3" />
                    </label>
                    <label>Fecha programada (opcional)
                      <input name="fecha_programada" type="datetime-local" />
                    </label>
                  </div>
                  <label>Observaciones
                    <textarea name="observaciones" rows="2"></textarea>
                  </label>
                  <button type="submit">Guardar datos</button>
                </form>
                <div id="orden-servicio-datos-msg" class="message" role="status"></div>
                <h4>Vinculos operativos</h4>
                <p class="hint" style="font-size:12px"><strong>Sin cambiar:</strong> no modifica ese vínculo. <strong>Quitar vínculo:</strong> envia <code>null</code> al servidor. Los demas IDs deben existir en el catalogo.</p>
                <form id="orden-servicio-vinculos-form">
                  <div class="three-col">
                    <label>Flete
                      <select id="orden-servicio-edit-flete" name="flete_id"></select>
                    </label>
                    <label>Viaje
                      <select id="orden-servicio-edit-viaje" name="viaje_id"></select>
                    </label>
                    <label>Despacho
                      <select id="orden-servicio-edit-despacho" name="despacho_id"></select>
                    </label>
                  </div>
                  <button type="submit">Guardar vinculos</button>
                </form>
                <div id="orden-servicio-vinculos-msg" class="message" role="status"></div>
                <div id="orden-servicio-delete-msg" class="message" role="status"></div>
                <div class="toolbar-actions" style="margin-top:10px">
                  <button type="button" id="orden-servicio-delete-btn" class="secondary-button">Eliminar orden</button>
                </div>
              </div>
              <div class="toolbar-actions">
                <button type="button" id="orden-servicio-detail-close" class="secondary-button">Cerrar</button>
              </div>
            </div>
          </article>
          <article class="card hidden manual-doc manual-interface" data-flete-tab-panel="manual">
            <div class="manual-interface-head">
              <h3>Manual del módulo Fletes</h3>
              <span class="manual-badge">Documentación en pantalla</span>
            </div>
            <div class="hint">El flete vincula cliente, transportista y viaje con precios y márgenes. Guía formal y operativa.</div>
            <div class="manual-interface-body">
              <nav class="manual-toc" id="manual-flete-toc" aria-label="Índice del manual de fletes">
                <div class="manual-toc-title">Contenido</div>
                <a href="#manual-flete-1">1. Objetivo</a>
                <a href="#manual-flete-2">2. Subopciones</a>
                <a href="#manual-flete-3">3. Nuevo flete</a>
                <a href="#manual-flete-4">4. Consultar y editar</a>
                <a href="#manual-flete-5">5. Cotización y tarifas</a>
                <a href="#manual-flete-6">6. Preguntas frecuentes</a>
                <a href="#manual-flete-7">7. Mensajes y errores</a>
                <a href="#manual-flete-8">8. Referencia técnica</a>
              </nav>
              <div class="manual-scroll" data-manual-scroll="flete" tabindex="0" role="region" aria-label="Texto del manual de fletes">
            <div class="manual-note"><strong>Prerrequisitos:</strong> clientes, transportistas y viajes dados de alta para poder seleccionarlos. Para cotizar con motor: tarifas de venta (y de compra si usa el boton de cotizacion de compra) alineadas en ambito, modalidad, origen/destino y tipo de unidad/carga.</div>
            <h4 id="manual-flete-1">1. Objetivo del módulo</h4>
            <p class="manual-p">Registrar cada ejercicio comercial de transporte (cotización, costos, venta, márgenes) asociado a cliente, transportista y viaje. Campos fiscales extendidos del flete (Carta Porte UUID/folio, factura de mercancía) pueden gestionarse por API si aún no aparecen en este formulario.</p>
            <h4 id="manual-flete-2">2. Subopciones</h4>
            <ul class="summary-list">
              <li><strong>Nuevo flete:</strong> alta del flete; botones <strong>Cotizar venta</strong> y <strong>Cotizar compra</strong> para sugerir montos según tarifas y datos capturados.</li>
              <li><strong>Consultar y editar:</strong> filtros por texto rapido, estado, cliente y transportista; <strong>Editar</strong> abre el panel de correccion.</li>
              <li><strong>Ordenes de servicio:</strong> filtros, tabla y <strong>Ver detalle</strong> (el detalle se recarga desde el servidor). Alta desde cotizacion aceptada o manual; en el detalle puede editar estatus, datos del compromiso, vínculos y <strong>Eliminar orden</strong> (con confirmacion). El rol <strong>consulta</strong> solo ve listado y texto de detalle (sin formularios ni borrado).</li>
              <li><strong>Manual:</strong> esta guía.</li>
            </ul>
            <h4 id="manual-flete-3">3. Nuevo flete</h4>
            <p class="manual-p">Complete codigo, estado, tipo de operacion, metodo de calculo (manual, tarifa, motor), moneda, cliente, transportista y viaje, tipo unidad/carga, peso (obligatorio para cotizar), distancia, montos y notas. El viaje seleccionado alimenta origen/destino al cotizar. Tras cotizar, valide precios antes de guardar.</p>
            <h4 id="manual-flete-4">4. Consultar y editar</h4>
            <p class="manual-p">Aplique filtros y pulse <strong>Editar</strong> en la fila. Puede volver a usar <strong>Cotizar venta/compra</strong> en edicion. Actualice costos reales o estados segun su proceso.</p>
            <h4 id="manual-flete-5">5. Cotización y tarifas</h4>
            <p class="manual-p">Los botones de cotizacion llaman al motor de tarifas; los resultados se muestran en el area de detalle bajo los botones. Deben coincidir ambito (local/estatal/federal), modalidad y textos de origen/destino con la tarifa vigente. El flujo completo cotizacion guardada → aceptada → conversion formal a flete puede requerir API u homologacion con sistemas; en panel suele bastar flete confirmado con precio coherente.</p>
            <h4 id="manual-flete-6">6. Preguntas frecuentes</h4>
            <p class="manual-p"><strong>¿Listas vacías en selectores?</strong> Cree primero los catálogos. <strong>¿Margen en cero?</strong> Revise precio de venta y costos capturados.</p>
            <h4 id="manual-flete-7">7. Mensajes y errores</h4>
            <p class="manual-p">Los mensajes vienen del servidor. Compruebe API y validaciones.</p>
            <h4 id="manual-flete-8">8. Referencia técnica</h4>
            <p class="manual-p"><a href="/docs">/docs</a> (Swagger).</p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="page" id="page-facturas">
        <div class="card">
          <div class="module-subpage-head">
            <div>
              <h3>Subopciones de facturas</h3>
              <div class="hint">Trabaja una parte a la vez para evitar confusión.</div>
            </div>
            <button type="button" class="secondary-button open-manual-btn" id="factura-open-manual-btn" title="Abrir el manual integrado">Abrir manual</button>
          </div>
          <div class="subpage-buttons">
            <button type="button" class="subpage-button" data-factura-tab="alta">Nueva factura</button>
            <button type="button" class="subpage-button active" data-factura-tab="consulta">Consultar y editar</button>
            <button type="button" class="subpage-button" data-factura-tab="manual">Manual</button>
          </div>
        </div>
        <div class="split">
          <article class="card hidden" data-factura-tab-panel="alta">
            <h3>Nueva factura</h3>
            <div class="hint">Simulación administrativa de facturación y cobranza ligada al cliente y al flete.</div>
            <p class="hint" id="factura-nueva-ayuda-flete" style="margin:0 0 8px 0;">
              Elegir solo <strong>Cliente</strong> y <strong>Flete</strong> no rellena concepto ni importes: pulse
              <strong>Autollenar desde flete</strong> (borrador en pantalla) o
              <strong>Generar automático desde flete</strong> (crea la factura en el servidor).
              La lista de fletes se acota al cliente seleccionado.
            </p>
            <form id="factura-form">
              <div class="three-col">
                <label>Serie
                  <input name="serie" placeholder="A, B, MXN..." />
                </label>
                <label>Fecha emision
                  <input name="fecha_emision" type="date" required />
                </label>
                <label>Fecha vencimiento
                  <input name="fecha_vencimiento" type="date" />
                </label>
              </div>
              <div class="three-col">
                <label>Cliente
                  <select id="factura-cliente" name="cliente_id" required></select>
                </label>
                <label>Flete
                  <select id="factura-flete" name="flete_id"></select>
                </label>
                <label>Orden de servicio
                  <input name="orden_servicio_id" id="factura-form-orden-servicio-id" placeholder="ID numerico (opcional)" />
                </label>
              </div>
              <div class="two-col">
                <label>Buscar por folio de orden (rellena el ID)
                  <input type="text" id="factura-os-folio-buscar" placeholder="Ej. OS20260412-0001" autocomplete="off" />
                </label>
                <div class="toolbar-actions" style="align-self:flex-end;padding-top:1.25rem;">
                  <button type="button" id="factura-os-folio-aplicar" class="secondary-button">Aplicar folio</button>
                </div>
              </div>
              <div class="three-col">
                <label>Concepto
                  <input name="concepto" required />
                </label>
                <label>Referencia
                  <input name="referencia" />
                </label>
                <label>Moneda
                  <input name="moneda" value="MXN" maxlength="3" />
                </label>
              </div>
              <div class="three-col">
                <label>Subtotal
                  <input name="subtotal" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" required />
                </label>
                <label>IVA %
                  <input name="iva_pct" type="number" step="0.0001" min="0" value="0.16" />
                </label>
                <label>IVA monto
                  <input name="iva_monto" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                </label>
              </div>
              <div class="three-col">
                <label>Retencion
                  <input name="retencion_monto" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" value="0" />
                </label>
                <label>Total
                  <input name="total" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                </label>
                <label>Saldo pendiente
                  <input name="saldo_pendiente" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                </label>
              </div>
              <div class="three-col">
                <label>Forma pago
                  <input name="forma_pago" placeholder="transferencia" />
                </label>
                <label>Metodo pago
                  <input name="metodo_pago" placeholder="PPD o PUE" />
                </label>
                <label>Uso CFDI
                  <input name="uso_cfdi" placeholder="G03, S01..." />
                </label>
              </div>
              <div class="two-col">
                <label>Estatus
                  <select name="estatus">
                    <option value="borrador" selected>borrador</option>
                    <option value="emitida">emitida</option>
                    <option value="enviada">enviada</option>
                    <option value="parcial">parcial</option>
                    <option value="cobrada">cobrada</option>
                    <option value="cancelada">cancelada</option>
                  </select>
                </label>
                <label class="check-row">
                  <input name="timbrada" type="checkbox" />
                  Marcada como timbrada
                </label>
              </div>
              <label>Observaciones
                <textarea name="observaciones"></textarea>
              </label>
              <label class="check-row">
                <input type="checkbox" id="factura-gen-usar-tarifa" />
                Al generar automático, usar precio recalculado con tarifas vigentes (si aplica)
              </label>
              <div class="toolbar-actions">
                <button type="button" id="factura-desde-flete-btn" class="secondary-button">Autollenar desde flete</button>
                <button type="button" id="factura-preview-flete-btn" class="secondary-button" title="Ver precio flete vs tarifa vigente">Vista previa (tarifa)</button>
                <button type="button" id="factura-generar-auto-btn" class="secondary-button">Generar automático desde flete</button>
                <button type="submit">Guardar factura</button>
              </div>
            </form>
            <div id="factura-message" class="message"></div>
          </article>
          <article class="card" data-factura-tab-panel="consulta">
            <h3>Listado de facturas</h3>
            <div class="toolbar">
              <h4>Consultar facturas</h4>
              <div class="filtro-busqueda-modo hint">
                <label>Como buscar el texto
                  <select class="buscar-modo-sync" title="Mismo criterio en todos los listados del panel; se guarda en el navegador">
                    <option value="contiene">Contiene (flexible, recomendado)</option>
                    <option value="prefijo_palabras">Prefijos de palabra (ej. Ro coincide con Rodriguez)</option>
                    <option value="todas_palabras">Todas las palabras, en cualquier orden</option>
                  </select>
                </label>
              </div>
              <form id="factura-filter-form">
                <p class="hint" style="margin:0 0 8px 0;">El texto en <strong>Buscar</strong> filtra al escribir; cliente y estatus al cambiar o con <strong>Aplicar filtro</strong>.</p>
                <div class="three-col">
                  <label>Buscar
                    <input id="factura-filter-buscar" name="buscar" type="search" list="factura-filter-buscar-dl" placeholder="Folio, concepto o referencia" autocomplete="off" />
                  </label>
                  <label>Cliente
                    <select id="factura-filter-cliente" name="cliente_id"></select>
                  </label>
                  <label>Estatus
                    <select id="factura-filter-estatus" name="estatus">
                      <option value="">Todas</option>
                      <option value="borrador">borrador</option>
                      <option value="emitida">emitida</option>
                      <option value="enviada">enviada</option>
                      <option value="parcial">parcial</option>
                      <option value="cobrada">cobrada</option>
                      <option value="cancelada">cancelada</option>
                    </select>
                  </label>
                </div>
                <datalist id="factura-filter-buscar-dl"></datalist>
                <div class="toolbar-actions">
                  <button type="submit">Aplicar filtro</button>
                  <button type="button" id="factura-filter-clear" class="secondary-button">Limpiar</button>
                </div>
              </form>
            </div>
            <div id="facturas-table"></div>
            <div id="factura-edit-panel" class="toolbar hidden">
              <h4>Editar factura</h4>
              <form id="factura-edit-form">
                <input name="id" type="hidden" />
                <div class="three-col">
                  <label>Serie
                    <input name="serie" />
                  </label>
                  <label>Fecha emision
                    <input name="fecha_emision" type="date" required />
                  </label>
                  <label>Fecha vencimiento
                    <input name="fecha_vencimiento" type="date" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Cliente
                    <select id="edit-factura-cliente" name="cliente_id" required></select>
                  </label>
                  <label>Flete
                    <select id="edit-factura-flete" name="flete_id"></select>
                  </label>
                  <label>Orden de servicio
                    <input name="orden_servicio_id" id="edit-factura-form-orden-servicio-id" placeholder="ID numerico (opcional)" />
                  </label>
                </div>
                <div class="two-col">
                  <label>Buscar por folio de orden (rellena el ID)
                    <input type="text" id="edit-factura-os-folio-buscar" placeholder="Ej. OS20260412-0001" autocomplete="off" />
                  </label>
                  <div class="toolbar-actions" style="align-self:flex-end;padding-top:1.25rem;">
                    <button type="button" id="edit-factura-os-folio-aplicar" class="secondary-button">Aplicar folio</button>
                  </div>
                </div>
                <div class="three-col">
                  <label>Concepto
                    <input name="concepto" required />
                  </label>
                  <label>Referencia
                    <input name="referencia" />
                  </label>
                  <label>Moneda
                    <input name="moneda" maxlength="3" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Subtotal
                    <input name="subtotal" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" required />
                  </label>
                  <label>IVA %
                    <input name="iva_pct" type="number" step="0.0001" min="0" />
                  </label>
                  <label>IVA monto
                    <input name="iva_monto" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Retencion
                    <input name="retencion_monto" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                  </label>
                  <label>Total
                    <input name="total" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                  </label>
                  <label>Saldo pendiente
                    <input name="saldo_pendiente" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Forma pago
                    <input name="forma_pago" />
                  </label>
                  <label>Metodo pago
                    <input name="metodo_pago" />
                  </label>
                  <label>Uso CFDI
                    <input name="uso_cfdi" />
                  </label>
                </div>
                <div class="two-col">
                  <label>Estatus
                    <select name="estatus">
                      <option value="borrador">borrador</option>
                      <option value="emitida">emitida</option>
                      <option value="enviada">enviada</option>
                      <option value="parcial">parcial</option>
                      <option value="cobrada">cobrada</option>
                      <option value="cancelada">cancelada</option>
                    </select>
                  </label>
                  <label class="check-row">
                    <input name="timbrada" type="checkbox" />
                    Marcada como timbrada
                  </label>
                </div>
                <label>Observaciones
                  <textarea name="observaciones"></textarea>
                </label>
                <div class="toolbar-actions">
                  <button type="submit">Guardar cambios</button>
                  <button type="button" id="factura-edit-cancel" class="secondary-button">Cancelar</button>
                </div>
              </form>
              <div id="factura-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card hidden manual-doc manual-interface" data-factura-tab-panel="manual">
            <div class="manual-interface-head">
              <h3>Manual del módulo Facturas</h3>
              <span class="manual-badge">Documentación en pantalla</span>
            </div>
            <div class="hint">Facturación administrativa simulada: montos, impuestos, estatus y vínculo a cliente y flete.</div>
            <div class="manual-interface-body">
              <nav class="manual-toc" id="manual-factura-toc" aria-label="Índice del manual de facturas">
                <div class="manual-toc-title">Contenido</div>
                <a href="#manual-factura-1">1. Objetivo</a>
                <a href="#manual-factura-2">2. Subopciones</a>
                <a href="#manual-factura-3">3. Nueva factura</a>
                <a href="#manual-factura-4">4. Consultar y editar</a>
                <a href="#manual-factura-5">5. Autollenar, vista previa y generar automático</a>
                <a href="#manual-factura-6">6. Orden de servicio y folio</a>
                <a href="#manual-factura-7">7. Preguntas frecuentes</a>
                <a href="#manual-factura-8">8. Mensajes y errores</a>
                <a href="#manual-factura-9">9. Referencia técnica</a>
              </nav>
              <div class="manual-scroll" data-manual-scroll="factura" tabindex="0" role="region" aria-label="Texto del manual de facturas">
            <div class="manual-note"><strong>Alcance:</strong> registro <strong>administrativo</strong> de cobro en SIFE-MXN; no sustituye al CFDI timbrado ante el SAT. Valide montos, forma y metodo de pago, uso CFDI y politica de timbrado con su area fiscal. La casilla <strong>Marcada como timbrada</strong> es informativa si el timbrado ocurre fuera del sistema.</div>
            <h4 id="manual-factura-1">1. Objetivo del módulo</h4>
            <p class="manual-p">Registrar folio interno (serie, fechas, importes, IVA, retenciones, forma y metodo de pago, uso CFDI, estatus), vinculo a <strong>cliente</strong> y, opcionalmente, a <strong>flete</strong> y a <strong>orden de servicio</strong> (por ID o mediante <strong>Aplicar folio</strong>).</p>
            <h4 id="manual-factura-2">2. Subopciones</h4>
            <ul class="summary-list">
              <li><strong>Nueva factura:</strong> alta del registro administrativo.</li>
              <li><strong>Consultar y editar:</strong> filtros por texto, cliente y estatus; edicion por fila.</li>
              <li><strong>Manual:</strong> esta guía.</li>
            </ul>
            <h4 id="manual-factura-3">3. Nueva factura</h4>
            <p class="manual-p">Seleccione <strong>Cliente</strong> y, si aplica, <strong>Flete</strong>. La lista de fletes se <strong>filtra al cliente</strong> elegido; si elige primero un flete, el cliente se sincroniza con el del flete. <strong>Solo elegir cliente y flete no rellena concepto ni importes:</strong> debe pulsar <strong>Autollenar desde flete</strong> (rellena el formulario en pantalla; aun debe <strong>Guardar factura</strong>) o <strong>Generar automático desde flete</strong> (crea el registro en servidor con logica de negocio; opcionalmente marque usar precio recalculado con tarifas vigentes). Puede usar <strong>Vista previa (tarifa)</strong> para comparar precio del flete frente a tarifa sin guardar.</p>
            <p class="manual-p">Complete fechas (emision obligatoria), concepto, montos o dejelos calcular tras autollenar; forma y metodo de pago (p. ej. PUE/PPD segun politica), uso CFDI, estatus (borrador hasta emitida/cobrada). Guarde con <strong>Guardar factura</strong>.</p>
            <h4 id="manual-factura-4">4. Consultar y editar</h4>
            <p class="manual-p">Use filtros; el texto en <strong>Buscar</strong> filtra al escribir. <strong>Editar</strong> abre el panel; mismo criterio de orden de servicio por ID o <strong>Aplicar folio</strong>. <strong>Limpiar</strong> restablece filtros.</p>
            <h4 id="manual-factura-5">5. Autollenar, vista previa y generar automático</h4>
            <p class="manual-p"><strong>Autollenar desde flete</strong> copia cliente, concepto, referencia, moneda y subtotal desde el precio del flete y recalcula IVA/total en pantalla; no persiste hasta Guardar. <strong>Generar automático desde flete</strong> llama al API y crea la factura con folio nuevo; tras exito suele mostrarse el listado. <strong>Vista previa (tarifa)</strong> solo muestra comparacion informativa.</p>
            <h4 id="manual-factura-6">6. Orden de servicio y folio</h4>
            <p class="manual-p">El campo <strong>Orden de servicio</strong> guarda el <strong>ID numerico</strong> de la orden, no el folio legible. Si solo conoce el folio (ej. OS…), escribalo en <strong>Buscar por folio de orden</strong> y pulse <strong>Aplicar folio</strong> para rellenar el ID. Puede obtener el ID en <strong>Fletes → Ordenes de servicio → Ver detalle</strong>.</p>
            <h4 id="manual-factura-7">7. Preguntas frecuentes</h4>
            <p class="manual-p"><strong>¿No aparece el flete?</strong> Compruebe que exista para ese cliente y que el catalogo se haya cargado (F5). <strong>¿Total incorrecto?</strong> Revise subtotal, IVA %, retencion y redondeos. <strong>¿Perdi datos al cambiar de pantalla?</strong> Lo no guardado no se recupera; guarde borrador o emitida segun politica. <strong>¿Metodo de pago PUE o PPD?</strong> PUE suele usarse en pago en una exhibicion; PPD en credito o parcialidades — confirme con fiscal.</p>
            <h4 id="manual-factura-8">8. Mensajes y errores</h4>
            <p class="manual-p">Los avisos bajo el formulario reproducen la respuesta del servidor (validacion, FK inexistente, etc.).</p>
            <h4 id="manual-factura-9">9. Referencia técnica</h4>
            <p class="manual-p">Endpoints <code>/facturas</code>, <code>/facturas/generar-desde-flete</code>, <code>/facturas/preview-desde-flete/…</code> en <a href="/docs">/docs</a>.</p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="page" id="page-tarifas">
        <div class="card">
          <div class="module-subpage-head">
            <div>
              <h3>Subopciones de tarifas</h3>
              <div class="hint">Trabaja una parte a la vez para evitar confusión.</div>
            </div>
            <button type="button" class="secondary-button open-manual-btn" id="tarifa-open-manual-btn" title="Abrir el manual integrado">Abrir manual</button>
          </div>
          <div class="subpage-buttons">
            <button type="button" class="subpage-button" data-tarifa-tab="alta">Nueva tarifa</button>
            <button type="button" class="subpage-button active" data-tarifa-tab="consulta">Consultar y editar</button>
            <button type="button" class="subpage-button" data-tarifa-tab="manual">Manual</button>
          </div>
        </div>
        <div class="split">
          <article class="card hidden" data-tarifa-tab-panel="alta">
            <h3>Nueva tarifa de flete</h3>
            <div class="hint">Define reglas base para proponer precio de venta por ruta, unidad y tipo de carga. <strong>Ambito</strong> y <strong>modalidad</strong> deben coincidir con la cotizacion; los porcentajes se aplican sobre el subtotal en el motor de cotizacion. <strong>Importes y porcentajes:</strong> formato Mexico (miles con coma, decimales con punto) al salir del campo. <strong>Enter</strong> pasa al siguiente campo; solo el boton <strong>Guardar tarifa</strong> envia el formulario.</div>
            <form id="tarifa-form">
              <div class="two-col">
                <label>Nombre tarifa
                  <input name="nombre_tarifa" id="tarifa-form-nombre-tarifa" required autocomplete="off" />
                </label>
                <label>Moneda
                  <input name="moneda" value="MXN" maxlength="3" />
                </label>
              </div>
              <p id="tarifa-form-nombre-aviso" class="hint" hidden style="margin:0;color:var(--error);font-weight:800;"></p>
              <div class="two-col">
                <label class="span-2">Tipo operacion (perfil de venta)
                  <select name="tipo_operacion">
                    <option value="propio">propio</option>
                    <option value="subcontratado" selected>subcontratado</option>
                    <option value="fletero">fletero</option>
                    <option value="aliado">aliado</option>
                  </select>
                </label>
              </div>
              <div class="two-col">
                <label>Ambito
                  <select name="ambito">
                    <option value="local">local</option>
                    <option value="estatal">estatal</option>
                    <option value="federal" selected>federal</option>
                  </select>
                </label>
                <label>Modalidad cobro
                  <select name="modalidad_cobro">
                    <option value="mixta" selected>mixta</option>
                    <option value="por_viaje">por_viaje</option>
                    <option value="por_km">por_km</option>
                    <option value="por_tonelada">por_tonelada</option>
                    <option value="por_hora">por_hora</option>
                    <option value="por_dia">por_dia</option>
                  </select>
                </label>
              </div>
              <div class="two-col">
                <label>Origen
                  <input name="origen" required />
                </label>
                <label>Destino
                  <input name="destino" required />
                </label>
              </div>
              <div class="two-col">
                <label>Tipo unidad
                  <input name="tipo_unidad" required />
                </label>
                <label>Tipo carga
                  <input name="tipo_carga" />
                </label>
              </div>
              <div class="three-col">
                <label>Tarifa base
                  <input name="tarifa_base" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" required />
                </label>
                <label>Tarifa por km
                  <input id="tarifa-venta-alta-tarifa-km" name="tarifa_km" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0" title="Formato Mexico (miles con coma, decimales con punto). Minimo 2 decimales visibles, alineado a tarifa base y recargo." />
                </label>
                <label>Tarifa por kg
                  <input name="tarifa_kg" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="6" value="0" />
                </label>
              </div>
              <div class="three-col">
                <label>Tarifa por tonelada
                  <input name="tarifa_tonelada" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0" />
                </label>
                <label>Tarifa por hora
                  <input name="tarifa_hora" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" value="0" />
                </label>
                <label>Tarifa por dia
                  <input name="tarifa_dia" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" value="0" />
                </label>
              </div>
              <div class="three-col">
                <label>Porc. utilidad (sobre subtotal)
                  <input name="porcentaje_utilidad" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0.20" />
                </label>
                <label>Porc. riesgo
                  <input name="porcentaje_riesgo" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0" />
                </label>
                <label>Porc. urgencia (si marca urgencia en cotizacion)
                  <input name="porcentaje_urgencia" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0" />
                </label>
              </div>
              <div class="two-col">
                <label>Porc. retorno vacio (si aplica en cotizacion)
                  <input name="porcentaje_retorno_vacio" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0" />
                </label>
                <label>Porc. carga especial (refrigerada o peligrosa)
                  <input name="porcentaje_carga_especial" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0" />
                </label>
              </div>
              <div class="three-col">
                <label>Recargo minimo
                  <input name="recargo_minimo" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" value="0" />
                </label>
                <label>Vigencia inicio
                  <input name="vigencia_inicio" type="date" title="Opcional. Use el calendario para evitar error de formato" />
                </label>
                <label>Vigencia fin
                  <input name="vigencia_fin" type="date" title="Opcional. Use el calendario para evitar error de formato" />
                </label>
              </div>
              <label class="check-row">
                <input name="activo" type="checkbox" checked />
                Tarifa activa
              </label>
              <button type="submit">Guardar tarifa</button>
            </form>
            <div id="tarifa-message" class="message"></div>
          </article>
          <article class="card" data-tarifa-tab-panel="consulta">
            <h3>Listado de tarifas</h3>
            <div class="toolbar">
              <div class="filtro-busqueda-modo hint">
                <label>Como buscar el texto
                  <select class="buscar-modo-sync" title="Mismo criterio en todos los listados del panel; se guarda en el navegador">
                    <option value="contiene">Contiene (flexible, recomendado)</option>
                    <option value="prefijo_palabras">Prefijos de palabra (ej. Ro coincide con Rodriguez)</option>
                    <option value="todas_palabras">Todas las palabras, en cualquier orden</option>
                  </select>
                </label>
              </div>
              <label>Buscar rapido (nombre, ruta, unidad, ambito, ID)
                <input id="tarifa-venta-filter-buscar" type="search" list="tarifa-venta-filter-buscar-dl" placeholder="Filtra la tabla mientras escribes" autocomplete="off" style="max-width:28rem" />
              </label>
              <datalist id="tarifa-venta-filter-buscar-dl"></datalist>
            </div>
            <div id="tarifas-table"></div>
            <div id="tarifa-edit-panel" class="toolbar hidden">
              <h4>Editar tarifa de flete</h4>
              <form id="tarifa-edit-form">
                <input name="id" type="hidden" />
                <div class="two-col">
                  <label>Nombre tarifa
                    <input name="nombre_tarifa" id="tarifa-edit-form-nombre-tarifa" required autocomplete="off" />
                  </label>
                  <label>Moneda
                    <input name="moneda" maxlength="3" />
                  </label>
                </div>
                <p id="tarifa-edit-form-nombre-aviso" class="hint" hidden style="margin:0;color:var(--error);font-weight:800;"></p>
                <div class="two-col">
                  <label class="span-2">Tipo operacion (perfil de venta)
                    <select name="tipo_operacion">
                      <option value="propio">propio</option>
                      <option value="subcontratado">subcontratado</option>
                      <option value="fletero">fletero</option>
                      <option value="aliado">aliado</option>
                    </select>
                  </label>
                </div>
                <div class="two-col">
                  <label>Ambito
                    <select name="ambito">
                      <option value="local">local</option>
                      <option value="estatal">estatal</option>
                      <option value="federal">federal</option>
                    </select>
                  </label>
                  <label>Modalidad cobro
                    <select name="modalidad_cobro">
                      <option value="mixta">mixta</option>
                      <option value="por_viaje">por_viaje</option>
                      <option value="por_km">por_km</option>
                      <option value="por_tonelada">por_tonelada</option>
                      <option value="por_hora">por_hora</option>
                      <option value="por_dia">por_dia</option>
                    </select>
                  </label>
                </div>
                <div class="two-col">
                  <label>Origen
                    <input name="origen" required />
                  </label>
                  <label>Destino
                    <input name="destino" required />
                  </label>
                </div>
                <div class="two-col">
                  <label>Tipo unidad
                    <input name="tipo_unidad" required />
                  </label>
                  <label>Tipo carga
                    <input name="tipo_carga" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Tarifa base
                    <input name="tarifa_base" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" required />
                  </label>
                  <label>Tarifa por km
                    <input id="tarifa-venta-edit-tarifa-km" name="tarifa_km" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0" title="Formato Mexico. Minimo 2 decimales visibles." />
                  </label>
                  <label>Tarifa por kg
                    <input name="tarifa_kg" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="6" value="0" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Tarifa por tonelada
                    <input name="tarifa_tonelada" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0" />
                  </label>
                  <label>Tarifa por hora
                    <input name="tarifa_hora" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" value="0" />
                  </label>
                  <label>Tarifa por dia
                    <input name="tarifa_dia" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" value="0" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Porc. utilidad (sobre subtotal)
                    <input name="porcentaje_utilidad" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0" />
                  </label>
                  <label>Porc. riesgo
                    <input name="porcentaje_riesgo" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0" />
                  </label>
                  <label>Porc. urgencia
                    <input name="porcentaje_urgencia" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0" />
                  </label>
                </div>
                <div class="two-col">
                  <label>Porc. retorno vacio
                    <input name="porcentaje_retorno_vacio" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0" />
                  </label>
                  <label>Porc. carga especial
                    <input name="porcentaje_carga_especial" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Recargo minimo
                    <input name="recargo_minimo" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" value="0" />
                  </label>
                  <label>Vigencia inicio
                    <input name="vigencia_inicio" type="date" title="Opcional. Use el calendario para evitar error de formato" />
                  </label>
                  <label>Vigencia fin
                    <input name="vigencia_fin" type="date" title="Opcional. Use el calendario para evitar error de formato" />
                  </label>
                </div>
                <label class="check-row">
                  <input name="activo" type="checkbox" />
                  Tarifa activa
                </label>
                <div class="toolbar-actions">
                  <button type="submit">Guardar cambios</button>
                  <button type="button" id="tarifa-edit-cancel" class="secondary-button">Cancelar</button>
                </div>
              </form>
              <div id="tarifa-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card hidden manual-doc manual-interface" data-tarifa-tab-panel="manual">
            <div class="manual-interface-head">
              <h3>Manual del módulo Tarifas (venta)</h3>
              <span class="manual-badge">Documentación en pantalla</span>
            </div>
            <div class="hint">Tarifas comerciales para cotización: ruta, unidad, componentes de precio y vigencia.</div>
            <div class="manual-interface-body">
              <nav class="manual-toc" id="manual-tarifa-toc" aria-label="Índice del manual de tarifas">
                <div class="manual-toc-title">Contenido</div>
                <a href="#manual-tarifa-1">1. Objetivo</a>
                <a href="#manual-tarifa-2">2. Subopciones</a>
                <a href="#manual-tarifa-3">3. Nueva tarifa</a>
                <a href="#manual-tarifa-4">4. Consulta</a>
                <a href="#manual-tarifa-5">5. Vigencia</a>
                <a href="#manual-tarifa-6">6. FAQ</a>
                <a href="#manual-tarifa-7">7. Mensajes</a>
                <a href="#manual-tarifa-8">8. Referencia</a>
              </nav>
              <div class="manual-scroll" data-manual-scroll="tarifa" tabindex="0" role="region" aria-label="Texto del manual de tarifas">
            <h4 id="manual-tarifa-1">1. Objetivo del módulo</h4>
            <p class="manual-p">Definir reglas de precio de venta por ruta (origen/destino), tipo de unidad y carga, con base, km, kg, recargo mínimo y vigencia.</p>
            <h4 id="manual-tarifa-2">2. Subopciones</h4>
            <ul class="summary-list"><li><strong>Nueva tarifa / Consultar:</strong> alta y listado.</li><li><strong>Manual:</strong> esta guía.</li></ul>
            <h4 id="manual-tarifa-3">3. Nueva tarifa</h4>
            <p class="manual-p">Complete nombre, moneda, tipo de operación (propio, subcontratado, fletero o aliado; predeterminado subcontratado), origen y destino, tipos, tarifa base y componentes opcionales, recargo mínimo, fechas de vigencia y marque si está activa. Use <strong>Enter</strong> para pasar de campo en campo; el guardado en alta ocurre solo al pulsar <strong>Guardar tarifa</strong>. Si guardó incompleta por error, en <strong>Consultar y editar</strong> use <strong>Editar</strong> en la fila para corregir y <strong>Guardar cambios</strong>.</p>
            <h4 id="manual-tarifa-4">4. Consulta</h4>
            <p class="manual-p">El listado muestra las tarifas registradas. En cada fila, <strong>Editar</strong> abre el panel para ajustar datos y vigencias.</p>
            <h4 id="manual-tarifa-5">5. Vigencia</h4>
            <p class="manual-p">Use vigencia inicio/fin para acotar el uso en <strong>Fletes</strong> con método de cálculo <strong>tarifa</strong> o <strong>motor</strong> y en los botones <strong>Cotizar venta</strong>. Las mismas reglas alimentan la <strong>Vista previa (tarifa)</strong> y la opción de recálculo al <strong>Generar automático</strong> de factura desde flete, si aplica.</p>
            <h4 id="manual-tarifa-6">6. Preguntas frecuentes</h4>
            <p class="manual-p"><strong>¿No aplica en flete?</strong> Verifique tipo de unidad/carga, textos de origen/destino, tipo de operación y vigencia. <strong>¿Precio distinto en factura?</strong> Compare con “usar precio recalculado” al generar desde flete y con el precio ya guardado en el flete.</p>
            <h4 id="manual-tarifa-7">7. Mensajes y errores</h4>
            <p class="manual-p">Mensajes del servidor bajo el formulario.</p>
            <h4 id="manual-tarifa-8">8. Referencia técnica</h4>
            <p class="manual-p"><a href="/docs">/docs</a>.</p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="page" id="page-tarifas-compra">
        <div class="card">
          <div class="module-subpage-head">
            <div>
              <h3>Subopciones de tarifas de compra</h3>
              <div class="hint">Trabaja una parte a la vez para evitar confusión.</div>
            </div>
            <button type="button" class="secondary-button open-manual-btn" id="tarifa-compra-open-manual-btn" title="Abrir el manual integrado">Abrir manual</button>
          </div>
          <div class="subpage-buttons">
            <button type="button" class="subpage-button" data-tarifa-compra-tab="alta">Nueva tarifa de compra</button>
            <button type="button" class="subpage-button active" data-tarifa-compra-tab="consulta">Consultar y editar</button>
            <button type="button" class="subpage-button" data-tarifa-compra-tab="manual">Manual</button>
          </div>
        </div>
        <div class="split">
          <article class="card hidden" data-tarifa-compra-tab-panel="alta">
            <h3>Nueva tarifa de compra</h3>
            <div class="hint">Define el costo negociado con cada transportista por ruta, unidad y tipo de carga. <strong>Importes y dias de credito:</strong> formato Mexico (miles con coma, decimales con punto) al salir del campo. <strong>Enter</strong> pasa al siguiente campo; solo el boton <strong>Guardar tarifa de compra</strong> envia el formulario.</div>
            <form id="tarifa-compra-form">
              <div class="hint form-callout">
                Aquí eliges el <strong>proveedor de transporte</strong> (catálogo de transportistas). No es el nombre de la tarifa de venta.
              </div>
              <div class="two-col">
                <label>Transportista
                  <select id="tarifa-compra-transportista" name="transportista_id" required></select>
                </label>
                <label>Nombre tarifa
                  <input name="nombre_tarifa" required />
                </label>
              </div>
              <div class="two-col">
                <label class="span-2">Tipo transportista (debe coincidir con el transportista)
                  <select id="tarifa-compra-tipo-transportista" name="tipo_transportista">
                    <option value="propio">propio</option>
                    <option value="subcontratado" selected>subcontratado</option>
                    <option value="fletero">fletero</option>
                    <option value="aliado">aliado</option>
                  </select>
                </label>
              </div>
              <div class="three-col">
                <label>Ambito
                  <select name="ambito">
                    <option value="local">local</option>
                    <option value="estatal">estatal</option>
                    <option value="federal" selected>federal</option>
                  </select>
                </label>
                <label>Modalidad
                  <select name="modalidad_cobro">
                    <option value="mixta" selected>mixta</option>
                    <option value="por_viaje">por_viaje</option>
                    <option value="por_km">por_km</option>
                    <option value="por_tonelada">por_tonelada</option>
                    <option value="por_hora">por_hora</option>
                    <option value="por_dia">por_dia</option>
                  </select>
                </label>
                <label>Moneda
                  <input name="moneda" value="MXN" maxlength="3" />
                </label>
              </div>
              <div class="two-col">
                <label>Origen
                  <input name="origen" required />
                </label>
                <label>Destino
                  <input name="destino" required />
                </label>
              </div>
              <div class="two-col">
                <label>Tipo unidad
                  <input name="tipo_unidad" required />
                </label>
                <label>Tipo carga
                  <input name="tipo_carga" />
                </label>
              </div>
              <div class="three-col">
                <label>Tarifa base
                  <input name="tarifa_base" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" required />
                </label>
                <label>Tarifa por km
                  <input id="tarifa-compra-alta-tarifa-km" name="tarifa_km" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0" title="Formato Mexico (miles con coma, decimales con punto). Minimo 2 decimales visibles como el resto de importes." />
                </label>
                <label>Tarifa por kg
                  <input name="tarifa_kg" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="6" value="0" />
                </label>
              </div>
              <div class="three-col">
                <label>Tarifa por tonelada
                  <input name="tarifa_tonelada" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" value="0" />
                </label>
                <label>Tarifa por hora
                  <input name="tarifa_hora" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" value="0" />
                </label>
                <label>Tarifa por dia
                  <input name="tarifa_dia" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" value="0" />
                </label>
              </div>
              <div class="three-col">
                <label>Recargo minimo
                  <input name="recargo_minimo" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" value="0" />
                </label>
                <label>Dias credito
                  <input name="dias_credito" type="text" inputmode="numeric" autocomplete="off" class="field-money" data-min-fraction-digits="0" data-max-fraction-digits="0" value="0" title="Enteros. Miles con coma (es-MX); salga del campo para aplicar formato." />
                </label>
                <label>Estatus
                  <select name="activo">
                    <option value="true" selected>activa</option>
                    <option value="false">inactiva</option>
                  </select>
                </label>
              </div>
              <div class="two-col">
                <label>Vigencia inicio
                  <input name="vigencia_inicio" type="date" title="Opcional. Elige con el calendario para evitar error de formato" />
                </label>
                <label>Vigencia fin
                  <input name="vigencia_fin" type="date" title="Opcional. Elige con el calendario para evitar error de formato" />
                </label>
              </div>
              <p class="hint" style="margin:0;font-size:12px;">Las vigencias son opcionales. Si el navegador muestra «valor no valido», usa el icono del calendario o borra el campo. <strong>Importes y dias de credito:</strong> formato Mexico (miles con coma, decimales con punto); al salir del campo se aplica el formato.</p>
              <label>Observaciones
                <textarea name="observaciones"></textarea>
              </label>
              <button type="submit">Guardar tarifa de compra</button>
            </form>
            <div id="tarifa-compra-message" class="message"></div>
          </article>
          <article class="card" data-tarifa-compra-tab-panel="consulta">
            <h3>Listado de tarifas de compra</h3>
            <div class="toolbar">
              <h4>Consultar tarifas de compra</h4>
              <div class="filtro-busqueda-modo hint">
                <label>Como buscar el texto
                  <select class="buscar-modo-sync" title="Mismo criterio en todos los listados del panel; se guarda en el navegador">
                    <option value="contiene">Contiene (flexible, recomendado)</option>
                    <option value="prefijo_palabras">Prefijos de palabra (ej. Ro coincide con Rodriguez)</option>
                    <option value="todas_palabras">Todas las palabras, en cualquier orden</option>
                  </select>
                </label>
              </div>
              <form id="tarifa-compra-filter-form">
                <div class="three-col">
                  <label>Buscar
                    <input id="tarifa-compra-filter-buscar" name="buscar" type="search" list="tarifa-compra-filter-buscar-dl" placeholder="Nombre, transportista, origen, destino" autocomplete="off" />
                  </label>
                  <label>Transportista
                    <select id="tarifa-compra-filter-transportista" name="transportista_id"></select>
                  </label>
                  <label>Estatus
                    <select id="tarifa-compra-filter-activo" name="activo">
                      <option value="">Todas</option>
                      <option value="true">activas</option>
                      <option value="false">inactivas</option>
                    </select>
                  </label>
                </div>
                <datalist id="tarifa-compra-filter-buscar-dl"></datalist>
                <div class="toolbar-actions">
                  <button type="submit">Aplicar filtro</button>
                  <button type="button" id="tarifa-compra-filter-clear" class="secondary-button">Limpiar</button>
                </div>
              </form>
            </div>
            <div id="tarifas-compra-table"></div>
            <div id="tarifa-compra-edit-panel" class="toolbar hidden">
              <h4>Editar tarifa de compra</h4>
              <form id="tarifa-compra-edit-form">
                <input id="tarifa-compra-edit-record-id" name="tarifa_compra_id" type="hidden" autocomplete="off" />
                <div class="two-col">
                  <label>Transportista
                    <select id="edit-tarifa-compra-transportista" name="transportista_id" required></select>
                  </label>
                  <label>Nombre tarifa
                    <input name="nombre_tarifa" required />
                  </label>
                </div>
                <div class="two-col">
                  <label class="span-2">Tipo transportista
                    <select id="edit-tarifa-compra-tipo-transportista" name="tipo_transportista">
                      <option value="propio">propio</option>
                      <option value="subcontratado">subcontratado</option>
                      <option value="fletero">fletero</option>
                      <option value="aliado">aliado</option>
                    </select>
                  </label>
                </div>
                <div class="three-col">
                  <label>Ambito
                    <select name="ambito">
                      <option value="local">local</option>
                      <option value="estatal">estatal</option>
                      <option value="federal">federal</option>
                    </select>
                  </label>
                  <label>Modalidad
                    <select name="modalidad_cobro">
                      <option value="mixta">mixta</option>
                      <option value="por_viaje">por_viaje</option>
                      <option value="por_km">por_km</option>
                      <option value="por_tonelada">por_tonelada</option>
                      <option value="por_hora">por_hora</option>
                      <option value="por_dia">por_dia</option>
                    </select>
                  </label>
                  <label>Moneda
                    <input name="moneda" maxlength="3" />
                  </label>
                </div>
                <div class="two-col">
                  <label>Origen
                    <input name="origen" required />
                  </label>
                  <label>Destino
                    <input name="destino" required />
                  </label>
                </div>
                <div class="two-col">
                  <label>Tipo unidad
                    <input name="tipo_unidad" required />
                  </label>
                  <label>Tipo carga
                    <input name="tipo_carga" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Tarifa base
                    <input name="tarifa_base" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" required />
                  </label>
                  <label>Tarifa por km
                    <input id="tarifa-compra-edit-tarifa-km" name="tarifa_km" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" title="Formato Mexico (miles con coma, decimales con punto). Minimo 2 decimales visibles." />
                  </label>
                  <label>Tarifa por kg
                    <input name="tarifa_kg" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="6" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Tarifa por tonelada
                    <input name="tarifa_tonelada" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="4" />
                  </label>
                  <label>Tarifa por hora
                    <input name="tarifa_hora" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                  </label>
                  <label>Tarifa por dia
                    <input name="tarifa_dia" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Recargo minimo
                    <input name="recargo_minimo" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" />
                  </label>
                  <label>Dias credito
                    <input name="dias_credito" type="text" inputmode="numeric" autocomplete="off" class="field-money" data-min-fraction-digits="0" data-max-fraction-digits="0" title="Enteros. Miles con coma (es-MX); salga del campo para aplicar formato." />
                  </label>
                  <label class="check-row">
                    <input name="activo" type="checkbox" />
                    Tarifa activa
                  </label>
                </div>
                <div class="two-col">
                  <label>Vigencia inicio
                    <input name="vigencia_inicio" type="date" title="Opcional. Elige con el calendario para evitar error de formato" />
                  </label>
                  <label>Vigencia fin
                    <input name="vigencia_fin" type="date" title="Opcional. Elige con el calendario para evitar error de formato" />
                  </label>
                </div>
                <p class="hint" style="margin:0;font-size:12px;">Si aparece error en fecha, borra el campo o usa el calendario. <strong>Importes y dias de credito:</strong> formato Mexico al salir del campo.</p>
                <label>Observaciones
                  <textarea name="observaciones"></textarea>
                </label>
                <div class="toolbar-actions">
                  <button type="submit" id="tarifa-compra-edit-save">Guardar cambios</button>
                  <button type="button" id="tarifa-compra-edit-cancel" class="secondary-button">Cancelar</button>
                </div>
              </form>
              <div id="tarifa-compra-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card hidden manual-doc manual-interface" data-tarifa-compra-tab-panel="manual">
            <div class="manual-interface-head">
              <h3>Manual del módulo Tarifas de compra</h3>
              <span class="manual-badge">Documentación en pantalla</span>
            </div>
            <div class="hint">Costos negociados por transportista, ruta y modalidad de cobro.</div>
            <div class="manual-interface-body">
              <nav class="manual-toc" id="manual-tarifa-compra-toc" aria-label="Índice del manual de tarifas de compra">
                <div class="manual-toc-title">Contenido</div>
                <a href="#manual-tarifa-compra-1">1. Objetivo</a>
                <a href="#manual-tarifa-compra-2">2. Subopciones</a>
                <a href="#manual-tarifa-compra-3">3. Nueva tarifa</a>
                <a href="#manual-tarifa-compra-4">4. Consultar</a>
                <a href="#manual-tarifa-compra-5">5. Modalidad y ámbito</a>
                <a href="#manual-tarifa-compra-6">6. FAQ</a>
                <a href="#manual-tarifa-compra-7">7. Mensajes</a>
                <a href="#manual-tarifa-compra-8">8. Referencia</a>
              </nav>
              <div class="manual-scroll" data-manual-scroll="tarifa-compra" tabindex="0" role="region" aria-label="Texto del manual de tarifas de compra">
            <h4 id="manual-tarifa-compra-1">1. Objetivo del módulo</h4>
            <p class="manual-p">Registrar el costo de compra acordado con cada transportista por ruta, tipo de unidad y carga, con componentes (base, km, kg, tonelada, hora, día) y días de crédito.</p>
            <h4 id="manual-tarifa-compra-2">2. Subopciones</h4>
            <ul class="summary-list"><li><strong>Nueva tarifa de compra / Consultar:</strong> alta, filtros y edición.</li><li><strong>Manual:</strong> esta guía.</li></ul>
            <h4 id="manual-tarifa-compra-3">3. Nueva tarifa de compra</h4>
            <p class="manual-p">Seleccione transportista, tipo de transportista (debe coincidir con el del transportista; predeterminado subcontratado), nombre de tarifa, ámbito (local/estatal/federal), modalidad de cobro, moneda, origen y destino, tipos, importes y vigencia. Marque activa si aplica.</p>
            <h4 id="manual-tarifa-compra-4">4. Consultar y editar</h4>
            <p class="manual-p">Filtre por transportista y criterios; use <strong>Editar</strong> o <strong>Eliminar</strong> según permisos.</p>
            <h4 id="manual-tarifa-compra-5">5. Modalidad y ámbito</h4>
            <p class="manual-p">Alinee modalidad (por viaje, km, etc.) y <strong>ámbito</strong> (local, estatal, federal) con el contrato real del transportista. Los importes y días de crédito usan <strong>formato México</strong> (miles con coma, decimales con punto) al salir del campo, igual que en el alta.</p>
            <h4 id="manual-tarifa-compra-6">6. Preguntas frecuentes</h4>
            <p class="manual-p"><strong>¿No sugiere costo en flete?</strong> Verifique transportista, ruta y tarifa activa.</p>
            <h4 id="manual-tarifa-compra-7">7. Mensajes y errores</h4>
            <p class="manual-p">Respuesta del servidor bajo cada formulario.</p>
            <h4 id="manual-tarifa-compra-8">8. Referencia técnica</h4>
            <p class="manual-p"><a href="/docs">/docs</a>.</p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="page" id="page-operadores">
        <div class="card">
          <div class="module-subpage-head">
            <div>
              <h3>Subopciones de operadores</h3>
              <div class="hint">Trabaja una parte a la vez para evitar confusión.</div>
            </div>
            <button type="button" class="secondary-button open-manual-btn" id="operador-open-manual-btn" title="Abrir el manual integrado">Abrir manual</button>
          </div>
          <div class="subpage-buttons">
            <button type="button" class="subpage-button" data-operador-tab="alta">Nuevo operador</button>
            <button type="button" class="subpage-button active" data-operador-tab="consulta">Consultar y editar</button>
            <button type="button" class="subpage-button" data-operador-tab="manual">Manual</button>
          </div>
        </div>
        <div class="split">
          <article class="card hidden" data-operador-tab-panel="alta">
            <h3>Nuevo operador</h3>
            <div class="hint">Captura basica del chofer para operacion. Los campos principales son obligatorios.</div>
            <form id="operador-form">
              <div class="three-col">
                <label>Transportista
                  <select id="operador-transportista" name="transportista_id"></select>
                </label>
                <label>Tipo contratacion
                  <select name="tipo_contratacion">
                    <option value="">Sin especificar</option>
                    <option value="interno">interno</option>
                    <option value="externo">externo</option>
                  </select>
                </label>
                <label>Estatus documental
                  <select name="estatus_documental">
                    <option value="">Sin especificar</option>
                    <option value="vigente">vigente</option>
                    <option value="vencido">vencido</option>
                    <option value="pendiente">pendiente</option>
                  </select>
                </label>
              </div>
              <div class="three-col">
                <label>Nombre
                  <input name="nombre" required />
                </label>
                <label>Apellido paterno
                  <input name="apellido_paterno" required />
                </label>
                <label>Apellido materno
                  <input name="apellido_materno" />
                </label>
              </div>
              <div class="three-col">
                <label>Fecha nacimiento
                  <input name="fecha_nacimiento" type="date" required />
                </label>
                <label>CURP
                  <input name="curp" minlength="18" maxlength="18" required />
                </label>
                <label>RFC
                  <input name="rfc" maxlength="13" required />
                </label>
              </div>
              <div class="three-col">
                <label>NSS
                  <input name="nss" minlength="11" maxlength="11" required />
                </label>
                <label>Licencia
                  <input name="licencia" />
                </label>
                <label>Tipo licencia
                  <input name="tipo_licencia" />
                </label>
              </div>
              <div class="three-col">
                <label>Vigencia licencia
                  <input name="vigencia_licencia" type="date" />
                </label>
                <label>Estado civil
                  <select name="estado_civil">
                    <option value="soltero">soltero</option>
                    <option value="casado">casado</option>
                    <option value="divorciado">divorciado</option>
                    <option value="viudo">viudo</option>
                    <option value="union_libre">union_libre</option>
                  </select>
                </label>
                <label>Tipo sangre
                  <select name="tipo_sangre">
                    <option value="A+">A+</option>
                    <option value="A-">A-</option>
                    <option value="B+">B+</option>
                    <option value="B-">B-</option>
                    <option value="AB+">AB+</option>
                    <option value="AB-">AB-</option>
                    <option value="O+">O+</option>
                    <option value="O-">O-</option>
                  </select>
                </label>
              </div>
              <div class="two-col">
                <label>Telefono principal
                  <input name="telefono_principal" required />
                </label>
                <label>Telefono emergencia
                  <input name="telefono_emergencia" />
                </label>
              </div>
              <div class="two-col">
                <label>Contacto emergencia
                  <input name="nombre_contacto_emergencia" />
                </label>
                <label>Correo electronico
                  <input name="correo_electronico" type="email" required />
                </label>
              </div>
              <div class="two-col">
                <label>Direccion
                  <input name="direccion" required />
                </label>
                <label>Colonia
                  <input name="colonia" required />
                </label>
              </div>
              <div class="three-col">
                <label>Municipio
                  <input name="municipio" required />
                </label>
                <label>Estado geografico
                  <input name="estado_geografico" required />
                </label>
                <label>Codigo postal
                  <input name="codigo_postal" minlength="5" maxlength="5" required />
                </label>
              </div>
              <div class="two-col">
                <label>Anios experiencia
                  <input name="anios_experiencia" type="number" min="0" step="1" inputmode="numeric" title="Solo numeros enteros" />
                </label>
                <label>Fotografia URL
                  <input name="fotografia" />
                </label>
              </div>
              <div class="two-col">
                <label>Tipos de unidad
                  <input name="tipos_unidad_manejadas" placeholder="torton, tractocamion" />
                </label>
                <label>Tipos de carga
                  <input name="tipos_carga_experiencia" placeholder="seca, paletizada" />
                </label>
              </div>
              <div class="two-col">
                <label>Rutas conocidas
                  <input name="rutas_conocidas" />
                </label>
                <label>Certificaciones
                  <input name="certificaciones" placeholder="Ej. licencia federal, permiso SCT, curso MMPP" title="Texto libre: constancias o capacitaciones relevantes para cumplimiento" />
                </label>
              </div>
              <div class="three-col">
                <label>Ultima revision medica
                  <input name="ultima_revision_medica" type="date" />
                </label>
                <label>Proxima revision medica
                  <input name="proxima_revision_medica" type="date" />
                </label>
                <label class="check-row">
                  <input name="resultado_apto" type="checkbox" />
                  Resultado apto
                </label>
              </div>
              <div class="two-col">
                <label>Puntualidad
                  <input name="puntualidad" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="0" data-max-fraction-digits="2" placeholder="0 a 100" title="0–100. En Mexico puede usar coma o punto como decimal; al salir del campo se aplica formato es-MX." />
                </label>
                <label>Calificacion general
                  <input name="calificacion_general" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="0" data-max-fraction-digits="2" placeholder="0 a 100" title="0–100. Coma o punto decimal; formato es-MX al salir." />
                </label>
              </div>
              <div class="two-col">
                <label>Consumo diesel (prom.)
                  <input name="consumo_diesel_promedio" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="0" data-max-fraction-digits="2" placeholder="ej. km/L" title="Promedio con unidades diesel (tractocamion, etc.); coma o punto decimal; formato Mexico al salir." />
                </label>
                <label>Consumo gasolina (prom.)
                  <input name="consumo_gasolina_promedio" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="0" data-max-fraction-digits="2" placeholder="ej. km/L" title="Promedio con unidades de gasolina; coma o punto decimal; formato Mexico al salir." />
                </label>
              </div>
              <label>Restricciones medicas
                <input name="restricciones_medicas" />
              </label>
              <label>Incidencias de desempeno
                <input name="incidencias_desempeno" />
              </label>
              <label>Comentarios de desempeno
                <textarea name="comentarios_desempeno"></textarea>
              </label>
              <button type="submit">Guardar operador</button>
            </form>
            <div id="operador-message" class="message"></div>
          </article>
          <article class="card" data-operador-tab-panel="consulta">
            <h3>Consultar y editar</h3>
            <div class="hint">Tabla de choferes registrados (filtro solo en pantalla; no borra datos). Si falta alguien, vacie el buscador o use <strong>Limpiar busqueda</strong>. Pulse <strong>Editar</strong> en una fila para el formulario debajo; el alta nuevo sigue en <strong>Nuevo operador</strong>.</div>
            <div class="toolbar">
              <div class="filtro-busqueda-modo hint">
                <label>Como buscar el texto
                  <select class="buscar-modo-sync" title="Mismo criterio en todos los listados del panel; se guarda en el navegador">
                    <option value="contiene">Contiene (flexible, recomendado)</option>
                    <option value="prefijo_palabras">Prefijos de palabra (ej. Ro coincide con Rodriguez)</option>
                    <option value="todas_palabras">Todas las palabras, en cualquier orden</option>
                  </select>
                </label>
              </div>
              <label>Buscar rapido (nombre, CURP, telefono, certificaciones, transportista, ID)
                <input id="operador-filter-buscar" type="search" list="operador-filter-buscar-dl" placeholder="Filtra la tabla mientras escribes" autocomplete="off" style="max-width:28rem" />
              </label>
              <datalist id="operador-filter-buscar-dl"></datalist>
              <div class="toolbar-actions">
                <button type="button" id="operador-filter-clear" class="secondary-button">Limpiar busqueda</button>
              </div>
            </div>
            <div id="operadores-table"></div>
            <div id="operador-edit-panel" class="toolbar hidden" aria-hidden="true">
              <h4>Editar operador seleccionado</h4>
              <p class="hint">Los cambios se guardan con el boton inferior. Para alta de otro operador use <strong>Nuevo operador</strong>.</p>
              <form id="operador-edit-form">
              <input type="hidden" name="id_operador" id="operador-edit-form-id" autocomplete="off" />
              <div class="three-col">
                <label>Transportista
                  <select id="edit-operador-transportista" name="transportista_id"></select>
                </label>
                <label>Tipo contratacion
                  <select name="tipo_contratacion">
                    <option value="">Sin especificar</option>
                    <option value="interno">interno</option>
                    <option value="externo">externo</option>
                  </select>
                </label>
                <label>Estatus documental
                  <select name="estatus_documental">
                    <option value="">Sin especificar</option>
                    <option value="vigente">vigente</option>
                    <option value="vencido">vencido</option>
                    <option value="pendiente">pendiente</option>
                  </select>
                </label>
              </div>
              <div class="three-col">
                <label>Nombre
                  <input name="nombre" required />
                </label>
                <label>Apellido paterno
                  <input name="apellido_paterno" required />
                </label>
                <label>Apellido materno
                  <input name="apellido_materno" />
                </label>
              </div>
              <div class="three-col">
                <label>Fecha nacimiento
                  <input name="fecha_nacimiento" type="date" required />
                </label>
                <label>CURP
                  <input name="curp" minlength="18" maxlength="18" required />
                </label>
                <label>RFC
                  <input name="rfc" maxlength="13" required />
                </label>
              </div>
              <div class="three-col">
                <label>NSS
                  <input name="nss" minlength="11" maxlength="11" required />
                </label>
                <label>Licencia
                  <input name="licencia" />
                </label>
                <label>Tipo licencia
                  <input name="tipo_licencia" />
                </label>
              </div>
              <div class="three-col">
                <label>Vigencia licencia
                  <input name="vigencia_licencia" type="date" />
                </label>
                <label>Estado civil
                  <select name="estado_civil">
                    <option value="soltero">soltero</option>
                    <option value="casado">casado</option>
                    <option value="divorciado">divorciado</option>
                    <option value="viudo">viudo</option>
                    <option value="union_libre">union_libre</option>
                  </select>
                </label>
                <label>Tipo sangre
                  <select name="tipo_sangre">
                    <option value="A+">A+</option>
                    <option value="A-">A-</option>
                    <option value="B+">B+</option>
                    <option value="B-">B-</option>
                    <option value="AB+">AB+</option>
                    <option value="AB-">AB-</option>
                    <option value="O+">O+</option>
                    <option value="O-">O-</option>
                  </select>
                </label>
              </div>
              <div class="two-col">
                <label>Telefono principal
                  <input name="telefono_principal" required />
                </label>
                <label>Telefono emergencia
                  <input name="telefono_emergencia" />
                </label>
              </div>
              <div class="two-col">
                <label>Contacto emergencia
                  <input name="nombre_contacto_emergencia" />
                </label>
                <label>Correo electronico
                  <input name="correo_electronico" type="email" required />
                </label>
              </div>
              <div class="two-col">
                <label>Direccion
                  <input name="direccion" required />
                </label>
                <label>Colonia
                  <input name="colonia" required />
                </label>
              </div>
              <div class="three-col">
                <label>Municipio
                  <input name="municipio" required />
                </label>
                <label>Estado geografico
                  <input name="estado_geografico" required />
                </label>
                <label>Codigo postal
                  <input name="codigo_postal" minlength="5" maxlength="5" required />
                </label>
              </div>
              <div class="two-col">
                <label>Anios experiencia
                  <input name="anios_experiencia" type="number" min="0" step="1" inputmode="numeric" title="Solo numeros enteros" />
                </label>
                <label>Fotografia URL
                  <input name="fotografia" />
                </label>
              </div>
              <div class="two-col">
                <label>Tipos de unidad
                  <input name="tipos_unidad_manejadas" placeholder="torton, tractocamion" />
                </label>
                <label>Tipos de carga
                  <input name="tipos_carga_experiencia" placeholder="seca, paletizada" />
                </label>
              </div>
              <div class="two-col">
                <label>Rutas conocidas
                  <input name="rutas_conocidas" />
                </label>
                <label>Certificaciones
                  <input name="certificaciones" placeholder="Ej. licencia federal, permiso SCT, curso MMPP" title="Texto libre: constancias o capacitaciones relevantes para cumplimiento" />
                </label>
              </div>
              <div class="three-col">
                <label>Ultima revision medica
                  <input name="ultima_revision_medica" type="date" />
                </label>
                <label>Proxima revision medica
                  <input name="proxima_revision_medica" type="date" />
                </label>
                <label class="check-row">
                  <input name="resultado_apto" type="checkbox" />
                  Resultado apto
                </label>
              </div>
              <div class="two-col">
                <label>Puntualidad
                  <input name="puntualidad" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="0" data-max-fraction-digits="2" placeholder="0 a 100" title="0–100. En Mexico puede usar coma o punto como decimal; al salir del campo se aplica formato es-MX." />
                </label>
                <label>Calificacion general
                  <input name="calificacion_general" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="0" data-max-fraction-digits="2" placeholder="0 a 100" title="0–100. Coma o punto decimal; formato es-MX al salir." />
                </label>
              </div>
              <div class="two-col">
                <label>Consumo diesel (prom.)
                  <input name="consumo_diesel_promedio" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="0" data-max-fraction-digits="2" placeholder="ej. km/L" title="Promedio con unidades diesel (tractocamion, etc.); coma o punto decimal; formato Mexico al salir." />
                </label>
                <label>Consumo gasolina (prom.)
                  <input name="consumo_gasolina_promedio" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="0" data-max-fraction-digits="2" placeholder="ej. km/L" title="Promedio con unidades de gasolina; coma o punto decimal; formato Mexico al salir." />
                </label>
              </div>
              <label>Restricciones medicas
                <input name="restricciones_medicas" />
              </label>
              <label>Incidencias de desempeno
                <input name="incidencias_desempeno" />
              </label>
              <label>Comentarios de desempeno
                <textarea name="comentarios_desempeno"></textarea>
              </label>
              <div class="toolbar-actions">
                <button type="submit">Guardar cambios</button>
                <button type="button" id="operador-edit-cancel" class="secondary-button">Cancelar</button>
              </div>
            </form>
            <div id="operador-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card hidden manual-doc manual-interface" data-operador-tab-panel="manual">
            <div class="manual-interface-head">
              <h3>Manual del módulo Operadores</h3>
              <span class="manual-badge">Documentación en pantalla</span>
            </div>
            <div class="hint">Expediente del chofer: datos personales, licencia, afiliación y desempeño.</div>
            <div class="manual-interface-body">
              <nav class="manual-toc" id="manual-operador-toc" aria-label="Índice del manual de operadores">
                <div class="manual-toc-title">Contenido</div>
                <a href="#manual-operador-1">1. Objetivo</a>
                <a href="#manual-operador-2">2. Subopciones</a>
                <a href="#manual-operador-3">3. Nuevo operador</a>
                <a href="#manual-operador-4">4. Consultar y editar</a>
                <a href="#manual-operador-5">5. FAQ</a>
                <a href="#manual-operador-6">6. Mensajes</a>
                <a href="#manual-operador-7">7. Referencia</a>
              </nav>
              <div class="manual-scroll" data-manual-scroll="operador" tabindex="0" role="region" aria-label="Texto del manual de operadores">
            <h4 id="manual-operador-1">1. Objetivo del módulo</h4>
            <p class="manual-p">Registrar operadores con vínculo al transportista, identificación oficial, licencia, datos de contacto, salud y métricas de desempeño para asignaciones.</p>
            <h4 id="manual-operador-2">2. Subopciones</h4>
            <ul class="summary-list"><li><strong>Nuevo operador:</strong> alta.</li><li><strong>Consultar y editar:</strong> listado con boton <strong>Editar</strong> y formulario debajo; los cambios se envian como actualizacion parcial (ver <a href="/docs">/docs</a>, operadores).</li><li><strong>Manual:</strong> esta guía.</li></ul>
            <h4 id="manual-operador-3">3. Nuevo operador</h4>
            <p class="manual-p">Complete transportista, tipo de contratación, datos personales, CURP, RFC, NSS, licencia, contactos, domicilio, referencias y campos de desempeño según política.</p>
            <p class="manual-p"><strong>Certificaciones:</strong> texto libre para anotar constancias o cursos (p. ej. licencia federal vigente, permisos estatales, capacitación en materiales peligrosos). Sirve para trazabilidad; la validación documental al registrar salida de despacho usa reglas adicionales sobre licencia y apto médico.</p>
            <h4 id="manual-operador-4">4. Consultar y editar</h4>
            <p class="manual-p">El listado muestra nombre, transportista, CURP, teléfono, certificaciones y la columna <strong>Acciones</strong>. Pulse <strong>Editar</strong> para desplegar el formulario debajo del listado; <strong>Guardar cambios</strong> actualiza el expediente vía API. El alta de un operador nuevo solo esta en la subopcion <strong>Nuevo operador</strong>.</p>
            <h4 id="manual-operador-5">5. Preguntas frecuentes</h4>
            <p class="manual-p"><strong>¿No aparece en asignación?</strong> Verifique que esté guardado y activo según reglas internas. <strong>¿Bloqueo de salida en Seguimiento?</strong> Complete tipo y vigencia de licencia, estatus documental y datos del expediente; parte del checklist puede considerar licencia federal tipo B/E según la configuración del sistema.</p>
            <h4 id="manual-operador-6">6. Mensajes y errores</h4>
            <p class="manual-p">Validaciones del servidor (CURP, NSS, etc.).</p>
            <h4 id="manual-operador-7">7. Referencia técnica</h4>
            <p class="manual-p"><a href="/docs">/docs</a>.</p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="page" id="page-unidades">
        <div class="card">
          <div class="module-subpage-head">
            <div>
              <h3>Subopciones de unidades</h3>
              <div class="hint">Trabaja una parte a la vez para evitar confusión.</div>
            </div>
            <button type="button" class="secondary-button open-manual-btn" id="unidad-open-manual-btn" title="Abrir el manual integrado">Abrir manual</button>
          </div>
          <div class="subpage-buttons">
            <button type="button" class="subpage-button" data-unidad-tab="alta">Nueva unidad</button>
            <button type="button" class="subpage-button active" data-unidad-tab="consulta">Consultar y editar</button>
            <button type="button" class="subpage-button" data-unidad-tab="manual">Manual</button>
          </div>
        </div>
        <div class="split">
          <article class="card hidden" data-unidad-tab-panel="alta">
            <h3>Nueva unidad</h3>
            <div class="hint">Vehiculos disponibles para asignacion operativa.</div>
            <form id="unidad-form">
              <div class="three-col">
                <label>Transportista
                  <select id="unidad-transportista" name="transportista_id"></select>
                </label>
                <label>Tipo propiedad
                  <select name="tipo_propiedad">
                    <option value="">Sin especificar</option>
                    <option value="propia">propia</option>
                    <option value="tercero">tercero</option>
                  </select>
                </label>
                <label>Estatus documental
                  <select name="estatus_documental">
                    <option value="">Sin especificar</option>
                    <option value="vigente">vigente</option>
                    <option value="vencido">vencido</option>
                    <option value="pendiente">pendiente</option>
                  </select>
                </label>
              </div>
              <div class="two-col">
                <label>Economico
                  <input name="economico" required />
                </label>
                <label>Placas
                  <input name="placas" />
                </label>
              </div>
              <label>Descripcion
                <input name="descripcion" />
              </label>
              <label>Detalle
                <textarea name="detalle"></textarea>
              </label>
              <div class="two-col">
                <label>Vigencia permiso SCT
                  <input name="vigencia_permiso_sct" type="date" />
                </label>
                <label>Vigencia seguro
                  <input name="vigencia_seguro" type="date" />
                </label>
              </div>
              <label class="check-row">
                <input name="activo" type="checkbox" checked />
                Unidad activa
              </label>
              <button type="submit">Guardar unidad</button>
            </form>
            <div id="unidad-message" class="message"></div>
          </article>
          <article class="card" data-unidad-tab-panel="consulta">
            <h3>Consultar y editar</h3>
            <div class="hint">Filtros solo en pantalla (no borran datos en el servidor). Si no ve una unidad, deje en <strong>Todos</strong> tipo de propiedad, estatus documental y activo, vacie el buscador y pulse <strong>Limpiar filtros</strong>. El modo de busqueda de texto es compartido con otros modulos del panel. <strong>Editar</strong> abre el formulario debajo; <strong>Eliminar</strong> borra la fila si no tiene asignaciones vinculadas (pide confirmacion). El alta nueva esta en <strong>Nueva unidad</strong>.</div>
            <div class="toolbar">
              <div class="filtro-busqueda-modo hint">
                <label>Como buscar el texto
                  <select class="buscar-modo-sync" title="Mismo criterio en todos los listados del panel; se guarda en el navegador">
                    <option value="contiene">Contiene (flexible, recomendado)</option>
                    <option value="prefijo_palabras">Prefijos de palabra (ej. Ro coincide con Rodriguez)</option>
                    <option value="todas_palabras">Todas las palabras, en cualquier orden</option>
                  </select>
                </label>
              </div>
              <label>Buscar rapido (economico, placas, descripcion, transportista, ID)
                <input id="unidad-filter-buscar" type="search" list="unidad-filter-buscar-dl" placeholder="Filtra la tabla mientras escribes" autocomplete="off" style="max-width:28rem" />
              </label>
              <datalist id="unidad-filter-buscar-dl"></datalist>
              <div class="three-col">
                <label>Tipo propiedad
                  <select id="unidad-filter-tipo-propiedad">
                    <option value="">Todos</option>
                    <option value="propia">propia</option>
                    <option value="tercero">tercero</option>
                  </select>
                </label>
                <label>Estatus documental
                  <select id="unidad-filter-estatus-doc">
                    <option value="">Todos</option>
                    <option value="vigente">vigente</option>
                    <option value="vencido">vencido</option>
                    <option value="pendiente">pendiente</option>
                  </select>
                </label>
                <label>Activo
                  <select id="unidad-filter-activo">
                    <option value="">Todos</option>
                    <option value="true">activa</option>
                    <option value="false">inactiva</option>
                  </select>
                </label>
              </div>
              <div class="toolbar-actions">
                <button type="button" id="unidad-filter-clear" class="secondary-button">Limpiar filtros</button>
                <button type="button" id="unidad-recargar-catalogo" class="secondary-button" title="Vuelve a pedir las unidades al servidor">Recargar catalogo</button>
              </div>
            </div>
            <div id="unidad-consulta-message" class="message" role="status" aria-live="polite"></div>
            <div id="unidades-table"></div>
            <div id="unidad-edit-panel" class="toolbar hidden" aria-hidden="true">
              <h4>Editar unidad seleccionada</h4>
              <p class="hint">Al guardar, la API devuelve fechas de alta y ultima actualizacion para auditoria; combine con filtros de la tabla para segmentar consultas.</p>
              <form id="unidad-edit-form">
              <input type="hidden" name="id_unidad" id="unidad-edit-form-id" autocomplete="off" />
              <div class="three-col">
                <label>Transportista
                  <select id="edit-unidad-transportista" name="transportista_id"></select>
                </label>
                <label>Tipo propiedad
                  <select name="tipo_propiedad">
                    <option value="">Sin especificar</option>
                    <option value="propia">propia</option>
                    <option value="tercero">tercero</option>
                  </select>
                </label>
                <label>Estatus documental
                  <select name="estatus_documental">
                    <option value="">Sin especificar</option>
                    <option value="vigente">vigente</option>
                    <option value="vencido">vencido</option>
                    <option value="pendiente">pendiente</option>
                  </select>
                </label>
              </div>
              <div class="two-col">
                <label>Economico
                  <input name="economico" required />
                </label>
                <label>Placas
                  <input name="placas" />
                </label>
              </div>
              <label>Descripcion
                <input name="descripcion" />
              </label>
              <label>Detalle
                <textarea name="detalle"></textarea>
              </label>
              <div class="two-col">
                <label>Vigencia permiso SCT
                  <input name="vigencia_permiso_sct" type="date" />
                </label>
                <label>Vigencia seguro
                  <input name="vigencia_seguro" type="date" />
                </label>
              </div>
              <label class="check-row">
                <input name="activo" type="checkbox" />
                Unidad activa
              </label>
              <div class="toolbar-actions">
                <button type="submit">Guardar cambios</button>
                <button type="button" id="unidad-edit-cancel" class="secondary-button">Cancelar</button>
              </div>
            </form>
            <div id="unidad-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card hidden manual-doc manual-interface" data-unidad-tab-panel="manual">
            <div class="manual-interface-head">
              <h3>Manual del módulo Unidades</h3>
              <span class="manual-badge">Documentación en pantalla</span>
            </div>
            <div class="hint">Vehículos económico/placas ligados a transportista para asignación.</div>
            <div class="manual-interface-body">
              <nav class="manual-toc" id="manual-unidad-toc" aria-label="Índice del manual de unidades">
                <div class="manual-toc-title">Contenido</div>
                <a href="#manual-unidad-1">1. Objetivo</a>
                <a href="#manual-unidad-2">2. Subopciones</a>
                <a href="#manual-unidad-3">3. Nueva unidad</a>
                <a href="#manual-unidad-4">4. Consulta</a>
                <a href="#manual-unidad-5">5. FAQ</a>
                <a href="#manual-unidad-6">6. Mensajes</a>
                <a href="#manual-unidad-7">7. Referencia</a>
              </nav>
              <div class="manual-scroll" data-manual-scroll="unidad" tabindex="0" role="region" aria-label="Texto del manual de unidades">
            <h4 id="manual-unidad-1">1. Objetivo del módulo</h4>
            <p class="manual-p">Catalogar unidades (económico, placas, descripción) con transportista, tipo de propiedad y estatus documental.</p>
            <h4 id="manual-unidad-2">2. Subopciones</h4>
            <ul class="summary-list"><li><strong>Nueva unidad / Consultar y editar:</strong> alta, tabla con filtros, <strong>Editar</strong> y <strong>Eliminar</strong> (con confirmación).</li><li><strong>Manual:</strong> esta guía.</li></ul>
            <h4 id="manual-unidad-3">3. Nueva unidad</h4>
            <p class="manual-p">Seleccione transportista, capture económico y placas, tipo de propiedad, estatus documental, descripción, vigencias de permiso SCT y de seguro, detalle y marque <strong>Unidad activa</strong> si aplica.</p>
            <h4 id="manual-unidad-4">4. Consulta</h4>
            <p class="manual-p">Tabla con columnas de documentación y vigencias; use el buscado rápido y los filtros (tipo de propiedad, estatus documental, activo) para segmentar. <strong>Editar</strong> abre el formulario inferior; <strong>Eliminar</strong> pide confirmación y solo procede si la unidad no tiene asignaciones vinculadas. Al guardar edición, la API mantiene fechas de alta y última actualización para auditoría e informes.</p>
            <h4 id="manual-unidad-5">5. Preguntas frecuentes</h4>
            <p class="manual-p"><strong>¿Unidad inactiva?</strong> No debería usarse en nuevas asignaciones según su política. <strong>¿Validación de cumplimiento?</strong> Registre vigencias de <strong>permiso SCT</strong> y <strong>seguro</strong>; el sistema puede contrastarlas al autorizar salida en Seguimiento.</p>
            <h4 id="manual-unidad-6">6. Mensajes y errores</h4>
            <p class="manual-p">Respuesta del servidor bajo el formulario.</p>
            <h4 id="manual-unidad-7">7. Referencia técnica</h4>
            <p class="manual-p"><a href="/docs">/docs</a>. Listado <code>GET /unidades</code> admite <code>activo</code>, <code>buscar</code>, <code>transportista_id</code>, <code>tipo_propiedad</code> y <code>estatus_documental</code> para reportes o integraciones.</p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="page" id="page-gastos">
        <div class="card">
          <div class="module-subpage-head">
            <div>
              <h3>Subopciones de gastos de viaje</h3>
              <div class="hint">Alta de gastos, consulta y edición del listado; en la misma vista, presupuesto y liquidación por flete.</div>
            </div>
            <button type="button" class="secondary-button open-manual-btn" id="gasto-open-manual-btn" title="Abrir el manual integrado">Abrir manual</button>
          </div>
          <div class="subpage-buttons">
            <button type="button" class="subpage-button" data-gasto-tab="alta">Nuevo gasto</button>
            <button type="button" class="subpage-button active" data-gasto-tab="consulta">Consultar y editar</button>
            <button type="button" class="subpage-button" data-gasto-tab="manual">Manual</button>
          </div>
        </div>
        <div class="split">
          <article class="card hidden" data-gasto-tab-panel="alta">
            <h3>Nuevo gasto de viaje</h3>
            <div class="hint">Cada gasto actualiza el <strong>costo real</strong> y el <strong>margen real</strong> del flete. Elija la <strong>categoría</strong> alineada al presupuesto y a la liquidación (operación propia: combustible, peajes, viáticos, operador, mantenimiento; terceros: pago a transportista; imprevistos y administrativos cuando aplique).</div>
            <form id="gasto-form">
              <div class="two-col">
                <label>Flete
                  <select id="gasto-flete" name="flete_id" required></select>
                </label>
                <label>Categoría de gasto
                  <select id="gasto-tipo-gasto" name="tipo_gasto" required>
                    <option value="">Seleccione…</option>
                    <option value="combustible">Combustible (diesel)</option>
                    <option value="peajes">Peajes / casetas</option>
                    <option value="viaticos">Viáticos operador</option>
                    <option value="operador">Mano de obra operador</option>
                    <option value="mantenimiento_km">Mantenimiento y desgaste (por km)</option>
                    <option value="imprevistos">Imprevistos (grúa, multas, ponchaduras…)</option>
                    <option value="administrativos">Administrativos del viaje (CP, seguro carga…)</option>
                    <option value="pago_transporte_tercero">Pago a transportista (subcontratado / fletero / aliado)</option>
                    <option value="otros">Otros (detalle en descripción)</option>
                  </select>
                </label>
              </div>
              <div class="two-col">
                <label>Monto
                  <input name="monto" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" required />
                </label>
                <label>Fecha gasto
                  <input name="fecha_gasto" type="date" required />
                </label>
              </div>
              <div class="two-col">
                <label>Referencia
                  <input name="referencia" />
                </label>
                <label>Comprobante URL
                  <input name="comprobante" />
                </label>
              </div>
              <label>Descripción (opcional, recomendada en «Otros» o para folio/ticket)
                <textarea name="descripcion" placeholder="Ej. folio caseta, litros, estación, incidencia…"></textarea>
              </label>
              <button type="submit">Guardar gasto</button>
            </form>
            <div id="gasto-message" class="message"></div>
          </article>
          <article class="card" data-gasto-tab-panel="consulta">
            <h3>Listado de gastos de viaje</h3>
            <div class="toolbar">
              <div class="filtro-busqueda-modo hint">
                <label>Como buscar el texto
                  <select class="buscar-modo-sync" title="Mismo criterio en todos los listados del panel; se guarda en el navegador">
                    <option value="contiene">Contiene (flexible, recomendado)</option>
                    <option value="prefijo_palabras">Prefijos de palabra (ej. Ro coincide con Rodriguez)</option>
                    <option value="todas_palabras">Todas las palabras, en cualquier orden</option>
                  </select>
                </label>
              </div>
              <label>Buscar rapido (flete, tipo, referencia, monto, ID)
                <input id="gasto-filter-buscar" type="search" list="gasto-filter-buscar-dl" placeholder="Filtra la tabla mientras escribes" autocomplete="off" style="max-width:28rem" />
              </label>
              <datalist id="gasto-filter-buscar-dl"></datalist>
            </div>
            <div id="gasto-list-message" class="message"></div>
            <div id="gastos-table"></div>
            <div id="gasto-edit-panel" class="toolbar hidden">
              <h4>Editar gasto de viaje</h4>
              <form id="gasto-edit-form">
                <input name="id" type="hidden" />
                <div class="two-col">
                  <label>Flete
                    <select id="edit-gasto-flete" name="flete_id" required></select>
                  </label>
                  <label>Categoría de gasto
                    <select id="edit-gasto-tipo-gasto" name="tipo_gasto" required>
                      <option value="combustible">Combustible (diesel)</option>
                      <option value="peajes">Peajes / casetas</option>
                      <option value="viaticos">Viáticos operador</option>
                      <option value="operador">Mano de obra operador</option>
                      <option value="mantenimiento_km">Mantenimiento y desgaste (por km)</option>
                      <option value="imprevistos">Imprevistos (grúa, multas, ponchaduras…)</option>
                      <option value="administrativos">Administrativos del viaje (CP, seguro carga…)</option>
                      <option value="pago_transporte_tercero">Pago a transportista (subcontratado / fletero / aliado)</option>
                      <option value="otros">Otros (detalle en descripción)</option>
                    </select>
                  </label>
                </div>
                <div class="two-col">
                  <label>Monto
                    <input name="monto" type="text" inputmode="decimal" autocomplete="off" class="field-money" data-min-fraction-digits="2" data-max-fraction-digits="2" required />
                  </label>
                  <label>Fecha gasto
                    <input name="fecha_gasto" type="date" required />
                  </label>
                </div>
                <div class="two-col">
                  <label>Referencia
                    <input name="referencia" />
                  </label>
                  <label>Comprobante URL
                    <input name="comprobante" />
                  </label>
                </div>
                <label>Descripción
                  <textarea name="descripcion" placeholder="Ej. folio, ticket, incidencia…"></textarea>
                </label>
                <div class="toolbar-actions">
                  <button type="submit">Guardar cambios</button>
                  <button type="button" id="gasto-edit-cancel" class="secondary-button">Cancelar</button>
                </div>
              </form>
              <div id="gasto-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card" data-gasto-tab-panel="consulta">
            <h3>Presupuesto y liquidación</h3>
            <div class="hint">Operación <strong>propia</strong>: genera presupuesto desglosado (combustible, peajes, viáticos, operador, mantenimiento, contingencia). <strong>Terceros</strong>: una línea con costo de transporte estimado. Compare con gastos reales capturados.</div>
            <div class="two-col" style="margin-top:0.75rem;">
              <label>Flete
                <select id="gasto-control-flete"></select>
              </label>
              <div class="row-actions" style="align-items:flex-end;padding-top:1.4rem;">
                <button type="button" class="secondary-button" id="gasto-presupuesto-generar">Generar presupuesto</button>
                <button type="button" class="secondary-button" id="gasto-liquidacion-ver">Ver liquidación</button>
              </div>
            </div>
            <pre id="gasto-control-output" class="hint" style="white-space:pre-wrap;max-height:22rem;overflow:auto;margin-top:0.75rem;font-size:0.85rem;"></pre>
          </article>
          <article class="card hidden manual-doc manual-interface" data-gasto-tab-panel="manual">
            <div class="manual-interface-head">
              <h3>Manual del módulo Gastos de viaje</h3>
              <span class="manual-badge">Documentación en pantalla</span>
            </div>
            <div class="hint">Costos reales por flete que actualizan margen real.</div>
            <div class="manual-interface-body">
              <nav class="manual-toc" id="manual-gasto-toc" aria-label="Índice del manual de gastos">
                <div class="manual-toc-title">Contenido</div>
                <a href="#manual-gasto-1">1. Objetivo</a>
                <a href="#manual-gasto-2">2. Subopciones</a>
                <a href="#manual-gasto-3">3. Nuevo gasto</a>
                <a href="#manual-gasto-4">4. Lista de gastos</a>
                <a href="#manual-gasto-5">5. Presupuesto y liquidación</a>
                <a href="#manual-gasto-6">6. Preguntas frecuentes</a>
                <a href="#manual-gasto-7">7. Mensajes y errores</a>
                <a href="#manual-gasto-8">8. Referencia técnica</a>
              </nav>
              <div class="manual-scroll" data-manual-scroll="gasto" tabindex="0" role="region" aria-label="Texto del manual de gastos">
            <div class="manual-note"><strong>Misma vista “Consultar y editar”:</strong> debajo del listado de gastos aparece el bloque <strong>Presupuesto y liquidación</strong> (select de flete y botones). No es una pestaña aparte: permanezca en <strong>Consultar y editar</strong> para ver ambos.</div>
            <h4 id="manual-gasto-1">1. Objetivo del módulo</h4>
            <p class="manual-p">Registrar gastos reales (combustible, peajes, viáticos, pago a terceros, etc.) ligados a un flete, actualizar <strong>costo real</strong> y <strong>margen real</strong>, y contrastar con presupuesto y liquidación operativa.</p>
            <h4 id="manual-gasto-2">2. Subopciones</h4>
            <ul class="summary-list">
              <li><strong>Nuevo gasto:</strong> alta de un movimiento de costo por flete y categoría.</li>
              <li><strong>Consultar y editar:</strong> buscador de texto (comparte modo de búsqueda con otros módulos), tabla con <strong>Editar</strong> y <strong>Eliminar</strong>, y debajo el área <strong>Presupuesto y liquidación</strong>.</li>
              <li><strong>Manual:</strong> esta guía.</li>
            </ul>
            <h4 id="manual-gasto-3">3. Nuevo gasto</h4>
            <p class="manual-p">Seleccione <strong>Flete</strong> y <strong>categoría de gasto</strong> alineada al presupuesto (operación propia: combustible, peajes, viáticos, operador, mantenimiento; terceros: pago a transportista; imprevistos y administrativos cuando aplique). Capture monto, fecha, referencia, URL de comprobante si aplica y descripción; en <strong>Otros</strong> el detalle en descripción es especialmente importante.</p>
            <h4 id="manual-gasto-4">4. Lista de gastos</h4>
            <p class="manual-p">El listado filtra mientras escribe en <strong>Buscar rápido</strong>. <strong>Editar</strong> abre el panel inferior; <strong>Eliminar</strong> pide confirmación y al quitar un gasto el sistema recalcula el costo real del flete.</p>
            <h4 id="manual-gasto-5">5. Presupuesto y liquidación</h4>
            <p class="manual-p">En la misma página que el listado, elija el <strong>Flete</strong> en el selector dedicado y pulse <strong>Generar presupuesto</strong> (desglose para operación propia o línea de costo de transporte para terceros). <strong>Ver liquidación</strong> compara presupuesto frente a gastos capturados y muestra alertas si el real excede al presupuesto en más del 5 % (ajuste según reglas del motor en servidor).</p>
            <h4 id="manual-gasto-6">6. Preguntas frecuentes</h4>
            <p class="manual-p"><strong>¿No cambia el margen?</strong> Confirme guardado del gasto y que el flete sea el correcto. <strong>¿No veo presupuesto?</strong> Baje en la misma pestaña <strong>Consultar y editar</strong> tras la tabla. <strong>¿Listado vacío?</strong> Verifique filtro de búsqueda y que existan gastos para ese flete.</p>
            <h4 id="manual-gasto-7">7. Mensajes y errores</h4>
            <p class="manual-p">Respuesta del servidor bajo el formulario de alta o edición.</p>
            <h4 id="manual-gasto-8">8. Referencia técnica</h4>
            <p class="manual-p">Rutas de gastos, presupuesto y liquidación en <a href="/docs">/docs</a>.</p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="page" id="page-asignaciones">
        <div class="card">
          <div class="module-subpage-head">
            <div>
              <h3>Subopciones de asignaciones</h3>
              <div class="hint">Alta de asignacion o consulta y edicion del listado.</div>
            </div>
            <button type="button" class="secondary-button open-manual-btn" id="asignacion-open-manual-btn" title="Abrir el manual integrado">Abrir manual</button>
          </div>
          <div class="subpage-buttons">
            <button type="button" class="subpage-button" data-asignacion-tab="alta">Nueva asignacion</button>
            <button type="button" class="subpage-button active" data-asignacion-tab="consulta">Consultar y editar</button>
            <button type="button" class="subpage-button" data-asignacion-tab="manual">Manual</button>
          </div>
        </div>
        <div class="split">
          <article class="card hidden" data-asignacion-tab-panel="alta">
            <h3>Nueva asignacion</h3>
            <div class="hint">Conecta operador, unidad y viaje. Operadores y unidades existentes se cargan automaticamente.</div>
            <form id="asignacion-form">
              <div class="three-col">
                <label>Operador
                  <select id="asignacion-operador" name="id_operador" required></select>
                </label>
                <label>Unidad
                  <select id="asignacion-unidad" name="id_unidad" required></select>
                </label>
                <label>Viaje
                  <select id="asignacion-viaje" name="id_viaje" required></select>
                </label>
              </div>
              <div class="three-col">
                <label>Fecha salida
                  <input name="fecha_salida" type="datetime-local" required />
                </label>
                <label>Fecha regreso
                  <input name="fecha_regreso" type="datetime-local" />
                </label>
                <label>Km inicial
                  <input name="km_inicial" type="number" step="0.01" min="0" />
                </label>
              </div>
              <div class="two-col">
                <label>Km final
                  <input name="km_final" type="number" step="0.01" min="0" />
                </label>
                <label>Rendimiento combustible
                  <input name="rendimiento_combustible" type="number" step="0.001" min="0" />
                </label>
              </div>
              <button type="submit">Guardar asignacion</button>
            </form>
            <div id="asignacion-message" class="message"></div>
          </article>
          <article class="card" data-asignacion-tab-panel="consulta">
            <h3>Listado de asignaciones</h3>
            <div class="toolbar">
              <h4>Consultar asignaciones</h4>
              <div class="filtro-busqueda-modo hint">
                <label>Como buscar el texto
                  <select class="buscar-modo-sync" title="Mismo criterio en todos los listados del panel; se guarda en el navegador">
                    <option value="contiene">Contiene (flexible, recomendado)</option>
                    <option value="prefijo_palabras">Prefijos de palabra (ej. Ro coincide con Rodriguez)</option>
                    <option value="todas_palabras">Todas las palabras, en cualquier orden</option>
                  </select>
                </label>
              </div>
              <form id="asignacion-filter-form">
                <div class="two-col">
                  <label class="span-2">Buscar rapido
                    <input id="asignacion-filter-buscar" name="buscar" type="search" list="asignacion-filter-buscar-dl" placeholder="Operador, economico, codigo viaje o ID" autocomplete="off" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Operador
                    <select id="asignacion-filter-operador" name="id_operador"></select>
                  </label>
                  <label>Unidad
                    <select id="asignacion-filter-unidad" name="id_unidad"></select>
                  </label>
                  <label>Viaje
                    <select id="asignacion-filter-viaje" name="id_viaje"></select>
                  </label>
                </div>
                <datalist id="asignacion-filter-buscar-dl"></datalist>
                <div class="toolbar-actions">
                  <button type="submit">Aplicar filtro</button>
                  <button type="button" id="asignacion-filter-clear" class="secondary-button">Limpiar</button>
                </div>
              </form>
            </div>
            <div id="asignaciones-table"></div>
            <div id="asignacion-edit-panel" class="toolbar hidden">
              <h4>Editar asignacion</h4>
              <form id="asignacion-edit-form">
                <input name="id_asignacion" type="hidden" />
                <div class="three-col">
                  <label>Operador
                    <select id="edit-asignacion-operador" name="id_operador" required></select>
                  </label>
                  <label>Unidad
                    <select id="edit-asignacion-unidad" name="id_unidad" required></select>
                  </label>
                  <label>Viaje
                    <select id="edit-asignacion-viaje" name="id_viaje" required></select>
                  </label>
                </div>
                <div class="three-col">
                  <label>Fecha salida
                    <input name="fecha_salida" type="datetime-local" required />
                  </label>
                  <label>Fecha regreso
                    <input name="fecha_regreso" type="datetime-local" />
                  </label>
                  <label>Km inicial
                    <input name="km_inicial" type="number" step="0.01" min="0" />
                  </label>
                </div>
                <div class="two-col">
                  <label>Km final
                    <input name="km_final" type="number" step="0.01" min="0" />
                  </label>
                  <label>Rendimiento combustible
                    <input name="rendimiento_combustible" type="number" step="0.001" min="0" />
                  </label>
                </div>
                <div class="toolbar-actions">
                  <button type="submit">Guardar cambios</button>
                  <button type="button" id="asignacion-edit-cancel" class="secondary-button">Cancelar</button>
                </div>
              </form>
              <div id="asignacion-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card hidden manual-doc manual-interface" data-asignacion-tab-panel="manual">
            <div class="manual-interface-head">
              <h3>Manual del módulo Asignaciones</h3>
              <span class="manual-badge">Documentación en pantalla</span>
            </div>
            <div class="hint">Vincula operador, unidad y viaje con fechas y kilometraje.</div>
            <div class="manual-interface-body">
              <nav class="manual-toc" id="manual-asignacion-toc" aria-label="Índice del manual de asignaciones">
                <div class="manual-toc-title">Contenido</div>
                <a href="#manual-asignacion-1">1. Objetivo</a>
                <a href="#manual-asignacion-2">2. Subopciones</a>
                <a href="#manual-asignacion-3">3. Nueva asignación</a>
                <a href="#manual-asignacion-4">4. Consultar y editar</a>
                <a href="#manual-asignacion-5">5. Filtros</a>
                <a href="#manual-asignacion-6">6. FAQ</a>
                <a href="#manual-asignacion-7">7. Mensajes</a>
                <a href="#manual-asignacion-8">8. Referencia</a>
              </nav>
              <div class="manual-scroll" data-manual-scroll="asignacion" tabindex="0" role="region" aria-label="Texto del manual de asignaciones">
            <h4 id="manual-asignacion-1">1. Objetivo del módulo</h4>
            <p class="manual-p">Crear la tripleta operador–unidad–viaje con ventana de salida/regreso y lecturas de kilometraje y rendimiento.</p>
            <h4 id="manual-asignacion-2">2. Subopciones</h4>
            <ul class="summary-list"><li><strong>Nueva asignación:</strong> alta.</li><li><strong>Consultar y editar:</strong> filtros por operador, unidad y viaje.</li><li><strong>Manual:</strong> esta guía.</li></ul>
            <h4 id="manual-asignacion-3">3. Nueva asignación</h4>
            <p class="manual-p">Elija <strong>operador</strong>, <strong>unidad</strong> y <strong>viaje</strong>; registre <strong>fecha salida</strong> (obligatoria), fecha de regreso si aplica, km inicial/final y rendimiento de combustible según su política.</p>
            <h4 id="manual-asignacion-4">4. Consultar y editar</h4>
            <p class="manual-p">Filtre por operador, unidad y viaje; use <strong>Buscar rápido</strong> (económico, código de viaje, etc.) con el mismo <strong>modo de búsqueda</strong> que otros listados del panel. <strong>Editar</strong> abre el panel inferior para actualizar fechas y kilometraje.</p>
            <h4 id="manual-asignacion-5">5. Filtros</h4>
            <p class="manual-p"><strong>Aplicar filtro</strong> y <strong>Limpiar</strong> ajustan la tabla y cierran edición si aplica. Las asignaciones sirven de base para <strong>Despachos → Nuevo despacho</strong>.</p>
            <h4 id="manual-asignacion-6">6. Preguntas frecuentes</h4>
            <p class="manual-p"><strong>¿Selectores vacíos?</strong> Cree operadores, unidades y viajes primero y recargue (F5). <strong>¿No puedo crear despacho?</strong> Debe existir una asignación vigente en catálogo; verifique en Despachos los filtros.</p>
            <h4 id="manual-asignacion-7">7. Mensajes y errores</h4>
            <p class="manual-p">Respuesta del servidor en el panel de mensajes.</p>
            <h4 id="manual-asignacion-8">8. Referencia técnica</h4>
            <p class="manual-p"><a href="/docs">/docs</a>.</p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="page" id="page-despachos">
        <div class="card">
          <div class="module-subpage-head">
            <div>
              <h3>Subopciones de despachos</h3>
              <div class="hint">Programacion de despacho o consulta y edicion del listado.</div>
            </div>
            <button type="button" class="secondary-button open-manual-btn" id="despacho-open-manual-btn" title="Abrir el manual integrado">Abrir manual</button>
          </div>
          <div class="subpage-buttons">
            <button type="button" class="subpage-button" data-despacho-tab="alta">Nuevo despacho</button>
            <button type="button" class="subpage-button active" data-despacho-tab="consulta">Consultar y editar</button>
            <button type="button" class="subpage-button" data-despacho-tab="manual">Manual</button>
          </div>
        </div>
        <div class="split">
          <article class="card hidden" data-despacho-tab-panel="alta">
            <h3>Nuevo despacho</h3>
            <div class="hint">Programa la operacion usando una asignacion y, si aplica, un flete.</div>
            <form id="despacho-form">
              <div class="two-col">
                <label>Asignacion
                  <select id="despacho-asignacion" name="id_asignacion" required></select>
                </label>
                <label>Flete
                  <select id="despacho-flete" name="id_flete"></select>
                </label>
              </div>
              <label>Salida programada
                <input name="salida_programada" type="datetime-local" />
              </label>
              <label>Observaciones de transito
                <textarea name="observaciones_transito"></textarea>
              </label>
              <button type="submit">Crear despacho</button>
            </form>
            <div id="despacho-message" class="message"></div>
          </article>
          <article class="card" data-despacho-tab-panel="consulta">
            <h3>Listado de despachos</h3>
            <div class="toolbar">
              <h4>Consultar despachos</h4>
              <div class="filtro-busqueda-modo hint">
                <label>Como buscar el texto
                  <select class="buscar-modo-sync" title="Mismo criterio en todos los listados del panel; se guarda en el navegador">
                    <option value="contiene">Contiene (flexible, recomendado)</option>
                    <option value="prefijo_palabras">Prefijos de palabra (ej. Ro coincide con Rodriguez)</option>
                    <option value="todas_palabras">Todas las palabras, en cualquier orden</option>
                  </select>
                </label>
              </div>
              <form id="despacho-filter-form">
                <div class="two-col">
                  <label class="span-2">Buscar rapido
                    <input id="despacho-filter-buscar" name="buscar" type="search" list="despacho-filter-buscar-dl" placeholder="Codigo flete, viaje, estatus o ID" autocomplete="off" />
                  </label>
                </div>
                <div class="three-col">
                  <label>Estatus
                    <select id="despacho-filter-estatus" name="estatus">
                      <option value="">Todos</option>
                      <option value="programado">programado</option>
                      <option value="despachado">despachado</option>
                      <option value="entregado">entregado</option>
                      <option value="cerrado">cerrado</option>
                      <option value="cancelado">cancelado</option>
                    </select>
                  </label>
                  <label>Asignacion
                    <select id="despacho-filter-asignacion" name="id_asignacion"></select>
                  </label>
                  <label>Flete
                    <select id="despacho-filter-flete" name="id_flete"></select>
                  </label>
                </div>
                <datalist id="despacho-filter-buscar-dl"></datalist>
                <div class="toolbar-actions">
                  <button type="submit">Aplicar filtro</button>
                  <button type="button" id="despacho-filter-clear" class="secondary-button">Limpiar</button>
                </div>
              </form>
            </div>
            <div id="despachos-table"></div>
            <div id="despacho-edit-panel" class="toolbar hidden">
              <h4>Editar despacho</h4>
              <form id="despacho-edit-form">
                <input type="hidden" name="id_despacho" id="despacho-edit-form-id" autocomplete="off" />
                <label>Asignacion actual
                  <input name="asignacion_label" readonly />
                </label>
                <div class="two-col">
                  <label>Flete
                    <select id="edit-despacho-flete" name="id_flete"></select>
                  </label>
                  <label>Estatus
                    <select name="estatus">
                      <option value="programado">programado</option>
                      <option value="despachado">despachado</option>
                      <option value="entregado">entregado</option>
                      <option value="cerrado">cerrado</option>
                      <option value="cancelado">cancelado</option>
                    </select>
                  </label>
                </div>
                <label>Salida programada
                  <input name="salida_programada" type="datetime-local" />
                </label>
                <label>Observaciones de transito
                  <textarea name="observaciones_transito"></textarea>
                </label>
                <label>Motivo cancelacion
                  <input name="motivo_cancelacion" />
                </label>
                <div class="toolbar-actions">
                  <button type="submit">Guardar cambios</button>
                  <button type="button" id="despacho-edit-cancel" class="secondary-button">Cancelar</button>
                </div>
              </form>
              <div id="despacho-edit-message" class="message"></div>
            </div>
          </article>
          <article class="card hidden manual-doc manual-interface" data-despacho-tab-panel="manual">
            <div class="manual-interface-head">
              <h3>Manual del módulo Despachos</h3>
              <span class="manual-badge">Documentación en pantalla</span>
            </div>
            <div class="hint">Programa la salida operativa vinculando asignación y flete.</div>
            <div class="manual-interface-body">
              <nav class="manual-toc" id="manual-despacho-toc" aria-label="Índice del manual de despachos">
                <div class="manual-toc-title">Contenido</div>
                <a href="#manual-despacho-1">1. Objetivo</a>
                <a href="#manual-despacho-2">2. Subopciones</a>
                <a href="#manual-despacho-3">3. Nuevo despacho</a>
                <a href="#manual-despacho-4">4. Consultar y editar</a>
                <a href="#manual-despacho-5">5. Estados</a>
                <a href="#manual-despacho-6">6. FAQ</a>
                <a href="#manual-despacho-7">7. Mensajes</a>
                <a href="#manual-despacho-8">8. Referencia</a>
              </nav>
              <div class="manual-scroll" data-manual-scroll="despacho" tabindex="0" role="region" aria-label="Texto del manual de despachos">
            <h4 id="manual-despacho-1">1. Objetivo del módulo</h4>
            <p class="manual-p">Crear el registro de despacho a partir de una <strong>asignación</strong> (operador–unidad–viaje) y, opcionalmente, un <strong>flete</strong>; definir salida programada y observaciones de tránsito para uso operativo y enlaces con seguimiento.</p>
            <h4 id="manual-despacho-2">2. Subopciones</h4>
            <ul class="summary-list"><li><strong>Nuevo despacho:</strong> alta.</li><li><strong>Consultar y editar:</strong> filtros por estatus, asignación y flete; edición de estatus, motivo de cancelación y demás campos permitidos.</li><li><strong>Manual:</strong> esta guía.</li></ul>
            <p class="manual-p"><strong>Relación con Seguimiento:</strong> aquí se administra el <strong>encabezado</strong> del despacho (estatus, vínculos). La <strong>salida real</strong>, eventos en ruta, entrega, cierre y cancelación con registro de hora se capturan en <strong>Seguimiento</strong> sobre el mismo despacho.</p>
            <h4 id="manual-despacho-3">3. Nuevo despacho</h4>
            <p class="manual-p">Seleccione <strong>Asignación</strong> (obligatoria) y <strong>Flete</strong> si aplica; indique <strong>Salida programada</strong> y observaciones. Tras crear, use <strong>Seguimiento → Registrar salida</strong> cuando el vehículo efectivamente salga a ruta.</p>
            <h4 id="manual-despacho-4">4. Consultar y editar</h4>
            <p class="manual-p">Use <strong>Buscar rápido</strong> y filtros; pulse <strong>Editar</strong> para ajustar estatus, flete, salida programada, observaciones y <strong>Motivo cancelación</strong> si el estatus es o pasará a cancelado. Los eventos puntuales (kilómetros de salida/llegada, etc.) siguen en Seguimiento.</p>
            <h4 id="manual-despacho-5">5. Estados</h4>
            <p class="manual-p">programado, despachado, entregado, cerrado, cancelado — alineados con el flujo en <strong>Seguimiento</strong> (salida, entrega, cierre, cancelación). Mantenga coherencia entre lo editado aquí y lo registrado en campo.</p>
            <h4 id="manual-despacho-6">6. Preguntas frecuentes</h4>
            <p class="manual-p"><strong>¿No hay asignación?</strong> Créela antes en el módulo <strong>Asignaciones</strong>. <strong>¿Bloqueo al registrar salida?</strong> Revise cumplimiento documental (Carta Porte, mercancía, seguros, licencias) en flete/transportista/operador; Seguimiento puede ofrecer omitir validación solo si su política lo autoriza.</p>
            <h4 id="manual-despacho-7">7. Mensajes y errores</h4>
            <p class="manual-p">Respuesta del servidor bajo cada formulario.</p>
            <h4 id="manual-despacho-8">8. Referencia técnica</h4>
            <p class="manual-p"><a href="/docs">/docs</a>.</p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="page" id="page-seguimiento">
        <div class="card">
          <div class="module-subpage-head">
            <div>
              <h3>Subopciones de seguimiento</h3>
              <div class="hint">Una accion por vista: salida, evento en ruta, entrega, cierre o cancelacion.</div>
            </div>
            <button type="button" class="secondary-button open-manual-btn" id="seguimiento-open-manual-btn" title="Abrir el manual integrado">Abrir manual</button>
          </div>
          <div class="subpage-buttons">
            <button type="button" class="subpage-button active" data-seguimiento-tab="salida">Registrar salida</button>
            <button type="button" class="subpage-button" data-seguimiento-tab="evento">Evento en ruta</button>
            <button type="button" class="subpage-button" data-seguimiento-tab="entrega">Registrar entrega</button>
            <button type="button" class="subpage-button" data-seguimiento-tab="cierre">Cerrar despacho</button>
            <button type="button" class="subpage-button" data-seguimiento-tab="cancelacion">Cancelar despacho</button>
            <button type="button" class="subpage-button" data-seguimiento-tab="manual">Manual</button>
          </div>
        </div>
        <div class="grid capture-grid">
          <article class="card capture-card" data-seguimiento-tab-panel="salida">
            <h3>Registrar salida</h3>
            <div class="hint">Marca que el despacho ya salio a ruta.</div>
            <form id="salida-form">
              <div class="two-col">
                <label>Despacho
                  <select id="salida-despacho" name="id_despacho" required></select>
                </label>
                <label>Fecha y hora real
                  <input name="salida_real" type="datetime-local" required />
                </label>
              </div>
              <div class="two-col">
                <label>Km salida
                  <input name="km_salida" type="number" step="0.01" min="0" />
                </label>
                <label>Observaciones
                  <input name="observaciones_salida" />
                </label>
              </div>
              <label class="check-row salida-omitir-cumplimiento" style="align-items:flex-start;margin:12px 0;max-width:42rem;">
                <input
                  type="checkbox"
                  name="omitir_validacion_cumplimiento"
                  id="salida-omitir-validacion-cumplimiento"
                  style="margin-top:4px;width:auto;flex-shrink:0;"
                  title="Solo uso operativo excepcional: salir sin Carta Porte, RC u otros requisitos del checklist."
                />
                <span>
                  <strong>Omitir validación documental</strong>
                  — Registrar salida aunque el checklist (Carta Porte, mercancía, seguros, etc.) no autorice.
                  Riesgo operativo; use solo en pruebas o si regularizará después.
                </span>
              </label>
              <button type="submit">Guardar salida</button>
            </form>
            <div id="salida-message" class="message"></div>
          </article>

          <article class="card capture-card hidden" data-seguimiento-tab-panel="evento">
            <h3>Agregar evento</h3>
            <div class="hint">Checkpoint o incidencia del viaje.</div>
            <form id="evento-form">
              <div class="three-col">
                <label>Despacho
                  <select id="evento-despacho" name="id_despacho" required></select>
                </label>
                <label>Tipo evento
                  <select name="tipo_evento">
                    <option value="checkpoint">checkpoint</option>
                    <option value="incidencia">incidencia</option>
                    <option value="salida">salida</option>
                    <option value="entrega">entrega</option>
                    <option value="cierre">cierre</option>
                    <option value="cancelacion">cancelacion</option>
                  </select>
                </label>
                <label>Fecha evento
                  <input name="fecha_evento" type="datetime-local" required />
                </label>
              </div>
              <div class="three-col">
                <label>Ubicacion
                  <input name="ubicacion" />
                </label>
                <label>Latitud
                  <input name="latitud" type="number" step="0.0000001" />
                </label>
                <label>Longitud
                  <input name="longitud" type="number" step="0.0000001" />
                </label>
              </div>
              <label>Descripcion
                <textarea name="descripcion" required></textarea>
              </label>
              <button type="submit">Guardar evento</button>
            </form>
            <div id="evento-message" class="message"></div>
          </article>

          <article class="card capture-card hidden" data-seguimiento-tab-panel="entrega">
            <h3>Registrar entrega</h3>
            <div class="hint">Guarda la evidencia y quien recibio.</div>
            <form id="entrega-form">
              <div class="two-col">
                <label>Despacho
                  <select id="entrega-despacho" name="id_despacho" required></select>
                </label>
                <label>Fecha entrega
                  <input name="fecha_entrega" type="datetime-local" required />
                </label>
              </div>
              <div class="two-col">
                <label>Evidencia URL
                  <input name="evidencia_entrega" />
                </label>
                <label>Firma recibe
                  <input name="firma_recibe" />
                </label>
              </div>
              <label>Observaciones entrega
                <textarea name="observaciones_entrega"></textarea>
              </label>
              <button type="submit">Guardar entrega</button>
            </form>
            <div id="entrega-message" class="message"></div>
          </article>

          <article class="card capture-card hidden" data-seguimiento-tab-panel="cierre">
            <h3>Cerrar despacho</h3>
            <div class="hint">Termina la operacion cuando ya regreso o concluyo formalmente.</div>
            <form id="cierre-form">
              <div class="three-col">
                <label>Despacho
                  <select id="cierre-despacho" name="id_despacho" required></select>
                </label>
                <label>Llegada real
                  <input name="llegada_real" type="datetime-local" required />
                </label>
                <label>Km llegada
                  <input name="km_llegada" type="number" step="0.01" min="0" />
                </label>
              </div>
              <label>Observaciones cierre
                <textarea name="observaciones_cierre"></textarea>
              </label>
              <button type="submit">Cerrar despacho</button>
            </form>
            <div id="cierre-message" class="message"></div>
          </article>

          <article class="card capture-card hidden" data-seguimiento-tab-panel="cancelacion">
            <h3>Cancelar despacho</h3>
            <div class="hint">Usalo solo cuando la operacion ya no va a continuar.</div>
            <form id="cancelacion-form">
              <div class="two-col">
                <label>Despacho
                  <select id="cancelacion-despacho" name="id_despacho" required></select>
                </label>
                <label>Motivo cancelacion
                  <input name="motivo_cancelacion" required minlength="3" />
                </label>
              </div>
              <button type="submit">Cancelar despacho</button>
            </form>
            <div id="cancelacion-message" class="message"></div>
          </article>
          <article class="card hidden manual-doc manual-interface" data-seguimiento-tab-panel="manual">
            <div class="manual-interface-head">
              <h3>Manual del módulo Seguimiento</h3>
              <span class="manual-badge">Documentación en pantalla</span>
            </div>
            <div class="hint">Registro de salida, eventos en ruta, entrega, cierre y cancelación de despachos.</div>
            <div class="manual-interface-body">
              <nav class="manual-toc" id="manual-seguimiento-toc" aria-label="Índice del manual de seguimiento">
                <div class="manual-toc-title">Contenido</div>
                <a href="#manual-seguimiento-1">1. Objetivo</a>
                <a href="#manual-seguimiento-2">2. Subopciones</a>
                <a href="#manual-seguimiento-3">3. Registrar salida</a>
                <a href="#manual-seguimiento-4">4. Evento en ruta</a>
                <a href="#manual-seguimiento-5">5. Entrega y cierre</a>
                <a href="#manual-seguimiento-6">6. Cancelación</a>
                <a href="#manual-seguimiento-7">7. Preguntas frecuentes</a>
                <a href="#manual-seguimiento-8">8. Referencia técnica</a>
              </nav>
              <div class="manual-scroll" data-manual-scroll="seguimiento" tabindex="0" role="region" aria-label="Texto del manual de seguimiento">
            <div class="manual-note"><strong>Consulta de historial:</strong> este módulo no incluye tabla de eventos con editar o eliminar. Para ver y editar el <strong>despacho</strong> como registro use <strong>Despachos → Consultar y editar</strong>. Los eventos quedan asociados al despacho en el servidor; correcciones puntuales de eventos pueden requerir API o proceso de sistemas.</div>
            <h4 id="manual-seguimiento-1">1. Objetivo del módulo</h4>
            <p class="manual-p">Documentar la ejecución del despacho: hora real de salida, eventos intermedios, entrega, cierre operativo o cancelación con motivo. Flujo de <strong>altas sucesivas</strong> (una acción por pestaña).</p>
            <h4 id="manual-seguimiento-2">2. Subopciones</h4>
            <ul class="summary-list">
              <li><strong>Registrar salida:</strong> confirma salida a ruta, km y observaciones; puede aplicar <strong>validacion documental</strong> (Carta Porte, mercancia, seguros, expediente operador). Si el checklist bloquea la salida y su proceso lo permite, use la opcion de <strong>omitir validacion documental</strong> (riesgo operativo; solo excepciones autorizadas).</li>
              <li><strong>Evento en ruta:</strong> checkpoints o incidencias con ubicación opcional y coordenadas.</li>
              <li><strong>Registrar entrega:</strong> fecha, evidencia URL y firma de quien recibe.</li>
              <li><strong>Cerrar despacho:</strong> llegada real y km finales.</li>
              <li><strong>Cancelar despacho:</strong> motivo obligatorio.</li>
              <li><strong>Manual:</strong> esta guía.</li>
            </ul>
            <h4 id="manual-seguimiento-3">3. Registrar salida</h4>
            <p class="manual-p">Seleccione el <strong>Despacho</strong> en la lista (debe existir en módulo Despachos). Capture fecha/hora real, km de salida y observaciones. Si aparece error de cumplimiento documental, complete datos en flete/transportista/operador por API o use omitir validación según política.</p>
            <h4 id="manual-seguimiento-4">4. Evento en ruta</h4>
            <p class="manual-p">Indique tipo de evento, fecha y descripción; ubicación y coordenadas opcionales.</p>
            <h4 id="manual-seguimiento-5">5. Entrega y cierre</h4>
            <p class="manual-p">En <strong>Entrega</strong> registre evidencia y receptor; en <strong>Cierre</strong> la llegada real y kilometraje final.</p>
            <h4 id="manual-seguimiento-6">6. Cancelación</h4>
            <p class="manual-p">Use solo si la operación no continuará; el motivo debe ser explícito.</p>
            <h4 id="manual-seguimiento-7">7. Preguntas frecuentes</h4>
            <p class="manual-p"><strong>¿No aparece el despacho?</strong> Créelo antes en <strong>Despachos → Nuevo despacho</strong> y verifique catálogos cargados (F5). <strong>¿Me equivoqué en un evento?</strong> En panel no hay edición de eventos; escale a sistemas o registre acuerdo interno. <strong>¿Dónde veo el listado de despachos?</strong> Módulo <strong>Despachos</strong>, no Seguimiento.</p>
            <h4 id="manual-seguimiento-8">8. Referencia técnica</h4>
            <p class="manual-p">Endpoints bajo <code>/despachos/…</code> (salida, eventos, entrega, cerrar, cancelar) y <code>/cumplimiento/…</code> en <a href="/docs">/docs</a>.</p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section class="page" id="page-usuarios-admin">
        <div class="grid">
          <article class="card" id="usuarios-self-pass-card">
            <h3>Cambiar mi contraseña</h3>
            <p class="hint">Solo con sesión JWT. Debe conocer su contraseña actual.</p>
            <form id="usuarios-self-pass-form">
              <label>Contraseña actual
                <input name="current" type="password" required autocomplete="current-password" />
              </label>
              <label>Nueva contraseña
                <input name="new1" type="password" required autocomplete="new-password" />
              </label>
              <label>Confirmar nueva
                <input name="new2" type="password" required autocomplete="new-password" />
              </label>
              <button type="submit">Actualizar mi clave</button>
            </form>
            <div id="usuarios-self-pass-msg" class="message" role="status"></div>
          </article>
          <article class="card" id="usuarios-admin-card">
            <h3>Usuarios del sistema</h3>
            <p class="hint">
              Roles <strong>admin</strong> y <strong>direccion</strong>. Dirección no puede crear ni editar cuentas con rol
              <strong>admin</strong> (jerarquía). Con solo API key en el panel también puede operar vía API.
            </p>
            <form id="usuarios-create-form">
              <h4>Nuevo usuario</h4>
              <div class="two-col">
                <label>Usuario
                  <input name="username" required autocomplete="off" />
                </label>
                <label>Contraseña inicial
                  <input name="password" type="password" required autocomplete="new-password" />
                </label>
                <label>Rol
                  <select name="role_name" id="usuarios-create-role" required></select>
                </label>
                <label>Email (opcional)
                  <input name="email" type="email" />
                </label>
              </div>
              <label>Nombre completo (opcional)
                <input name="full_name" />
              </label>
              <button type="submit">Crear usuario</button>
            </form>
            <div id="usuarios-admin-msg" class="message" role="status"></div>
            <div style="overflow: auto; margin-top: 14px">
              <table style="width: 100%; border-collapse: collapse; font-size: 14px">
                <thead>
                  <tr style="text-align: left; border-bottom: 1px solid #334155">
                    <th style="padding: 6px">Id</th>
                    <th style="padding: 6px">Usuario</th>
                    <th style="padding: 6px">Rol</th>
                    <th style="padding: 6px">Activo</th>
                    <th style="padding: 6px">Acciones</th>
                  </tr>
                </thead>
                <tbody id="usuarios-admin-tbody"></tbody>
              </table>
            </div>
          </article>
        </div>
      </section>

      <section class="page" id="page-audit-logs">
        <div class="grid">
          <article class="card">
            <h3>Pista de auditoría</h3>
            <p class="hint">Consulta de cambios críticos (solo JWT admin/dirección).</p>
            <form id="audit-logs-form" class="two-col">
              <label>Entidad
                <input id="audit-entity" name="entity" placeholder="flete, usuario, despacho..." />
              </label>
              <label>Entidad ID
                <input id="audit-entity-id" name="entity_id" placeholder="123" />
              </label>
              <label>Acción
                <input id="audit-action" name="action" placeholder="create, update, delete..." />
              </label>
              <label>Actor (usuario)
                <input id="audit-actor" name="actor_username" placeholder="usuario_jwt" />
              </label>
              <label>Skip
                <input id="audit-skip" name="skip" type="number" min="0" value="0" />
              </label>
              <label>Limit
                <input id="audit-limit" name="limit" type="number" min="1" max="200" value="50" />
              </label>
              <div class="span-2 toolbar-actions">
                <button type="submit">Consultar auditoría</button>
                <button type="button" class="secondary-button" id="audit-clear-btn">Limpiar filtros</button>
              </div>
            </form>
            <div id="audit-message" class="message"></div>
          </article>
        </div>
        <div class="grid" style="margin-top: 16px;">
          <article class="card">
            <h3>Resultados</h3>
            <div class="hint" id="audit-summary">Sin consulta.</div>
            <div id="audit-logs-list" style="overflow:auto; margin-top:12px;"></div>
          </article>
        </div>
      </section>

      <section class="page" id="page-direccion">
        <div class="grid">
          <article class="card">
            <h3>Tablero ejecutivo</h3>
            <p class="hint">Indicadores diarios/semanales para dirección. Disponible para roles admin y direccion.</p>
            <form id="direccion-filtros-form" class="two-col">
              <label>Desde
                <input id="direccion-desde" name="desde" type="date" required />
              </label>
              <label>Hasta
                <input id="direccion-hasta" name="hasta" type="date" required />
              </label>
              <div class="span-2 toolbar-actions">
                <button type="submit">Actualizar tablero</button>
                <button type="button" class="secondary-button" id="direccion-export-dashboard-btn">Exportar CSV dashboard</button>
                <button type="button" class="secondary-button" id="direccion-export-completo-btn">Exportar CSV reporte integral</button>
                <button type="button" class="secondary-button" id="direccion-export-incidencias-btn">Exportar CSV incidencias</button>
                <button type="button" class="secondary-button" id="direccion-export-acciones-btn">Exportar CSV acciones</button>
              </div>
            </form>
            <div id="direccion-message" class="message"></div>
          </article>
        </div>

        <div class="status-grid" style="margin-top: 16px;">
          <div class="stat"><strong id="dir-kpi-fletes">0</strong><div>Fletes</div></div>
          <div class="stat"><strong id="dir-kpi-os">0</strong><div>Órdenes de servicio</div></div>
          <div class="stat"><strong id="dir-kpi-asignaciones">0</strong><div>Asignaciones</div></div>
          <div class="stat"><strong id="dir-kpi-despachos">0</strong><div>Despachos</div></div>
          <div class="stat"><strong id="dir-kpi-cerrados">0</strong><div>Despachos cerrados</div></div>
          <div class="stat"><strong id="dir-kpi-facturas">0</strong><div>Facturas</div></div>
          <div class="stat"><strong id="dir-kpi-facturas-emitidas">0</strong><div>Facturas emitidas+</div></div>
          <div class="stat"><strong id="dir-kpi-incidencias">0</strong><div>Incidencias despacho</div></div>
        </div>

        <div class="grid" style="margin-top: 16px;">
          <article class="card">
            <h3>Embudo operativo</h3>
            <table>
              <thead>
                <tr><th>Conversión</th><th>Valor</th></tr>
              </thead>
              <tbody id="direccion-embudo-body">
                <tr><td>Fletes -> OS</td><td>0%</td></tr>
                <tr><td>OS -> Asignación</td><td>0%</td></tr>
                <tr><td>Asignación -> Despacho</td><td>0%</td></tr>
                <tr><td>Despacho -> Factura</td><td>0%</td></tr>
              </tbody>
            </table>
          </article>

          <article class="card">
            <h3>Tiempos de ciclo (horas)</h3>
            <table>
              <thead>
                <tr><th>Tramo</th><th>Promedio</th></tr>
              </thead>
              <tbody id="direccion-tiempos-body">
                <tr><td>Flete -> Factura</td><td>—</td></tr>
                <tr><td>Orden -> Despacho</td><td>—</td></tr>
                <tr><td>Despacho -> Factura</td><td>—</td></tr>
              </tbody>
            </table>
          </article>

          <article class="card">
            <h3>Semáforo ejecutivo</h3>
            <table>
              <thead>
                <tr><th>Dimensión</th><th>Estado</th></tr>
              </thead>
              <tbody id="direccion-semaforo-body">
                <tr><td>Operación</td><td>—</td></tr>
                <tr><td>Sistema</td><td>—</td></tr>
                <tr><td>Dato</td><td>—</td></tr>
                <tr><td>Cobranza</td><td>—</td></tr>
              </tbody>
            </table>
          </article>
        </div>

        <div class="grid" style="margin-top: 16px;">
          <article class="card">
            <h3>Resumen semanal automático</h3>
            <p id="direccion-resumen-texto" class="hint">Sin datos aún.</p>
            <div id="direccion-riesgos-texto" class="hint"></div>
          </article>
          <article class="card">
            <h3>Tendencia semanal</h3>
            <div class="hint">Últimas semanas: despachos cerrados, facturas emitidas y semáforo operativo.</div>
            <svg id="direccion-historico-chart" viewBox="0 0 720 220" width="100%" height="220" role="img" aria-label="Tendencia semanal"></svg>
            <div id="direccion-historico-tabla" style="overflow:auto; margin-top:10px;"></div>
          </article>
        </div>

        <div class="grid" style="margin-top: 16px;">
          <article class="card">
            <h3>Reporte integral CEO</h3>
            <div class="hint">Rentabilidad, conversión, cartera, productividad y sostenibilidad en una sola vista.</div>
            <p id="direccion-threshold-edit-window-msg" class="hint" style="display:none; margin-top:8px;"></p>
            <form id="direccion-umbrales-form" class="two-col" style="margin-top:10px;">
              <label>Margen verde >=
                <input name="margen_verde_min" type="number" step="0.1" value="15" />
              </label>
              <label>Margen amarillo >=
                <input name="margen_amarillo_min" type="number" step="0.1" value="8" />
              </label>
              <label>Utilidad/km verde >=
                <input name="utilidad_km_verde_min" type="number" step="0.1" value="5" />
              </label>
              <label>Utilidad/km amarillo >=
                <input name="utilidad_km_amarillo_min" type="number" step="0.1" value="2" />
              </label>
              <label>Conversión verde >=
                <input name="conversion_verde_min" type="number" step="0.1" value="30" />
              </label>
              <label>Conversión amarillo >=
                <input name="conversion_amarillo_min" type="number" step="0.1" value="20" />
              </label>
              <label>Cartera vencida verde <=
                <input name="vencida_verde_max" type="number" step="0.1" value="20" />
              </label>
              <label>Cartera vencida amarillo <=
                <input name="vencida_amarillo_max" type="number" step="0.1" value="35" />
              </label>
              <label>Viajes con carga verde >=
                <input name="carga_verde_min" type="number" step="0.1" value="80" />
              </label>
              <label>Viajes con carga amarillo >=
                <input name="carga_amarillo_min" type="number" step="0.1" value="65" />
              </label>
              <div class="span-2 toolbar-actions">
                <button type="submit" class="secondary-button">Guardar umbrales</button>
                <button type="button" class="secondary-button" id="direccion-threshold-preset-ceo-btn">Preset CEO</button>
                <button type="button" class="secondary-button" id="direccion-threshold-preset-operacion-btn">Preset Operación</button>
                <button type="button" class="secondary-button" id="direccion-threshold-preset-cobranza-btn">Preset Cobranza</button>
                <button type="button" class="secondary-button" id="direccion-threshold-reset-btn">Restaurar base</button>
                <button type="button" class="secondary-button" id="direccion-export-resumen-btn">Exportar resumen comité</button>
                <button type="button" class="secondary-button" id="direccion-export-estado-guerra-btn">Exportar estado de guerra</button>
              </div>
            </form>
            <div class="status-grid" style="margin-top:10px;">
              <div class="stat" id="dir-ri-card-ingresos"><strong id="dir-ri-ingresos">0</strong><div>Ingresos facturados</div></div>
              <div class="stat" id="dir-ri-card-utilidad"><strong id="dir-ri-utilidad">0</strong><div>Utilidad real</div></div>
              <div class="stat" id="dir-ri-card-margen"><strong id="dir-ri-margen">0%</strong><div>Margen</div></div>
              <div class="stat" id="dir-ri-card-utilidad-km"><strong id="dir-ri-utilidad-km">0</strong><div>Utilidad por km</div></div>
              <div class="stat" id="dir-ri-card-conv"><strong id="dir-ri-conv">0%</strong><div>Conversión cotizaciones</div></div>
              <div class="stat" id="dir-ri-card-vencida"><strong id="dir-ri-vencida">0%</strong><div>Cartera vencida</div></div>
              <div class="stat" id="dir-ri-card-carga"><strong id="dir-ri-carga">0%</strong><div>Viajes con carga</div></div>
              <div class="stat" id="dir-ri-card-sostenibilidad"><strong id="dir-ri-sostenibilidad">—</strong><div>Estado sostenibilidad</div></div>
            </div>
            <div id="direccion-reporte-alertas" class="hint" style="margin-top:10px;">Sin alertas.</div>
            <div id="direccion-reporte-priorizadas" style="overflow:auto; margin-top:10px;"></div>
            <div id="direccion-reporte-resumen-ejecutivo" class="hint" style="margin-top:10px;">Sin resumen ejecutivo.</div>
            <div id="direccion-reporte-estado-guerra" style="overflow:auto; margin-top:10px;"></div>
            <div id="direccion-reporte-guardrails" style="overflow:auto; margin-top:10px;"></div>
            <div id="direccion-reporte-seguimiento" style="overflow:auto; margin-top:10px;"></div>
            <div id="direccion-threshold-history" style="overflow:auto; margin-top:10px;"></div>
            <div id="direccion-committee-snapshots" style="margin-top:12px;">
              <h4>Snapshots semanales (comité)</h4>
              <p class="hint">Congela el reporte integral de la semana ISO (lun–dom) en base de datos. Idempotente por semana. Tareas programadas: POST <code>/api/v1/internal/direccion/committee-snapshot</code> con cabecera <code>X-SIFE-Direccion-Cron-Secret</code> (variables <code>DIRECCION_COMMITTEE_SNAPSHOT_CRON_SECRET</code> y opcional <code>DIRECCION_COMMITTEE_SNAPSHOT_CRON_ACTOR_USERNAME</code> en <code>.env</code>).</p>
              <div class="toolbar-actions">
                <button type="button" class="secondary-button" id="direccion-snapshot-create-btn">Congelar semana ISO actual</button>
                <button type="button" class="secondary-button" id="direccion-snapshot-refresh-btn">Actualizar lista</button>
              </div>
              <div id="direccion-snapshot-list" style="overflow:auto; margin-top:10px;"></div>
            </div>
            <div id="direccion-role-threshold-admin" style="margin-top:10px; display:none;">
              <h4>Gobierno de umbrales por rol (admin)</h4>
              <div class="two-col">
                <label>Rol objetivo
                  <select id="direccion-threshold-role-select"></select>
                </label>
                <label style="display:flex; align-items:center; gap:8px; margin-top:24px;">
                  <input type="checkbox" id="direccion-threshold-role-override-toggle" checked />
                  Permitir override por usuario para este rol
                </label>
                <div class="toolbar-actions" style="align-self:end;">
                  <button type="button" class="secondary-button" id="direccion-threshold-role-load-btn">Cargar rol</button>
                  <button type="button" class="secondary-button" id="direccion-threshold-role-apply-btn">Aplicar umbrales actuales al rol</button>
                  <button type="button" class="secondary-button" id="direccion-threshold-role-policy-save-btn">Guardar política</button>
                  <button type="button" class="secondary-button" id="direccion-threshold-role-clear-overrides-btn">Limpiar overrides usuarios del rol</button>
                </div>
              </div>
              <div id="direccion-role-threshold-message" class="hint"></div>
              <div id="direccion-role-threshold-governance" style="overflow:auto; margin-top:10px;"></div>
              <div id="direccion-role-threshold-users" style="overflow:auto; margin-top:10px;"></div>
            </div>
          </article>
        </div>

        <div class="grid" style="margin-top: 16px;">
          <article class="card">
            <h3>Finanzas y conversión</h3>
            <div id="direccion-reporte-finanzas" style="overflow:auto;"></div>
            <div id="direccion-reporte-conversion" style="overflow:auto; margin-top:10px;"></div>
          </article>
          <article class="card">
            <h3>Cartera y productividad</h3>
            <div id="direccion-reporte-cartera" style="overflow:auto;"></div>
            <div id="direccion-reporte-productividad" style="overflow:auto; margin-top:10px;"></div>
          </article>
        </div>

        <div class="grid" style="margin-top: 16px;">
          <article class="card">
            <h3>Top clientes por rentabilidad</h3>
            <div id="direccion-reporte-clientes" style="overflow:auto;"></div>
            <div id="direccion-reporte-destruye-margen" style="overflow:auto; margin-top:10px;"></div>
          </article>
        </div>

        <div class="grid" style="margin-top: 16px;">
          <article class="card">
            <h3>Incidencias operativas</h3>
            <form id="direccion-incidencia-form" class="grid">
              <div class="two-col">
                <label>Título
                  <input name="titulo" required maxlength="160" />
                </label>
                <label>Módulo
                  <input name="modulo" value="general" required maxlength="64" />
                </label>
                <label>Severidad
                  <select name="severidad">
                    <option value="baja">baja</option>
                    <option value="media" selected>media</option>
                    <option value="alta">alta</option>
                    <option value="critica">critica</option>
                  </select>
                </label>
                <label>Fecha detectada
                  <input name="fecha_detectada" type="date" required />
                </label>
                <label>Responsable
                  <input name="responsable" maxlength="120" />
                </label>
                <label>Estatus
                  <select name="estatus">
                    <option value="abierta" selected>abierta</option>
                    <option value="en_progreso">en_progreso</option>
                    <option value="resuelta">resuelta</option>
                  </select>
                </label>
              </div>
              <label>Detalle
                <textarea name="detalle"></textarea>
              </label>
              <div class="toolbar-actions">
                <button type="submit">Registrar incidencia</button>
              </div>
            </form>
            <div id="direccion-incidencia-message" class="message"></div>
            <div id="direccion-incidencias-lista" style="overflow:auto; margin-top:12px;"></div>
          </article>

          <article class="card">
            <h3>Plan de acción semanal</h3>
            <form id="direccion-accion-form" class="grid">
              <div class="two-col">
                <label>Semana inicio
                  <input name="week_start" type="date" required />
                </label>
                <label>Semana fin
                  <input name="week_end" type="date" required />
                </label>
                <label>Título
                  <input name="titulo" required maxlength="180" />
                </label>
                <label>Responsable
                  <input name="owner" required maxlength="120" />
                </label>
                <label>Fecha compromiso
                  <input name="due_date" type="date" />
                </label>
                <label>Estatus
                  <select name="estatus">
                    <option value="pendiente" selected>pendiente</option>
                    <option value="en_curso">en_curso</option>
                    <option value="completada">completada</option>
                    <option value="cancelada">cancelada</option>
                  </select>
                </label>
              </div>
              <label>Impacto esperado
                <input name="impacto" maxlength="255" />
              </label>
              <label>Descripción
                <textarea name="descripcion"></textarea>
              </label>
              <div class="toolbar-actions">
                <button type="submit">Guardar acción</button>
              </div>
            </form>
            <div id="direccion-accion-message" class="message"></div>
            <div id="direccion-acciones-lista" style="overflow:auto; margin-top:12px;"></div>
          </article>
        </div>
      </section>

      <section class="page" id="page-bajas-danos">
        <div class="grid">
          <article class="card">
            <h3>Alta rápida</h3>
            <p class="hint">Registre bajas (operador/unidad) o daños a activo/carga, con vínculo opcional a flete.</p>
            <form id="bajas-danos-form">
              <div class="field-row">
                <label>Tipo
                  <select name="tipo" required>
                    <option value="baja">Baja</option>
                    <option value="dano">Daño</option>
                  </select>
                </label>
                <label>Fecha del evento
                  <input type="date" name="fecha_evento" required />
                </label>
              </div>
              <label>Título
                <input type="text" name="titulo" maxlength="255" required placeholder="Resumen breve" />
              </label>
              <label>Detalle
                <textarea name="detalle" rows="3" placeholder="Descripción (opcional)"></textarea>
              </label>
              <div class="field-row">
                <label>ID flete (opcional)
                  <input type="number" name="flete_id" min="1" step="1" placeholder="—" />
                </label>
                <label>ID unidad (opcional)
                  <input type="number" name="id_unidad" min="1" step="1" placeholder="—" />
                </label>
                <label>ID operador (opcional)
                  <input type="number" name="id_operador" min="1" step="1" placeholder="—" />
                </label>
              </div>
              <div class="field-row">
                <label>Estatus
                  <select name="estatus">
                    <option value="abierta">Abierta</option>
                    <option value="en_seguimiento">En seguimiento</option>
                    <option value="cerrada">Cerrada</option>
                  </select>
                </label>
                <label>Costo estimado (opcional)
                  <input type="text" name="costo_estimado" inputmode="decimal" placeholder="0.00" />
                </label>
              </div>
              <button type="submit">Guardar</button>
            </form>
            <div id="bajas-danos-form-message" class="message"></div>
          </article>
          <article class="card">
            <h3>Listado</h3>
            <form id="bajas-danos-filtros" class="field-row" style="align-items:flex-end; flex-wrap:wrap; gap:10px;">
              <label>Tipo
                <select id="bajas-danos-filtro-tipo">
                  <option value="">Todos</option>
                  <option value="baja">Baja</option>
                  <option value="dano">Daño</option>
                </select>
              </label>
              <label>ID flete
                <input type="number" id="bajas-danos-filtro-flete" min="1" step="1" placeholder="Opcional" />
              </label>
              <button type="submit" class="secondary-button">Aplicar filtros</button>
              <button type="button" id="bajas-danos-refresh-btn" class="secondary-button">Recargar</button>
            </form>
            <div id="bajas-danos-list-message" class="message"></div>
            <div id="bajas-danos-tabla" style="overflow:auto; margin-top:12px;"></div>
          </article>
        </div>
      </section>
    </main>
  </div>

  
  <script>
    window.__SIFE_PANEL_BOOT__ = { apiBase: "/api/v1", apiKey: __API_KEY__ };
  </script>
  <script src="/static/panel/panel.js" defer></script>
  <script src="/static/panel/panel-direccion.js" defer></script>
</body>
</html>
"""


def _render_ui() -> str:
    html = _UI_TEMPLATE.replace("__PROJECT_NAME__", escape(settings.PROJECT_NAME))
    return html.replace("__API_KEY__", json.dumps(settings.API_KEY))


@router.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/ui", status_code=307)


@router.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    return Response(status_code=204)


@router.get("/manual/cumplimiento", include_in_schema=False)
def manual_cumplimiento() -> HTMLResponse:
    path = Path(__file__).resolve().parent / "static" / "cumplimiento_manual.html"
    if not path.is_file():
        return HTMLResponse("<p>Manual no encontrado.</p>", status_code=404)
    return HTMLResponse(path.read_text(encoding="utf-8"))


@router.get("/login", include_in_schema=False)
def login_page() -> HTMLResponse:
    path = Path(__file__).resolve().parent / "static" / "login.html"
    if not path.is_file():
        return HTMLResponse("<p>Login no encontrado.</p>", status_code=404)
    html = path.read_text(encoding="utf-8")
    html = html.replace("__API_V1_PREFIX__", json.dumps(settings.API_V1_PREFIX))
    return HTMLResponse(
        html,
        headers={"Cache-Control": "no-store, no-cache, max-age=0, must-revalidate"},
    )


@router.get("/ui", include_in_schema=False)
def ui_dashboard() -> HTMLResponse:
    return HTMLResponse(
        _render_ui(),
        headers={"Cache-Control": "no-store, no-cache, max-age=0, must-revalidate"},
    )
