"""
Pruebas E2E para endpoints de salud (Health Check)
"""
import pytest
import requests


class TestSalud:
    """Pruebas para endpoints de salud del sistema"""
    
    def test_health_check(self, base_url):
        """
        SC-001: Health Check
        Verificar que el servidor está activo
        """
        response = requests.get(f"{base_url}/salud")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
    
    def test_raiz_sistema(self, base_url):
        """
        SLD-002: Verificar endpoint raíz
        Verifica que la raíz redirige o da un mensaje de bienvenida (HTML)
        """
        response = requests.get(f"{base_url}/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "SRCM" in response.text or "Catastral" in response.text
