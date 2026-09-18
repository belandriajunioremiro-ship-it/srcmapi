# 🧪 Guía de Pruebas Unitarias (Unit Tests) para SRCM

¡Excelente iniciativa! Las **Pruebas Unitarias** son el siguiente paso lógico para profesionalizar aún más el backend de Catastro. 

## 1. ¿Qué es una Prueba Unitaria vs. Pruebas E2E (Las que ya tienes)?

- **Prueba End-to-End (E2E):** Prueba todo el flujo. Hace una petición HTTP (`requests.post`), pasa por el router de FastAPI, ejecuta la lógica del servicio, inserta en la base de datos real (PostgreSQL), activa los Triggers, y devuelve el JSON. *(Es lenta pero muy segura, toma ~1.5 segundos por test).*
- **Prueba Unitaria (Unit Test):** Prueba **una sola función de Python** de forma aislada. NO se conecta a la base de datos. Si la función necesita consultar la base de datos, usamos un **"Mock"** (un doble de riesgo/simulador) para que la función crea que la base de datos respondió. *(Es extremadamente rápida, toma ~0.001 segundos por test).*

---

## 2. ¿Qué Pruebas Unitarias podemos hacer en SRCM?

En lugar de probar los *endpoints*, vamos a probar los *servicios* y las *utilidades* internas. Aquí tienes los mejores candidatos en tu código:

### A. Pruebas de Servicios Geográficos (`geo_service.py`)
Tu sistema maneja conversiones espaciales. Si algo falla aquí, el sistema colapsa.
- **Test 1:** Validar que la función `wkb_to_geojson` procesa correctamente un binario PostGIS y lo transforma en el diccionario de coordenadas exacto.
- **Test 2:** Comprobar qué pasa si a `wkb_to_geojson` se le pasa un valor nulo (`None`). (Debería retornar `None` sin romper el código).

### B. Pruebas de Seguridad (`security.py`)
- **Test 3:** Probar que la función que decodifica el token de Supabase lance una excepción `HTTPException 401` si el token está expirado.
- **Test 4:** Verificar que lance un error si al token le falta el claim del rol de `administrador`.

### C. Pruebas de Mapeo y Pydantic (`inmueble_mapper.py`)
- **Test 5:** Crear un objeto de base de datos "simulado" (fake) de `Inmueble` y pasarlo por `inmueble_a_out`. Verificar que el formateo del código catastral funcione (por ejemplo, que devuelva `"06-099-123"` en lugar de `"06099123"`).

### D. Pruebas de Servicios de Inmuebles (`inmueble_service.py`) con "Mocks"
- **Test 6:** Probar `obtener_inmueble_por_id`. Simulamos (Mocreamos) la sesión de base de datos para que devuelva un inmueble. Comprobamos que el servicio retorna ese mismo inmueble sin errores.
- **Test 7:** Simulamos que la base de datos devuelve `None` (no se encontró) y comprobamos que el servicio arroje el error `HTTPException 404 Inmueble no encontrado`.

---

## 3. ¿Cómo se vería el Código de estas Pruebas?

Para hacer pruebas unitarias en Python, usamos la misma librería `pytest`, junto con `unittest.mock` (incluida en Python) para simular la base de datos.

### Ejemplo 1: Probando una función pura (Sin BD)
```python
# Archivo: tests/unitarios/test_catastro_codigo.py
from app.utils.catastro_codigo import formatear_codigo_catastral

def test_formatear_codigo_catastral_correcto():
    # Arrange (Preparar datos)
    codigo_crudo = "06099140"
    
    # Act (Ejecutar la función pura)
    resultado = formatear_codigo_catastral(codigo_crudo)
    
    # Assert (Comprobar el resultado)
    assert resultado == "06-099-140"

def test_formatear_codigo_catastral_vacio():
    assert formatear_codigo_catastral(None) is None
```

### Ejemplo 2: Probando un servicio aislando la Base de Datos (Mocks)
```python
# Archivo: tests/unitarios/test_inmueble_service.py
import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from app.services.inmueble_service import obtener_inmueble_por_id
from app.models.inmueble import Inmueble

def test_obtener_inmueble_existente():
    # 1. Creamos un "Doble" (Mock) de la base de datos
    db_mock = MagicMock()
    
    # 2. Simulamos que al hacer ".first()", devuelve un Inmueble válido
    inmueble_falso = Inmueble(id="123", sector="06")
    db_mock.query().filter().first.return_value = inmueble_falso
    
    # 3. Ejecutamos el servicio pasándole la BD falsa
    resultado = obtener_inmueble_por_id(db_mock, "123")
    
    # 4. Verificamos que devolvió el inmueble correctamente
    assert resultado.sector == "06"

def test_obtener_inmueble_no_existe_arroja_404():
    db_mock = MagicMock()
    
    # Simulamos que la BD no encontró nada
    db_mock.query().filter().first.return_value = None
    
    # Verificamos que se levante la excepción HTTP 404
    with pytest.raises(HTTPException) as error_info:
        obtener_inmueble_por_id(db_mock, "123")
        
    assert error_info.value.status_code == 404
    assert error_info.value.detail == "Inmueble no encontrado"
```

## 4. Conclusión y Beneficios para el SRCM

Si agregamos unas 30 pruebas unitarias como las de arriba:
1. **Velocidad:** Las 30 pruebas se ejecutarán en **0.1 segundos**.
2. **Casos Extremos (Edge Cases):** Podremos probar qué pasa si un usuario envía coordenadas en Rusia (fuera del Municipio Torbes), sin ensuciar la base de datos real con registros basura.
3. **Mantenimiento:** Si mañana cambias la fórmula de depreciación del inmueble o el cálculo del valor catastral en Python, la prueba unitaria te avisará inmediatamente si el cálculo falló en un centavo, sin necesidad de levantar el servidor.
