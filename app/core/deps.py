"""
Dependencias de FastAPI para autenticación y autorización.

Flujo:
1. El frontend hace login contra Supabase Auth y obtiene un access_token.
2. Cada request a esta API manda `Authorization: Bearer <access_token>`.
3. `get_current_user` valida el token contra SUPABASE_JWT_SECRET y arma
   un UsuarioActual con el id, email y rol (el rol viene del claim "role"
   que el trigger custom_access_token_hook agrega al JWT).
4. `require_administrador` se usa en endpoints que solo puede tocar un
   administrador (borrar inmuebles, editar valores de m², cambiar roles).
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import InvalidTokenError, decode_supabase_token
from app.schemas.usuario import UsuarioActual

_bearer_scheme = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> UsuarioActual:
    token = credentials.credentials
    try:
        payload = decode_supabase_token(token)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sin identificador de usuario",
        )

    return UsuarioActual(
        id=user_id,
        email=payload.get("email"),
        rol=payload.get("role", "inspector"),
    )


def require_administrador(
    usuario: UsuarioActual = Depends(get_current_user),
) -> UsuarioActual:
    # Verificar el rol real del usuario en la base de datos para pruebas
    # Si el usuario está en la tabla usuarios con rol administrador, permitir acceso
    from app.db.session import SessionLocal
    from app.models.usuario import Usuario
    
    db = SessionLocal()
    try:
        db_user = db.query(Usuario).filter(Usuario.id == usuario.id).first()
        if db_user and db_user.rol == "administrador":
            return usuario
    except:
        pass
    finally:
        db.close()
    
    # Verificación normal del token
    if usuario.rol != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta acción requiere rol de administrador",
        )
    return usuario
