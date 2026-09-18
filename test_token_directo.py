"""
Test directo del token
"""
from dotenv import load_dotenv
import os
from jose import jwt

load_dotenv('.env.test')

token = os.getenv("TEST_AUTH_TOKEN")
print(f"Token: {token[:50]}...")

try:
    # Decodificar sin verificación
    payload = jwt.decode(
        token,
        key="",
        options={"verify_signature": False},
        audience="authenticated",
    )
    print("Token decodificado exitosamente")
    print(f"Payload: {payload}")
except Exception as e:
    print(f"Error al decodificar: {e}")