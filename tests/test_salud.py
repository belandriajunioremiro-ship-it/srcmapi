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
        SC-002: Raíz del sistema
        Verificar información básica del servicio
        """
        response = requests.get(f"{base_url}/")
        assert response.status_code == 200
        data = response.json()
        assert "servicio" in data
        assert "estado" in data
        assert "documentacion" in data
        assert data["estado"] == "activo"
