# Guía de operación diaria (SIFE-MXN)

## 1) Arranque rápido del sistema

```powershell
cd C:\SIFE-MXN
.\venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

URLs:
- Panel: `http://127.0.0.1:8000/ui`
- Login: `http://127.0.0.1:8000/login`
- Swagger: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

## 2) Primeros checks si algo no abre

1. Confirmar que el puerto 8000 no esté ocupado por proceso viejo:
   ```powershell
   netstat -ano -p tcp | findstr :8000
   ```
2. Si hay conflicto, terminar proceso viejo:
   ```powershell
   taskkill /PID <PID> /F
   ```
3. Recargar navegador con cache limpia: `Ctrl + F5`.

## 3) Login JWT para probar permisos por rol

- Entrar a `http://127.0.0.1:8000/login`.
- Si no existe usuario, crear uno:

```powershell
python scripts/create_admin_user.py --username admin --password "TuClaveSegura"
python scripts/create_admin_user.py --username ope1 --password "TuClaveSegura" --role operaciones
```

Nota: para login JWT, definir `JWT_SECRET_KEY` en `.env`.

## 4) Ubicación de Bajas y daños

- En el panel: **Operación -> Bajas y daños**.
- Endpoint API: `GET/POST /api/v1/bajas-danos`.

## 5) Aplicar migraciones cuando haya cambios de DB

```powershell
python -m alembic upgrade head
python -m alembic current
```

## 6) Backup manual de MySQL

```powershell
python scripts/backup_mysql.py
```

Si falla por `mysqldump` no encontrado, pasar ruta explícita:

```powershell
python scripts/backup_mysql.py --mysqldump "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe"
```

## 7) Pruebas rápidas recomendadas

```powershell
python -m pytest tests/ -q
```

