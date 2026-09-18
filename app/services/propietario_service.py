"""
Servicio para gestión de propietarios con paginación, búsqueda y ordenamiento.
"""
from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.propietario import Propietario


def listar_propietarios(
    db: Session,
    pagina: int = 1,
    por_pagina: int = 25,
    busqueda: Optional[str] = None,
    ordenar_por: str = "nombre",
    orden: str = "asc",
) -> tuple[int, list[Propietario]]:
    """
    Listado paginado de propietarios con búsqueda y ordenamiento.

    Args:
        pagina: Número de página (empezando en 1)
        por_pagina: Elementos por página (máximo 100)
        busqueda: Búsqueda parcial por nombre, apellido o cédula/RIF
        ordenar_por: Campo de ordenamiento (nombre, apellido, cedula_rif, created_at)
        orden: Dirección de ordenamiento (asc, desc)

    Returns:
        Tuple con (total, resultados)
    """
    # Validar y normalizar parámetros
    pagina = max(pagina, 1)
    por_pagina = min(max(por_pagina, 1), 100)
    orden = orden.lower() if orden.lower() in ("asc", "desc") else "asc"

    # Campos permitidos para ordenamiento
    campos_ordenamiento = {
        "nombre": Propietario.nombre,
        "apellido": Propietario.apellido,
        "cedula_rif": Propietario.cedula_rif,
        "created_at": Propietario.created_at,
    }
    campo_orden = campos_ordenamiento.get(ordenar_por, Propietario.nombre)

    # Construir query base
    stmt = select(Propietario)

    # Aplicar búsqueda si se proporciona
    if busqueda:
        patron = f"%{busqueda}%"
        stmt = stmt.where(
            or_(
                Propietario.nombre.ilike(patron),
                Propietario.apellido.ilike(patron),
                Propietario.cedula_rif.ilike(patron),
            )
        )

    # Contar total antes de paginación
    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()

    # Aplicar ordenamiento
    if orden == "desc":
        stmt = stmt.order_by(campo_orden.desc())
    else:
        stmt = stmt.order_by(campo_orden.asc())

    # Aplicar paginación
    stmt = stmt.offset((pagina - 1) * por_pagina).limit(por_pagina)

    resultados = db.execute(stmt).scalars().all()
    return total, list(resultados)


def obtener_propietario(db: Session, propietario_id: str) -> Optional[Propietario]:
    """Obtener un propietario por ID."""
    return db.get(Propietario, propietario_id)


def crear_propietario(db: Session, data: dict) -> Propietario:
    """Crear un nuevo propietario."""
    propietario = Propietario(**data)
    db.add(propietario)
    db.commit()
    db.refresh(propietario)
    return propietario


def actualizar_propietario(db: Session, propietario: Propietario, data: dict) -> Propietario:
    """Actualizar un propietario existente."""
    for campo, valor in data.items():
        setattr(propietario, campo, valor)
    db.commit()
    db.refresh(propietario)
    return propietario


def eliminar_propietario(db: Session, propietario: Propietario) -> None:
    """Eliminar un propietario."""
    db.delete(propietario)
    db.commit()
