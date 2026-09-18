-- ============================================
-- SQL PARA VERIFICAR Y ARREGLAR PROBLEMAS DE BASE DE DATOS
-- SRCM - Sistema de Registro Catastral Municipal
-- ============================================
-- Instrucciones:
-- 1. Copiar este archivo
-- 2. Ir a Supabase Dashboard → SQL Editor
-- 3. Ejecutar cada sección paso a paso
-- 4. Verificar los resultados antes de continuar
-- ============================================

-- ============================================
-- SECCIÓN 1: VERIFICAR TRIGGER valor_terreno
-- ============================================

-- 1.1 Verificar triggers existentes en tabla inmuebles
SELECT 
    trigger_name,
    event_manipulation,
    event_object_table,
    action_statement,
    action_timing
FROM information_schema.triggers
WHERE event_object_table = 'inmuebles'
ORDER BY trigger_name;

-- 1.2 Verificar estructura de tabla inmuebles
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'inmuebles'
ORDER BY ordinal_position;

-- 1.3 Verificar si hay triggers que calculan valor_terreno
SELECT 
    routine_name,
    routine_definition
FROM information_schema.routines
WHERE routine_name LIKE '%valor%'
   OR routine_name LIKE '%terreno%'
   OR routine_definition LIKE '%valor_terreno%';

-- ============================================
-- SECCIÓN 2: ARREGLAR TRIGGER valor_terreno
-- ============================================

-- OPCIÓN A: Desactivar trigger temporalmente (para pruebas)
-- Descomenta y ejecuta SOLO si necesitas desactivar el trigger

-- DROP TRIGGER IF EXISTS calcular_valor_terreno ON inmuebles;
-- DROP TRIGGER IF EXISTS trigger_calcular_valor ON inmuebles;
-- DROP TRIGGER IF EXISTS valor_terreno_trigger ON inmuebles;

-- OPCIÓN B: Modificar trigger para permitir inserciones manuales
-- Descomenta y ejecuta SOLO si necesitas modificar el trigger

-- CREATE OR REPLACE FUNCTION calcular_valor_terreno_fn()
-- RETURNS TRIGGER AS $$
-- BEGIN
--     -- Si valor_terreno ya viene en el INSERT, usarlo
--     IF NEW.valor_terreno IS NOT NULL THEN
--         RETURN NEW;
--     END IF;
--     
--     -- Si no viene, calcularlo automáticamente
--     NEW.valor_terreno := NEW.area_terreno_m2 * 150;
--     RETURN NEW;
-- END;
-- $$ LANGUAGE plpgsql;

-- OPCIÓN C: Hacer valor_terreno nullable con valor por defecto
-- Descomenta y ejecuta SOLO si necesitas modificar la columna

-- ALTER TABLE inmuebles ALTER COLUMN valor_terreno DROP NOT NULL;
-- ALTER TABLE inmuebles ALTER COLUMN valor_terreno SET DEFAULT 0;

-- ============================================
-- SECCIÓN 3: VERIFICAR ROL DE USUARIO DE PRUEBA
-- ============================================

-- 3.1 Verificar el usuario de prueba en tabla usuarios
SELECT 
    id,
    email,
    rol,
    cedula,
    nombre,
    apellido,
    activo
FROM usuarios
WHERE email = 'belandriajunioremiro@gmail.com';

-- 3.2 Verificar todos los usuarios con rol administrador
SELECT 
    id,
    email,
    rol,
    cedula,
    nombre,
    apellido,
    activo
FROM usuarios
WHERE rol = 'administrador';

-- 3.3 Verificar todos los usuarios existentes
SELECT 
    id,
    email,
    rol,
    cedula,
    nombre,
    apellido,
    activo,
    created_at
FROM usuarios
ORDER BY created_at DESC
LIMIT 10;

-- ============================================
-- SECCIÓN 4: ARREGLAR ROL DE USUARIO DE PRUEBA
-- ============================================

-- 4.1 Actualizar el usuario de prueba a rol administrador
UPDATE usuarios 
SET rol = 'administrador',
    activo = true
WHERE email = 'belandriajunioremiro@gmail.com';

-- Verificar el cambio
SELECT 
    id,
    email,
    rol,
    cedula,
    nombre,
    apellido,
    activo
FROM usuarios
WHERE email = 'belandriajunioremiro@gmail.com';

-- 4.2 OPCIÓN: Crear un usuario administrador específico para pruebas
-- Descomenta y ejecuta SOLO si necesitas un usuario separado

-- INSERT INTO usuarios (id, email, rol, cedula, nombre, apellido, activo)
-- VALUES (
--     gen_random_uuid(),
--     'admin.prueba@test.com',
--     'administrador',
--     'V-99999999',
--     'Admin',
--     'Prueba',
--     true
-- );

-- ============================================
-- SECCIÓN 5: VERIFICAR CONFIGURACIÓN DE SUPABASE AUTH
-- ============================================

-- 5.1 Verificar tabla auth.users (si tienes acceso)
-- NOTA: Esta tabla puede no ser accesible directamente en Supabase
-- Puedes verificar esto desde Supabase Dashboard → Authentication → Users

-- 5.2 Verificar si hay funciones personalizadas de JWT
SELECT 
    routine_name,
    routine_definition
