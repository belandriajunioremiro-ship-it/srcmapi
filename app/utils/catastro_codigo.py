"""
Espejo en Python de la función SQL `formatear_codigo_catastral` — solo
para formateo de presentación (agregar guiones). El CÓDIGO en sí
(los 23 dígitos) siempre lo genera la base de datos
(generar_codigo_catastral / trigger antes_de_guardar_inmueble); esta
función NUNCA se usa para crear o validar un código, solo para mostrarlo
bonito sin tener que ir a la BD de nuevo.

Bloques (23 caracteres): E(2) M(2) P(2) S(2) Ma(3) Pa(3) SP(3) N(3) U(3)
"""
from typing import Optional


def formatear_codigo_catastral(codigo: Optional[str]) -> Optional[str]:
    if not codigo or len(codigo) != 23:
        return codigo
    bloques = [
        codigo[0:2],
        codigo[2:4],
        codigo[4:6],
        codigo[6:8],
        codigo[8:11],
        codigo[11:14],
        codigo[14:17],
        codigo[17:20],
        codigo[20:23],
    ]
    return "-".join(bloques)
