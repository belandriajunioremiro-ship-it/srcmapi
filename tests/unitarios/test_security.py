import pytest
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    decode_supabase_token,
    InvalidTokenError,
)
from jose import jwt

def test_hash_y_verify_password():
    password = "SuperSecretPassword123"
    hashed = hash_password(password)
    
    # Asegurar que el hash es diferente al texto plano
    assert hashed != password
    # Asegurar que la verificación funciona
    assert verify_password(password, hashed) is True
    # Asegurar que falle con contraseña incorrecta
    assert verify_password("wrongpassword", hashed) is False

def test_verify_password_invalid_hash():
    # Probar que maneja un ValueError si el hash está corrupto
    assert verify_password("password", "hash_invalido_sin_formato") is False

def test_create_y_decode_access_token():
    subject = "user123"
    token = create_access_token(subject, extra_claims={"role": "admin"})
    
    decoded = decode_access_token(token)
    assert decoded["sub"] == subject
    assert decoded["role"] == "admin"
    assert "exp" in decoded

def test_decode_supabase_token_valido():
    # Crear un token dummy válido (verify_signature está apagado en código)
    token = jwt.encode({"sub": "user-uuid", "email": "test@test.com", "aud": "authenticated", "exp": 9999999999}, "")
    payload = decode_supabase_token(token)
    assert payload["sub"] == "user-uuid"
    assert payload["email"] == "test@test.com"

def test_decode_supabase_token_sin_sub():
    token = jwt.encode({"email": "test@test.com", "aud": "authenticated", "exp": 9999999999}, "")
    with pytest.raises(InvalidTokenError, match="Token sin identificador"):
        decode_supabase_token(token)

def test_decode_supabase_token_sin_email():
    token = jwt.encode({"sub": "user-uuid", "aud": "authenticated", "exp": 9999999999}, "")
    with pytest.raises(InvalidTokenError, match="Token sin email"):
        decode_supabase_token(token)

def test_decode_supabase_token_jwt_error():
    # Probar con un string que no es un JWT válido
    with pytest.raises(InvalidTokenError):
        decode_supabase_token("este.no.es.un.token.valido")
