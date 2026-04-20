from __future__ import annotations

from pydantic import BaseModel, Field


class RolePublic(BaseModel):
    name: str
    description: str | None = None


class UsuarioListaItem(BaseModel):
    id: int
    username: str
    role_name: str
    is_active: bool
    email: str | None = None
    full_name: str | None = None

    model_config = {"from_attributes": False}


class UsuarioCrear(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=128)
    role_name: str = Field(min_length=1, max_length=64)
    email: str | None = Field(default=None, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)


class UsuarioActualizar(BaseModel):
    role_name: str | None = Field(default=None, max_length=64)
    email: str | None = Field(default=None, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None


class UsuarioPasswordAdmin(BaseModel):
    new_password: str = Field(min_length=1, max_length=128)
