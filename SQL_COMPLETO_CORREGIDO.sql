-- ============================================
-- SQL COMPLETO CORREGIDO - VERSIÓN SIMPLIFICADA
-- SRCM - Sistema de Registro Catastral Municipal
-- ============================================
-- INSTRUCCIONES:
-- 1. Copiar TODO este archivo
-- 2. Ir a Supabase Dashboard → SQL Editor
-- 3. Pegar y ejecutar TODO de una vez
-- ============================================

-- ============================================
-- PARTE 1: ACTUALIZAR ROL DE USUARIO A ADMINISTRADOR
-- ============================================

UPDATE usuarios 
SET rol = 'administrador', activo = true
WHERE email = 'belandriajunioremiro@gmail.com';

-- Si el usuario no existe, crear uno nuevo
INSERT INTO usuarios (id, email, rol, cedula, nombre, apellido, activo)
SELECT 
    gen_random_uuid(),
    'admin.prueba@test.com',
    'administrador',
    'V-99999999',
    'Admin',
    'Prueba',
    true
WHERE NOT EXISTS (
    SELECT 1 FROM usuarios WHERE email = 'admin.prueba@test.com'
);

-- ============================================
-- PARTE 2: ELIMINAR TRIGGERS PROBLEMÁTICOS
-- ============================================

DROP TRIGGER IF EXISTS calcular_valor_terreno ON inmuebles;
DROP TRIGGER IF EXISTS trigger_calcular_valor ON inmuebles;
DROP TRIGGER IF EXISTS valor_terreno_trigger ON inmuebles;
DROP TRIGGER IF EXISTS set_valor_terreno ON inmuebles;
DROP TRIGGER IF EXISTS inmuebles_before_insert ON inmuebles;

-- ============================================
-- PARTE 3: HACER COLUMNA valor_terreno NULLABLE
-- ============================================

-- Verificar si la columna existe y modificarla
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'inmuebles' AND column_name = 'valor_terreno'
    ) THEN
        ALTER TABLE inmuebles ALTER COLUMN valor_terreno DROP NOT NULL;
        ALTER TABLE inmuebles ALTER COLUMN valor_terreno SET DEFAULT 0;
    END IF;
END $$;

-- ============================================
-- PARTE 4: CREAR FUNCIÓN DE TRIGGER MEJORADA
-- ============================================

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

-- ============================================
-- PARTE 5: CREAR TRIGGER NUEVO
-- ============================================

DROP TRIGGER IF EXISTS calcular_valor_terreno ON inmuebles;

CREATE TRIGGER calcular_valor_terreno
BEFORE INSERT ON inmuebles
FOR EACH ROW
EXECUTE FUNCTION calcular_valor_terreno_fn();

-- ============================================
-- PARTE 6: LIMPIEZA DE DATOS DE PRUEBA
-- ============================================

DELETE FROM propietarios WHERE cedula_rif LIKE 'V-99%';
DELETE FROM inmuebles WHERE propietario_id IS NULL;

-- ============================================
-- PARTE 7: VERIFICACIÓN FINAL
-- ============================================

-- Verificar usuarios por rol
SELECT 
    'USUARIOS' as categoria,
    COUNT(*) as total,
    COUNT(CASE WHEN rol = 'administrador' THEN 1 END) as administradores,
    COUNT(CASE WHEN rol = 'inspector' THEN 1 END) as inspectores,
    COUNT(CASE WHEN rol = 'authenticated' THEN 1 END) as authenticated
FROM usuarios;

-- Verificar triggers
SELECT 
    'TRIGGERS' as categoria,
    COUNT(*) as total_triggers
FROM information_schema.triggers
WHERE event_object_table = 'inmuebles';

-- Verificar estructura de valor_terreno
SELECT 
    'COLUMNA valor_terreno' as categoria,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'inmuebles' AND column_name = 'valor_terreno';

-- Verificar usuario específico
SELECT 
    'USUARIO PRINCIPAL' as categoria,
    email,
    rol,
    activo
FROM usuarios
WHERE email = 'belandriajunioremiro@gmail.com'
UNION ALL
SELECT 
    'USUARIO ADMIN PRUEBA' as categoria,
    email,
    rol,
    activo
FROM usuarios
WHERE email = 'admin.prueba@test.com';

-- ============================================
-- FIN DEL SCRIPT
-- ============================================