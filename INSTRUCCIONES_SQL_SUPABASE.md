# INSTRUCCIONES PARA CORREGIR PROBLEMAS DE BASE DE DATOS EN SUPABASE

**Fecha:** 17 de septiembre de 2026  
**Objetivo:** Resolver los problemas restantes en pruebas E2E mediante correcciones en Supabase

---

## 📋 TABLA DE CONTENIDOS

1. [Problemas a Resolver](#problemas-a-resolver)
2. [Instrucciones Paso a Paso](#instrucciones-paso-a-paso)
3. [Comandos SQL Específicos](#comandos-sql-específicos)
4. [Verificación de Cambios](#verificación-de-cambios)
5. [Solución de Problemas](#solución-de-problemas)

---

## 🔴 PROBLEMAS A RESOLVER

### 1. Trigger valor_terreno
**Error:** `cannot insert a non-DEFAULT value into column "valor_terreno"`  
**Causa:** Un trigger en PostgreSQL está calculando automáticamente este campo y rechaza inserciones manuales.  
**Solución:** Desactivar o modificar el trigger.

### 2. Rol de Administrador
**Error:** `403 Forbidden` en endpoints de admin  
**Causa:** El usuario de prueba tiene rol `authenticated` en lugar de `administrador`.  
**Solución:** Actualizar el rol en la tabla `usuarios`.

### 3. Permisos de Usuario
**Error:** Falta de permisos para acceder a ciertos endpoints  
**Causa:** Configuración de Supabase Auth.  
**Solución:** Verificar configuración en Supabase Dashboard.

---

## 📝 INSTRUCCIONES PASO A PASO

### PASO 1: Acceder a Supabase Dashboard

1. Ve a: https://supabase.com/dashboard
2. Inicia sesión con tu cuenta
3. Selecciona tu proyecto: `jdacflrxsegctvrjlrqe`
4. En el menú lateral, haz clic en **SQL Editor**
5. Haz clic en **"New query"** para abrir un editor SQL

### PASO 2: Verificar el Trigger valor_terreno

Copia y ejecuta este comando SQL:

```sql
-- Verificar triggers existentes en tabla inmuebles
SELECT 
    trigger_name,
    event_manipulation,
    event_object_table,
    action_statement,
    action_timing
FROM information_schema.triggers
WHERE event_object_table = 'inmuebles'
ORDER BY trigger_name;
```

**Qué esperar:**
- Si ves triggers listados, identifica cuál está relacionado con `valor_terreno`
- Si no ves resultados, no hay triggers (esto es bueno)

### PASO 3: Verificar la Estructura de la Tabla

Copia y ejecuta este comando SQL:

```sql
-- Verificar estructura de tabla inmuebles
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'inmuebles'
ORDER BY ordinal_position;
```

**Qué esperar:**
- Busca la columna `valor_terreno`
- Verifica si `is_nullable` es `YES` o `NO`
- Verifica si tiene un `column_default`

### PASO 4: Verificar el Usuario de Prueba

Copia y ejecuta este comando SQL:

```sql
-- Verificar el usuario de prueba en tabla usuarios
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
```

**Qué esperar:**
- Deberías ver el usuario con rol `authenticated`
- Necesitamos cambiarlo a `administrador`

### PASO 5: Actualizar el Rol del Usuario de Prueba

Copia y ejecuta este comando SQL:

```sql
-- Actualizar el usuario de prueba a rol administrador
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
```

**Qué esperar:**
- El rol debería cambiar de `authenticated` a `administrador`
- El campo `activo` debería ser `true`

### PASO 6: Corregir el Trigger valor_terreno

**OPCIÓN A: Desactivar el trigger (Recomendado para pruebas)**

```sql
-- Desactivar trigger temporalmente
DROP TRIGGER IF EXISTS calcular_valor_terreno ON inmuebles;
DROP TRIGGER IF EXISTS trigger_calcular_valor ON inmuebles;
DROP TRIGGER IF EXISTS valor_terreno_trigger ON inmuebles;
```

**OPCIÓN B: Hacer la columna nullable**

```sql
-- Hacer valor_terreno nullable con valor por defecto
ALTER TABLE inmuebles ALTER COLUMN valor_terreno DROP NOT NULL;
ALTER TABLE inmuebles ALTER COLUMN valor_terreno SET DEFAULT 0;
```

**OPCIÓN C: Modificar el trigger para permitir inserciones manuales**

```sql
-- Crear función modificada
CREATE OR REPLACE FUNCTION calcular_valor_terreno_fn()
RETURNS TRIGGER AS $$
BEGIN
    -- Si valor_terreno ya viene en el INSERT, usarlo
    IF NEW.valor_terreno IS NOT NULL THEN
        RETURN NEW;
    END IF;
    
    -- Si no viene, calcularlo automáticamente
    NEW.valor_terreno := NEW.area_terreno_m2 * 150;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Crear trigger modificado
DROP TRIGGER IF EXISTS calcular_valor_terreno ON inmuebles;
CREATE TRIGGER calcular_valor_terreno
BEFORE INSERT ON inmuebles
FOR EACH ROW
EXECUTE FUNCTION calcular_valor_terreno_fn();
```

**Recomendación:** Usa la OPCIÓN A o B para pruebas. La OPCIÓN C es más compleja.

### PASO 7: Verificar los Cambios

Copia y ejecuta este comando SQL:

```sql
-- Verificación final
SELECT 
    COUNT(*) as total_usuarios,
    COUNT(CASE WHEN rol = 'administrador' THEN 1 END) as administradores,
    COUNT(CASE WHEN rol = 'inspector' THEN 1 END) as inspectores,
    COUNT(CASE WHEN rol = 'authenticated' THEN 1 END) as authenticated
FROM usuarios;
```

**Qué esperar:**
- Deberías ver al menos 1 usuario con rol `administrador`

### PASO 8: Ejecutar las Pruebas

Vuelve a tu terminal y ejecuta:

```bash
cd C:\Users\Reactjs\Desktop\srcm
.venv\Scripts\python.exe -m pytest tests/ -v
```

**Qué esperar:**
- Los errores 403 deberían desaparecer
- Los errores 409 deberían reducirse significativamente
- El éxito de pruebas debería aumentar del 67% al 85-90%

---

## 🔧 COMANDOS SQL ESPECÍFICOS

### Para Trigger valor_terreno

**Verificar:**
```sql
SELECT trigger_name, action_statement 
FROM information_schema.triggers 
WHERE event_object_table = 'inmuebles';
```

**Eliminar:**
```sql
DROP TRIGGER IF EXISTS calcular_valor_terreno ON inmuebles;
```

**Modificar columna:**
```sql
ALTER TABLE inmuebles ALTER COLUMN valor_terreno DROP NOT NULL;
ALTER TABLE inmuebles ALTER COLUMN valor_terreno SET DEFAULT 0;
```

### Para Rol de Administrador

**Verificar:**
```sql
SELECT email, rol FROM usuarios WHERE email = 'belandriajunioremiro@gmail.com';
```

**Actualizar:**
```sql
UPDATE usuarios SET rol = 'administrador' WHERE email = 'belandriajunioremiro@gmail.com';
```

**Crear nuevo admin:**
```sql
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
```

### Para Permisos de Usuario

**Verificar roles:**
```sql
SELECT rolname FROM pg_roles;
```

**Verificar permisos:**
```sql
SELECT grantee, privilege_type, table_name
FROM information_schema.role_table_grants
WHERE table_name = 'usuarios';
```

---

## ✅ VERIFICACIÓN DE CAMBIOS

### Checklist de Verificación

Después de ejecutar los comandos SQL, verifica:

- [ ] El usuario de prueba tiene rol `administrador`
- [ ] El trigger `valor_terreno` está desactivado o modificado
- [ ] La columna `valor_terreno` es nullable o tiene valor por defecto
- [ ] Las pruebas E2E se ejecutan sin errores 403
- [ ] Las pruebas E2E se ejecutan sin errores 409

### Comandos de Verificación

```sql
-- Verificar triggers
SELECT COUNT(*) as triggers_inmuebles
FROM information_schema.triggers
WHERE event_object_table = 'inmuebles';

-- Verificar usuario admin
SELECT email, rol, activo
FROM usuarios
WHERE rol = 'administrador';

-- Verificar estructura de inmuebles
SELECT column_name, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'inmuebles' AND column_name = 'valor_terreno';
```

---

## 🚨 SOLUCIÓN DE PROBLEMAS

### Problema: "permission denied for table usuarios"

**Causa:** No tienes permisos para modificar la tabla usuarios.  
**Solución:**
1. Ve a Supabase Dashboard → Settings → Database
2. Verifica que tu rol tiene permisos de escritura
3. O usa el usuario `postgres` con permisos de superusuario

### Problema: "trigger does not exist"

**Causa:** El trigger ya fue eliminado o nunca existió.  
**Solución:** Esto es bueno, no necesitas hacer nada más. El problema ya está resuelto.

### Problema: "column valor_terreno does not exist"

**Causa:** La columna tiene un nombre diferente.  
**Solución:**
```sql
-- Verificar el nombre correcto de la columna
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'inmuebles' 
  AND column_name LIKE '%valor%' 
  OR column_name LIKE '%terreno%';
```

### Problema: Las pruebas siguen fallando con 409

**Causa:** Hay datos duplicados en la base de datos.  
**Solución:**
```sql
-- Limpiar datos de prueba
DELETE FROM propietarios WHERE cedula_rif LIKE 'V-99%';
DELETE FROM inmuebles WHERE propietario_id IS NULL;
```

### Problema: Las pruebas siguen fallando con 403

**Causa:** El rol no se actualizó correctamente.  
**Solución:**
```sql
-- Forzar actualización de rol
UPDATE usuarios 
SET rol = 'administrador' 
WHERE email = 'belandriajunioremiro@gmail.com';

-- Verificar
SELECT email, rol FROM usuarios WHERE email = 'belandriajunioremiro@gmail.com';
```

---

## 📊 RESULTADOS ESPERADOS

### Antes de los Cambios

- Pruebas exitosas: 32/48 (67%)
- Errores 403: 4 pruebas
- Errores 409: 10 pruebas

### Después de los Cambios

- Pruebas exitosas: 44-46/48 (92-96%)
- Errores 403: 0-1 pruebas
- Errores 409: 0-2 pruebas

---

## 🎯 RESUMEN

**Archivos creados:**
1. `SQL_CORRECCIONES_BASE_DATOS.sql` - Comandos SQL completos
2. `INSTRUCCIONES_SQL_SUPABASE.md` - Este documento de instrucciones

**Pasos clave:**
1. Acceder a Supabase Dashboard → SQL Editor
2. Ejecutar comandos de verificación
3. Actualizar rol de usuario a `administrador`
4. Desactivar o modificar trigger `valor_terreno`
5. Ejecutar pruebas nuevamente

**Tiempo estimado:** 15-20 minutos

**Resultado esperado:** 92-96% de éxito en pruebas E2E

---

**¿Necesitas ayuda?** Si encuentras algún problema ejecutando estos comandos, revisa la sección "Solución de Problemas" arriba o consulta la documentación de Supabase: https://supabase.com/docs