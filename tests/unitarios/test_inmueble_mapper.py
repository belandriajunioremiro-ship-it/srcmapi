import pytest
import uuid
from datetime import datetime
from app.models.inmueble import Inmueble
from app.services.inmueble_mapper import inmueble_a_out, inmueble_a_list_item

def _crear_inmueble_mock():
    # Helper para instanciar un SQLAlchemy model en memoria sin persistir
    inmueble = Inmueble(
        id=uuid.uuid4(),
        propietario_id=uuid.uuid4(),
        direccion="Calle Prueba",
        sector="06",
        manzana="099",
        parcela="100",
        subparcela="000",
        nivel="000",
        unidad="000",
        tenencia="propio",
        descripcion_uso="Residencial",
        area_terreno_m2=100.0,
        area_construccion_m2=50.0,
        codigo_catastral="06099100000000000000000",
        aguas_blancas=True,
        aguas_servidas=True,
        electricidad=True,
        contador=True,
        existe_vivienda=True,
        sala=True,
        cocina=True,
        estado_sync="PENDING",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    # Como geom usa GeoAlchemy que espera el DB, para el mock le pasamos None
    # ya que el validador del Schema lo maneja
    inmueble.geom = None
    return inmueble

def test_inmueble_a_out():
    inmueble_mock = _crear_inmueble_mock()
    resultado = inmueble_a_out(inmueble_mock)
    
    assert resultado.id == inmueble_mock.id
    assert resultado.codigo_catastral == "06099100000000000000000"
    # Verificar que el código se formateó correctamente (separado por guiones)
    assert resultado.codigo_catastral_formato == "06-09-91-00-000-000-000-000-000"
    assert resultado.direccion == "Calle Prueba"

def test_inmueble_a_list_item():
    inmueble_mock = _crear_inmueble_mock()
    resultado = inmueble_a_list_item(inmueble_mock)
    
    assert resultado.id == inmueble_mock.id
    assert resultado.codigo_catastral == "06099100000000000000000"
    assert resultado.codigo_catastral_formato == "06-09-91-00-000-000-000-000-000"
