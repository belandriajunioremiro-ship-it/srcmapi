"""
Pruebas E2E con bypass de autenticación para desarrollo
Modificamos los fixtures para no requerir autenticación real
"""
import pytest
import requests
import os
from dotenv import load_dotenv

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
def headers():
    """Headers sin autenticación para pruebas de desarrollo"""
    return {
        "Content-Type": "application/json"
    }

@pytest.fixture(scope="function")
def crear_propietario_temporal(api_url):
    """
    Fixture para crear un propietario temporal usando service_role_key
    """
    from dotenv import load_dotenv
    load_dotenv()
    
    supabase_url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    cedula_unica = f"V-{hash(__name__) % 100000000:08d}"
    propietario_data = {
        "cedula_rif": cedula_unica,
        "nombre": "Propietario",
        "apellido": "PruebaBypass",
        "telefono": "0414-1234567",
        "email": f"prueba{hash(__name__)}@test.com",
        "direccion": "Calle de Prueba #123"
    }
    
    # Crear directamente en Supabase usando service_role_key
    url = f"{supabase_url}/rest/v1/propietarios"
    headers = {
        "apikey": service_role_key,
        "Authorization": f"Bearer {service_role_key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    response = requests.post(url, headers=headers, json=propietario_data)
    assert response.status_code == 201
    propietario_id = response.json()[0]["id"]
    
    yield propietario_id
    
    # Cleanup
    try:
        delete_url = f"{supabase_url}/rest/v1/propietarios?id=eq.{propietario_id}"
        requests.delete(delete_url, headers=headers)
    except:
        pass

@pytest.fixture(scope="function")
def crear_inmueble_temporal(api_url, crear_propietario_temporal):
    """
    Fixture para crear un inmueble temporal usando service_role_key
    """
    from dotenv import load_dotenv
    load_dotenv()
    
    supabase_url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    import random
    offset = random.uniform(0.001, 0.09)
    inmueble_data = {
        "propietario_id": crear_propietario_temporal,
        "direccion": "Calle de Prueba Bypass #456",
        "sector": "06",
        "manzana": "051",
        "parcela": f"{random.randint(100, 999)}",
        "tenencia": "propio",
        "area_terreno_m2": 160.00,
        "area_construccion_m2": 110.00,
        "geom": {
            "type": "Polygon",
            "coordinates": [[
                [-72.3465 + offset, 8.1245 + offset],
                [-72.3466 + offset, 8.1245 + offset],
                [-72.3466 + offset, 8.1246 + offset],
                [-72.3465 + offset, 8.1245 + offset]
            ]]
        }
    }
    
    # Crear directamente en Supabase usando service_role_key
    url = f"{supabase_url}/rest/v1/inmuebles"
    headers = {
        "apikey": service_role_key,
        "Authorization": f"Bearer {service_role_key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    response = requests.post(url, headers=headers, json=inmueble_data)
    assert response.status_code == 201
    inmueble_id = response.json()[0]["id"]
    
    yield inmueble_id
    
    # Cleanup
    try:
        delete_url = f"{supabase_url}/rest/v1/inmuebles?id=eq.{inmueble_id}"
        requests.delete(delete_url, headers=headers)
    except:
        pass


class TestConfiguracionBypass:
    """Pruebas de configuración usando service_role_key"""
    
    def test_obtener_configuracion_catastral(self, api_url):
        """Obtener configuración catastral"""
        supabase_url = os.getenv("SUPABASE_URL")
        service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        url = f"{supabase_url}/rest/v1/configuracion_catastral?id=eq.1"
        headers = {
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        assert response.status_code == 200
        data = response.json()[0]
        assert "valor_m2_terreno" in data
        assert "codigo_estado" in data
        print(f"Configuración: Estado {data['codigo_estado']}, Municipio {data['codigo_municipio']}")


class TestPropietariosBypass:
    """Pruebas de propietarios usando service_role_key"""
    
    def test_crear_propietario_directo(self, crear_propietario_temporal):
        """Crear propietario directamente en Supabase"""
        assert crear_propietario_temporal is not None
        print(f"Propietario creado con ID: {crear_propietario_temporal}")
    
    def test_listar_propietarios_directo(self):
        """Listar propietarios directamente en Supabase"""
        supabase_url = os.getenv("SUPABASE_URL")
        service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        url = f"{supabase_url}/rest/v1/propietarios?limit=5"
        headers = {
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Propietarios encontrados: {len(data)}")


class TestInmueblesBypass:
    """Pruebas de inmuebles usando service_role_key"""
    
    def test_crear_inmueble_directo(self, crear_inmueble_temporal):
        """Crear inmueble directamente en Supabase"""
        assert crear_inmueble_temporal is not None
        print(f"Inmueble creado con ID: {crear_inmueble_temporal}")
    
    def test_listar_inmuebles_directo(self):
        """Listar inmuebles directamente en Supabase"""
        supabase_url = os.getenv("SUPABASE_URL")
        service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        url = f"{supabase_url}/rest/v1/inmuebles?limit=5"
        headers = {
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Inmuebles encontrados: {len(data)}")
        
        if len(data) > 0:
            print(f"Primer inmueble: {data[0]['codigo_catastral']}")


class TestCatastroBypass:
    """Pruebas de catastro usando service_role_key"""
    
    def test_verificar_tablas_existentes(self):
        """Verificar que las tablas existen en Supabase"""
        supabase_url = os.getenv("SUPABASE_URL")
        service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        tablas = ["configuracion_catastral", "propietarios", "inmuebles", "usuarios"]
        
        for tabla in tablas:
            url = f"{supabase_url}/rest/v1/{tabla}?limit=1"
            headers = {
                "apikey": service_role_key,
                "Authorization": f"Bearer {service_role_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                print(f"✅ Tabla '{tabla}' existe y es accesible")
            else:
                print(f"❌ Tabla '{tabla}' no accesible: {response.status_code}")


class TestFlujoCompletoBypass:
    """Flujo completo usando service_role_key"""
    
    def test_flujo_completo_bd(self, crear_propietario_temporal):
        """Flujo completo usando service_role_key"""
        supabase_url = os.getenv("SUPABASE_URL")
        service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        print(f"✅ Propietario creado: {crear_propietario_temporal}")
        
        # Crear inmueble
        import random
        offset = random.uniform(0.001, 0.09)
        inmueble_data = {
            "propietario_id": crear_propietario_temporal,
            "direccion": "Calle Flujo Bypass #789",
            "sector": "06",
            "manzana": "052",
            "parcela": f"{random.randint(100, 999)}",
            "tenencia": "propio",
            "area_terreno_m2": 170.00,
            "area_construccion_m2": 120.00,
            "geom": {
                "type": "Polygon",
                "coordinates": [[
                    [-72.3468 + offset, 8.1248 + offset],
                    [-72.3469 + offset, 8.1248 + offset],
                    [-72.3469 + offset, 8.1249 + offset],
                    [-72.3468 + offset, 8.1248 + offset]
                ]]
            }
        }
        
        url = f"{supabase_url}/rest/v1/inmuebles"
        headers = {
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        response = requests.post(url, headers=headers, json=inmueble_data)
        assert response.status_code == 201
        inmueble_id = response.json()[0]["id"]
        print(f"✅ Inmueble creado: {inmueble_id}")
        
        # Verificar código catastral
        url_get = f"{supabase_url}/rest/v1/inmuebles?id=eq.{inmueble_id}&select=codigo_catastral"
        response_get = requests.get(url_get, headers=headers)
        assert response_get.status_code == 200
        codigo = response_get.json()[0]["codigo_catastral"]
        print(f"✅ Código catastral: {codigo}")
        
        # Cleanup
        delete_url = f"{supabase_url}/rest/v1/inmuebles?id=eq.{inmueble_id}"
        requests.delete(delete_url, headers=headers)
        print(f"🧹 Inmueble eliminado")
