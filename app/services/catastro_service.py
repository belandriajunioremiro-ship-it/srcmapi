"""
Envoltorios delgados sobre las funciones SQL ya definidas en la base de
datos (mapa_catastral, estadisticas_catastro, predios_por_sector,
detectar_solapamientos). Se prefiere dejar esta lógica en Postgres
(donde vive PostGIS) y que el backend solo la invoque — es más rápido
y evita duplicar reglas espaciales en Python.
"""
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session


def obtener_mapa_catastral(
    db: Session,
    bbox: Optional[tuple[float, float, float, float]] = None,
) -> dict[str, Any]:
    """
    Devuelve el GeoJSON FeatureCollection de los predios.

    bbox: (min_lon, min_lat, max_lon, max_lat). Si es None, trae todos
    los predios (usar solo en municipios pequeños o para exportar; para
    el mapa interactivo del frontend, siempre pasa el bbox visible).
    """
    if bbox:
        min_lon, min_lat, max_lon, max_lat = bbox
        result = db.execute(
            text("SELECT mapa_catastral(:min_lon, :min_lat, :max_lon, :max_lat)"),
            {
                "min_lon": min_lon,
                "min_lat": min_lat,
                "max_lon": max_lon,
                "max_lat": max_lat,
            },
        ).scalar_one()
    else:
        result = db.execute(text("SELECT mapa_catastral()")).scalar_one()
    return result


def obtener_estadisticas(db: Session) -> dict[str, Any]:
    return db.execute(text("SELECT estadisticas_catastro()")).scalar_one()


def obtener_predios_por_sector(db: Session) -> list[dict[str, Any]]:
    """Obtener predios agrupados por sector.
    
    La función SQL predios_por_sector() retorna un jsonb_object_agg
    (dict con sectores como claves). Lo convertimos a lista de objetos
    con campo 'sector' para que sea consistente con el router.
    """
    try:
        result = db.execute(text("SELECT predios_por_sector()")).scalar_one()
        # Si el resultado es None (no hay datos), retornar lista vacía
        if result is None:
            return []
        # Si ya es una lista, devolverla directamente
        if isinstance(result, list):
            return result
        # Si es un dict (jsonb_object_agg), convertirlo a lista
        if isinstance(result, dict):
            return [
                {"sector": sector, **datos}
                for sector, datos in result.items()
            ]
        return []
    except Exception as e:
        # En caso de error, retornar lista vacía para no romper el API
        print(f"Error en obtener_predios_por_sector: {e}")
        return []


def detectar_solapamientos(db: Session) -> dict[str, Any]:
    """Auditoría: predios que topológicamente se solapan (no debería pasar,
    porque el trigger prevenir_solape_predios los bloquea al guardar, pero
    sirve para detectar datos importados o cargados por otra vía).
    
    Nota: La función SQL detectar_solapamientos(p_geom) requiere un polígono
    como argumento. Para auditoría global, usamos una query SQL directa que
    detecta todos los pares de predios solapados.
    """
    try:
        result = db.execute(text("""
            SELECT COALESCE(jsonb_agg(jsonb_build_object(
                'inmueble_a', a.codigo_catastral,
                'inmueble_b', b.codigo_catastral,
                'area_solape_m2', round(ST_Area(ST_Intersection(a.geom, b.geom)::geography)::numeric, 2)
            )), '[]'::jsonb)
            FROM inmuebles a
            JOIN inmuebles b ON a.id < b.id
                AND ST_Intersects(a.geom, b.geom)
                AND ST_Area(ST_Intersection(a.geom, b.geom)::geography) > 1
        """)).scalar_one()
        return {"solapamientos": result if result else []}
    except Exception as e:
        print(f"Error en detectar_solapamientos: {e}")
        return {"solapamientos": []}
