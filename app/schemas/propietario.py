import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PropietarioBase(BaseModel):
    cedula_rif: str = Field(..., min_length=5, max_length=20)
    nombre: str = Field(..., min_length=1)
    apellido: str = Field(..., min_length=1)
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    direccion: Optional[str] = None


class PropietarioCreate(PropietarioBase):
    pass


class PropietarioUpdate(BaseModel):
    cedula_rif: Optional[str] = None
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    direccion: Optional[str] = None


class PropietarioOut(PropietarioBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime


class PropietarioPaginado(BaseModel):
    """Versión paginada para listados de propietarios."""
    total: int
    pagina: int
    por_pagina: int
    resultados: list[PropietarioOut]
