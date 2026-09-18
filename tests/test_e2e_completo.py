"""
Prueba E2E completa que simula el flujo real de uso del sistema
"""
import pytest
import requests
import uuid


class TestFlujoCompleto:
    """Prueba el flujo completo de registro de un inmueble"""
    
    def test_flujo_registro_completo(self, api_url, headers):
        """
        Flujo completo: Crear propietario → Crear inmueble → Agregar hitos → Generar cédula
        """
        # 1. Verificar configuración del sistema
        response_config = requests.get(f"{api_url}/configuracion/catastral", headers=headers)
        assert response_config.status_code == 200
        config = response_config.json()
        print(f"✅ Configuración verificada: Estado {config['codigo_estado']}, Municipio {config['codigo_municipio']}")
        
        # 2. Crear propietario
        cedula_unica = f"V-{uuid.uuid4().int % 100000000:08d}"
        propietario_data = {
            "cedula_rif": cedula_unica,
            "nombre": "Carlos",
            "apellido": "Rodríguez",
            "telefono": "0414-5555555",
            "email": f"carlos.rodriguez{uuid.uuid4().int}@test.com",
            "direccion": "Avenida Principal #456"
        }
        
        response_prop = requests.post(f"{api_url}/propietarios", headers=headers, json=propietario_data)
        assert response_prop.status_code == 201
        propietario_id = response_prop.json()["id"]
        print(f"✅ Propietario creado: {propietario_id}")
        
        try:
            # 3. Crear inmueble
            import random
            offset = random.uniform(0.001, 0.09)
            
            inmueble_data = {
                "propietario_id": propietario_id,
                "direccion": "Calle Flujo Completo #789",
                "sector": "06",
                "manzana": "050",
                "parcela": f"{random.randint(100, 999)}",
                "tenencia": "propio",
                "area_terreno_m2": 180.00,
                "area_construccion_m2": 130.00,
                "geom": {  # Cambiado de geometry a geom según el schema del backend
                    "type": "Polygon",
                    "coordinates": [[
                        [-72.3462 + offset, 8.1240 + offset],
                        [-72.3463 + offset, 8.1240 + offset],
                        [-72.3463 + offset, 8.1241 + offset],
                        [-72.3462 + offset, 8.1240 + offset]
                    ]]
                }
            }
            
            response_inm = requests.post(f"{api_url}/inmuebles", headers=headers, json=inmueble_data)
            assert response_inm.status_code == 201
            inmueble_data_resp = response_inm.json()
            inmueble_id = inmueble_data_resp["id"]
            codigo_catastral = inmueble_data_resp["codigo_catastral"]
            print(f"✅ Inmueble creado: {codigo_catastral}")
            
            # 4. Verificar código catastral generado
            assert codigo_catastral is not None
            assert len(codigo_catastral) == 23
            print(f"✅ Código catastral válido: {codigo_catastral}")
            
            # 5. Agregar hitos prediales
            hito_data = {
                "indice_vertice": 1,
                "descripcion": "Vértice Noroeste",
                "lat": 8.1240,
                "lon": -72.3462,
                "utm_norte": 1126000.00,
                "utm_este": 526000.00
            }
            
            response_hito = requests.post(f"{api_url}/inmuebles/{inmueble_id}/hitos", 
                                         headers=headers, json=hito_data)
            assert response_hito.status_code == 201
            print(f"✅ Hito predial agregado")
            
            # 6. Agregar foto
            foto_data = {
                "url": "https://example.com/foto_inmueble.jpg",
                "descripcion": "Foto frontal del inmueble"
            }
            
            response_foto = requests.post(f"{api_url}/inmuebles/{inmueble_id}/fotos", 
                                         headers=headers, json=foto_data)
            assert response_foto.status_code == 201
            print(f"✅ Foto agregada")
            
            # 7. Obtener datos para cédula catastral
            response_cedula = requests.get(f"{api_url}/inmuebles/{inmueble_id}/cedula-datos", 
                                          headers=headers)
            assert response_cedula.status_code == 200
            cedula_data = response_cedula.json()
            assert cedula_data["codigo_catastral"] == codigo_catastral
            print(f"✅ Datos de cédula obtenidos")
            
            # 8. Verificar que el inmueble aparece en el listado
            response_list = requests.get(f"{api_url}/inmuebles", headers=headers)
            assert response_list.status_code == 200
            inmuebles = response_list.json()["resultados"]
            assert any(inm["id"] == inmueble_id for inm in inmuebles)
            print(f"✅ Inmueble aparece en el listado general")
            
            # 9. Verificar que el inmueble aparece en el mapa
            response_mapa = requests.get(f"{api_url}/catastro/mapa", headers=headers)
            assert response_mapa.status_code == 200
            mapa_data = response_mapa.json()
            assert any(feature["properties"]["id"] == str(inmueble_id) for feature in mapa_data["features"])
            print(f"✅ Inmueble aparece en el mapa catastral")
            
            print(f"🎉 Flujo completo ejecutado exitosamente")
            
        finally:
            # Cleanup: eliminar inmueble y propietario
            try:
                requests.delete(f"{api_url}/inmuebles/{inmueble_id}", headers=headers)
                print(f"🧹 Inmueble eliminado (cleanup)")
            except:
                pass
            
            try:
                requests.delete(f"{api_url}/propietarios/{propietario_id}", headers=headers)
                print(f"🧹 Propietario eliminado (cleanup)")
            except:
                pass
    
    def test_flujo_consulta_busqueda(self, api_url, headers):
        """
        Flujo de consulta y búsqueda: Listar → Filtrar → Buscar → Ver detalles
        """
        # 1. Listar inmuebles sin filtros
        response = requests.get(f"{api_url}/inmuebles", headers=headers)
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Listado general: {data['total']} inmuebles")
        
        # 2. Aplicar filtro por sector
        response_sector = requests.get(f"{api_url}/inmuebles?sector=06", headers=headers)
        assert response_sector.status_code == 200
        print(f"✅ Filtro por sector aplicado")
        
        # 3. Aplicar filtro por tenencia
        response_tenencia = requests.get(f"{api_url}/inmuebles?tenencia=propio", headers=headers)
        assert response_tenencia.status_code == 200
        print(f"✅ Filtro por tenencia aplicado")
        
        # 4. Búsqueda por texto
        response_busqueda = requests.get(f"{api_url}/inmuebles?q=calle", headers=headers)
        assert response_busqueda.status_code == 200
        print(f"✅ Búsqueda por texto ejecutada")
        
        # 5. Obtener estadísticas
        response_stats = requests.get(f"{api_url}/catastro/estadisticas", headers=headers)
        assert response_stats.status_code == 200
        stats = response_stats.json()
        print(f"✅ Estadísticas obtenidas: {stats['total_predios']} inmuebles, "
              f"Superficie total: {stats['superficie_total_m2']} m²")
        
        print(f"🎉 Flujo de consulta y búsqueda completado")
