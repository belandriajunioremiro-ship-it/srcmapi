import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_administrador
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioActual, UsuarioOut, UsuarioRolUpdate


class UsuarioEstadoUpdate(BaseModel):
    """Schema para actualizar el estado activo/inactivo de un usuario."""

    activo: bool

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("/me", response_model=UsuarioOut)
def perfil_actual(
    usuario: UsuarioActual = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    perfil = db.get(Usuario, usuario.id)
    if not perfil:
        raise HTTPException(
            status_code=404,
            detail="Perfil no encontrado (el registro en 'usuarios' se crea "
            "automáticamente al hacer signup en Supabase Auth).",
        )
    return perfil


@router.get("", response_model=list[UsuarioOut])
def listar_usuarios(
    db: Session = Depends(get_db),
    _usuario: UsuarioActual = Depends(require_administrador),
):
    return db.query(Usuario).order_by(Usuario.nombre).all()


@router.patch("/{usuario_id}/rol", response_model=UsuarioOut)
def cambiar_rol(
    usuario_id: uuid.UUID,
    data: UsuarioRolUpdate,
    db: Session = Depends(get_db),
    _usuario: UsuarioActual = Depends(require_administrador),
):
    perfil = db.get(Usuario, usuario_id)
    if not perfil:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    perfil.rol = data.rol
    db.commit()
    db.refresh(perfil)
    return perfil


@router.patch("/{usuario_id}/estado", response_model=UsuarioOut)
def cambiar_estado(
    usuario_id: uuid.UUID,
    data: UsuarioEstadoUpdate,
    db: Session = Depends(get_db),
    _usuario: UsuarioActual = Depends(require_administrador),
):
    """
    Activar o desactivar un usuario.
    Solo administradores pueden cambiar el estado de un usuario.
    """
    perfil = db.get(Usuario, usuario_id)
    if not perfil:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    perfil.activo = data.activo
    db.commit()
    db.refresh(perfil)
    return perfil
