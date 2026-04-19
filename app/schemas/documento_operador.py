from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.documento_operador import EstatusDocumentoOperador, TipoDocumentoOperador


class DocumentoOperadorBase(BaseModel):
    tipo_documento: TipoDocumentoOperador
    numero_documento: str | None = Field(None, max_length=120)
    fecha_expedicion: date | None = None
    fecha_vencimiento: date | None = None
    archivo: str | None = Field(None, max_length=1024)
    estatus: EstatusDocumentoOperador = EstatusDocumentoOperador.VIGENTE


class DocumentoOperadorCreate(DocumentoOperadorBase):
    pass


class DocumentoOperadorUpdate(BaseModel):
    tipo_documento: TipoDocumentoOperador | None = None
    numero_documento: str | None = Field(None, max_length=120)
    fecha_expedicion: date | None = None
    fecha_vencimiento: date | None = None
    archivo: str | None = Field(None, max_length=1024)
    estatus: EstatusDocumentoOperador | None = None


class DocumentoOperadorRead(DocumentoOperadorBase):
    model_config = ConfigDict(from_attributes=True)

    id_documento: int
    id_operador: int
    created_at: datetime
    updated_at: datetime


class DocumentoOperadorListResponse(BaseModel):
    items: list[DocumentoOperadorRead]
    total: int
