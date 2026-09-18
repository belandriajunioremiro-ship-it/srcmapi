from typing import List, Literal

from pydantic import BaseModel, Field

# Coordenada [lon, lat] — igual que GeoJSON estándar (y que PostGIS/ST_AsGeoJSON)
Coordenada = List[float]
Anillo = List[Coordenada]  # lista de coordenadas que forman un anillo cerrado


class GeoJSONPolygon(BaseModel):
    """
    Polígono GeoJSON estándar (RFC 7946).

    Ejemplo:
    {
      "type": "Polygon",
      "coordinates": [[[lon1, lat1], [lon2, lat2], [lon3, lat3], [lon1, lat1]]]
    }

    El primer y último punto de cada anillo deben coincidir (polígono cerrado).
    """

    type: Literal["Polygon"] = "Polygon"
    coordinates: List[Anillo] = Field(..., min_length=1)


class GeoJSONFeature(BaseModel):
    type: Literal["Feature"] = "Feature"
    geometry: GeoJSONPolygon
    properties: dict = Field(default_factory=dict)


class GeoJSONFeatureCollection(BaseModel):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: List[GeoJSONFeature] = Field(default_factory=list)
