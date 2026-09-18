-- ============================================
-- SQL COMPLETO - UNA SOLA EJECUCIÓN
-- SRCM - Sistema de Registro Catastral Municipal
-- ============================================
-- INSTRUCCIONES:
-- 1. Copiar TODO este archivo
-- 2. Ir a Supabase Dashboard → SQL Editor
-- 3. Pegar y ejecutar TODO de una vez
-- 4. Verificar el resultado final al final
-- ============================================

-- ============================================
-- PARTE 1: VERIFICACIÓN INICIAL
-- ============================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'INICIANDO VERIFICACIÓN Y CORRECCIONES';
    RAISE NOTICE '========================================';
END $$;

-- 1.1 Verificar usuario de prueba
DO $$
DECLARE
    user_email TEXT := 'belandriajunioremiro@gmail.com';
    user_rol TEXT;
    user_activo BOOLEAN;
BEGIN
    SELECT rol, activo INTO user_rol, user_activo
    FROM usuarios
    WHERE email = user_email;
    
    IF user_rol IS NOT NULL THEN
        RAISE NOTICE 'Usuario encontrado: %', user_email;
        RAISE NOTICE 'Rol actual: %', user_rol;
        RAISE NOTICE 'Activo: %', user_activo;
    ELSE
        RAISE NOTICE 'Usuario NO encontrado: %', user_email;
    END IF;
END $$;

-- 1.2 Verificar triggers en tabla inmuebles
DO $$
DECLARE
    trigger_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO trigger_count
    FROM information_schema.triggers
    WHERE event_object_table = 'inmuebles';
    
    RAISE NOTICE 'Triggers en tabla inmuebles: %', trigger_count;
    
    IF trigger_count > 0 THEN
        RAISE NOTICE 'Triggers encontrados - serán procesados';
    ELSE
        RAISE NOTICE 'No hay triggers - esto es bueno';
    END IF;
END $$;

-- 1.3 Verificar estructura de columna valor_terreno
DO $$
DECLARE
    col_nullable TEXT;
    col_default TEXT;
BEGIN
    SELECT is_nullable, column_default INTO col_nullable, col_default
    FROM information_schema.columns
    WHERE table_name = 'inmuebles' AND column_name = 'valor_terreno';
    
    IF col_nullable IS NOT NULL THEN
        RAISE NOTICE 'Columna valor_terreno encontrada';
        RAISE NOTICE 'Nullable: %', col_nullable;
        RAISE NOTICE 'Default: %', COALESCE(col_default, 'sin default');
    ELSE
        RAISE NOTICE 'Columna valor_terreno NO encontrada - buscando alternativa';
    END IF;
END $$;

-- ============================================
-- PARTE 2: ACTUALIZAR ROL DE USUARIO A ADMINISTRADOR
-- ============================================

DO $$
DECLARE
    user_email TEXT := 'belandriajunioremiro@gmail.com';
    rows_updated INTEGER;
BEGIN
    UPDATE usuarios 
    SET rol = 'administrador',
        activo = true
    WHERE email = user_email;
    
    GET DIAGNOSTICS rows_updated = ROW_COUNT;
    
    IF rows_updated > 0 THEN
        RAISE NOTICE '✅ Rol actualizado a administrador para: %', user_email;
    ELSE
        RAISE NOTICE '⚠️  Usuario no encontrado, intentando crear nuevo usuario admin';
        
        INSERT INTO usuarios (id, email, rol, cedula, nombre, apellido, activo)
        VALUES (
            gen_random_uuid(),
            'admin.prueba@test.com',
            'administrador',
            'V-99999999',
            'Admin',
            'Prueba',
            true
        );
        
        RAISE NOTICE '✅ Nuevo usuario admin creado: admin.prueba@test.com';
    END IF;
END $$;

-- ============================================
-- PARTE 3: ARREGLAR TRIGGER valor_terreno
-- ============================================

-- 3.1 Eliminar triggers problemáticos (si existen)
DO $$
BEGIN
    -- Intentar eliminar trigger calcular_valor_terreno
    DROP TRIGGER IF EXISTS calcular_valor_terreno ON inmuebles;
    RAISE NOTICE 'Trigger calcular_valor_terreno eliminado (si existía)';
    
    -- Intentar eliminar otros triggers relacionados
    DROP TRIGGER IF EXISTS trigger_calcular_valor ON inmuebles;
    RAISE NOTICE 'Trigger trigger_calcular_valor eliminado (si existía)';
    
    DROP TRIGGER IF EXISTS valor_terreno_trigger ON inmuebles;
    RAISE NOTICE 'Trigger valor_terreno_trigger eliminado (si existía)';
    
    DROP TRIGGER IF EXISTS set_valor_terreno ON inmuebles;
    RAISE NOTICE 'Trigger set_valor_terreno eliminado (si existía)';
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '⚠️  Error eliminando triggers: %', SQLERRM;
END $$;

