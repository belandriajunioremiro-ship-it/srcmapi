"""
Servicio para gestión de configuración catastral y del sistema.
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.models.configuracion import ConfiguracionCatastral, ConfiguracionSistema


def obtener_configuracion_catastral(db: Session) -> Optional[ConfiguracionCatastral]:
    """Obtener la configuración catastral (fila única id=1)."""
    return db.get(ConfiguracionCatastral, 1)


def actualizar_configuracion_catastral(
    db: Session, data: dict
) -> ConfiguracionCatastral:
    """Actualizar la configuración catastral."""
    config = db.get(ConfiguracionCatastral, 1)
    if not config:
        raise ValueError("Configuración catastral no encontrada")

    for campo, valor in data.items():
        setattr(config, campo, valor)

    db.commit()
    db.refresh(config)
    return config


def obtener_configuracion_sistema(db: Session) -> Optional[ConfiguracionSistema]:
    """Obtener la configuración del sistema (fila única id=1)."""
    return db.get(ConfiguracionSistema, 1)


def actualizar_configuracion_sistema(
    db: Session, data: dict
) -> ConfiguracionSistema:
    """Actualizar la configuración del sistema."""
    config = db.get(ConfiguracionSistema, 1)
    if not config:
        raise ValueError("Configuración del sistema no encontrada")

    for campo, valor in data.items():
        setattr(config, campo, valor)

    db.commit()
    db.refresh(config)
    return config
