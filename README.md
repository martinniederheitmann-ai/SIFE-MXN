# SIFE-MXN

API REST del ERP logístico **SIFE-MXN** (FastAPI, SQLAlchemy 2, MySQL). Incluye **viajes**, **clientes**, **transportistas**, **fletes**, **asignaciones** y **despachos**, con migraciones en **Alembic**.

## Requisitos

- Python 3.11 o superior (recomendado)
- MySQL 8.0 o superior (se usan `DATETIME(6)` y `CURRENT_TIMESTAMP(6)` en la migración inicial)

## Configuración del entorno

1. Clona o copia el proyecto y entra en la carpeta raíz (`SIFE-MXN`).

2. Crea y activa un entorno virtual:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Instala dependencias:

   ```powershell
   pip install -r requirements.txt
   ```

4. Crea el archivo de variables de entorno a partir del ejemplo:

   ```powershell
   copy .env.example .env
   ```

   Edita `.env` y define usuario, contraseña, host, puerto y nombre de la base de datos MySQL. Configura también `API_KEY` para proteger los endpoints versionados.

   Para **usuarios del panel con JWT**, define además `JWT_SECRET_KEY` (cadena larga y aleatoria; no la compartas ni la subas al repositorio). Sin esta clave, el login por usuario/contraseña devolverá error; la API seguirá aceptando solo `X-API-Key` como hasta ahora.

## Autenticación (API key y JWT)

Los endpoints bajo `/api/v1` aceptan **uno** de estos métodos:

- **Header `X-API-Key`**: igual que antes (integraciones y panel si no hay sesión JWT).
- **Header `Authorization: Bearer <token>`**: token obtenido con `POST /api/v1/auth/login` (formulario OAuth2: `username`, `password`).

Rutas útiles:

- `POST /api/v1/auth/login` — obtiene el JWT (Swagger: *Authorize* con Bearer tras obtener token).
- `GET /api/v1/auth/me` — perfil del usuario (solo Bearer JWT).

**Panel web:** en [http://127.0.0.1:8000/ui](http://127.0.0.1:8000/ui) puede seguir usándose la API key inyectada desde `.env`, o iniciar sesión en [http://127.0.0.1:8000/login](http://127.0.0.1:8000/login) para guardar el JWT en el navegador.

**Primer usuario administrador** (tras migraciones y con `JWT_SECRET_KEY` en `.env`):

```powershell
python scripts/create_admin_user.py --username admin --password "TuPasswordSeguro"
```

Roles iniciales en base de datos: `admin`, `operaciones`, `contabilidad`, `ventas`, `consulta` (los permisos por pantalla se pueden afinar en versiones siguientes).

## Base de datos MySQL

1. Crea la base de datos (ajusta el nombre si cambiaste `MYSQL_DB`):

   ```sql
   CREATE DATABASE sife_mxn CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. Asegúrate de que el usuario de `.env` tenga permisos sobre esa base.

## Migraciones (Alembic)

Desde la raíz del proyecto, con el virtualenv activado:

```powershell
python -m alembic upgrade head
```

Esto aplica las revisiones hasta `head` (tablas `viajes`, `clientes`, `transportistas`, `fletes`, `operadores`, `unidades`, `asignaciones`, `despachos`, `roles`, `users`, etc.).

Para comprobar el estado:

```powershell
python -m alembic current
```

Para generar nuevas migraciones después de cambiar modelos:

```powershell
python -m alembic revision --autogenerate -m "descripcion_del_cambio"
python -m alembic upgrade head
```

## Ejecutar la API

```powershell
python -m uvicorn main:app --reload
```

- Documentación interactiva: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Salud del servicio: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- API versionada: prefijo `/api/v1` (configurable con `API_V1_PREFIX` en `.env`)
- Los endpoints bajo `/api/v1` requieren el header `X-API-Key` (o el header configurado en `API_KEY_HEADER`).

### Ejercicio de flete (orden sugerido)

1. `POST /api/v1/clientes` — registrar quien contrata o embarca la carga.
2. `POST /api/v1/transportistas` — registrar el transportista.
3. (Opcional) `POST /api/v1/viajes` — si ya tienes un viaje planificado.
4. `POST /api/v1/fletes` — crear el flete con peso, monto estimado, moneda y, si aplica, `viaje_id`. Los listados y el detalle devuelven datos resumidos de cliente, transportista y viaje.

Estados del flete: `cotizado`, `confirmado`, `asignado`, `en_transito`, `entregado`, `cancelado`.

### Tarifas y cotizacion de fletes

SIFE-MXN ya soporta:

- tarifas por ambito: `local`, `estatal`, `federal`
- modalidades: `mixta`, `por_viaje`, `por_km`, `por_tonelada`, `por_hora`, `por_dia`
- factores comerciales: utilidad, riesgo, urgencia, retorno vacio y carga especial

Para cargar tarifas iniciales de ejemplo:

```powershell
python scripts/seed_tarifas_flete.py
```

Para cargar clientes ejemplo y acuerdos especiales:

```powershell
python scripts/seed_clientes_tarifas_especiales.py
```

Para cotizar desde la API:

```http
POST /api/v1/fletes/cotizar
```

Ejemplo de body:

```json
{
  "ambito": "federal",
  "origen": "Veracruz",
  "destino": "Ciudad de Mexico",
  "tipo_unidad": "tractocamion",
  "tipo_carga": "general",
  "distancia_km": 400,
  "peso_kg": 18000,
  "horas_servicio": 0,
  "dias_servicio": 0,
  "urgencia": false,
  "retorno_vacio": true,
  "riesgo_pct_extra": 0.02,
  "recargos": 500
}
```

Flujo comercial sugerido:

1. `POST /api/v1/fletes/cotizaciones` - cotiza y guarda historial.
2. `POST /api/v1/fletes/cotizaciones/{id}/estatus` - enviar, aceptar o rechazar.
3. `POST /api/v1/fletes/cotizaciones/{id}/convertir` - convierte la cotizacion aceptada en un flete real.

Si envias `cliente_id` en la cotizacion, el sistema intentara aplicar una tarifa especial vigente para ese cliente sobre la tarifa base coincidente.

### Ejecucion operativa (despacho)

1. `POST /api/v1/asignaciones` - vincular operador, unidad y viaje.
2. `POST /api/v1/despachos` - programar el despacho para una asignacion y, si aplica, asociarlo a un flete.
3. `POST /api/v1/despachos/{id_despacho}/salida` - registrar salida real.
4. `POST /api/v1/despachos/{id_despacho}/eventos` - registrar checkpoints o incidencias.
5. `POST /api/v1/despachos/{id_despacho}/entrega` y `POST /api/v1/despachos/{id_despacho}/cerrar` - completar la ejecucion.

## Notas

- No subas el archivo `.env` al repositorio; está listado en `.gitignore`.
- La URL de conexión codifica usuario y contraseña para caracteres especiales (`app/core/config.py`).
- Si necesitas crear tablas sin Alembic en un entorno muy temporal, existe `init_db()` en `app/core/database.py`; en condiciones normales usa solo Alembic.
