import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.geojson import GeoJSONPolygon
from app.schemas.propietario import PropietarioOut


class InmuebleBase(BaseModel):
    # --- Bloques del código catastral (el código completo lo calcula la BD) ---
    sector: str = Field(..., min_length=2, max_length=2)
    manzana: str = Field(..., min_length=3, max_length=3)
    parcela: str = Field(..., min_length=3, max_length=3)
    subparcela: str = Field(default="000", min_length=3, max_length=3)
    nivel: str = Field(default="000", min_length=3, max_length=3)
    unidad: str = Field(default="000", min_length=3, max_length=3)

    propietario_id: Optional[uuid.UUID] = None
    direccion: str = Field(..., min_length=1)

    documento_tipo: Optional[str] = None
    documento_numero: Optional[str] = None
    documento_tomo: Optional[str] = None
    documento_folio: Optional[str] = None
    documento_protocolo: Optional[str] = None
    documento_fecha: Optional[date] = None

    tenencia: str = Field(default="propio")
    contrato_arrendamiento_num: Optional[str] = None
    contrato_arrendamiento_fecha: Optional[date] = None

    lindero_norte_doc: Optional[str] = None
    lindero_norte_mts: Optional[float] = None
    lindero_sur_doc: Optional[str] = None
    lindero_sur_mts: Optional[float] = None
    lindero_este_doc: Optional[str] = None
    lindero_este_mts: Optional[float] = None
    lindero_oeste_doc: Optional[str] = None
    lindero_oeste_mts: Optional[float] = None

    lindero_norte_top: Optional[str] = None
    lindero_norte_top_mts: Optional[float] = None
    lindero_sur_top: Optional[str] = None
    lindero_sur_top_mts: Optional[float] = None
    lindero_este_top: Optional[str] = None
    lindero_este_top_mts: Optional[float] = None
    lindero_oeste_top: Optional[str] = None
    lindero_oeste_top_mts: Optional[float] = None

    aguas_blancas: bool = False
    aguas_servidas: bool = False
    electricidad: bool = False
    contador: bool = False

    existe_vivienda: bool = False
    tipo_vivienda: Optional[str] = None
    descripcion_uso: str = "residencial"
    numero_plantas: Optional[int] = None
    uso_segun_zonificacion: Optional[str] = None

    area_terreno_m2: Optional[float] = None
    valor_unit_terreno: Optional[float] = None
    area_construccion_m2: Optional[float] = None
    valor_unit_construccion: Optional[float] = None
    area_comercio_m2: Optional[float] = None
    valor_unit_comercio: Optional[float] = None

    via_acceso: Optional[str] = None
    estructura_techo: Optional[str] = None
    estructura_paredes: Optional[str] = None
    piso: Optional[str] = None
    dormitorios: Optional[int] = None
    banos: Optional[int] = None
    sala: bool = False
    cocina: bool = False
    ambiente_otro: Optional[str] = None
    caracteristica_general: Optional[str] = None

    observaciones: Optional[str] = None

    fecha_emision: Optional[date] = None

    # Campos para cédula catastral (v2.5)
    fecha_recibo: Optional[date] = None
    numero_recibo: Optional[str] = None

    @field_validator("tenencia")
    @classmethod
    def validar_tenencia(cls, v: str) -> str:
        permitidos = {"propio", "ejido", "arrendado"}
        if v not in permitidos:
            raise ValueError(f"tenencia debe ser una de {permitidos}")
        return v


class InmuebleCreate(InmuebleBase):
    """
    Payload para crear un inmueble. `geom` es el polígono capturado en el
    mapa (frontend) o en campo (app móvil), en GeoJSON estándar (WGS84 / EPSG:4326).

    NO se envían: codigo_catastral, expediente_numero, vigente_hasta,
    superficie_gis_m2, perimetro_gis_m, utm_norte, utm_este, valor_terreno,
    valor_construccion, valor_comercio, valor_catastral_total — todos los
    calcula la base de datos (triggers / columnas generadas).
    """

    geom: GeoJSONPolygon


class InmuebleUpdate(BaseModel):
    """Todos los campos opcionales — solo se actualiza lo que se envía."""

    model_config = ConfigDict(extra="ignore")

    propietario_id: Optional[uuid.UUID] = None
    direccion: Optional[str] = None
    documento_tipo: Optional[str] = None
    documento_numero: Optional[str] = None
    documento_tomo: Optional[str] = None
    documento_folio: Optional[str] = None
    documento_protocolo: Optional[str] = None
    documento_fecha: Optional[date] = None
    tenencia: Optional[str] = None
    contrato_arrendamiento_num: Optional[str] = None
    contrato_arrendamiento_fecha: Optional[date] = None
    area_terreno_m2: Optional[float] = None
    valor_unit_terreno: Optional[float] = None
    area_construccion_m2: Optional[float] = None
    valor_unit_construccion: Optional[float] = None
    area_comercio_m2: Optional[float] = None
    valor_unit_comercio: Optional[float] = None
    existe_vivienda: Optional[bool] = None
    tipo_vivienda: Optional[str] = None
    descripcion_uso: Optional[str] = None
    numero_plantas: Optional[int] = None
    uso_segun_zonificacion: Optional[str] = None
    observaciones: Optional[str] = None
    fecha_emision: Optional[date] = None
    fecha_recibo: Optional[date] = None
    numero_recibo: Optional[str] = None
    geom: Optional[GeoJSONPolygon] = None


class InmuebleOut(InmuebleBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    codigo_catastral: Optional[str] = None
    codigo_catastral_formato: Optional[str] = None
    expediente_numero: Optional[str] = None
    propietario: Optional[PropietarioOut] = None

    valor_terreno: Optional[float] = None
    valor_construccion: Optional[float] = None
    valor_comercio: Optional[float] = None
    valor_catastral_total: Optional[float] = None

    geom: Optional[GeoJSONPolygon] = None

    @field_validator("geom", mode="before")
    @classmethod
    def parse_wkb(cls, v):
        if v is not None and not isinstance(v, dict):
            # Si es un objeto de geoalchemy2 (WKBElement), lo convertimos
            try:
                from app.services.geo_service import wkb_to_geojson
                return wkb_to_geojson(v)
            except Exception:
                pass
        return v
    utm_norte: Optional[float] = None
    utm_este: Optional[float] = None
    superficie_gis_m2: Optional[float] = None
    perimetro_gis_m: Optional[float] = None

    estado_sync: str
    vigente_hasta: Optional[date] = None
    created_at: datetime
    updated_at: datetime


class InmuebleListItem(BaseModel):
    """Versión ligera para listados paginados (sin todos los campos)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    codigo_catastral: Optional[str] = None
    codigo_catastral_formato: Optional[str] = None
    direccion: str
    sector: str
    tenencia: str
    existe_vivienda: bool
    valor_catastral_total: Optional[float] = None
    vigente_hasta: Optional[date] = None
    estado_sync: str


class InmueblePaginado(BaseModel):
    total: int
    pagina: int
    por_pagina: int
    resultados: list[InmuebleListItem]
