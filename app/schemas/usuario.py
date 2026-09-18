import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    cedula: str
    nombre: str
    apellido: str
    rol: str
    activo: bool
    created_at: datetime
    updated_at: datetime


class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    cedula: Optional[str] = None


class UsuarioRolUpdate(BaseModel):
    """Solo un administrador puede cambiar el rol de otro usuario."""

    rol: str = Field(..., pattern="^(administrador|inspector)$")


class UsuarioActual(BaseModel):
    """Representa al usuario autenticado, derivado del JWT de Supabase."""

    id: uuid.UUID
    email: Optional[str] = None
    rol: str = "inspector"
