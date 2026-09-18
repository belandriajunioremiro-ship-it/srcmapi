from app.utils.catastro_codigo import formatear_codigo_catastral

def test_formatear_codigo_catastral_correcto():
    # Arrange (Preparar datos)
    codigo_crudo = "20270106049328000000000"
    
    # Act (Ejecutar la función)
    resultado = formatear_codigo_catastral(codigo_crudo)
    
    # Assert (Comprobar)
    assert resultado == "20-27-01-06-049-328-000-000-000"

def test_formatear_codigo_catastral_vacio():
    assert formatear_codigo_catastral(None) is None

def test_formatear_codigo_catastral_incompleto():
    # Si no tiene exactamente 23 caracteres, debe devolverlo igual sin formatear
    codigo_incompleto = "202701"
    assert formatear_codigo_catastral(codigo_incompleto) == "202701"
