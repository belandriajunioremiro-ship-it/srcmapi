"""
Pruebas E2E para endpoints de propietarios
"""
import pytest
import requests


class TestPropietarios:
    """Pruebas para gestión de propietarios"""
    
    def test_crear_propietario(self, api_url, headers):
        """
        PR-001: Crear propietario
        Verificar que se puede registrar un nuevo propietario con datos aleatorios
        """
        import random
        import time
        
        timestamp = int(time.time())
        random_num = random.randint(10000000, 99999999)
        
        propietario_data = {
            "cedula_rif": f"V-{random_num}",
            "nombre": f"Juan{timestamp}",
            "apellido": f"PruebaE2E{random_num}",
            "telefono": f"0414-{random.randint(1000000, 9999999)}",
            "email": f"juan.pruebae2e{timestamp}@test.com",
            "direccion": f"Calle de Prueba E2E #{random.randint(100, 999)}"
        }
        
        response = requests.post(f"{api_url}/propietarios", headers=headers, json=propietario_data)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["cedula_rif"] == propietario_data["cedula_rif"]
        assert data["nombre"] == propietario_data["nombre"]
        
        # Cleanup
        propietario_id = data["id"]
        requests.delete(f"{api_url}/propietarios/{propietario_id}", headers=headers)
    
    def test_listar_propietarios(self, api_url, headers):
        """
        PR-002: Listar propietarios
        Verificar que se pueden listar propietarios con paginación
        """
        response = requests.get(f"{api_url}/propietarios", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "resultados" in data
        assert "total" in data
        assert "pagina" in data
        assert isinstance(data["resultados"], list)
    
    def test_obtener_propietario_por_id(self, api_url, headers, crear_propietario_temporal):
        """
        PR-003: Obtener propietario por ID
        Verificar que se pueden obtener detalles de un propietario
        """
        response = requests.get(f"{api_url}/propietarios/{crear_propietario_temporal}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "cedula_rif" in data
        assert "nombre" in data
        assert "apellido" in data
    
    def test_actualizar_propietario(self, api_url, headers, crear_propietario_temporal):
        """
        PR-004: Actualizar propietario
        Verificar que se pueden actualizar datos de propietario
        """
        update_data = {
            "telefono": "0424-1111111",
            "email": "nuevo.email@test.com"
        }
        
        response = requests.patch(f"{api_url}/propietarios/{crear_propietario_temporal}", 
                                 headers=headers, json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["telefono"] == "0424-1111111"
        assert data["email"] == "nuevo.email@test.com"
    
    def test_listar_inmuebles_propietario(self, api_url, headers, crear_propietario_temporal):
        """
        PR-006: Listar inmuebles de propietario
        Verificar que se pueden obtener inmuebles asociados a un propietario
        """
        response = requests.get(f"{api_url}/propietarios/{crear_propietario_temporal}/inmuebles", 
                              headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Validar estructura paginada en lugar de lista simple
        assert "resultados" in data
        assert "total" in data
        assert "pagina" in data
        assert isinstance(data["resultados"], list)
        assert isinstance(data["total"], int)
        assert isinstance(data["pagina"], int)