FROM information_schema.routines
WHERE routine_name LIKE '%jwt%'
   OR routine_name LIKE '%auth%'
   OR routine_name LIKE '%token%';

-- 5.3 Verificar triggers personalizados de auth
SELECT 
    trigger_name,
    event_object_table,
    action_statement
FROM information_schema.triggers
WHERE event_object_table LIKE '%auth%'
   OR event_object_table LIKE '%user%';

-- ============================================
-- SECCIÓN 6: VERIFICAR PERMISOS Y ROLES
-- ============================================

-- 6.1 Verificar roles de PostgreSQL disponibles
SELECT rolname FROM pg_roles;

-- 6.2 Verificar permisos del usuario actual
SELECT 
    grantee,
    privilege_type,
    table_name
FROM information_schema.role_table_grants
WHERE table_name = 'usuarios'
   OR table_name = 'inmuebles';

-- 6.3 Verificar restricciones en tabla inmuebles
SELECT 
    constraint_name,
    constraint_type
FROM information_schema.table_constraints
WHERE table_name = 'inmuebles';

-- ============================================
-- SECCIÓN 7: VERIFICAR DATOS DE PRUEBA EXISTENTES
-- ============================================

-- 7.1 Verificar inmuebles existentes
SELECT 
    id,
    codigo_catastral,
    direccion,
    sector,
    manzana,
    parcela,
    area_terreno_m2,
    valor_terreno
FROM inmuebles
LIMIT 10;

-- 7.2 Verificar propietarios existentes
SELECT 
    id,
    cedula_rif,
    nombre,
    apellido,
    email
FROM propietarios
LIMIT 10;

-- 7.3 Verificar si hay datos duplicados que causan conflictos
SELECT 
    sector,
    manzana,
    parcela,
    COUNT(*) as cantidad
FROM inmuebles
GROUP BY sector, manzana, parcela
HAVING COUNT(*) > 1;

-- ============================================
-- SECCIÓN 8: LIMPIEZA DE DATOS DE PRUEBA (OPCIONAL)
-- ============================================

-- 8.1 Eliminar propietarios de prueba (cedulas que empiezan con V-99)
-- Descomenta SOLO si estás seguro de eliminar estos datos

-- DELETE FROM propietarios
-- WHERE cedula_rif LIKE 'V-99%';

-- 8.2 Eliminar inmuebles sin propietario
-- Descomenta SOLO si estás seguro de eliminar estos datos

-- DELETE FROM inmuebles
-- WHERE propietario_id IS NULL;

-- 8.3 Eliminar usuarios de prueba (email contiene "prueba" o "test")
-- Descomenta SOLO si estás seguro de eliminar estos datos

-- DELETE FROM usuarios
-- WHERE email LIKE '%prueba%' 
--    OR email LIKE '%test%';

-- ============================================
-- SECCIÓN 9: VERIFICACIÓN FINAL
-- ============================================

-- 9.1 Verificar estado final de usuarios
SELECT 
    COUNT(*) as total_usuarios,
    COUNT(CASE WHEN rol = 'administrador' THEN 1 END) as administradores,
    COUNT(CASE WHEN rol = 'inspector' THEN 1 END) as inspectores,
    COUNT(CASE WHEN rol = 'authenticated' THEN 1 END) as authenticated
FROM usuarios;

-- 9.2 Verificar estado final de inmuebles
SELECT 
    COUNT(*) as total_inmuebles,
    COUNT(CASE WHEN valor_terreno IS NOT NULL THEN 1 END) as con_valor_terreno,
    COUNT(CASE WHEN valor_terreno IS NULL THEN 1 END) as sin_valor_terreno
FROM inmuebles;

-- 9.3 Verificar estado final de triggers
SELECT 
    COUNT(*) as total_triggers,
    string_agg(trigger_name, ', ') as nombres_triggers
FROM information_schema.triggers
WHERE event_object_table = 'inmuebles';

-- ============================================
-- SECCIÓN 10: COMANDOS PARA PROBAR LA CONEXIÓN
-- ============================================

-- 10.1 Prueba de inserción simple de inmueble
-- Descomenta para probar si la inserción funciona después de los cambios

-- INSERT INTO inmuebles (
--     id,
--     propietario_id,
--     direccion,
--     sector,
--     manzana,
--     parcela,
--     tenencia,
--     area_terreno_m2,
--     area_construccion_m2,
--     valor_terreno,
--     geom
-- ) VALUES (
--     gen_random_uuid(),
--     (SELECT id FROM propietarios LIMIT 1),
--     'Calle de Prueba SQL',
--     '06',
--     '049',
--     '999',
--     'propio',
--     150.00,
--     120.00,
--     22500.00,
--     ST_GeomFromText('POLYGON((-72.3456 8.1234, -72.3457 8.1235, -72.3458 8.1236, -72.3456 8.1234))', 2201)
-- );

-- Verificar si la inserción funcionó
-- SELECT id, direccion, valor_terreno FROM inmuebles WHERE direccion = 'Calle de Prueba SQL';

-- ============================================
-- FIN DEL ARCHIVO SQL
-- ============================================
-- Después de ejecutar estos comandos, ejecuta las pruebas:
-- .venv\Scripts\python.exe -m pytest tests/ -v
-- ============================================