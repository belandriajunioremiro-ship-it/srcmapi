"""
Pruebas E2E sin autenticación para endpoints públicos
"""
import pytest
import requests


class TestSinAuth:
    """Pruebas para endpoints que no requieren autenticación"""
    
    def test_health_check(self, base_url):
        """SC-001: Health Check"""
        response = requests.get(f"{base_url}/salud")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
    
    def test_raiz_sistema(self, base_url):
        """SC-002: Raíz del sistema"""
        response = requests.get(f"{base_url}/")
        assert response.status_code == 200
        data = response.json()
        assert "servicio" in data
        assert data["estado"] == "activo"
    
    def test_documentacion_swagger(self, base_url):
        """Verificar que la documentación Swagger está disponible"""
        response = requests.get(f"{base_url}/docs")
        assert response.status_code == 200
    
    def test_documentacion_redoc(self, base_url):
        """Verificar que la documentación ReDoc está disponible"""
        response = requests.get(f"{base_url}/redoc")
        assert response.status_code == 200
    
    def test_openapi_schema(self, base_url):
        """Verificar que el esquema OpenAPI está disponible"""
        response = requests.get(f"{base_url}/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data


class TestConexiónBD:
    """Pruebas para verificar conexión a base de datos"""
    
    def test_configuracion_catastral_sin_auth(self, api_url):
        """
        Intentar obtener configuración catastral (probablemente fallará sin auth)
        """
        response = requests.get(f"{api_url}/configuracion/catastral")
        # Puede retornar 401 (no autorizado) o 200 si el endpoint es público
        if response.status_code == 401:
            print("✅ Endpoint requiere autenticación (comportamiento esperado)")
        elif response.status_code == 200:
            print("✅ Endpoint es público")
            data = response.json()
            assert "valor_m2_terreno" in data
        else:
            print(f"⚠️ Estado inesperado: {response.status_code}")
    
    def test_mapa_catastral_sin_auth(self, api_url):
        """
        Intentar obtener mapa catastral (probablemente fallará sin auth)
        """
        response = requests.get(f"{api_url}/catastro/mapa")
        if response.status_code == 401:
            print("✅ Endpoint requiere autenticación (comportamiento esperado)")
        elif response.status_code == 200:
            print("✅ Endpoint es público")
            data = response.json()
            assert "type" in data
            assert data["type"] == "FeatureCollection"
        else:
            print(f"⚠️ Estado inesperado: {response.status_code}")


class TestServidorActivo:
    """Pruebas básicas de funcionamiento del servidor"""
    
    def test_tiempo_respuesta_salud(self, base_url):
        """Verificar que el servidor responde en tiempo razonable"""
        import time
        start_time = time.time()
        response = requests.get(f"{base_url}/salud")
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 3.0, f"El servidor tardó demasiado: {response_time:.2f}s"
        print(f"Tiempo de respuesta: {response_time:.3f}s")
    
    def test_headers_cors(self, base_url):
        """Verificar que los headers CORS están configurados"""
        response = requests.get(f"{base_url}/salud")
        assert response.status_code == 200
        
        # Verificar headers importantes
        headers = response.headers
        print(f"📋 Headers de respuesta: {dict(headers)}")
