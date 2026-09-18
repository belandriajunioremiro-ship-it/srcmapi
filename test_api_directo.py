"""
Test directo de la API con token
"""
from dotenv import load_dotenv
import os
import requests

load_dotenv('.env.test')

token = os.getenv("TEST_AUTH_TOKEN")
base_url = os.getenv("BASE_URL", "http://localhost:8000")
api_v1_prefix = os.getenv("API_V1_PREFIX", "/api/v1")

print(f"Token: {token[:50]}...")
print(f"Base URL: {base_url}")
print(f"API Prefix: {api_v1_prefix}")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Probar endpoint de usuarios
try:
    response = requests.get(f"{base_url}{api_v1_prefix}/usuarios/me", headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")