from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_administrador
from app.db.session import get_db
from app.schemas.geojson import GeoJSONFeatureCollection
from app.schemas.usuario import UsuarioActual
from app.services import catastro_service

router = APIRouter(prefix="/catastro", tags=["Catastro"])


@router.get("/mapa", response_model=GeoJSONFeatureCollection)
def mapa_catastral(
    min_lon: float | None = Query(None, description="Longitud mínima del bbox visible"),
    min_lat: float | None = Query(None, description="Latitud mínima del bbox visible"),
    max_lon: float | None = Query(None, description="Longitud máxima del bbox visible"),
    max_lat: float | None = Query(None, description="Latitud máxima del bbox visible"),
    db: Session = Depends(get_db),
    _usuario: UsuarioActual = Depends(get_current_user),
):
    """
    Devuelve el GeoJSON de los predios para pintar en el mapa (Leaflet,
    Mapbox GL, Google Maps, etc.). Pasa siempre el bbox del área visible
    en pantalla (min_lon, min_lat, max_lon, max_lat) para que el mapa no
    tenga que cargar TODO el catastro en cada movimiento — la función
    mapa_catastral() en Postgres ya está indexada espacialmente (GiST)
    para resolver esto rápido.
    """
    bbox = None
    if None not in (min_lon, min_lat, max_lon, max_lat):
        bbox = (min_lon, min_lat, max_lon, max_lat)
    return catastro_service.obtener_mapa_catastral(db, bbox)


@router.get("/estadisticas")
def estadisticas(
    db: Session = Depends(get_db),
    _usuario: UsuarioActual = Depends(get_current_user),
):
    """Totales generales: predios, superficie, valor catastral, por tenencia y sector."""
    return catastro_service.obtener_estadisticas(db)


@router.get("/por-sector")
def por_sector(
    db: Session = Depends(get_db),
    _usuario: UsuarioActual = Depends(get_current_user),
):
    return catastro_service.obtener_predios_por_sector(db)


@router.get("/solapamientos")
def solapamientos(
    db: Session = Depends(get_db),
    _usuario: UsuarioActual = Depends(require_administrador),
):
    """
    Auditoría de topología: predios que se solapan más de 1 m². En
    condiciones normales esto siempre debe devolver una lista vacía,
    porque el trigger prevenir_solape_predios bloquea el guardado de
    polígonos superpuestos; útil tras una carga masiva de datos.
    """
    return catastro_service.detectar_solapamientos(db)


@router.get("/sectores")
def listar_sectores(
    db: Session = Depends(get_db),
    _usuario: UsuarioActual = Depends(get_current_user),
):
    """
    Listar todos los sectores catastrales disponibles con estadísticas.
    Útil para filtros en el frontend y formularios.
    """
    from app.models.inmueble import Inmueble

    stmt = (
        select(
            Inmueble.sector,
            func.count(Inmueble.id).label("total_predios"),
            func.sum(Inmueble.superficie_gis_m2).label("superficie_total_m2"),
            func.sum(Inmueble.valor_catastral_total).label("valor_catastral_total"),
        )
        .group_by(Inmueble.sector)
        .order_by(Inmueble.sector)
    )

    resultados = db.execute(stmt).all()

    return [
        {
            "codigo": row.sector,
            "total_predios": row.total_predios or 0,
            "superficie_total_m2": float(row.superficie_total_m2 or 0),
            "valor_catastral_total": float(row.valor_catastral_total or 0),
        }
        for row in resultados
    ]
