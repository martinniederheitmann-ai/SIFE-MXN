from pathlib import Path
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict

# Raíz del repo (donde está main.py y .env), no el cwd desde el que arranque uvicorn.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_ENV_FILE = _PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "SIFE-MXN"
    API_V1_PREFIX: str = "/api/v1"
    API_KEY: str = "cambia-esta-api-key"
    API_KEY_HEADER: str = "X-API-Key"
    API_KEY_DENY_PREFIXES: str = "usuarios,direccion,audit-logs"
    API_KEY_WRITE_DENY_PREFIXES: str = "usuarios,direccion,audit-logs"

    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_HOST: str = "127.0.0.1"
    MYSQL_PORT: int = 3306
    MYSQL_DB: str = "sife_mxn"

    # JWT (usuarios del panel / integraciones con Bearer). Genera una clave larga y aleatoria en producción.
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 12

    # Dirección: ventana de edición de umbrales KPI (operación cerrada fuera de ventana).
    # Solo aplica a usuarios no-admin que intentan PUT /direccion/reportes/thresholds (override usuario).
    DIRECCION_THRESHOLD_EDIT_WINDOW_ENABLED: bool = False
    DIRECCION_THRESHOLD_EDIT_TIMEZONE: str = "America/Mexico_City"
    DIRECCION_THRESHOLD_EDIT_WEEKDAY_START: int = 0  # 0=lunes … 6=domingo
    DIRECCION_THRESHOLD_EDIT_WEEKDAY_END: int = 4  # inclusive (p.ej. 4=viernes)
    DIRECCION_THRESHOLD_EDIT_HOUR_START: int = 9  # inclusive
    DIRECCION_THRESHOLD_EDIT_HOUR_END: int = 18  # exclusive (hasta 17:59)

    # Snapshot comité: POST sin JWT bajo /api/v1/internal/... con cabecera X-SIFE-Direccion-Cron-Secret.
    DIRECCION_COMMITTEE_SNAPSHOT_CRON_SECRET: str = ""
    DIRECCION_COMMITTEE_SNAPSHOT_CRON_ACTOR_USERNAME: str = ""

    @property
    def database_url(self) -> str:
        user = quote_plus(self.MYSQL_USER)
        password = quote_plus(self.MYSQL_PASSWORD)
        return (
            f"mysql+pymysql://{user}:{password}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
        )


settings = Settings()
