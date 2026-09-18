from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_administrador
from app.db.session import get_db
from app.schemas.configuracion import (
    ConfiguracionCatastralOut,
    ConfiguracionCatastralUpdate,
    ConfiguracionSistemaOut,
    ConfiguracionSistemaUpdate,
)
from app.schemas.usuario import UsuarioActual
from app.services import configuracion_service

router = APIRouter(prefix="/configuracion", tags=["Configuracion"])


@router.get("/catastral", response_model=ConfiguracionCatastralOut)
def obtener_configuracion_catastral(
    db: Session = Depends(get_db),
    _usuario: UsuarioActual = Depends(get_current_user),
):
    """
    Obtener la configuración catastral actual.
    Incluye valores por m², vigencia, datos institucionales y códigos geográficos.
    """
    config = configuracion_service.obtener_configuracion_catastral(db)
    if not config:
        raise HTTPException(
            status_code=404,
            detail="Configuración catastral no encontrada. Ejecuta el script SQL.",
        )
    return config


@router.patch("/catastral", response_model=ConfiguracionCatastralOut)
def actualizar_configuracion_catastral(
    data: ConfiguracionCatastralUpdate,
    db: Session = Depends(get_db),
    _usuario: UsuarioActual = Depends(require_administrador),
):
    """
    Actualizar la configuración catastral.
    Solo administradores pueden modificar estos valores.
    """
    try:
        config = configuracion_service.actualizar_configuracion_catastral(
            db, data.model_dump(exclude_unset=True)
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return config


@router.get("/sistema", response_model=ConfiguracionSistemaOut)
def obtener_configuracion_sistema(
    db: Session = Depends(get_db),
    _usuario: UsuarioActual = Depends(get_current_user),
):
    """
    Obtener la configuración del sistema.
    Usada por el trigger de validación del código catastral.
    """
    config = configuracion_service.obtener_configuracion_sistema(db)
    if not config:
        raise HTTPException(
            status_code=404,
            detail="Configuración del sistema no encontrada. Ejecuta el script SQL.",
        )
    return config


@router.patch("/sistema", response_model=ConfiguracionSistemaOut)
def actualizar_configuracion_sistema(
    data: ConfiguracionSistemaUpdate,
    db: Session = Depends(get_db),
    _usuario: UsuarioActual = Depends(require_administrador),
):
    """
    Actualizar la configuración del sistema.
    Solo administradores pueden modificar estos valores.
    IMPORTANTE: Debe mantenerse sincronizada con configuracion_catastral.
    """
    try:
        config = configuracion_service.actualizar_configuracion_sistema(
            db, data.model_dump(exclude_unset=True)
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return config


@router.get("/catastral/pdf-config")
def obtener_configuracion_pdf(
    db: Session = Depends(get_db),
    _usuario: UsuarioActual = Depends(get_current_user),
):
    """
    Devuelve la configuración institucional necesaria para generar el PDF
    desde el frontend (datos institucionales: autoridades, logos, notas legales).
    """
    from app.models.configuracion import ConfiguracionCatastral
    
    config = db.get(ConfiguracionCatastral, 1)
    if not config:
        raise HTTPException(
            status_code=404,
            detail="Configuración catastral no encontrada. Ejecuta el script SQL.",
        )
    
    return {
        "nombre_estado": config.nombre_estado,
        "nombre_municipio": config.nombre_municipio,
        "nombre_parroquia": config.nombre_parroquia,
        "rif_alcaldia": config.rif_alcaldia,
        "direccion_institucional": config.direccion_institucional,
        "nombre_maxima_autoridad": config.nombre_maxima_autoridad,
        "cargo_maxima_autoridad": config.cargo_maxima_autoridad,
        "texto_acta_maxima_autoridad": config.texto_acta_maxima_autoridad,
        "nombre_director_catastro": config.nombre_director_catastro,
        "cargo_director_catastro": config.cargo_director_catastro,
        "texto_resolucion_director": config.texto_resolucion_director,
        "notas_legales": config.notas_legales,
    }
