import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_administrador
from app.db.session import get_db
from app.models.foto import FotoInmueble
from app.models.hito import HitoPredial
from app.schemas.foto import FotoInmuebleCreate, FotoInmuebleOut
from app.schemas.hito import HitoPredialCreate, HitoPredialOut
from app.schemas.inmueble import (
    InmuebleCreate,
    InmuebleOut,
    InmueblePaginado,
    InmuebleUpdate,
)
from app.schemas.usuario import UsuarioActual
from app.services import inmueble_service
from app.services.cedula_service import generar_pdf_cedula
from app.services.inmueble_mapper import inmueble_a_list_item, inmueble_a_out
from app.utils.db_errors import mensaje_error_postgres

router = APIRouter(prefix="/inmuebles", tags=["Inmuebles"])


def _obtener_o_404(db: Session, inmueble_id: uuid.UUID):
    inmueble = inmueble_service.obtener_inmueble(db, inmueble_id)
    if not inmueble:
        raise HTTPException(status_code=404, detail="Inmueble no encontrado")
    return inmueble


@router.post("", response_model=InmuebleOut, status_code=status.HTTP_201_CREATED)
def crear_inmueble(
    data: InmuebleCreate,
    db: Session = Depends(get_db),
    usuario: UsuarioActual = Depends(get_current_user),
):
    """
    Crea un inmueble a partir del polígono dibujado/capturado en el mapa.
    El código catastral, expediente, vigencia y valores UTM los calcula
    la base de datos automáticamente al insertar (ver triggers en el SQL).
    """
    try:
        inmueble = inmueble_service.crear_inmueble(
            db, data, registrado_por=usuario.id
        )
    except ValueError as exc:
        # geometría inválida (detectada en Shapely antes de llegar a la BD)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except (IntegrityError, DBAPIError) as exc:
        db.rollback()
        # Aquí caen, por ejemplo: solape_topologico (trigger
        # prevenir_solape_predios) o código catastral duplicado.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=mensaje_error_postgres(exc),
        ) from exc
    return inmueble_a_out(inmueble)


@router.get("", response_model=InmueblePaginado)
def listar_inmuebles(
    pagina: int = 1,
    por_pagina: int = 25,
    sector: str | None = None,
    tenencia: str | None = None,
    q: str | None = None,
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
    vigente: bool | None = None,
    ordenar_por: str = "created_at",
    orden: str = "desc",
    db: Session = Depends(get_db),
    _usuario: UsuarioActual = Depends(get_current_user),
):
    """
    Listar inmuebles con paginación, filtros múltiples, búsqueda y ordenamiento.

    Args:
        pagina: Número de página (default: 1)
        por_pagina: Elementos por página (default: 25, max: 100)
        sector: Filtrar por sector catastral
        tenencia: Filtrar por tipo de tenencia (propio, ejido, arrendado)
        q: Búsqueda parcial por dirección o datos del propietario
        fecha_desde: Filtrar inmuebles creados desde esta fecha (YYYY-MM-DD)
        fecha_hasta: Filtrar inmuebles creados hasta esta fecha (YYYY-MM-DD)
        vigente: Filtrar por vigencia de la cédula (true=vigentes, false=vencidos)
        ordenar_por: Campo de ordenamiento (created_at, codigo_catastral, direccion, valor_catastral_total, fecha_emision, sector)
        orden: Dirección de ordenamiento (asc, desc)
    """
    from datetime import datetime

    pagina = max(pagina, 1)
    por_pagina = min(max(por_pagina, 1), 100)

    # Convertir fechas de string a date si se proporcionan
    fecha_desde_date = None
    fecha_hasta_date = None
    if fecha_desde:
        try:
            fecha_desde_date = datetime.strptime(fecha_desde, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=422, detail="fecha_desde debe estar en formato YYYY-MM-DD")
    if fecha_hasta:
        try:
            fecha_hasta_date = datetime.strptime(fecha_hasta, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=422, detail="fecha_hasta debe estar en formato YYYY-MM-DD")

    total, resultados = inmueble_service.listar_inmuebles(
        db,
        pagina=pagina,
        por_pagina=por_pagina,
        sector=sector,
        tenencia=tenencia,
        busqueda=q,
        fecha_desde=fecha_desde_date,
        fecha_hasta=fecha_hasta_date,
        vigente=vigente,
        ordenar_por=ordenar_por,
        orden=orden,
    )
    return InmueblePaginado(
        total=total,
        pagina=pagina,
        por_pagina=por_pagina,
        resultados=[inmueble_a_list_item(i) for i in resultados],
    )


@router.get("/{inmueble_id}", response_model=InmuebleOut)
def obtener_inmueble(
    inmueble_id: uuid.UUID,
    db: Session = Depends(get_db),
    _usuario: UsuarioActual = Depends(get_current_user),
):
    inmueble = _obtener_o_404(db, inmueble_id)
    return inmueble_a_out(inmueble)


@router.patch("/{inmueble_id}", response_model=InmuebleOut)
def actualizar_inmueble(
    inmueble_id: uuid.UUID,
    data: InmuebleUpdate,
    db: Session = Depends(get_db),
    _usuario: UsuarioActual = Depends(get_current_user),
):
    inmueble = _obtener_o_404(db, inmueble_id)
    try:
        inmueble = inmueble_service.actualizar_inmueble(db, inmueble, data)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except (IntegrityError, DBAPIError) as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=mensaje_error_postgres(exc),
        ) from exc
    return inmueble_a_out(inmueble)


@router.delete("/{inmueble_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_inmueble(
    inmueble_id: uuid.UUID,
    db: Session = Depends(get_db),
    _usuario: UsuarioActual = Depends(require_administrador),
):
    inmueble = _obtener_o_404(db, inmueble_id)
    inmueble_service.eliminar_inmueble(db, inmueble)


