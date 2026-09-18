import pytest
from app.services.geo_service import wkb_to_geojson, geojson_to_geoalchemy
from app.schemas.geojson import GeoJSONPolygon

def test_wkb_to_geojson_none():
    assert wkb_to_geojson(None) is None

def test_geojson_to_geoalchemy_invalid_polygon():
    # Polygon where coordinates don't form a closed ring or intersect
    # According to GeoJSON, a Polygon's first and last coordinate must be the same to close the ring
    invalid_geom = GeoJSONPolygon(
        type="Polygon",
        coordinates=[[
            [-72.0, 8.0],
            [-72.1, 8.1], # cruza
            [-72.1, 8.0],
            [-72.0, 8.1], # cruza
            [-72.0, 8.0]
        ]]
    )
    
    with pytest.raises(ValueError) as exc:
        geojson_to_geoalchemy(invalid_geom)
        
    assert "no es geométricamente válido" in str(exc.value)

def test_geojson_to_geoalchemy_valid():
    valid_geom = GeoJSONPolygon(
        type="Polygon",
        coordinates=[[
            [-72.0, 8.0],
            [-72.0, 8.1],
            [-72.1, 8.1],
            [-72.0, 8.0] # Cerrado correctamente
        ]]
    )
    wkb = geojson_to_geoalchemy(valid_geom)
    assert wkb is not None
    assert wkb.srid == 4326

def test_wkb_to_geojson_valid():
    # Creamos un polygon y lo convertimos a WKB para luego devolverlo a dict
    valid_geom = GeoJSONPolygon(
        type="Polygon",
        coordinates=[[
            [-72.0, 8.0],
            [-72.0, 8.1],
            [-72.1, 8.1],
            [-72.0, 8.0]
        ]]
    )
    wkb = geojson_to_geoalchemy(valid_geom)
    
    geojson_dict = wkb_to_geojson(wkb)
    assert geojson_dict["type"] == "Polygon"
    assert len(geojson_dict["coordinates"][0]) == 4
