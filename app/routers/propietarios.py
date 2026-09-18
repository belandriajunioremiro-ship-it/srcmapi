import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_administrador
from app.db.session import get_db
from app.models.propietario import Propietario
from app.schemas.propietario import PropietarioCreate, PropietarioOut, PropietarioPaginado, PropietarioUpdate
from app.schemas.usuario import UsuarioActual
from app.services import propietario_service
from app.utils.db_errors import mensaje_error_postgres

router = APIRouter(prefix="/propietarios", tags=["Propietarios"])


@router.post("", response_model=PropietarioOut, status_code=status.HTTP_201_CREATED)
def crear_propietario(
    data: PropietarioCreate,
    db: Session = Depends(get_db),
    _usuario: UsuarioActual = Depends(get_current_user),
):
    try:
        propietario = propietario_service.crear_propietario(db, data.model_dump())
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=mensaje_error_postgres(exc),
        ) from exc
    return propietario


@router.get("", response_model=PropietarioPaginado)
def listar_propietarios(
    pagina: int = 1,
    por_pagina: int = 25,
    q: str | None = None,
    ordenar_por: str = "nombre",
    orden: str = "asc",
    db: Session = Depends(get_db),
    _usuario: UsuarioActual = Depends(get_current_user),
):
    """
    Listar propietarios con paginación, búsqueda y ordenamiento.

    Args:
        pagina: Número de página (default: 1)
        por_pagina: Elementos por página (default: 25, max: 100)
        q: Búsqueda parcial por nombre, apellido o cédula/RIF
        ordenar_por: Campo de ordenamiento (nombre, apellido, cedula_rif, created_at)
        orden: Dirección de ordenamiento (asc, desc)
    """
    total, resultados = propietario_service.listar_propietarios(
        db,
        pagina=pagina,
        por_pagina=por_pagina,
        busqueda=q,
        ordenar_por=ordenar_por,
        orden=orden,
    )
    return PropietarioPaginado(
        total=total,
        pagina=pagina,
        por_pagina=por_pagina,
        resultados=resultados,
    )


@router.get("/{propietario_id}", response_model=PropietarioOut)
def obtener_propietario(
    propietario_id: uuid.UUID,
    db: Session = Depends(get_db),
    _usuario: UsuarioActual = Depends(get_current_user),
):
    propietario = propietario_service.obtener_propietario(db, str(propietario_id))
    if not propietario:
        raise HTTPException(status_code=404, detail="Propietario no encontrado")
    return propietario


@router.patch("/{propietario_id}", response_model=PropietarioOut)
def actualizar_propietario(
    propietario_id: uuid.UUID,
    data: PropietarioUpdate,
    db: Session = Depends(get_db),
    _usuario: UsuarioActual = Depends(get_current_user),
):
    propietario = propietario_service.obtener_propietario(db, str(propietario_id))
    if not propietario:
        raise HTTPException(status_code=404, detail="Propietario no encontrado")

    try:
        propietario = propietario_service.actualizar_propietario(
            db, propietario, data.model_dump(exclude_unset=True)
        )
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=mensaje_error_postgres(exc),
        ) from exc
    return propietario


@router.delete("/{propietario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_propietario(
    propietario_id: uuid.UUID,
    db: Session = Depends(get_db),
    _usuario: UsuarioActual = Depends(require_administrador),
):
    propietario = propietario_service.obtener_propietario(db, str(propietario_id))
    if not propietario:
        raise HTTPException(status_code=404, detail="Propietario no encontrado")
    try:
        propietario_service.eliminar_propietario(db, propietario)
    except IntegrityError as exc:
        db.rollback()
        # ON DELETE RESTRICT en inmuebles.propietario_id
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar: el propietario tiene inmuebles registrados.",
        ) from exc


@router.get("/{propietario_id}/inmuebles")
def listar_inmuebles_propietario(
    propietario_id: uuid.UUID,
    pagina: int = 1,
    por_pagina: int = 25,
    vigente: bool | None = None,
    db: Session = Depends(get_db),
    _usuario: UsuarioActual = Depends(get_current_user),
):
    """
    Listar todos los inmuebles de un propietario específico.
    """
    from datetime import date

    from app.models.inmueble import Inmueble
    from app.schemas.inmueble import InmuebleListItem

    # Validar que el propietario existe
    propietario = propietario_service.obtener_propietario(db, str(propietario_id))
    if not propietario:
        raise HTTPException(status_code=404, detail="Propietario no encontrado")

    # Validar y normalizar parámetros
    pagina = max(pagina, 1)
    por_pagina = min(max(por_pagina, 1), 100)

    # Construir query base
    stmt = select(Inmueble).where(Inmueble.propietario_id == propietario_id)

    # Aplicar filtro por vigencia si se proporciona
    if vigente is not None:
        hoy = date.today()
        if vigente:
            stmt = stmt.where(Inmueble.vigente_hasta >= hoy)
        else:
            stmt = stmt.where(Inmueble.vigente_hasta < hoy)

    # Contar total
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()

    # Aplicar paginación
    stmt = (
        stmt.order_by(Inmueble.created_at.desc())
        .offset((pagina - 1) * por_pagina)
        .limit(por_pagina)
    )

    resultados = db.execute(stmt).scalars().all()

    return {
        "total": total,
        "pagina": pagina,
        "por_pagina": por_pagina,
        "resultados": [InmuebleListItem.model_validate(i) for i in resultados],
    }
