"""
Los triggers de la base de datos (validar_codigo_catastral_dinamico,
prevenir_solape_predios, etc.) hacen RAISE EXCEPTION con mensajes en
español pensados para el usuario final. Esta utilidad extrae ese mensaje
desde la excepción de SQLAlchemy/psycopg2 para devolverlo tal cual en
la respuesta de la API, en vez de un genérico "internal server error".
"""
from sqlalchemy.exc import IntegrityError, DBAPIError


def mensaje_error_postgres(exc: Exception) -> str:
    """
    Intenta extraer el mensaje de error "humano" que lanzó un trigger de
    Postgres (pgerror) o, si no lo encuentra, un mensaje genérico.
    """
    orig = getattr(exc, "orig", None)
    if orig is not None:
        pgerror = getattr(orig, "pgerror", None)
        if pgerror:
            # pgerror típico: "ERROR:  solape_topologico: el polígono...\n"
            lineas = [l for l in pgerror.splitlines() if l.strip()]
            if lineas:
                return lineas[0].replace("ERROR:", "").strip()
        diag = getattr(orig, "diag", None)
        if diag is not None and getattr(diag, "message_primary", None):
            return diag.message_primary

    if isinstance(exc, IntegrityError):
        return "Violación de una restricción de integridad (dato duplicado o inválido)."
    if isinstance(exc, DBAPIError):
        return "Error al comunicarse con la base de datos."
    return str(exc)
