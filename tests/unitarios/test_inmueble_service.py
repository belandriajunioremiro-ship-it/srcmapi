import pytest
import uuid
from unittest.mock import MagicMock
from app.services.inmueble_service import obtener_inmueble, crear_inmueble
from app.models.inmueble import Inmueble

def test_obtener_inmueble_existente():
    db_mock = MagicMock()
    
    # Simular la respuesta de db.execute().scalar_one_or_none()
    inmueble_falso = Inmueble(id=uuid.uuid4(), sector="06")
    db_mock.execute.return_value.scalar_one_or_none.return_value = inmueble_falso
    
    resultado = obtener_inmueble(db_mock, inmueble_falso.id)
    
    assert resultado is not None
    assert resultado.sector == "06"
    db_mock.execute.assert_called_once()

def test_obtener_inmueble_no_existe():
    db_mock = MagicMock()
    db_mock.execute.return_value.scalar_one_or_none.return_value = None
    
    resultado = obtener_inmueble(db_mock, uuid.uuid4())
    
    assert resultado is None
    db_mock.execute.assert_called_once()