# ============================================================
# Cédula Catastral (PDF) — generada enteramente en el backend
# ============================================================
@router.get("/{inmueble_id}/cedula", response_class=Response)
def descargar_cedula_catastral(
    inmueble_id: uuid.UUID,
    db: Session = Depends(get_db),
    _usuario: UsuarioActual = Depends(get_current_user),
):
    """
    Genera y devuelve el PDF de la cédula catastral. El PDF se arma con
    los datos que ya están en la base de datos (vista v_pdf_cedula_catastral)
    — el cliente nunca envía ni puede alterar los valores que aparecen en
    el documento, lo cual es más seguro que generar el PDF en el frontend.
    """
    try:
        pdf_bytes = generar_pdf_cedula(db, str(inmueble_id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    filename = f"cedula_catastral_{inmueble_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{inmueble_id}/cedula-datos")
def obtener_datos_cedula_catastral(
    inmueble_id: uuid.UUID,
    db: Session = Depends(get_db),
    _usuario: UsuarioActual = Depends(get_current_user),
):
    """
    Devuelve todos los datos necesarios para generar la cédula catastral desde el frontend.
    El frontend usa estos datos para generar el PDF con @react-pdf/renderer.
    """
    from sqlalchemy import text

    inmueble = _obtener_o_404(db, inmueble_id)
    
    # Obtener datos de la vista completa de cédula catastral
    result = db.execute(
        text("SELECT * FROM v_pdf_cedula_catastral WHERE inmueble_id = :id"),
        {"id": str(inmueble_id)}
    ).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Datos de cédula no encontrados")
    
    # Convertir a diccionario para respuesta JSON
    return dict(result._mapping)


# ============================================================
# Hitos prediales (vértices GPS del polígono)
# ============================================================
@router.post(
    "/{inmueble_id}/hitos",
    response_model=HitoPredialOut,
    status_code=status.HTTP_201_CREATED,
)
def agregar_hito(
    inmueble_id: uuid.UUID,
    data: HitoPredialCreate,
    db: Session = Depends(get_db),
    _usuario: UsuarioActual = Depends(get_current_user),
):
    _obtener_o_404(db, inmueble_id)  # valida que el inmueble exista
    hito = HitoPredial(inmueble_id=inmueble_id, **data.model_dump())
    db.add(hito)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=mensaje_error_postgres(exc),
        ) from exc
    db.refresh(hito)
    return hito


@router.get("/{inmueble_id}/hitos", response_model=list[HitoPredialOut])
def listar_hitos(
    inmueble_id: uuid.UUID,
    db: Session = Depends(get_db),
    _usuario: UsuarioActual = Depends(get_current_user),
):
    _obtener_o_404(db, inmueble_id)
    return (
        db.query(HitoPredial)
        .filter(HitoPredial.inmueble_id == inmueble_id)
        .order_by(HitoPredial.indice_vertice)
        .all()
    )


@router.delete("/{inmueble_id}/hitos/{hito_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_hito(
    inmueble_id: uuid.UUID,
    hito_id: uuid.UUID,
    db: Session = Depends(get_db),
    _usuario: UsuarioActual = Depends(require_administrador),
):
    """Eliminar un hito predial específico de un inmueble."""
    _obtener_o_404(db, inmueble_id)
    hito = db.get(HitoPredial, hito_id)
    if not hito:
        raise HTTPException(status_code=404, detail="Hito no encontrado")
    if hito.inmueble_id != inmueble_id:
        raise HTTPException(
            status_code=400, detail="El hito no pertenece a este inmueble"
        )
    db.delete(hito)
    db.commit()


# ============================================================
# Fotos del inmueble
# (la subida física del archivo se hace a Supabase Storage desde el
# frontend o mediante un endpoint de storage aparte; aquí solo se
# registra la URL resultante)
# ============================================================
@router.post(
    "/{inmueble_id}/fotos",
    response_model=FotoInmuebleOut,
    status_code=status.HTTP_201_CREATED,
)
def agregar_foto(
    inmueble_id: uuid.UUID,
    data: FotoInmuebleCreate,
    db: Session = Depends(get_db),
    _usuario: UsuarioActual = Depends(get_current_user),
):
    _obtener_o_404(db, inmueble_id)
    foto = FotoInmueble(inmueble_id=inmueble_id, **data.model_dump())
    db.add(foto)
    db.commit()
    db.refresh(foto)
    return foto


@router.get("/{inmueble_id}/fotos", response_model=list[FotoInmuebleOut])
def listar_fotos(
    inmueble_id: uuid.UUID,
    db: Session = Depends(get_db),
    _usuario: UsuarioActual = Depends(get_current_user),
):
    _obtener_o_404(db, inmueble_id)
    return (
        db.query(FotoInmueble)
        .filter(FotoInmueble.inmueble_id == inmueble_id)
        .order_by(FotoInmueble.created_at)
        .all()
    )


@router.delete("/{inmueble_id}/fotos/{foto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_foto(
    inmueble_id: uuid.UUID,
    foto_id: uuid.UUID,
    db: Session = Depends(get_db),
    _usuario: UsuarioActual = Depends(require_administrador),
):
    """Eliminar una foto específica de un inmueble."""
    _obtener_o_404(db, inmueble_id)
    foto = db.get(FotoInmueble, foto_id)
    if not foto:
        raise HTTPException(status_code=404, detail="Foto no encontrada")
    if foto.inmueble_id != inmueble_id:
        raise HTTPException(
            status_code=400, detail="La foto no pertenece a este inmueble"
        )
    db.delete(foto)
    db.commit()
