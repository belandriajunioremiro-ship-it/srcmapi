-- Crear usuario de prueba para las pruebas E2E
-- Ejecuta esto en el SQL Editor de Supabase

-- 1. Crear usuario en auth.users (Supabase Auth)
-- Nota: Normalmente esto se hace a través de la API de Supabase Auth
-- pero para pruebas podemos crearlo directamente si tenemos acceso

-- 2. Crear el registro correspondiente en nuestra tabla usuarios
INSERT INTO usuarios (id, cedula, nombre, apellido, rol, activo)
VALUES (
  '00000000-0000-0000-0000-000000000999',
  'V-99999999',
  'Usuario',
  'PruebaE2E',
  'administrador',
  true
)
ON CONFLICT (cedula) DO NOTHING;

-- Verificar que se creó
SELECT * FROM usuarios WHERE cedula = 'V-99999999';
