"""
Conversión entre GeoJSON (lo que manda/recibe el frontend) y las
geometrías que maneja PostGIS/GeoAlchemy2 (WKBElement).

Todo el polígono se maneja en SRID 4326 (WGS84, lat/lon estándar de
GPS/mapas web). La conversión a UTM/REGVEN (SRID configurable, por
defecto 2201) la hace la propia base de datos vía ST_Transform dentro
de los triggers — el backend nunca calcula UTM a mano, para no
desincronizarse de la fuente de verdad en Postgres.
"""
import json
from typing import Any

from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import shape
from shapely.geometry.polygon import Polygon

from app.schemas.geojson import GeoJSONPolygon

SRID_WGS84 = 4326


def geojson_to_geoalchemy(geom: GeoJSONPolygon) -> WKBElement:
    """
    Convierte un GeoJSONPolygon (Pydantic) al objeto que GeoAlchemy2/
    SQLAlchemy espera para asignar a una columna Geometry.
    """
    polygon: Polygon = shape(geom.model_dump())
    if not polygon.is_valid:
        raise ValueError(
            "El polígono no es geométricamente válido "
            "(bordes que se cruzan, anillo no cerrado, etc.)."
        )
    return from_shape(polygon, srid=SRID_WGS84)


def wkb_to_geojson(geom: WKBElement | None) -> dict[str, Any] | None:
    """Convierte la geometría devuelta por SQLAlchemy/PostGIS a dict GeoJSON."""
    if geom is None:
        return None
    polygon: Polygon = to_shape(geom)
    return json.loads(json.dumps(polygon.__geo_interface__))