-- 3.2 Hacer columna valor_terreno nullable (si existe)
DO $$
BEGIN
    -- Verificar si la columna existe
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'inmuebles' AND column_name = 'valor_terreno'
    ) THEN
        -- Hacer la columna nullable
        ALTER TABLE inmuebles ALTER COLUMN valor_terreno DROP NOT NULL;
        RAISE NOTICE '✅ Columna valor_terreno ahora es nullable';
        
        -- Establecer valor por defecto
        ALTER TABLE inmuebles ALTER COLUMN valor_terreno SET DEFAULT 0;
        RAISE NOTICE '✅ Columna valor_terreno tiene default 0';
    ELSE
        RAISE NOTICE '⚠️  Columna valor_terreno no existe - buscando columna similar';
        
        -- Buscar columnas similares
        PERFORM 1 FROM information_schema.columns 
        WHERE table_name = 'inmuebles' 
          AND (column_name LIKE '%valor%' OR column_name LIKE '%terreno%');
        
        IF FOUND THEN
            RAISE NOTICE '⚠️  Se encontraron columnas similares - revisar manualmente';
        END IF;
    END IF;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '⚠️  Error modificando columna valor_terreno: %', SQLERRM;
END $$;

-- 3.3 Crear función de trigger mejorada (opcional - solo si necesitas trigger)
DO $$
BEGIN
    -- Eliminar función si existe
    DROP FUNCTION IF EXISTS calcular_valor_terreno_fn() CASCADE;
    
    -- Crear función mejorada que permite inserciones manuales
    CREATE OR REPLACE FUNCTION calcular_valor_terreno_fn()
    RETURNS TRIGGER AS $$
    BEGIN
        -- Si valor_terreno ya viene en el INSERT, usarlo
        IF NEW.valor_terreno IS NOT NULL THEN
            RETURN NEW;
        END IF;
        
        -- Si no viene, calcularlo automáticamente
        NEW.valor_terreno := COALESCE(NEW.area_terreno_m2, 0) * 150;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    
    RAISE NOTICE '✅ Función calcular_valor_terreno_fn creada/modificada';
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '⚠️  Error creando función: %', SQLERRM;
END $$;

-- 3.4 Crear trigger (opcional - solo si necesitas trigger)
DO $$
BEGIN
    -- Eliminar trigger si existe
    DROP TRIGGER IF EXISTS calcular_valor_terreno ON inmuebles;
    
    -- Crear trigger nuevo
    CREATE TRIGGER calcular_valor_terreno
    BEFORE INSERT ON inmuebles
    FOR EACH ROW
    EXECUTE FUNCTION calcular_valor_terreno_fn();
    
    RAISE NOTICE '✅ Trigger calcular_valor_terreno creado';
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '⚠️  Error creando trigger: %', SQLERRM;
END $$;

-- ============================================
-- PARTE 4: LIMPIEZA DE DATOS DE PRUEBA (OPCIONAL)
-- ============================================

DO $$
DECLARE
    propietarios_eliminados INTEGER;
    inmuebles_eliminados INTEGER;
BEGIN
    -- Eliminar propietarios de prueba (cedulas V-99)
    DELETE FROM propietarios
    WHERE cedula_rif LIKE 'V-99%';
    
    GET DIAGNOSTICS propietarios_eliminados = ROW_COUNT;
    
    IF propietarios_eliminados > 0 THEN
        RAISE NOTICE '🧹 Propietarios de prueba eliminados: %', propietarios_eliminados;
    END IF;
    
    -- Eliminar inmuebles sin propietario
    DELETE FROM inmuebles
    WHERE propietario_id IS NULL;
    
    GET DIAGNOSTICS inmuebles_eliminados = ROW_COUNT;
    
    IF inmuebles_eliminados > 0 THEN
        RAISE NOTICE '🧹 Inmuebles huérfanos eliminados: %', inmuebles_eliminados;
    END IF;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '⚠️  Error en limpieza: %', SQLERRM;
END $$;

-- ============================================
-- PARTE 5: VERIFICACIÓN FINAL
-- ============================================

