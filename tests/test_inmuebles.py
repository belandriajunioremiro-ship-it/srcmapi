"""
Pruebas E2E para endpoints de inmuebles
"""
import pytest
import requests


class TestInmuebles:
    """Pruebas para gestión de inmuebles catastrales"""
    
    def test_crear_inmueble(self, api_url, headers, crear_propietario_temporal):
        """
        IN-001: Crear inmueble
        Verificar que se puede crear un nuevo inmueble catastral
        """
        import random
        offset = random.uniform(0.001, 0.09)
        
        inmueble_data = {
            "propietario_id": crear_propietario_temporal,
            "direccion": "Calle de Prueba Inmueble #789",
            "sector": "06",
            "manzana": "049",
            "parcela": f"{random.randint(100, 999)}",  # Parcela de 3 dígitos
            "tenencia": "propio",
            "area_terreno_m2": 200.00,
            "valor_unit_terreno": 24500.00,  # Valor unitario del terreno
            "area_construccion_m2": 150.00,
            "valor_unit_construccion": 85400.00,  # Valor unitario de construcción
            "geom": {  # Cambiado de geometry a geom según el schema del backend
                "type": "Polygon",
                "coordinates": [[
                    [-72.3459 + offset, 8.1237 + offset],
                    [-72.3460 + offset, 8.1237 + offset],
                    [-72.3460 + offset, 8.1238 + offset],
                    [-72.3459 + offset, 8.1237 + offset]
                ]]
            }
        }
        
        response = requests.post(f"{api_url}/inmuebles", headers=headers, json=inmueble_data)
        
        # Si falla, imprimir error para debugging
        if response.status_code != 201:
            print(f"Error creando inmueble: {response.status_code}")
            print(f"Response: {response.text}")
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert "codigo_catastral" in data
        assert data["direccion"] == "Calle de Prueba Inmueble #789"
        assert "valor_catastral_total" in data
        
        # Cleanup
        inmueble_id = data["id"]
        requests.delete(f"{api_url}/inmuebles/{inmueble_id}", headers=headers)
    
    def test_listar_inmuebles(self, api_url, headers):
        """
        IN-002: Listar inmuebles
        Verificar que se pueden listar inmuebles con paginación y filtros
        """
        response = requests.get(f"{api_url}/inmuebles", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "resultados" in data
        assert "total" in data
        assert "pagina" in data
        assert isinstance(data["resultados"], list)
    
    def test_listar_inmuebles_con_filtros(self, api_url, headers):
        """
        IN-002: Listar inmuebles con filtros
        Verificar que funcionan los filtros de búsqueda
        """
        # Filtro por sector
        response = requests.get(f"{api_url}/inmuebles?sector=06", headers=headers)
        assert response.status_code == 200
        
        # Filtro por tenencia
        response = requests.get(f"{api_url}/inmuebles?tenencia=propio", headers=headers)
        assert response.status_code == 200
        
        # Búsqueda por texto
        response = requests.get(f"{api_url}/inmuebles?q=prueba", headers=headers)
        assert response.status_code == 200
    
    def test_obtener_inmueble_por_id(self, api_url, headers, crear_inmueble_temporal):
        """
        IN-003: Obtener inmueble por ID
        Verificar que se pueden obtener detalles completos de un inmueble
        """
        response = requests.get(f"{api_url}/inmuebles/{crear_inmueble_temporal}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "codigo_catastral" in data
        assert "direccion" in data
        assert "geom" in data
        assert "valor_catastral_total" in data
    
    def test_actualizar_inmueble(self, api_url, headers, crear_inmueble_temporal):
        """
        IN-004: Actualizar inmueble
        Verificar que se pueden actualizar datos de inmueble
        """
        update_data = {
            "direccion": "Calle Actualizada #999",
            "area_terreno_m2": 250.00
        }
        
        response = requests.patch(f"{api_url}/inmuebles/{crear_inmueble_temporal}", 
                                 headers=headers, json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["direccion"] == "Calle Actualizada #999"
        assert data["area_terreno_m2"] == 250.00
    
    def test_obtener_datos_cedula(self, api_url, headers, crear_inmueble_temporal):
        """
        IN-007: Obtener datos para cédula
        Verificar que se obtienen todos los datos necesarios para generar PDF
        """
        response = requests.get(f"{api_url}/inmuebles/{crear_inmueble_temporal}/cedula-datos", 
                              headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "inmueble_id" in data
        assert "codigo_catastral" in data
        assert "direccion" in data
        assert "propietario_nombre" in data
    
    def test_agregar_hito_predial(self, api_url, headers, crear_inmueble_temporal):
        """
        IN-011: Agregar hito predial
        Verificar que se pueden agregar vértices GPS al polígono
        """
        hito_data = {
            "indice_vertice": 1,
            "descripcion": "Vértice de prueba",
            "lat": 8.1234,
            "lon": -72.3456,
            "utm_norte": 1125000.00,
            "utm_este": 525000.00
        }
        
        response = requests.post(f"{api_url}/inmuebles/{crear_inmueble_temporal}/hitos", 
                               headers=headers, json=hito_data)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["indice_vertice"] == 1
        assert data["descripcion"] == "Vértice de prueba"
    
    def test_listar_hitos(self, api_url, headers, crear_inmueble_temporal):
        """
        IN-012: Listar hitos de inmueble
        Verificar que se pueden listar todos los hitos de un inmueble
        """
        response = requests.get(f"{api_url}/inmuebles/{crear_inmueble_temporal}/hitos", 
                              headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_agregar_foto(self, api_url, headers, crear_inmueble_temporal):
        """
        IN-008: Agregar foto a inmueble
        Verificar que se puede registrar la URL de una foto
        """
        foto_data = {
            "url": "https://example.com/foto_prueba.jpg",
            "descripcion": "Foto de prueba"
        }
        
        response = requests.post(f"{api_url}/inmuebles/{crear_inmueble_temporal}/fotos", 
                               headers=headers, json=foto_data)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["url"] == "https://example.com/foto_prueba.jpg"
    
    def test_listar_fotos(self, api_url, headers, crear_inmueble_temporal):
        """
        IN-009: Listar fotos de inmueble
        Verificar que se pueden listar todas las fotos de un inmueble
        """
        response = requests.get(f"{api_url}/inmuebles/{crear_inmueble_temporal}/fotos", 
                              headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
