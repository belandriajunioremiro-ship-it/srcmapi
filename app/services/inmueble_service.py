import uuid
from datetime import date
from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.inmueble import Inmueble
from app.models.propietario import Propietario
from app.schemas.inmueble import InmuebleCreate, InmuebleUpdate
from app.services.geo_service import geojson_to_geoalchemy


def crear_inmueble(
    db: Session, data: InmuebleCreate, registrado_por: Optional[uuid.UUID] = None
) -> Inmueble:
    payload = data.model_dump(exclude={"geom"})
    inmueble = Inmueble(
        **payload,
        geom=geojson_to_geoalchemy(data.geom),
        registrado_por=registrado_por,
    )
    db.add(inmueble)
    db.commit()
    # El código catastral, expediente, vigencia, UTM y superficie los
    # calculan los triggers en el INSERT — hay que refrescar el objeto
    # para traerlos de vuelta.
    db.refresh(inmueble)
    return inmueble


def obtener_inmueble(db: Session, inmueble_id: uuid.UUID) -> Optional[Inmueble]:
    stmt = (
        select(Inmueble)
        .options(joinedload(Inmueble.propietario))
        .where(Inmueble.id == inmueble_id)
    )
    return db.execute(stmt).scalar_one_or_none()


def listar_inmuebles(
    db: Session,
    pagina: int = 1,
    por_pagina: int = 25,
    sector: Optional[str] = None,
    tenencia: Optional[str] = None,
    busqueda: Optional[str] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    vigente: Optional[bool] = None,
    ordenar_por: str = "created_at",
    orden: str = "desc",
) -> tuple[int, list[Inmueble]]:
    """
    Listado paginado con filtros opcionales y ordenamiento.

    `busqueda` hace ILIKE sobre dirección y nombre/apellido/cédula del propietario
    (usa los índices trigram creados en el script SQL: idx_inm_direccion_trgm,
    idx_prop_nombre_trgm, idx_prop_apellido_trgm, idx_prop_cedula_trgm).

    Args:
        pagina: Número de página (empezando en 1)
        por_pagina: Elementos por página (máximo 100)
        sector: Filtrar por sector catastral
        tenencia: Filtrar por tipo de tenencia
        busqueda: Búsqueda parcial por dirección o datos del propietario
        fecha_desde: Filtrar inmuebles creados desde esta fecha
        fecha_hasta: Filtrar inmuebles creados hasta esta fecha
        vigente: Filtrar por vigencia de la cédula (true=vigentes, false=vencidos)
        ordenar_por: Campo de ordenamiento
        orden: Dirección de ordenamiento (asc, desc)

    Returns:
        Tuple con (total, resultados)
    """
    # Validar y normalizar parámetros
    pagina = max(pagina, 1)
    por_pagina = min(max(por_pagina, 1), 100)
    orden = orden.lower() if orden.lower() in ("asc", "desc") else "desc"

    # Campos permitidos para ordenamiento
    campos_ordenamiento = {
        "created_at": Inmueble.created_at,
        "codigo_catastral": Inmueble.codigo_catastral,
        "direccion": Inmueble.direccion,
        "valor_catastral_total": Inmueble.valor_catastral_total,
        "fecha_emision": Inmueble.fecha_emision,
        "sector": Inmueble.sector,
    }
    campo_orden = campos_ordenamiento.get(ordenar_por, Inmueble.created_at)

    # Construir query base con join para búsquedas en propietario
    stmt = select(Inmueble).outerjoin(Propietario)

    # Aplicar filtros sectoriales
    if sector:
        stmt = stmt.where(Inmueble.sector == sector)
    if tenencia:
        stmt = stmt.where(Inmueble.tenencia == tenencia)

    # Aplicar filtros por fechas
    if fecha_desde:
        stmt = stmt.where(Inmueble.created_at >= fecha_desde)
    if fecha_hasta:
        stmt = stmt.where(Inmueble.created_at <= fecha_hasta)

    # Aplicar filtro por vigencia
    if vigente is not None:
        hoy = date.today()
        if vigente:
            # Solo vigentes (vigente_hasta >= hoy)
            stmt = stmt.where(Inmueble.vigente_hasta >= hoy)
        else:
            # Solo vencidos (vigente_hasta < hoy)
            stmt = stmt.where(Inmueble.vigente_hasta < hoy)

    # Aplicar búsqueda si se proporciona (usa índices trigram)
    if busqueda:
        patron = f"%{busqueda}%"
        stmt = stmt.where(
            or_(
                Inmueble.direccion.ilike(patron),
                Propietario.nombre.ilike(patron),
                Propietario.apellido.ilike(patron),
                Propietario.cedula_rif.ilike(patron),
            )
        )

    # Contar total antes de paginación
    total = db.execute(
        select(func.count()).select_from(stmt.subquery())
    ).scalar_one()

    # Aplicar ordenamiento
    if orden == "desc":
        stmt = stmt.order_by(campo_orden.desc())
    else:
        stmt = stmt.order_by(campo_orden.asc())

    # Aplicar paginación
    stmt = (
        stmt.options(joinedload(Inmueble.propietario))
        .offset((pagina - 1) * por_pagina)
        .limit(por_pagina)
    )

    resultados = db.execute(stmt).unique().scalars().all()
    return total, list(resultados)


def actualizar_inmueble(
    db: Session, inmueble: Inmueble, data: InmuebleUpdate
) -> Inmueble:
    cambios = data.model_dump(exclude_unset=True, exclude={"geom"})
    for campo, valor in cambios.items():
        setattr(inmueble, campo, valor)

    if data.geom is not None:
        inmueble.geom = geojson_to_geoalchemy(data.geom)

    db.add(inmueble)
    db.commit()
    db.refresh(inmueble)
    return inmueble


def eliminar_inmueble(db: Session, inmueble: Inmueble) -> None:
    db.delete(inmueble)
    db.commit()
