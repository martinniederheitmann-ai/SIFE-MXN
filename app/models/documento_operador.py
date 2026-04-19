from __future__ import annotations

import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class TipoDocumentoOperador(str, enum.Enum):
    LICENCIA_FEDERAL_B = "licencia_federal_tipo_b"
    LICENCIA_FEDERAL_E = "licencia_federal_tipo_e"
    INE = "ine"
    COMPROBANTE_DOMICILIO = "comprobante_domicilio"
    ANTECEDENTES_NO_PENALES = "carta_antecedentes_no_penales"
    APTO_MEDICO_SCT = "apto_medico_sct"
    OTRO = "otro"


class EstatusDocumentoOperador(str, enum.Enum):
    VIGENTE = "vigente"
    VENCIDO = "vencido"


def _doc_enum(cls: type[enum.Enum], length: int) -> Enum:
    return Enum(
        cls,
        values_callable=lambda x: [e.value for e in x],
        native_enum=False,
        length=length,
    )


class DocumentoOperador(Base):
    __tablename__ = "documentos_operador"

    id_documento: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_operador: Mapped[int] = mapped_column(
        ForeignKey("operadores.id_operador", ondelete="CASCADE"), nullable=False, index=True
    )
    tipo_documento: Mapped[TipoDocumentoOperador] = mapped_column(
        _doc_enum(TipoDocumentoOperador, 48), nullable=False
    )
    numero_documento: Mapped[str | None] = mapped_column(String(120), nullable=True)
    fecha_expedicion: Mapped[date | None] = mapped_column(Date, nullable=True)
    fecha_vencimiento: Mapped[date | None] = mapped_column(Date, nullable=True)
    archivo: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    estatus: Mapped[EstatusDocumentoOperador] = mapped_column(
        _doc_enum(EstatusDocumentoOperador, 16),
        default=EstatusDocumentoOperador.VIGENTE,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    operador: Mapped["Operador"] = relationship("Operador", lazy="select")
