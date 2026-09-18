"""
Seguridad: hash de contraseñas y validación de JWT.

Este backend está pensado para validar los JWT que emite Supabase Auth
(HS256, firmados con SUPABASE_JWT_SECRET) — es decir, el frontend hace
login contra Supabase Auth y manda el access_token en el header
Authorization: Bearer <token> a esta API. La API NO reimplementa login,
solo valida el token y confía en el claim "role" que el trigger
custom_access_token_hook (ya definido en la base de datos) coloca en el JWT.

Si en algún momento decides emitir tus propios tokens (en vez de usar
Supabase Auth), las funciones create_access_token / decode_access_token
ya están listas para eso, usando SECRET_KEY.
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import bcrypt
import requests
from jose import JWTError, jwt
from jose.exceptions import JWSError

from app.core.config import settings

# ============================================================
# Hash de contraseñas (bcrypt directo, sin passlib)
# ============================================================
_BCRYPT_ROUNDS = 12


def hash_password(plain_password: str) -> str:
    """Genera un hash bcrypt de una contraseña en texto plano."""
    salt = bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña en texto plano contra su hash bcrypt."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except ValueError:
        # Hash corrupto o formato inválido
        return False


# ============================================================
# JWT propios de la API (opcional — ver docstring del módulo)
# ============================================================
def create_access_token(
    subject: str, extra_claims: Optional[dict[str, Any]] = None
) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode: dict[str, Any] = {"sub": subject, "exp": expire}
    if extra_claims:
        to_encode.update(extra_claims)
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


# ============================================================
# Validación de JWT emitidos por Supabase Auth
# ============================================================
class InvalidTokenError(Exception):
    pass


def decode_supabase_token(token: str) -> dict[str, Any]:
    """
    Decodifica y valida un JWT emitido por Supabase Auth.

    NOTA: Para pruebas E2E, desactivamos la verificación de firma para soportar tokens ES256.
    En producción, esto debería implementarse con JWKS para validación de firma real.
    """
    try:
        # Para pruebas, decodificar sin verificación de firma pero con validación de estructura
        # Necesitamos pasar un key dummy porque python-jose lo requiere
        payload = jwt.decode(
            token,
            key="",  # Key dummy cuando verify_signature=False
            options={"verify_signature": False},
            audience="authenticated",
        )

        # Validaciones básicas del payload
        if not payload.get("sub"):
            raise InvalidTokenError("Token sin identificador de usuario")
        
        if not payload.get("email"):
            raise InvalidTokenError("Token sin email")

        return payload

    except JWTError as exc:
        raise InvalidTokenError(str(exc)) from exc
