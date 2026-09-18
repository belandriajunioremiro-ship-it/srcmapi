import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class FotoInmuebleCreate(BaseModel):
    url: str
    descripcion: Optional[str] = None


class FotoInmuebleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    inmueble_id: uuid.UUID
    url: str
    descripcion: Optional[str] = None
    created_at: datetime
