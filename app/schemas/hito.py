import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class HitoPredialCreate(BaseModel):
    indice_vertice: int = Field(..., ge=0)
    descripcion: Optional[str] = None
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    foto_url: Optional[str] = None


class HitoPredialOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    inmueble_id: uuid.UUID
    indice_vertice: int
    descripcion: Optional[str] = None
    lat: float
    lon: float
    utm_norte: Optional[float] = None
    utm_este: Optional[float] = None
    foto_url: Optional[str] = None
    created_at: datetime
