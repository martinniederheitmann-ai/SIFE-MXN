from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.operador_laboral import (
    EstatusLaboralOperador,
    PuestoOperador,
    TipoContratoOperador,
    TipoPagoLaboral,
)


class OperadorLaboralBase(BaseModel):
    fecha_ingreso: date
    tipo_contrato: TipoContratoOperador
    puesto: PuestoOperador
    salario_base: Decimal = Field(..., ge=0)
    tipo_pago: TipoPagoLaboral
    estatus: EstatusLaboralOperador = EstatusLaboralOperador.ACTIVO


class OperadorLaboralCreate(OperadorLaboralBase):
    pass


class OperadorLaboralUpdate(BaseModel):
    fecha_ingreso: date | None = None
    tipo_contrato: TipoContratoOperador | None = None
    puesto: PuestoOperador | None = None
    salario_base: Decimal | None = Field(None, ge=0)
    tipo_pago: TipoPagoLaboral | None = None
    estatus: EstatusLaboralOperador | None = None


class OperadorLaboralRead(OperadorLaboralBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    id_operador: int
    created_at: datetime
    updated_at: datetime
