-- ============================================
-- SQL SOLO PARA ACTUALIZAR ROL DE USUARIO
-- SRCM - Sistema de Registro Catastral Municipal
-- ============================================
-- NOTA: valor_terreno es una columna GENERADA, no se puede modificar
-- El problema debe solucionarse en los tests (no enviar valor_terreno)
-- ============================================

-- ============================================
-- ACTUALIZAR ROL DE USUARIO A ADMINISTRADOR
-- ============================================

-- Actualizar usuario por cédula (V-20394453 es la cédula del usuario de prueba)
UPDATE usuarios 
SET rol = 'administrador', activo = true
WHERE cedula = 'V-20394453';

-- Si el usuario no existe, crear uno nuevo con cédula de prueba
INSERT INTO usuarios (id, cedula, nombre, apellido, rol, activo)
SELECT 
    gen_random_uuid(),
    'V-99999999',
    'Admin',
    'Prueba',
    'administrador',
    true
WHERE NOT EXISTS (
    SELECT 1 FROM usuarios WHERE cedula = 'V-99999999'
);

-- ============================================
-- VERIFICACIÓN
-- ============================================

-- Verificar usuarios por rol
SELECT 
    'USUARIOS' as categoria,
    COUNT(*) as total,
    COUNT(CASE WHEN rol = 'administrador' THEN 1 END) as administradores,
    COUNT(CASE WHEN rol = 'inspector' THEN 1 END) as inspectores
FROM usuarios;

-- Verificar usuario específico por cédula
SELECT 
    'USUARIO PRINCIPAL (V-20394453)' as categoria,
    cedula,
    nombre,
    apellido,
    rol,
    activo
FROM usuarios
WHERE cedula = 'V-20394453'
UNION ALL
SELECT 
    'USUARIO ADMIN PRUEBA (V-99999999)' as categoria,
    cedula,
    nombre,
    apellido,
    rol,
    activo
FROM usuarios
WHERE cedula = 'V-99999999';

-- ============================================
-- FIN DEL SCRIPT
-- ============================================