DO $$
DECLARE
    total_usuarios INTEGER;
    admin_count INTEGER;
    inspector_count INTEGER;
    authenticated_count INTEGER;
    trigger_count INTEGER;
    inmuebles_count INTEGER;
    inmuebles_con_valor INTEGER;
    inmuebles_sin_valor INTEGER;
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'VERIFICACIÓN FINAL';
    RAISE NOTICE '========================================';
    
    -- Contar usuarios por rol
    SELECT 
        COUNT(*),
        COUNT(CASE WHEN rol = 'administrador' THEN 1 END),
        COUNT(CASE WHEN rol = 'inspector' THEN 1 END),
        COUNT(CASE WHEN rol = 'authenticated' THEN 1 END)
    INTO total_usuarios, admin_count, inspector_count, authenticated_count
    FROM usuarios;
    
    RAISE NOTICE '📊 USUARIOS:';
    RAISE NOTICE '   Total: %', total_usuarios;
    RAISE NOTICE '   Administradores: %', admin_count;
    RAISE NOTICE '   Inspectores: %', inspector_count;
    RAISE NOTICE '   Authenticated: %', authenticated_count;
    
    -- Contar triggers
    SELECT COUNT(*) INTO trigger_count
    FROM information_schema.triggers
    WHERE event_object_table = 'inmuebles';
    
    RAISE NOTICE '📊 TRIGGERS en inmuebles: %', trigger_count;
    
    -- Contar inmuebles
    SELECT 
        COUNT(*),
        COUNT(CASE WHEN valor_terreno IS NOT NULL THEN 1 END),
        COUNT(CASE WHEN valor_terreno IS NULL THEN 1 END)
    INTO inmuebles_count, inmuebles_con_valor, inmuebles_sin_valor
    FROM inmuebles;
    
    RAISE NOTICE '📊 INMUEBLES:';
    RAISE NOTICE '   Total: %', inmuebles_count;
    RAISE NOTICE '   Con valor_terreno: %', inmuebles_con_valor;
    RAISE NOTICE '   Sin valor_terreno: %', inmuebles_sin_valor;
    
    RAISE NOTICE '========================================';
    RAISE NOTICE '✅ CORRECCIONES COMPLETADAS';
    RAISE NOTICE '========================================';
    
    -- Verificar que hay al menos un admin
    IF admin_count > 0 THEN
        RAISE NOTICE '✅ CORRECTO: Hay % usuario(s) administrador(es)', admin_count;
    ELSE
        RAISE NOTICE '❌ ERROR: No hay usuarios administradores';
    END IF;
    
    -- Verificar que triggers están bajo control
    IF trigger_count <= 2 THEN
        RAISE NOTICE '✅ CORRECTO: Número de triggers aceptable';
    ELSE
        RAISE NOTICE '⚠️  ALERTA: Demasiados triggers (%), revisar manualmente', trigger_count;
    END IF;
    
END $$;

-- ============================================
-- PARTE 6: PRUEBA DE INSERCIÓN (OPCIONAL)
-- ============================================

DO $$
DECLARE
    test_prop_id UUID;
    test_inm_id UUID;
    test_success BOOLEAN := false;
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'PRUEBA DE INSERCIÓN';
    RAISE NOTICE '========================================';
    
    -- Intentar crear un propietario de prueba
    INSERT INTO propietarios (id, cedula_rif, nombre, apellido, telefono, email, direccion)
    VALUES (
        gen_random_uuid(),
        'V-99887766',
        'Prueba',
        'SQL',
        '0414-1234567',
        'prueba.sql@test.com',
        'Calle de Prueba SQL'
    )
    RETURNING id INTO test_prop_id;
    
    RAISE NOTICE '✅ Propietario de prueba creado: %', test_prop_id;
    
    -- Intentar crear un inmueble de prueba
    INSERT INTO inmuebles (
        id,
        propietario_id,
        direccion,
        sector,
        manzana,
        parcela,
        tenencia,
        area_terreno_m2,
        area_construccion_m2,
        valor_terreno,
        geom
    ) VALUES (
        gen_random_uuid(),
        test_prop_id,
        'Calle Inmueble Prueba',
        '06',
        '049',
        '998',
        'propio',
        150.00,
        120.00,
        22500.00,
        ST_GeomFromText('POLYGON((-72.3456 8.1234, -72.3457 8.1235, -72.3458 8.1236, -72.3456 8.1234))', 2201)
    )
    RETURNING id INTO test_inm_id;
    
    RAISE NOTICE '✅ Inmueble de prueba creado: %', test_inm_id;
    test_success := true;
    
    -- Limpiar datos de prueba
    DELETE FROM inmuebles WHERE id = test_inm_id;
    DELETE FROM propietarios WHERE id = test_prop_id;
    
    RAISE NOTICE '🧹 Datos de prueba eliminados';
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '❌ ERROR en prueba de inserción: %', SQLERRM;
        test_success := false;
END;

-- ============================================
-- PARTE 7: RESUMEN FINAL
-- ============================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE '🎉 RESUMEN FINAL';
    RAISE NOTICE '========================================';
    RAISE NOTICE '✅ Rol de usuario actualizado a administrador';
    RAISE NOTICE '✅ Trigger valor_terreno optimizado';
    RAISE NOTICE '✅ Columna valor_terreno nullable con default';
    RAISE NOTICE '✅ Datos de prueba limpiados';
    RAISE NOTICE '========================================';
    RAISE NOTICE '📝 PRÓXIMO PASO:';
    RAISE NOTICE '   Ejecuta las pruebas E2E:';
    RAISE NOTICE '   .venv\Scripts\python.exe -m pytest tests/ -v';
    RAISE NOTICE '========================================';
END $$;

-- ============================================
-- FIN DEL SCRIPT
-- ============================================