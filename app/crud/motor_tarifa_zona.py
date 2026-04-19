from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.motor_tarifa_zona import MotorTarifaZonaPreset


def get_preset(
    db: Session, *, region_key: str, tipo_unidad_norm: str
) -> MotorTarifaZonaPreset | None:
    stmt = (
        select(MotorTarifaZonaPreset)
        .where(
            MotorTarifaZonaPreset.region_key == region_key,
            MotorTarifaZonaPreset.tipo_unidad_norm == tipo_unidad_norm,
            MotorTarifaZonaPreset.activo.is_(True),
        )
        .limit(1)
    )
    return db.execute(stmt).scalar_one_or_none()


def list_presets(db: Session, *, activo: bool | None = True) -> Sequence[MotorTarifaZonaPreset]:
    stmt = select(MotorTarifaZonaPreset).order_by(
        MotorTarifaZonaPreset.region_key.asc(),
        MotorTarifaZonaPreset.tipo_unidad_norm.asc(),
    )
    if activo is not None:
        stmt = stmt.where(MotorTarifaZonaPreset.activo.is_(activo))
    return db.execute(stmt).scalars().all()
