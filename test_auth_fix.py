"""
Script para probar la corrección del algoritmo JWT
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
API_V1_PREFIX = os.getenv("API_V1_PREFIX", "/api/v1")

# Leer el token de prueba
with open("token_obtenido.txt", "r") as f:
    token = f.read().strip()

print("🔍 Probando corrección de algoritmo JWT ES256")
print(f"Token (primeros 50 chars): {token[:50]}...")
print()

# Headers con autenticación
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Probar endpoint de perfil de usuario
print("📡 Probando GET /api/v1/usuarios/me")
try:
    response = requests.get(f"{BASE_URL}{API_V1_PREFIX}/usuarios/me", headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ ÉXITO: Autenticación ES256 funciona correctamente")
        print(f"Response: {response.json()}")
    elif response.status_code == 401:
        print("❌ ERROR: Autenticación falló (401 Unauthorized)")
        print(f"Response: {response.text}")
    else:
        print(f"⚠️  Status inesperado: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error de conexión: {e}")