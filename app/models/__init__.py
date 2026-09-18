"""
Importa todos los modelos para que queden registrados en Base.metadata
(necesario para que las relationships con strings tipo "Inmueble" se
resuelvan y para herramientas como Alembic autogenerate).
"""
from app.models.configuracion import ConfiguracionCatastral, ConfiguracionSistema  # noqa: F401
from app.models.foto import FotoInmueble  # noqa: F401
from app.models.hito import HitoPredial  # noqa: F401
from app.models.inmueble import Inmueble  # noqa: F401
from app.models.propietario import Propietario  # noqa: F401
from app.models.usuario import Usuario  # noqa: F401

__all__ = [
    "ConfiguracionCatastral",
    "ConfiguracionSistema",
    "FotoInmueble",
    "HitoPredial",
    "Inmueble",
    "Propietario",
    "Usuario",
]
