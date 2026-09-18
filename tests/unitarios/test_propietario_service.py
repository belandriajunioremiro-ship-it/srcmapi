import pytest
import uuid
from unittest.mock import MagicMock
from app.services.propietario_service import obtener_propietario, listar_propietarios
from app.models.propietario import Propietario

def test_obtener_propietario_existente():
    db_mock = MagicMock()
    
    # Creamos un Propietario mock
    prop_falso = Propietario(id=uuid.uuid4(), cedula_rif="V-12345678", nombre="Juan")
    
    # db.get(Propietario, propietario_id)
    db_mock.get.return_value = prop_falso
    
    resultado = obtener_propietario(db_mock, prop_falso.id)
    
    assert resultado is not None
    assert resultado.nombre == "Juan"
    db_mock.get.assert_called_once_with(Propietario, prop_falso.id)

def test_obtener_propietario_no_existe():
    db_mock = MagicMock()
    db_mock.get.return_value = None
    
    resultado = obtener_propietario(db_mock, uuid.uuid4())
    
    assert resultado is None

def test_listar_propietarios_paginacion():
    db_mock = MagicMock()
    
    # El servicio usa db.execute() dos veces: una para total (scalar_one), otra para items (scalars().all())
    # Hacemos que db.execute devuelva un mock que manejamos según el orden o encadenamiento
    mock_result_1 = MagicMock()
    mock_result_1.scalar_one.return_value = 10  # total
    
    mock_result_2 = MagicMock()
    mock_result_2.scalars().all.return_value = [
        Propietario(nombre="P1"), Propietario(nombre="P2")
    ]
    
    # Cuando db.execute se llame iterativamente, devuelve primero el mock 1, luego el 2
    db_mock.execute.side_effect = [mock_result_1, mock_result_2]
    
    total, items = listar_propietarios(db_mock, pagina=2, por_pagina=2)
    
    assert total == 10
    assert len(items) == 2

def test_listar_propietarios_busqueda():
    db_mock = MagicMock()
    mock_result_1 = MagicMock()
    mock_result_1.scalar_one.return_value = 1
    
    mock_result_2 = MagicMock()
    mock_result_2.scalars().all.return_value = [Propietario(nombre="Juan")]
    
    db_mock.execute.side_effect = [mock_result_1, mock_result_2]
    
    # Usamos 'busqueda' no 'q'
    total, items = listar_propietarios(db_mock, busqueda="Juan")
    
    assert total == 1
    assert items[0].nombre == "Juan"
