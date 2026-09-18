import pytest
from unittest.mock import MagicMock
from app.services.configuracion_service import (
    obtener_configuracion_catastral,
    actualizar_configuracion_catastral,
    obtener_configuracion_sistema,
    actualizar_configuracion_sistema
)
from app.models.configuracion import ConfiguracionCatastral, ConfiguracionSistema

def test_obtener_configuracion_catastral():
    db_mock = MagicMock()
    config_mock = ConfiguracionCatastral(id=1, valor_m2_terreno=500.0)
    db_mock.get.return_value = config_mock
    
    resultado = obtener_configuracion_catastral(db_mock)
    
    assert resultado.valor_m2_terreno == 500.0
    db_mock.get.assert_called_once_with(ConfiguracionCatastral, 1)

def test_actualizar_configuracion_catastral():
    db_mock = MagicMock()
    config_mock = ConfiguracionCatastral(id=1, valor_m2_terreno=500.0)
    db_mock.get.return_value = config_mock
    
    data = {"valor_m2_terreno": 600.0}
    resultado = actualizar_configuracion_catastral(db_mock, data)
    
    assert resultado.valor_m2_terreno == 600.0
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(config_mock)

def test_actualizar_configuracion_catastral_no_encontrada():
    db_mock = MagicMock()
    db_mock.get.return_value = None
    
    with pytest.raises(ValueError, match="Configuración catastral no encontrada"):
        actualizar_configuracion_catastral(db_mock, {"valor_m2_terreno": 600.0})

def test_obtener_configuracion_sistema():
    db_mock = MagicMock()
    config_mock = ConfiguracionSistema(id=1, nombre_municipio="Torbes")
    db_mock.get.return_value = config_mock
    
    resultado = obtener_configuracion_sistema(db_mock)
    
    assert resultado.nombre_municipio == "Torbes"
    db_mock.get.assert_called_once_with(ConfiguracionSistema, 1)

def test_actualizar_configuracion_sistema_no_encontrada():
    db_mock = MagicMock()
    db_mock.get.return_value = None
    
    with pytest.raises(ValueError, match="Configuración del sistema no encontrada"):
        actualizar_configuracion_sistema(db_mock, {"nombre_municipio": "Otro"})
