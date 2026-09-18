import pytest
import requests
import random
import time
import uuid

def print_title(title):
    print(f"\n{'-'*70}")
    print(f" {title.upper()} ".center(70, '-'))
    print(f"{'-'*70}")

def print_ok(method, endpoint):
    """Formatea la salida para que se vea alineada en consola Windows."""
    text = f"  {method:<6} {endpoint} "
    # Rellena con puntos hasta los 58 caracteres y añade [ OK ]
    print(f"{text:.<58} [ OK ]")

class TestFlujoDefinitivo:
    """
    Prueba maestra E2E: Ejecuta un flujo secuencial masivo visual,
    tocando todas las tablas y los ~35 endpoints del sistema SRCM.
    """

    def test_prueba_maestra_sistema_completo(self, api_url, headers):
        print("\n\n" + "="*70)
        print(" INICIANDO PRUEBA MAESTRA SRCM: 35 ENDPOINTS ".center(70, "="))
        print("="*70)

        # ---------------------------------------------------------
        # 1. CONFIGURACIÓN
        # ---------------------------------------------------------
        print_title("1. Modulo de Configuraciones")
        
        resp = requests.get(f"{api_url}/configuracion/catastral", headers=headers)
        assert resp.status_code == 200
        print_ok("GET", "/configuracion/catastral")
        
        old_val = float(resp.json()["valor_m2_terreno"])
        resp = requests.patch(f"{api_url}/configuracion/catastral", headers=headers, json={"valor_m2_terreno": old_val + 1.0})
        assert resp.status_code == 200
        print_ok("PATCH", "/configuracion/catastral")

        resp = requests.get(f"{api_url}/configuracion/catastral/pdf-config", headers=headers)
        assert resp.status_code == 200
        print_ok("GET", "/configuracion/catastral/pdf-config")

        resp = requests.get(f"{api_url}/configuracion/sistema", headers=headers)
        assert resp.status_code == 200
        print_ok("GET", "/configuracion/sistema")

        resp = requests.patch(f"{api_url}/configuracion/sistema", headers=headers, json={"mantenimiento_activo": False})
        assert resp.status_code == 200
        print_ok("PATCH", "/configuracion/sistema")

        # ---------------------------------------------------------
        # 2. USUARIOS
        # ---------------------------------------------------------
        print_title("2. Modulo de Usuarios")
        
        resp = requests.get(f"{api_url}/usuarios/me", headers=headers)
        assert resp.status_code == 200
        print_ok("GET", "/usuarios/me")

        resp = requests.get(f"{api_url}/usuarios", headers=headers)
        assert resp.status_code == 200
        print_ok("GET", "/usuarios")

        # ---------------------------------------------------------
        # 3. PROPIETARIOS
        # ---------------------------------------------------------
        print_title("3. Modulo de Propietarios")
        rnd = random.randint(10000, 99999)
        prop_data = {
            "nacionalidad": "V",
            "cedula_rif": f"{rnd}4453",
            "nombre": "Prueba Maestra",
            "apellido": "Definitiva",
            "telefono": "04141234567",
            "email": f"maestra_{rnd}@test.com",
            "direccion": "Calle Principal SRCM"
        }
        
        resp = requests.post(f"{api_url}/propietarios", headers=headers, json=prop_data)
        assert resp.status_code == 201
        propietario_id = resp.json()["id"]
        print_ok("POST", "/propietarios")

        resp = requests.get(f"{api_url}/propietarios", headers=headers)
        assert resp.status_code == 200
        print_ok("GET", "/propietarios")

        resp = requests.get(f"{api_url}/propietarios/{propietario_id}", headers=headers)
        assert resp.status_code == 200
        print_ok("GET", f"/propietarios/{{id}}")

        resp = requests.patch(f"{api_url}/propietarios/{propietario_id}", headers=headers, json={"telefono": "04240000000"})
        assert resp.status_code == 200
        print_ok("PATCH", f"/propietarios/{{id}}")

        # ---------------------------------------------------------
        # 4. INMUEBLES
        # ---------------------------------------------------------
        print_title("4. Modulo de Inmuebles")
        offset = random.uniform(0.001, 0.09)
        inmueble_data = {
            "propietario_id": propietario_id,
            "direccion": "Calle Flujo Maestro",
            "sector": "06",
            "manzana": "099",
            "parcela": f"{random.randint(100, 999)}",
            "tenencia": "propio",
            "area_terreno_m2": 500.00,
            "area_construccion_m2": 250.00,
            "geom": {
                "type": "Polygon",
                "coordinates": [[
                    [-72.3480 + offset, 8.1250 + offset],
                    [-72.3481 + offset, 8.1250 + offset],
                    [-72.3481 + offset, 8.1251 + offset],
                    [-72.3480 + offset, 8.1250 + offset]
                ]]
            }
        }
        
        resp = requests.post(f"{api_url}/inmuebles", headers=headers, json=inmueble_data)
        assert resp.status_code == 201
        inmueble_id = resp.json()["id"]
        print_ok("POST", "/inmuebles")

        resp = requests.get(f"{api_url}/inmuebles", headers=headers)
        assert resp.status_code == 200
        print_ok("GET", "/inmuebles")

        resp = requests.get(f"{api_url}/inmuebles/{inmueble_id}", headers=headers)
        assert resp.status_code == 200
        print_ok("GET", f"/inmuebles/{{id}}")

        resp = requests.patch(f"{api_url}/inmuebles/{inmueble_id}", headers=headers, json={"existe_vivienda": True})
        assert resp.status_code == 200
        print_ok("PATCH", f"/inmuebles/{{id}}")

        resp = requests.get(f"{api_url}/propietarios/{propietario_id}/inmuebles", headers=headers)
        assert resp.status_code == 200
        print_ok("GET", f"/propietarios/{{id}}/inmuebles")

        # HITOS
        print_title("5. Sub-Entidades (Hitos y Fotos)")
        hito_data = {
            "indice_vertice": 1,
            "descripcion": "Vértice de prueba maestra",
            "lat": 8.1250 + offset,
            "lon": -72.3480 + offset,
            "utm_norte": 1125000.00,
            "utm_este": 525000.00
        }
        resp = requests.post(f"{api_url}/inmuebles/{inmueble_id}/hitos", headers=headers, json=hito_data)
        assert resp.status_code == 201
        hito_id = resp.json()["id"]
        print_ok("POST", f"/inmuebles/{{id}}/hitos")

        resp = requests.get(f"{api_url}/inmuebles/{inmueble_id}/hitos", headers=headers)
        assert resp.status_code == 200
        print_ok("GET", f"/inmuebles/{{id}}/hitos")

        # FOTOS
        foto_data = {
            "url": "https://example.com/foto_prueba.jpg",
            "descripcion": "Fachada de prueba maestra"
        }
        resp = requests.post(f"{api_url}/inmuebles/{inmueble_id}/fotos", headers=headers, json=foto_data)
        assert resp.status_code == 201
        foto_id = resp.json()["id"]
        print_ok("POST", f"/inmuebles/{{id}}/fotos")

        resp = requests.get(f"{api_url}/inmuebles/{inmueble_id}/fotos", headers=headers)
        assert resp.status_code == 200
        print_ok("GET", f"/inmuebles/{{id}}/fotos")

        # CEDULA
        resp = requests.get(f"{api_url}/inmuebles/{inmueble_id}/cedula-datos", headers=headers)
        assert resp.status_code == 200
        print_ok("GET", f"/inmuebles/{{id}}/cedula-datos")

        resp = requests.get(f"{api_url}/inmuebles/{inmueble_id}/cedula", headers=headers)
        assert resp.status_code == 200
        print_ok("GET", f"/inmuebles/{{id}}/cedula")

        # ---------------------------------------------------------
        # 5. CATASTRO Y ESPACIAL
        # ---------------------------------------------------------
        print_title("6. Rutas Catastrales y Analisis Espacial")
        
        resp = requests.get(f"{api_url}/catastro/estadisticas", headers=headers)
        assert resp.status_code == 200
        print_ok("GET", "/catastro/estadisticas")
        
        resp = requests.get(f"{api_url}/catastro/por-sector", headers=headers)
        assert resp.status_code == 200
        print_ok("GET", "/catastro/por-sector")
        
        resp = requests.get(f"{api_url}/catastro/solapamientos", headers=headers)
        assert resp.status_code == 200
        print_ok("GET", "/catastro/solapamientos")

        resp = requests.get(f"{api_url}/catastro/sectores", headers=headers)
        assert resp.status_code == 200
        print_ok("GET", "/catastro/sectores")

        resp = requests.get(f"{api_url}/catastro/mapa", headers=headers)
        assert resp.status_code == 200
        print_ok("GET", "/catastro/mapa")

        # ---------------------------------------------------------
        # 6. LIMPIEZA / ELIMINACIÓN
        # ---------------------------------------------------------
        print_title("7. Limpieza Final y Borrado (Cascada)")
        
        resp = requests.delete(f"{api_url}/inmuebles/{inmueble_id}/fotos/{foto_id}", headers=headers)
        assert resp.status_code == 204
        print_ok("DELETE", f"/inmuebles/{{id}}/fotos/{{foto_id}}")

        resp = requests.delete(f"{api_url}/inmuebles/{inmueble_id}/hitos/{hito_id}", headers=headers)
        assert resp.status_code == 204
        print_ok("DELETE", f"/inmuebles/{{id}}/hitos/{{hito_id}}")

        resp = requests.delete(f"{api_url}/inmuebles/{inmueble_id}", headers=headers)
        assert resp.status_code == 204
        print_ok("DELETE", f"/inmuebles/{{id}}")

        resp = requests.delete(f"{api_url}/propietarios/{propietario_id}", headers=headers)
        assert resp.status_code == 204
        print_ok("DELETE", f"/propietarios/{{id}}")

        print("\n" + "="*70)
        print(" PRUEBA MAESTRA COMPLETADA AL 100% ".center(70, "="))
        print("="*70 + "\n")
