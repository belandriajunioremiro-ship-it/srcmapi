"""
Pruebas E2E para endpoints de configuración catastral
"""
import pytest
import requests


class TestConfiguracionCatastral:
    """Pruebas para configuración catastral"""
    
    def test_obtener_configuracion_catastral(self, api_url, headers):
        """
        CC-001: Obtener configuración catastral
        Verificar que se obtienen los valores catastrales actuales
        """
        response = requests.get(f"{api_url}/configuracion/catastral", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "valor_m2_terreno" in data
        assert "valor_m2_construccion" in data
        assert "valor_m2_comercio" in data
        assert "vigencia_cedula_meses" in data
        assert "codigo_estado" in data
        assert "codigo_municipio" in data
        assert "codigo_parroquia" in data
    
    def test_obtener_configuracion_sistema(self, api_url, headers):
        """
        CC-003: Obtener configuración del sistema
        Verificar configuración de validación de códigos
        """
        response = requests.get(f"{api_url}/configuracion/sistema", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "estado_codigo" in data
        assert "municipio_codigo" in data
        assert "parroquia_codigo" in data
        assert "nombre_municipio" in data
    
    def test_obtener_configuracion_pdf(self, api_url, headers):
        """
        CC-005: Obtener configuración para PDF
        Verificar datos institucionales para cédulas
        """
        response = requests.get(f"{api_url}/configuracion/catastral/pdf-config", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "rif_alcaldia" in data
        assert "direccion_institucional" in data
        assert "nombre_maxima_autoridad" in data
        assert "cargo_maxima_autoridad" in data
        assert "notas_legales" in data
    
    def test_actualizar_configuracion_catastral(self, api_url, admin_headers):
        """
        CC-002: Actualizar configuración catastral
        Verificar que se pueden actualizar los valores catastrales
        Requiere rol de administrador.
        """
        # Obtener configuración actual
        response_get = requests.get(f"{api_url}/configuracion/catastral", headers=admin_headers)
        valor_original = response_get.json()["valor_m2_terreno"]
        
        # Convertir a float para operaciones matemáticas
        valor_original_float = float(valor_original)
        
        # Actualizar con un valor temporal
        nuevo_valor = valor_original_float + 100
        update_data = {"valor_m2_terreno": nuevo_valor}
        
        response = requests.patch(f"{api_url}/configuracion/catastral", headers=admin_headers, json=update_data)
        assert response.status_code == 200
        
        # Verificar que se actualizó
        response_verify = requests.get(f"{api_url}/configuracion/catastral", headers=admin_headers)
        valor_actualizado = float(response_verify.json()["valor_m2_terreno"])
        assert valor_actualizado == nuevo_valor
        
        # Restaurar valor original
        restore_data = {"valor_m2_terreno": valor_original}
        requests.patch(f"{api_url}/configuracion/catastral", headers=admin_headers, json=restore_data)
