"""
Configuración de pytest para pruebas E2E
"""
import pytest
import requests
import os
import time
import uuid
import random
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('.env.test')
# También cargar el archivo .env principal como fallback
load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
API_V1_PREFIX = os.getenv("API_V1_PREFIX", "/api/v1")

@pytest.fixture(scope="session")
def base_url():
    """URL base para las pruebas"""
    return BASE_URL

@pytest.fixture(scope="session")
def api_url():
    """URL base de la API"""
    return f"{BASE_URL}{API_V1_PREFIX}"

@pytest.fixture(scope="session")
def auth_token():
    """
    Token de autenticación para las pruebas.
    Nota: Debes obtener un token válido de Supabase Auth y configurarlo
    en la variable de entorno TEST_AUTH_TOKEN o hardcodearlo temporalmente.
    """
    token = os.getenv("TEST_AUTH_TOKEN")
    if not token:
        pytest.skip("TEST_AUTH_TOKEN no configurado. Obtén un token de Supabase Auth y configúralo.")
    return token

@pytest.fixture(scope="session")
def headers(auth_token):
    """Headers con autenticación para las pruebas"""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }

@pytest.fixture(scope="session")
def admin_headers(auth_token):
    """
    Headers con autenticación de administrador.
    NOTA: Para pruebas, usamos el mismo token pero el rol se valida en el backend.
    """
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }

@pytest.fixture(scope="function")
def crear_propietario_temporal(api_url, headers):
    """
    Fixture para crear un propietario temporal y limpiarlo después de la prueba.
    Genera datos aleatorios para evitar conflictos.
    """
    import random
    import uuid
    
    timestamp = int(time.time())
    random_id = uuid.uuid4().hex[:8]
    
    propietario_data = {
        "cedula_rif": f"V-{random.randint(10000000, 99999999)}",
        "nombre": f"Propietario{random_id}",
        "apellido": f"Prueba{timestamp}",
        "telefono": f"0414-{random.randint(1000000, 9999999)}",
        "email": f"propietario{random_id}{timestamp}@test.com",
        "direccion": f"Calle de Prueba #{random.randint(100, 999)}"
    }
    
    response = requests.post(f"{api_url}/propietarios", headers=headers, json=propietario_data)
    assert response.status_code == 201
    propietario_id = response.json()["id"]
    
    yield propietario_id
    
    # Cleanup: eliminar el propietario después de la prueba
    try:
        requests.delete(f"{api_url}/propietarios/{propietario_id}", headers=headers)
    except:
        pass  # Si falla la eliminación, continuamos

@pytest.fixture(scope="function")
def crear_inmueble_temporal(api_url, headers, crear_propietario_temporal):
    """
    Fixture para crear un inmueble temporal y limpiarlo después de la prueba.
    """
    import random
    import time
    
    timestamp = int(time.time())
    random_id = random.randint(1000, 9999)
    
    import random
    offset = random.uniform(0.001, 0.09)
    inmueble_data = {
        "propietario_id": crear_propietario_temporal,
        "direccion": f"Calle de Prueba #{random_id}",
        "sector": "06",
        "manzana": "049",
        "parcela": f"{random.randint(100, 999)}",  # Parcela de 3 dígitos
        "tenencia": "propio",
        "area_terreno_m2": 150.50,
        "valor_unit_terreno": 24500.00,  # Valor unitario del terreno (debe venir de configuración)
        "area_construccion_m2": 120.00,
        "valor_unit_construccion": 85400.00,  # Valor unitario de construcción
        "geom": {  # Cambiado de geometry a geom según el schema del backend
            "type": "Polygon",
            "coordinates": [[
                [-72.3456 + offset, 8.1234 + offset],
                [-72.3457 + offset, 8.1234 + offset],
                [-72.3457 + offset, 8.1235 + offset],
                [-72.3456 + offset, 8.1234 + offset]
            ]]
        }
    }
    
    response = requests.post(f"{api_url}/inmuebles", headers=headers, json=inmueble_data)
    
    # Si falla, imprimir error para debugging
    if response.status_code != 201:
        print(f"Error creando inmueble: {response.status_code}")
        print(f"Response: {response.text}")
    
    assert response.status_code == 201
    inmueble_id = response.json()["id"]
    
    yield inmueble_id
    
    # Cleanup: eliminar el inmueble después de la prueba
    try:
        requests.delete(f"{api_url}/inmuebles/{inmueble_id}", headers=headers)
    except:
        pass  # Si falla la eliminación, continuamos

@pytest.fixture(scope="function", autouse=True)
def cleanup_database(api_url, headers):
    """
    Fixture automático para limpiar datos de prueba después de cada test.
    Elimina propietarios creados durante las pruebas con cédulas de prueba.
    """
    yield
    
    try:
        # Eliminar propietarios de prueba (cedula que empieza con V-99 o contiene 'PruebaE2E')
        response = requests.get(f"{api_url}/propietarios", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if "resultados" in data:
                for prop in data["resultados"]:
                    cedula = prop.get("cedula_rif", "")
                    nombre = prop.get("nombre", "")
                    if cedula.startswith("V-99") or "PruebaE2E" in nombre:
                        try:
                            requests.delete(f"{api_url}/propietarios/{prop['id']}", headers=headers)
                        except:
                            pass  # No fallar el test si el cleanup falla
    except:
        pass  # No fallar el test si el cleanup falla
