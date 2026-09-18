from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ConfiguracionCatastralBase(BaseModel):
    """Base schema para configuración catastral."""

    codigo_estado: str = Field(..., min_length=2, max_length=2)
    codigo_municipio: str = Field(..., min_length=2, max_length=2)
    codigo_parroquia: str = Field(..., min_length=2, max_length=2)
    nombre_estado: str = Field(..., min_length=1)
    nombre_municipio: str = Field(..., min_length=1)
    nombre_parroquia: str = Field(..., min_length=1)
    ordenanza_referencia: Optional[str] = None
    srid_utm: int = Field(..., gt=0)
    valor_m2_terreno: Decimal = Field(..., gt=0)
    valor_m2_construccion: Decimal = Field(..., gt=0)
    valor_m2_comercio: Decimal = Field(..., gt=0)
    alicuota_impuesto: Decimal = Field(..., ge=0, le=1)
    vigencia_cedula_meses: int = Field(..., gt=0)

    # Campos institucionales para cédula catastral (v2.5)
    rif_alcaldia: str = Field(..., min_length=1)
    direccion_institucional: str = Field(..., min_length=1)
    nombre_maxima_autoridad: str = Field(..., min_length=1)
    cargo_maxima_autoridad: str = Field(..., min_length=1)
    texto_acta_maxima_autoridad: str = Field(..., min_length=1)
    nombre_director_catastro: str = Field(..., min_length=1)
    cargo_director_catastro: str = Field(..., min_length=1)
    texto_resolucion_director: str = Field(..., min_length=1)
    notas_legales: str = Field(..., min_length=1)


class ConfiguracionCatastralUpdate(BaseModel):
    """Schema para actualizar configuración catastral (todos los campos opcionales)."""

    model_config = ConfigDict(extra="ignore")

    codigo_estado: Optional[str] = Field(None, min_length=2, max_length=2)
    codigo_municipio: Optional[str] = Field(None, min_length=2, max_length=2)
    codigo_parroquia: Optional[str] = Field(None, min_length=2, max_length=2)
    nombre_estado: Optional[str] = None
    nombre_municipio: Optional[str] = None
    nombre_parroquia: Optional[str] = None
    ordenanza_referencia: Optional[str] = None
    srid_utm: Optional[int] = Field(None, gt=0)
    valor_m2_terreno: Optional[Decimal] = Field(None, gt=0)
    valor_m2_construccion: Optional[Decimal] = Field(None, gt=0)
    valor_m2_comercio: Optional[Decimal] = Field(None, gt=0)
    alicuota_impuesto: Optional[Decimal] = Field(None, ge=0, le=1)
    vigencia_cedula_meses: Optional[int] = Field(None, gt=0)

    # Campos institucionales
    rif_alcaldia: Optional[str] = None
    direccion_institucional: Optional[str] = None
    nombre_maxima_autoridad: Optional[str] = None
    cargo_maxima_autoridad: Optional[str] = None
    texto_acta_maxima_autoridad: Optional[str] = None
    nombre_director_catastro: Optional[str] = None
    cargo_director_catastro: Optional[str] = None
    texto_resolucion_director: Optional[str] = None
    notas_legales: Optional[str] = None


class ConfiguracionCatastralOut(ConfiguracionCatastralBase):
    """Schema de salida para configuración catastral."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    updated_at: datetime


class ConfiguracionSistemaBase(BaseModel):
    """Base schema para configuración del sistema."""

    estado_codigo: str = Field(..., min_length=2, max_length=2)
    municipio_codigo: str = Field(..., min_length=2, max_length=2)
    parroquia_codigo: str = Field(..., min_length=2, max_length=2)
    nombre_municipio: str = Field(..., min_length=1)


class ConfiguracionSistemaUpdate(BaseModel):
    """Schema para actualizar configuración del sistema (todos los campos opcionales)."""

    model_config = ConfigDict(extra="ignore")

    estado_codigo: Optional[str] = Field(None, min_length=2, max_length=2)
    municipio_codigo: Optional[str] = Field(None, min_length=2, max_length=2)
    parroquia_codigo: Optional[str] = Field(None, min_length=2, max_length=2)
    nombre_municipio: Optional[str] = None


class ConfiguracionSistemaOut(ConfiguracionSistemaBase):
    """Schema de salida para configuración del sistema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
