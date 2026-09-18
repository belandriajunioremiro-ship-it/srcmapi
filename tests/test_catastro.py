"""
Pruebas E2E para endpoints de catastro geoespacial
"""
import pytest
import requests


class TestCatastro:
    """Pruebas para funcionalidades geoespaciales y catastro"""
    
    def test_obtener_mapa_catastral(self, api_url, headers):
        """
        CA-001: Obtener mapa catastral
        Verificar que se obtiene el GeoJSON de todos los predios
        """
        response = requests.get(f"{api_url}/catastro/mapa", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "type" in data
        assert "features" in data
        assert data["type"] == "FeatureCollection"
        assert isinstance(data["features"], list)
    
    def test_obtener_estadisticas(self, api_url, headers):
        """
        CA-002: Obtener estadísticas generales
        Verificar que se obtienen estadísticas del catastro
        """
        response = requests.get(f"{api_url}/catastro/estadisticas", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_predios" in data  # Corregido: total_inmuebles → total_predios
        assert "superficie_total_m2" in data  # Corregido: area_total_terreno_m2 → superficie_total_m2
        assert "valor_catastral_total" in data  # Corregido: valor_total_catastral → valor_catastral_total
    
    def test_obtener_predios_por_sector(self, api_url, headers):
        """
        CA-003: Obtener predios por sector
        Verificar que se pueden agrupar inmuebles por sector
        """
        response = requests.get(f"{api_url}/catastro/por-sector", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Verificar que cada elemento tiene estructura correcta
        if len(data) > 0:
            assert "sector" in data[0]
            assert "total_predios" in data[0]
    
    def test_auditoria_solapamientos(self, api_url, admin_headers):
        """
        CA-004: Auditoría de solapamientos
        Verificar que se pueden detectar polígonos solapados
        Requiere rol de administrador.
        """
        response = requests.get(f"{api_url}/catastro/solapamientos", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "solapamientos" in data
        assert isinstance(data["solapamientos"], list)
    
    def test_listar_sectores(self, api_url, headers):
        """
        CA-005: Listar sectores disponibles
        Verificar que se obtiene la lista de sectores
        """
        response = requests.get(f"{api_url}/catastro/sectores", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
