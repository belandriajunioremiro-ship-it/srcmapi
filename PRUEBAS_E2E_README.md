# Guía Completa de Pruebas E2E - SRCM API

**Sistema de Registro Catastral Municipal - Municipio Torbes, Estado Táchira, Venezuela**

**Versión:** 2.5.0  
**Fecha:** 16 de septiembre de 2026  
**Total Endpoints:** 35  
**Total Tablas BD:** 7

---

## 📋 Índice

- [Introducción](#introducción)
- [Arquitectura de Pruebas](#arquitectura-de-pruebas)
- [Configuración del Entorno de Pruebas](#configuración-del-entorno-de-pruebas)
- [Herramientas Necesarias](#herramientas-necesarias)
- [Estrategia de Pruebas](#estrategia-de-pruebas)
- [Pruebas por Tabla de Base de Datos](#pruebas-por-tabla-de-base-de-datos)
- [Pruebas por Endpoint API](#pruebas-por-endpoint-api)
- [Casos de Prueba E2E Completos](#casos-de-prueba-e2e-completos)
- [Scripts de Prueba](#scripts-de-prueba)
- [Ejecución Automatizada](#ejecución-automatizada)
- [Reportes y Métricas](#reportes-y-métricas)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Introducción

Este documento proporciona una guía completa para implementar pruebas End-to-End (E2E) para el sistema SRCM. Las pruebas E2E simulan el comportamiento de un usuario real interactuando con el sistema completo, desde la interfaz hasta la base de datos.

### Objetivos de las Pruebas E2E

- ✅ **Validar integración completa** entre frontend, backend y base de datos
- ✅ **Verificar flujos de negocio** reales del sistema catastral
- ✅ **Detectar regresiones** en nuevas implementaciones
- ✅ **Asegurar calidad** antes de despliegues a producción
- ✅ **Documentar comportamiento** esperado del sistema

### Alcance

- **35 endpoints API** completamente probados
- **7 tablas de base de datos** con casos de prueba específicos
- **Flujos de negocio** completos (registro → gestión → consulta)
- **Escenarios positivos y negativos** (happy path y edge cases)

---

## 🏗️ Arquitectura de Pruebas

```
┌─────────────────────────────────────────────────────────────┐
│                    Pruebas E2E SRCM                        │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐         ┌─────▼─────┐         ┌────▼────┐
   │ Playwright│         │  Postman  │         │  Curl   │
   │  E2E UI  │         │  Manual   │         │  CLI    │
   └────┬────┘         └─────┬─────┘         └────┬────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   SRCM API FastAPI │
                    │   http://localhost:8000  │
                    └─────────┬─────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐         ┌─────▼─────┐         ┌────▼────┐
   │ Inmuebles│         │Propietarios│         │Usuarios  │
   │ Router  │         │  Router   │         │ Router  │
   └────┬────┘         └─────┬─────┘         └────┬────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Servicios Python  │
                    │  (Business Logic)│
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │   SQLAlchemy ORM  │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │   PostgreSQL +     │
                    │   PostGIS (Supabase)│
                    └───────────────────┘
```

---

## ⚙️ Configuración del Entorno de Pruebas

### 1. Base de Datos de Pruebas

```bash
# Crear proyecto separado en Supabase para pruebas
# Nombre: srcm-pruebas
# Región: same as production

# Ejecutar script SQL completo en ambiente de pruebas
psql -h db.xxx.supabase.co -U postgres -d srcm-pruebas -f srcm_supabase_completo.sql
```

### 2. Variables de Entorno para Pruebas

```env
# .env.test
APP_NAME=SRCM API - Pruebas
APP_ENV=testing
DEBUG=True
API_V1_PREFIX=/api/v1

# Base de datos de pruebas
DATABASE_URL=postgresql://postgres:[password]@[test-project-ref].supabase.co:5432/postgres

# Supabase Auth (pruebas)
SUPABASE_URL=https://[test-project-ref].supabase.co
SUPABASE_ANON_KEY=[test-anon-key]
SUPABASE_SERVICE_ROLE_KEY=[test-service-role-key]
SUPABASE_JWT_SECRET=[test-jwt-secret]

# Seguridad
SECRET_KEY=test-secret-key-for-testing-only
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALGORITHM=HS256

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:54545

# Storage
SUPABASE_STORAGE_BUCKET=catastro-archivos-test

# Configuración catastral
CODIGO_ESTADO=20
CODIGO_MUNICIPIO=27
CODIGO_PARROQUIA=01
SRID_UTM=2201
```

### 3. Usuarios de Prueba

```sql
-- Crear usuarios de prueba en Supabase Auth
-- Usuario Administrador de Pruebas
INSERT INTO usuarios (id, cedula, nombre, apellido, email, rol, activo)
VALUES (
  '00000000-0000-0000-0000-000000000001',
  'V-12345678',
  'Admin',
  'Pruebas',
  'admin@pruebas.srcm',
  'administrador',
  true
);

-- Usuario Inspector de Pruebas
INSERT INTO usuarios (id, cedula, nombre, apellido, email, rol, activo)
VALUES (
  '00000000-0000-0000-0000-000000000002',
  'V-87654321',
  'Inspector',
  'Pruebas',
  'inspector@pruebas.srcm',
  'inspector',
  true
);
```

---

## 🛠️ Herramientas Necesarias

### Para Pruebas E2E Automatizadas

```bash
# Instalación de dependencias
pip install pytest pytest-asyncio httpx playwright pytest-playwright
```

### Para Pruebas Manuales

- **Postman** o **Insomnia** - Para pruebas manuales de API
- **pgAdmin** o **DBeaver** - Para inspección directa de base de datos
- **Browser** - Para pruebas UI manuales

### Dependencias Python para Testing

```txt
# requirements-test.txt
pytest==8.3.0
pytest-asyncio==0.24.0
httpx==0.27.0
playwright==1.48.0
pytest-playwright==0.5.0
faker==30.0.0
pydantic==2.9.2
```

---

## 📊 Estrategia de Pruebas

### Matriz de Pruebas

| Prioridad | Tipo | Cobertura | Frecuencia |
|-----------|------|-----------|-----------|
| **P0** | E2E Críticos | 100% | Cada commit |
| **P1** | E2E Importantes | 80% | Diario |
| **P2** | E2E Normales | 50% | Semanal |
| **P3** | E2E Edge Cases | 20% | Mensual |

### Categorización de Casos de Prueba

#### **P0 - Críticos (Si fallan, bloquean release)**
- Autenticación y autorización
- CRUD básico de inmuebles
- Generación de cédulas catastrales
- Mapa catastral

#### **P1 - Importantes (Impactan negocio principal)**
- Gestión de propietarios
- Configuración catastral
- Estadísticas y reportes

#### **P2 - Normales (Funcionalidad secundaria)**
- Gestión de fotos y hitos
- Validaciones topológicas
- Auditoría de solapamientos

#### **P3 - Edge Cases (Situaciones excepcionales)**
- Manejo de errores de red
- Validaciones de datos extremos
- Concurrencia

---

## 🗄️ Pruebas por Tabla de Base de Datos

### 1. Tabla: `configuracion_catastral`

**Propósito:** Almacena valores catastrales y datos institucionales

#### Casos de Prueba

| ID | Caso | Entrada | Esperado | Prioridad |
|----|------|---------|----------|-----------|
| CC-001 | Crear configuración inicial | Valores válidos | Registro creado | P0 |
| CC-002 | Actualizar valor m² terreno | Nuevo valor | Valor actualizado | P0 |
| CC-003 | Actualizar datos institucionales | Nuevos autoridades | Datos actualizados | P1 |
| CC-004 | Validar valor negativo | valor_m2_terreno = -1 | Error de validación | P2 |
| CC-005 | Actualizar vigencia cédulas | Nuevos meses | Vigencia actualizada | P1 |

#### Script de Prueba SQL

```sql
-- CC-001: Crear configuración inicial
INSERT INTO configuracion_catastral (
  id, codigo_estado, codigo_municipio, codigo_parroquia,
  valor_m2_terreno, valor_m2_construccion, valor_m2_comercio,
  vigencia_cedula_meses, nombre_estado, nombre_municipio
) VALUES (
  1, '20', '27', '01',
  100.00, 150.00, 200.00,
  12, 'Táchira', 'Torbes'
);

-- Verificación
SELECT * FROM configuracion_catastral WHERE id = 1;

-- CC-002: Actualizar valor m² terreno
UPDATE configuracion_catastral 
SET valor_m2_terreno = 120.50 
WHERE id = 1;

-- Verificación
SELECT valor_m2_terreno FROM configuracion_catastral WHERE id = 1;
-- Esperado: 120.50
```

---

### 2. Tabla: `configuracion_sistema`

**Propósito:** Configuración del sistema para validación de códigos

#### Casos de Prueba

| ID | Caso | Entrada | Esperado | Prioridad |
|----|------|---------|----------|-----------|
| CS-001 | Crear configuración sistema | Códigos válidos | Registro creado | P0 |
| CS-002 | Sincronizar con configuración catastral | Mismos códigos | Sincronización exitosa | P0 |
| CS-003 | Código estado inválido | estado_codigo = '99' | Error validación | P2 |
| CS-004 | Actualizar códigos geográficos | Nuevos códigos | Actualización exitosa | P1 |

#### Script de Prueba SQL

```sql
-- CS-001: Crear configuración sistema
INSERT INTO configuracion_sistema (
  id, estado_codigo, municipio_codigo, parroquia_codigo, nombre_municipio
) VALUES (
  1, '20', '27', '01', 'Torbes'
);

-- Verificación
SELECT * FROM configuracion_sistema WHERE id = 1;

-- CS-002: Verificar sincronización
SELECT 
  cc.codigo_estado = cs.estado_codigo AS estado_match,
  cc.codigo_municipio = cs.municipio_codigo AS municipio_match,
  cc.codigo_parroquia = cs.parroquia_codigo AS parroquia_match
FROM configuracion_catastral cc
CROSS JOIN configuracion_sistema cs
WHERE cc.id = 1 AND cs.id = 1;
-- Esperado: true, true, true
```

---

### 3. Tabla: `usuarios`

**Propósito:** Gestión de usuarios del sistema

#### Casos de Prueba

| ID | Caso | Entrada | Esperado | Prioridad |
|----|------|---------|----------|-----------|
| US-001 | Crear usuario administrador | Datos válidos admin | Usuario creado con rol admin | P0 |
| US-002 | Crear usuario inspector | Datos válidos inspector | Usuario creado con rol inspector | P0 |
| US-003 | Cambiar rol de usuario | Nuevo rol | Rol actualizado | P1 |
| US-004 | Desactivar usuario | activo = false | Usuario desactivado | P1 |
| US-005 | Cédula duplicada | Cédula existente | Error de duplicidad | P2 |
| US-006 | Email inválido | email = 'invalido' | Error de validación | P2 |

#### Script de Prueba SQL

```sql
-- US-001: Crear usuario administrador
INSERT INTO usuarios (
  id, cedula, nombre, apellido, email, rol, activo
) VALUES (
  gen_random_uuid(),
  'V-12345678',
  'Admin',
  'Pruebas',
  'admin@pruebas.srcm',
  'administrador',
  true
);

-- Verificación
SELECT * FROM usuarios WHERE cedula = 'V-12345678';
-- Esperado: rol = 'administrador', activo = true

-- US-003: Cambiar rol de usuario
UPDATE usuarios 
SET rol = 'inspector' 
WHERE cedula = 'V-12345678';

-- Verificación
SELECT rol FROM usuarios WHERE cedula = 'V-12345678';
-- Esperado: 'inspector'
```

---

### 4. Tabla: `propietarios`

**Propósito:** Gestión de propietarios de inmuebles

#### Casos de Prueba

| ID | Caso | Entrada | Esperado | Prioridad |
|----|------|---------|----------|-----------|
| PR-001 | Crear propietario completo | Todos los campos | Propietario creado | P0 |
| PR-002 | Crear propietario mínimo | Campos requeridos | Propietario creado | P0 |
| PR-003 | Actualizar propietario | Nuevos datos | Datos actualizados | P1 |
| PR-004 | Eliminar propietario sin inmuebles | ID propietario | Propietario eliminado | P1 |
| PR-005 | Eliminar propietario con inmuebles | ID propietario con inmuebles | Error restricción | P2 |
| PR-006 | Cédula/RIF duplicado | Cédula existente | Error duplicidad | P2 |

#### Script de Prueba SQL

```sql
-- PR-001: Crear propietario completo
INSERT INTO propietarios (
  cedula_rif, nombre, apellido, direccion, telefono, email
) VALUES (
  'V-15123456',
  'Juan',
  'Pérez',
  'Calle Principal #123',
  '0414-1234567',
  'juan.perez@email.com'
);

-- Verificación
SELECT * FROM propietarios WHERE cedula_rif = 'V-15123456';
-- Esperado: Registro con todos los campos

-- PR-004: Intentar eliminar propietario (sin inmuebles)
DELETE FROM propietarios WHERE cedula_rif = 'V-15123456';

-- Verificación
SELECT * FROM propietarios WHERE cedula_rif = 'V-15123456';
-- Esperado: 0 filas (eliminado exitosamente)
```

---

### 5. Tabla: `inmuebles`

**Propósito:** Gestión de inmuebles catastrales (tabla principal)

#### Casos de Prueba

| ID | Caso | Entrada | Esperado | Prioridad |
|----|------|---------|----------|-----------|
| IN-001 | Crear inmueble completo | Todos los campos válidos | Inmueble creado con código auto | P0 |
| IN-002 | Crear inmueble con geometría válida | Polígono GeoJSON válido | Inmueble creado con coordenadas | P0 |
| IN-003 | Crear inmueble sin propietario | Sin propietario_id | Error de validación | P0 |
| IN-004 | Actualizar inmueble | Nuevos datos | Datos actualizados | P1 |
| IN-005 | Eliminar inmueble | ID inmueble | Inmueble eliminado | P1 |
| IN-006 | Geometría inválida | Polígono inválido | Error validación geometría | P2 |
| IN-007 | Solapamiento de polígonos | Polígono solapado | Error trigger prevención | P2 |
| IN-008 | Actualizar fecha emisión | Nueva fecha | Vigencia recalculada | P1 |

#### Script de Prueba SQL

```sql
-- PRIMERO: Crear propietario para asociar
INSERT INTO propietarios (cedula_rif, nombre, apellido)
VALUES ('V-99887766', 'María', 'García');

-- IN-001: Crear inmueble completo
INSERT INTO inmuebles (
  propietario_id,
  direccion,
  sector,
  tenencia,
  area_terreno_m2,
  area_construccion_m2,
  geometry
) VALUES (
  (SELECT id FROM propietarios WHERE cedula_rif = 'V-99887766'),
  'Calle de Prueba #456',
  '06',
  'propio',
  150.50,
  120.00,
  ST_GeomFromText('POLYGON((-72.3456 8.1234, -72.3457 8.1235, -72.3458 8.1236, -72.3456 8.1234))', 4326)
);

-- Verificación
SELECT 
  codigo_catastral,
  direccion,
  valor_catastral_total
FROM inmuebles 
WHERE direccion = 'Calle de Prueba #456';
-- Esperado: Código generado, dirección correcta, valor calculado

-- IN-008: Actualizar fecha emisión y verificar vigencia
UPDATE inmuebles 
SET fecha_emision = '2024-01-15' 
WHERE direccion = 'Calle de Prueba #456';

-- Verificación
SELECT 
  fecha_emision,
  vigente_hasta,
  vigente_hasta - fecha_emision AS dias_vigencia
FROM inmuebles 
WHERE direccion = 'Calle de Prueba #456';
-- Esperado: vigente_hasta = fecha_emision + vigencia_cedula_meses
```

---

### 6. Tabla: `hitos_prediales`

**Propósito:** Almacena vértices GPS de polígonos (linderos)

#### Casos de Prueba

| ID | Caso | Entrada | Esperado | Prioridad |
|----|------|---------|----------|-----------|
| HI-001 | Agregar hito a inmueble | Coordenadas válidas | Hito creado | P1 |
| HI-002 | Listar hitos de inmueble | ID inmueble | Lista de hitos | P1 |
| HI-003 | Eliminar hito | ID hito | Hito eliminado | P2 |
| HI-004 | Hito con coordenadas inválidas | Coordenadas fuera rango | Error validación | P2 |
| HI-005 | Ordenar hitos por índice | Varios hitos | Orden correcto por índice | P2 |

#### Script de Prueba SQL

```sql
-- PRIMERO: Crear inmueble para asociar hitos
INSERT INTO inmuebles (propietario_id, direccion, geometry)
VALUES (
  (SELECT id FROM propietarios LIMIT 1),
  'Inmueble para Hitos',
  ST_GeomFromText('POLYGON((-72.3456 8.1234, -72.3457 8.1235, -72.3458 8.1236, -72.3456 8.1234))', 4326)
);

-- HI-001: Agregar hito a inmueble
INSERT INTO hitos_prediales (
  inmueble_id,
  indice_vertice,
  descripcion,
  utm_norte,
  utm_este,
  latitud,
  longitud
) VALUES (
  (SELECT id FROM inmuebles WHERE direccion = 'Inmueble para Hitos'),
  1,
  'Vértice Norte',
  1125000.00,
  525000.00,
  8.1234,
  -72.3456
);

-- Verificación
SELECT * FROM hitos_prediales WHERE descripcion = 'Vértice Norte';
-- Esperado: Hito creado con índice 1

-- HI-002: Listar hitos de inmueble
SELECT 
  indice_vertice,
  descripcion,
  latitud,
  longitud
FROM hitos_prediales 
WHERE inmueble_id = (SELECT id FROM inmuebles WHERE direccion = 'Inmueble para Hitos')
ORDER BY indice_vertice;
-- Esperado: Lista ordenada por índice_vertice
```

---

### 7. Tabla: `fotos_inmueble`

**Propósito:** Almacena URLs de fotos de inmuebles

#### Casos de Prueba

| ID | Caso | Entrada | Esperado | Prioridad |
|----|------|---------|----------|-----------|
| FO-001 | Agregar foto a inmueble | URL válida | Foto creada | P1 |
| FO-002 | Listar fotos de inmueble | ID inmueble | Lista de fotos | P1 |
| FO-003 | Eliminar foto | ID foto | Foto eliminada | P2 |
| FO-004 | URL inválida | URL mal formateada | Error validación | P2 |
| FO-005 | Multiple fotos mismo inmueble | Varias URLs | Todas creadas | P2 |

#### Script de Prueba SQL

```sql
-- PRIMERO: Crear inmueble para asociar fotos
INSERT INTO inmuebles (propietario_id, direccion, geometry)
VALUES (
  (SELECT id FROM propietarios LIMIT 1),
  'Inmueble para Fotos',
  ST_GeomFromText('POLYGON((-72.3456 8.1234, -72.3457 8.1235, -72.3458 8.1236, -72.3456 8.1234))', 4326)
);

-- FO-001: Agregar foto a inmueble
INSERT INTO fotos_inmueble (
  inmueble_id,
  url,
  descripcion,
  tipo
) VALUES (
  (SELECT id FROM inmuebles WHERE direccion = 'Inmueble para Fotos'),
  'https://storage.srcm.ve/fotos/test001.jpg',
  'Foto frontal del inmueble',
  'frontal'
);

-- Verificación
SELECT * FROM fotos_inmueble WHERE url LIKE '%test001.jpg';
-- Esperado: Foto creada con tipo 'frontal'

-- FO-002: Listar fotos de inmueble
SELECT 
  url,
  descripcion,
  tipo,
  created_at
FROM fotos_inmueble 
WHERE inmueble_id = (SELECT id FROM inmuebles WHERE direccion = 'Inmueble para Fotos')
ORDER BY created_at;
-- Esperado: Lista de fotos ordenadas por fecha
```

---

## 🌐 Pruebas por Endpoint API

### Categoría: Salud (2 endpoints)

#### 1. `GET /` - Raíz del sistema

**Propósito:** Verificar que el servicio está activo

| Caso | Método | Esperado | Prioridad |
|------|--------|----------|-----------|
| SC-001 | GET / | 200 OK con respuesta básica | P0 |

**Prueba con Curl:**
```bash
curl -X GET http://localhost:8000/
```

**Respuesta Esperada:**
```json
{
  "servicio": "SRCM API - Sistema de Registro Catastral Municipal - 35 Endpoints",
  "estado": "activo",
  "documentacion": "/docs"
}
```

---

#### 2. `GET /salud` - Health Check

**Propósito:** Health check para monitoreo

| Caso | Método | Esperado | Prioridad |
|------|--------|----------|-----------|
| SC-002 | GET /salud | 200 OK con status ok | P0 |

**Prueba con Curl:**
```bash
curl -X GET http://localhost:8000/salud
```

**Respuesta Esperada:**
```json
{
  "status": "ok"
}
```

---

### Categoría: Inmuebles (13 endpoints)

#### 1. `POST /api/v1/inmuebles` - Crear Inmueble

**Propósito:** Crear nuevo inmueble catastral

| Caso | Request Body | Esperado | Prioridad |
|------|--------------|----------|-----------|
| IN-API-001 | Datos completos válidos | 201 Created + código generado | P0 |
| IN-API-002 | Sin propietario_id | 422 Validation Error | P0 |
| IN-API-003 | Geometría inválida | 422 Validation Error | P0 |
| IN-API-004 | Polígono solapado | 409 Conflict (trigger) | P2 |
| IN-API-005 | Campos faltantes | 422 Validation Error | P1 |

**Prueba con Curl:**
```bash
curl -X POST http://localhost:8000/api/v1/inmuebles \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "propietario_id": "uuid-del-propietario",
    "direccion": "Calle de Prueba #123",
    "sector": "06",
    "tenencia": "propio",
    "area_terreno_m2": 150.50,
    "area_construccion_m2": 120.00,
    "geometry": {
      "type": "Polygon",
      "coordinates": [[
        [-72.3456, 8.1234],
        [-72.3457, 8.1235],
        [-72.3458, 8.1236],
        [-72.3456, 8.1234]
      ]]
    }
  }'
```

**Respuesta Esperada (201):**
```json
{
  "id": "uuid-generado",
  "codigo_catastral": "20-27-01-06-049-135-000-000-000",
  "direccion": "Calle de Prueba #123",
  "valor_catastral_total": 27900.00,
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

#### 2. `GET /api/v1/inmuebles` - Listar Inmuebles

**Propósito:** Listar inmuebles con paginación y filtros

| Caso | Query Params | Esperado | Prioridad |
|------|--------------|----------|-----------|
| IN-API-006 | Sin filtros | Lista paginada | P0 |
| IN-API-007 | Filtro por sector | Solo del sector | P1 |
| IN-API-008 | Filtro por tenencia | Solo de esa tenencia | P1 |
| IN-API-009 | Búsqueda por dirección | Resultados coincidentes | P1 |
| IN-API-010 | Paginación (página 2) | Segunda página | P1 |
| IN-API-011 | Filtro por vigencia | Solo vigentes/vencidos | P2 |

**Prueba con Curl:**
```bash
curl -X GET "http://localhost:8000/api/v1/inmuebles?pagina=1&por_pagina=10&sector=06" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta Esperada (200):**
```json
{
  "total": 25,
  "pagina": 1,
  "por_pagina": 10,
  "resultados": [
    {
      "id": "uuid-1",
      "codigo_catastral": "20-27-01-06-049-135-000-000-000",
      "direccion": "Calle Principal #123",
      "sector": "06",
      "valor_catastral_total": 27900.00
    }
  ]
}
```

---

#### 3. `GET /api/v1/inmuebles/{id}` - Obtener Inmueble

**Propósito:** Obtener detalles de un inmueble específico

| Caso | ID | Esperado | Prioridad |
|------|----|----------|-----------|
| IN-API-012 | ID válido | Datos completos del inmueble | P0 |
| IN-API-013 | ID inválido | 404 Not Found | P0 |
| IN-API-014 | ID formateado incorrecto | 422 Validation Error | P2 |

**Prueba con Curl:**
```bash
curl -X GET http://localhost:8000/api/v1/inmuebles/uuid-del-inmueble \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

#### 4. `PATCH /api/v1/inmuebles/{id}` - Actualizar Inmueble

**Propósito:** Actualizar datos de un inmueble

| Caso | Request Body | Esperado | Prioridad |
|------|--------------|----------|-----------|
| IN-API-015 | Actualización válida | 200 OK + datos actualizados | P1 |
| IN-API-016 | Actualización geometría solapada | 409 Conflict | P2 |
| IN-API-017 | Actualización código existente | 409 Conflict | P2 |

**Prueba con Curl:**
```bash
curl -X PATCH http://localhost:8000/api/v1/inmuebles/uuid-del-inmueble \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "direccion": "Calle Actualizada #456",
    "tenencia": "arrendado"
  }'
```

---

#### 5. `DELETE /api/v1/inmuebles/{id}` - Eliminar Inmueble

**Propósito:** Eliminar un inmueble del sistema

| Caso | ID | Esperado | Prioridad |
|------|----|----------|-----------|
| IN-API-018 | ID válido | 204 No Content | P1 |
| IN-API-019 | ID inválido | 404 Not Found | P0 |
| IN-API-020 | ID sin permisos admin | 403 Forbidden | P1 |

**Prueba con Curl:**
```bash
curl -X DELETE http://localhost:8000/api/v1/inmuebles/uuid-del-inmueble \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

#### 6. `GET /api/v1/inmuebles/{id}/cedula` - Descargar PDF Cédula

**Propósito:** Generar y descargar PDF de cédula catastral

| Caso | ID | Esperado | Prioridad |
|------|----|----------|-----------|
| IN-API-021 | ID válido con datos completos | 200 OK + PDF | P0 |
| IN-API-022 | ID sin datos cédula | 404 Not Found | P1 |
| IN-API-023 | ID inválido | 404 Not Found | P0 |

**Prueba con Curl:**
```bash
curl -X GET http://localhost:8000/api/v1/inmuebles/uuid-del-inmueble/cedula \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --output cedula_catastral.pdf
```

---

#### 7. `GET /api/v1/inmuebles/{id}/cedula-datos` - Obtener Datos Cédula

**Propósito:** Obtener datos para generar PDF desde frontend

| Caso | ID | Esperado | Prioridad |
|------|----|----------|-----------|
| IN-API-024 | ID válido | JSON con 60+ campos | P0 |
| IN-API-025 | ID inválido | 404 Not Found | P0 |

**Prueba con Curl:**
```bash
curl -X GET http://localhost:8000/api/v1/inmuebles/uuid-del-inmueble/cedula-datos \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta Esperada (200):**
```json
{
  "inmueble_id": "uuid",
  "codigo_catastral": "20270106049135000000000",
  "expediente_numero": "EXP-2024-0001",
  "propietario_nombre": "Juan Pérez",
  "direccion": "Calle Principal #123",
  "valor_catastral_total": 27900.00,
  "nombre_estado": "Táchira",
  "nombre_municipio": "Torbes",
  "...": "60+ campos más"
}
```

---

#### 8-13. Endpoints de Hitos y Fotos

| Endpoint | Método | Casos de Prueba | Prioridad |
|----------|--------|-----------------|-----------|
| `/api/v1/inmuebles/{id}/hitos` | POST | HI-API-001: Crear hito válido | P1 |
| `/api/v1/inmuebles/{id}/hitos` | GET | HI-API-002: Listar hitos | P1 |
| `/api/v1/inmuebles/{id}/hitos/{hito_id}` | DELETE | HI-API-003: Eliminar hito | P2 |
| `/api/v1/inmuebles/{id}/fotos` | POST | FO-API-001: Agregar foto | P1 |
| `/api/v1/inmuebles/{id}/fotos` | GET | FO-API-002: Listar fotos | P1 |
| `/api/v1/inmuebles/{id}/fotos/{foto_id}` | DELETE | FO-API-003: Eliminar foto | P2 |

---

### Categoría: Propietarios (6 endpoints)

#### 1. `POST /api/v1/propietarios` - Crear Propietario

| Caso | Request Body | Esperado | Prioridad |
|------|--------------|----------|-----------|
| PR-API-001 | Datos completos válidos | 201 Created | P0 |
| PR-API-002 | Cédula duplicada | 409 Conflict | P2 |
| PR-API-003 | Email inválido | 422 Validation Error | P2 |

**Prueba con Curl:**
```bash
curl -X POST http://localhost:8000/api/v1/propietarios \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cedula_rif": "V-15987654",
    "nombre": "Carlos",
    "apellido": "Rodríguez",
    "direccion": "Av. Bolívar #789",
    "telefono": "0414-9876543",
    "email": "carlos.rodriguez@email.com"
  }'
```

---

#### 2-6. Endpoints CRUD Propietarios

| Endpoint | Método | Casos de Prueba | Prioridad |
|----------|--------|-----------------|-----------|
| `/api/v1/propietarios` | GET | PR-API-004: Listar paginado | P0 |
| `/api/v1/propietarios/{id}` | GET | PR-API-005: Obtener propietario | P0 |
| `/api/v1/propietarios/{id}` | PATCH | PR-API-006: Actualizar propietario | P1 |
| `/api/v1/propietarios/{id}` | DELETE | PR-API-007: Eliminar sin inmuebles | P1 |
| `/api/v1/propietarios/{id}/inmuebles` | GET | PR-API-008: Listar inmuebles | P1 |

---

### Categoría: Catastro (5 endpoints)

#### 1. `GET /api/v1/catastro/mapa` - Mapa Catastral

| Caso | Query Params | Esperado | Prioridad |
|------|--------------|----------|-----------|
| CA-API-001 | Sin bbox | GeoJSON de todos los predios | P0 |
| CA-API-002 | Con bbox válido | GeoJSON del área visible | P0 |
| CA-API-003 | Bbox inválido | 422 Validation Error | P2 |

**Prueba con Curl:**
```bash
curl -X GET "http://localhost:8000/api/v1/catastro/mapa?min_lon=-72.35&min_lat=8.12&max_lon=-72.34&max_lat=8.13" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta Esperada (200):**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[...]]
      },
      "properties": {
        "id": "uuid",
        "codigo_catastral": "20-27-01-06-049-135-000-000-000",
        "direccion": "Calle Principal #123"
      }
    }
  ]
}
```

---

#### 2-5. Endpoints Catastro

| Endpoint | Método | Casos de Prueba | Prioridad |
|----------|--------|-----------------|-----------|
| `/api/v1/catastro/estadisticas` | GET | CA-API-004: Estadísticas generales | P0 |
| `/api/v1/catastro/por-sector` | GET | CA-API-005: Predios por sector | P1 |
| `/api/v1/catastro/solapamientos` | GET | CA-API-006: Auditoría topológica | P2 |
| `/api/v1/catastro/sectores` | GET | CA-API-007: Listar sectores | P1 |

---

### Categoría: Configuración (5 endpoints)

#### 1. `GET /api/v1/configuracion/catastral` - Obtener Configuración

| Caso | Esperado | Prioridad |
|------|----------|-----------|
| CF-API-001 | Configuración completa | 200 OK + todos los campos | P0 |
| CF-API-002 | Sin configuración | 404 Not Found | P1 |

---

#### 2-5. Endpoints Configuración

| Endpoint | Método | Casos de Prueba | Prioridad |
|----------|--------|-----------------|-----------|
| `/api/v1/configuracion/catastral` | PATCH | CF-API-003: Actualizar configuración | P1 |
| `/api/v1/configuracion/sistema` | GET | CF-API-004: Obtener config sistema | P0 |
| `/api/v1/configuracion/sistema` | PATCH | CF-API-005: Actualizar config sistema | P1 |
| `/api/v1/configuracion/catastral/pdf-config` | GET | CF-API-006: Configuración PDF | P1 |

---

### Categoría: Usuarios (4 endpoints)

#### 1. `GET /api/v1/usuarios/me` - Perfil Actual

| Caso | Esperado | Prioridad |
|------|----------|-----------|
| US-API-001 | Usuario autenticado | 200 OK + perfil | P0 |
| US-API-002 | Sin autenticación | 401 Unauthorized | P0 |

---

#### 2-4. Endpoints Usuarios

| Endpoint | Método | Casos de Prueba | Prioridad |
|----------|--------|-----------------|-----------|
| `/api/v1/usuarios` | GET | US-API-003: Listar usuarios (admin) | P1 |
| `/api/v1/usuarios/{id}/rol` | PATCH | US-API-004: Cambiar rol (admin) | P1 |
| `/api/v1/usuarios/{id}/estado` | PATCH | US-API-005: Activar/desactivar | P1 |

---

## 🎭 Casos de Prueba E2E Completos

### Caso E2E-001: Flujo Completo de Registro de Inmueble

**Descripción:** Simula el proceso completo de registrar un nuevo inmueble en el sistema

**Pasos:**
1. Crear propietario
2. Crear inmueble asociado al propietario
3. Verificar código catastral generado
4. Agregar hitos prediales
5. Agregar foto del inmueble
6. Generar cédula catastral
7. Verificar que todo esté en la base de datos

**Script de Prueba (Python):**

```python
import pytest
import httpx
import uuid
from datetime import datetime

@pytest.mark.e2e
async def test_flujo_completo_registro_inmueble():
    """E2E: Flujo completo de registro de inmueble"""
    
    async with httpx.AsyncClient() as client:
        # 1. Login para obtener token
        login_response = await client.post(
            "https://api.pruebas.srcm/api/v1/auth/login",
            json={"email": "admin@pruebas.srcm", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Crear propietario
        propietario_data = {
            "cedula_rif": "V-E2E-001",
            "nombre": "E2E",
            "apellido": "Test",
            "direccion": "Calle E2E #001",
            "telefono": "0414-0000001",
            "email": "e2e@test.srcm"
        }
        
        prop_response = await client.post(
            "http://localhost:8000/api/v1/propietarios",
            json=propietario_data,
            headers=headers
        )
        assert prop_response.status_code == 201
        propietario_id = prop_response.json()["id"]
        
        # 3. Crear inmueble
        inmueble_data = {
            "propietario_id": propietario_id,
            "direccion": "Calle E2E #002",
            "sector": "06",
            "tenencia": "propio",
            "area_terreno_m2": 200.00,
            "area_construccion_m2": 150.00,
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-72.3456, 8.1234],
                    [-72.3457, 8.1235],
                    [-72.3458, 8.1236],
                    [-72.3456, 8.1234]
                ]]
            }
        }
        
        inm_response = await client.post(
            "http://localhost:8000/api/v1/inmuebles",
            json=inmueble_data,
            headers=headers
        )
        assert inm_response.status_code == 201
        inmueble = inm_response.json()
        inmueble_id = inmueble["id"]
        
        # 4. Verificar código catastral generado
        assert inmueble["codigo_catastral"] is not None
        assert len(inmueble["codigo_catastral"]) == 23
        assert inmueble["valor_catastral_total"] > 0
        
        # 5. Agregar hito predial
        hito_data = {
            "indice_vertice": 1,
            "descripcion": "Vértice E2E",
            "utm_norte": 1125000.00,
            "utm_este": 525000.00,
            "latitud": 8.1234,
            "longitud": -72.3456
        }
        
        hito_response = await client.post(
            f"http://localhost:8000/api/v1/inmuebles/{inmueble_id}/hitos",
            json=hito_data,
            headers=headers
        )
        assert hito_response.status_code == 201
        
        # 6. Agregar foto
        foto_data = {
            "url": "https://storage.srcm.ve/fotos/e2e-test.jpg",
            "descripcion": "Foto E2E",
            "tipo": "frontal"
        }
        
        foto_response = await client.post(
            f"http://localhost:8000/api/v1/inmuebles/{inmueble_id}/fotos",
            json=foto_data,
            headers=headers
        )
        assert foto_response.status_code == 201
        
        # 7. Obtener datos para cédula
        cedula_response = await client.get(
            f"http://localhost:8000/api/v1/inmuebles/{inmueble_id}/cedula-datos",
            headers=headers
        )
        assert cedula_response.status_code == 200
        cedula_data = cedula_response.json()
        
        # 8. Verificar datos completos
        assert cedula_data["propietario_nombre"] == "E2E Test"
        assert cedula_data["direccion"] == "Calle E2E #002"
        assert cedula_data["valor_catastral_total"] > 0
        assert cedula_data["nombre_estado"] == "Táchira"
        assert cedula_data["nombre_municipio"] == "Torbes"
        
        print(f"✅ Test E2E completado: Inmueble {inmueble['codigo_catastral']} registrado exitosamente")
```

---

### Caso E2E-002: Flujo de Gestión de Configuración Catastral

**Descripción:** Simula la actualización de valores catastrales y verificación de impacto

**Pasos:**
1. Obtener configuración actual
2. Actualizar valor por m² de terreno
3. Verificar que la actualización se aplicó
4. Crear inmueble nuevo
5. Verificar que usa nuevos valores

**Script de Prueba (Python):**

```python
@pytest.mark.e2e
async def test_flujo_configuracion_catastral():
    """E2E: Actualización de configuración catastral"""
    
    async with httpx.AsyncClient() as client:
        # Login
        token = await obtener_token_admin(client)
        headers = {"Authorization": f"Bearer {token}"}
        
        # 1. Obtener configuración actual
        config_response = await client.get(
            "http://localhost:8000/api/v1/configuracion/catastral",
            headers=headers
        )
        assert config_response.status_code == 200
        config_actual = config_response.json()
        valor_anterior = config_actual["valor_m2_terreno"]
        
        # 2. Actualizar valor m² terreno
        nuevo_valor = valor_anterior + 50.00
        update_response = await client.patch(
            "http://localhost:8000/api/v1/configuracion/catastral",
            json={"valor_m2_terreno": nuevo_valor},
            headers=headers
        )
        assert update_response.status_code == 200
        
        # 3. Verificar actualización
        verify_response = await client.get(
            "http://localhost:8000/api/v1/configuracion/catastral",
            headers=headers
        )
        config_actualizado = verify_response.json()
        assert config_actualizado["valor_m2_terreno"] == nuevo_valor
        
        # 4. Crear inmueble para verificar que usa nuevos valores
        # (implementación similar al caso anterior)
        
        print(f"✅ Configuración actualizada: valor m² terreno {valor_anterior} → {nuevo_valor}")
```

---

### Caso E2E-003: Flujo de Consulta de Mapa Catastral

**Descripción:** Simula la consulta del mapa catastral con filtros

**Pasos:**
1. Consultar mapa sin filtros
2. Consultar mapa con bbox específico
3. Consultar estadísticas generales
4. Consultar predios por sector
5. Verificar consistencia de datos

**Script de Prueba (Python):**

```python
@pytest.mark.e2e
async def test_flujo_mapa_catastral():
    """E2E: Consulta de mapa catastral con filtros"""
    
    async with httpx.AsyncClient() as client:
        token = await obtener_token_inspector(client)
        headers = {"Authorization": f"Bearer {token}"}
        
        # 1. Mapa completo
        mapa_response = await client.get(
            "http://localhost:8000/api/v1/catastro/mapa",
            headers=headers
        )
        assert mapa_response.status_code == 200
        mapa_completo = mapa_response.json()
        assert mapa_completo["type"] == "FeatureCollection"
        total_features_completo = len(mapa_completo["features"])
        
        # 2. Mapa con bbox
        bbox_response = await client.get(
            "http://localhost:8000/api/v1/catastro/mapa?min_lon=-72.35&min_lat=8.12&max_lon=-72.34&max_lat=8.13",
            headers=headers
        )
        assert bbox_response.status_code == 200
        mapa_bbox = bbox_response.json()
        total_features_bbox = len(mapa_bbox["features"])
        
        # 3. Verificar que bbox reduce resultados
        assert total_features_bbox <= total_features_completo
        
        # 4. Estadísticas generales
        stats_response = await client.get(
            "http://localhost:8000/api/v1/catastro/estadisticas",
            headers=headers
        )
        assert stats_response.status_code == 200
        estadisticas = stats_response.json()
        assert estadisticas["total_predios"] > 0
        assert estadisticas["superficie_total_m2"] > 0
        
        # 5. Predios por sector
        sector_response = await client.get(
            "http://localhost:8000/api/v1/catastro/por-sector",
            headers=headers
        )
        assert sector_response.status_code == 200
        por_sector = sector_response.json()
        assert len(por_sector) > 0
        
        print(f"✅ Mapa catastral: {total_features_completo} predios totales, {total_features_bbox} en bbox")
```

---

## 🧪 Scripts de Prueba

### Script 1: Setup de Base de Datos de Pruebas

```bash
#!/bin/bash
# setup_test_db.sh

echo "🔄 Configurando base de datos de pruebas..."

# Variables
TEST_DB_URL="postgresql://postgres:[password]@[test-project].supabase.co:5432/postgres"
SQL_FILE="srcm_supabase_completo.sql"

# Ejecutar script SQL
psql $TEST_DB_URL -f $SQL_FILE

# Crear usuarios de prueba
psql $TEST_DB_URL << EOF
-- Insertar usuarios de prueba
INSERT INTO usuarios (id, cedula, nombre, apellido, email, rol, activo)
VALUES 
  ('00000000-0000-0000-0000-000000000001', 'V-12345678', 'Admin', 'Pruebas', 'admin@pruebas.srcm', 'administrador', true),
  ('00000000-0000-0000-0000-000000000002', 'V-87654321', 'Inspector', 'Pruebas', 'inspector@pruebas.srcm', 'inspector', true)
ON CONFLICT DO NOTHING;
EOF

echo "✅ Base de datos de pruebas configurada"
```

### Script 2: Ejecución de Pruebas E2E

```bash
#!/bin/bash
# run_e2e_tests.sh

echo "🧪 Ejecutando pruebas E2E SRCM..."

# Activar entorno virtual
source .venv/Scripts/activate

# Configurar variables de prueba
export APP_ENV=testing
export DATABASE_URL="postgresql://postgres:[password]@[test-project].supabase.co:5432/postgres"

# Ejecutar pruebas E2E
pytest tests_e2e/ -v --tb=short --html=reporte_e2e.html

echo "✅ Pruebas E2E completadas. Ver reporte en reporte_e2e.html"
```

### Script 3: Limpieza de Datos de Pruebas

```bash
#!/bin/bash
# cleanup_test_data.sh

echo "🧹 Limpiando datos de pruebas..."

psql $DATABASE_URL << EOF
-- Limpiar inmuebles de prueba
DELETE FROM inmuebles WHERE direccion LIKE '%E2E%' OR direccion LIKE '%Prueba%';

-- Limpiar propietarios de prueba
DELETE FROM propietarios WHERE cedula_rif LIKE '%E2E%' OR nombre LIKE '%Test%';

-- Limpiar usuarios de prueba (excepto admin e inspector principales)
DELETE FROM usuarios WHERE email LIKE '%@pruebas.srcm' AND id NOT IN ('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000002');
EOF

echo "✅ Datos de pruebas limpiados"
```

---

## 🤖 Ejecución Automatizada

### Configuración pytest.ini

```ini
[pytest]
testpaths = tests_e2e
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --html=reports/pytest.html
    --self-contained-html
markers =
    e2e: Pruebas End-to-End
    api: Pruebas de API
    db: Pruebas de Base de Datos
    smoke: Pruebas de humo
    regress: Pruebas de regresión
asyncio_mode = auto
```

### Estructura de Directorios de Pruebas

```
srcm/
├── tests_e2e/
│   ├── conftest.py                 # Configuración pytest
│   ├── test_configuracion.py       # Setup y teardown
│   ├── test_inmuebles_e2e.py       # Pruebas E2E inmuebles
│   ├── test_propietarios_e2e.py    # Pruebas E2E propietarios
│   ├── test_catastro_e2e.py       # Pruebas E2E catastro
│   ├── test_configuracion_e2e.py   # Pruebas E2E configuración
│   ├── test_usuarios_e2e.py       # Pruebas E2E usuarios
│   └── test_flujos_completos.py    # Pruebas E2E integración
├── fixtures/
│   ├── propietario_fixture.py      # Datos de prueba propietarios
│   ├── inmueble_fixture.py         # Datos de prueba inmuebles
│   └── usuario_fixture.py          # Datos de prueba usuarios
└── reports/                       # Directorio para reportes
```

### Archivo conftest.py

```python
import pytest
import httpx
from typing import AsyncGenerator

@pytest.fixture(scope="session")
async def http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Cliente HTTP para pruebas E2E"""
    async with httpx.AsyncClient() as client:
        yield client

@pytest.fixture(scope="session")
async def admin_token(http_client: httpx.AsyncClient) -> str:
    """Token de administrador para pruebas"""
    response = await http_client.post(
        "http://localhost:8000/api/v1/auth/login",
        json={"email": "admin@pruebas.srcm", "password": "password123"}
    )
    return response.json()["access_token"]

@pytest.fixture(scope="session")
async def inspector_token(http_client: httpx.AsyncClient) -> str:
    """Token de inspector para pruebas"""
    response = await http_client.post(
        "http://localhost:8000/api/v1/auth/login",
        json={"email": "inspector@pruebas.srcm", "password": "password123"}
    )
    return response.json()["access_token"]

@pytest.fixture(scope="function")
async def cleanup_db():
    """Limpieza de base de datos después de cada test"""
    yield
    # Aquí iría la lógica de limpieza
    pass
```

---

## 📊 Reportes y Métricas

### Métricas a Recolectar

- **Cobertura de endpoints:** % de endpoints probados
- **Cobertura de tablas BD:** % de tablas con casos de prueba
- **Tasa de éxito:** % de pruebas que pasan
- **Tiempo de ejecución:** Duración de cada prueba
- **Tendencias:** Regresiones detectadas

### Formato de Reporte

```markdown
# Reporte de Pruebas E2E - SRCM API

**Fecha:** 2024-01-15  
**Ejecución:** Automatizada  
**Total Pruebas:** 85  
**Aprobadas:** 82  
**Fallidas:** 3  
**Tasa de Éxito:** 96.5%

## Resumen por Categoría

| Categoría | Total | Pasaron | Fallaron | % Éxito |
|-----------|-------|---------|----------|---------|
| Inmuebles | 25 | 24 | 1 | 96% |
| Propietarios | 12 | 12 | 0 | 100% |
| Catastro | 10 | 10 | 0 | 100% |
| Configuración | 8 | 8 | 0 | 100% |
| Usuarios | 6 | 6 | 0 | 100% |
| Salud | 2 | 2 | 0 | 100% |
| Flujos Completos | 22 | 20 | 2 | 91% |

## Pruebas Fallidas

| ID | Prueba | Error | Severidad |
|----|-------|-------|-----------|
| IN-API-004 | Actualización con solapamiento | Timeout DB | Alta |
| E2E-001 | Flujo completo registro | Error validación geometría | Media |
| E2E-003 | Mapa catastral bbox | Error conversión coordenadas | Baja |

## Recomendaciones

1. Investigar timeout en base de datos para IN-API-004
2. Mejorar validación de geometría en E2E-001
3. Agregar manejo de errores en conversión de coordenadas
```

---

## 🔧 Troubleshooting

### Problemas Comunes

#### 1. Error de Conexión a Base de Datos

**Error:** `connection refused` o `timeout`

**Solución:**
```bash
# Verificar que el servidor de pruebas esté corriendo
curl http://localhost:8000/salud

# Verificar conexión a base de datos
psql $DATABASE_URL -c "SELECT 1"
```

#### 2. Error de Autenticación

**Error:** `401 Unauthorized`

**Solución:**
```bash
# Verificar que el usuario de prueba exista
psql $DATABASE_URL -c "SELECT * FROM usuarios WHERE email = 'admin@pruebas.srcm'"

# Regenerar token de prueba
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d '{"email": "admin@pruebas.srcm", "password": "password123"}'
```

#### 3. Error de Geometría

**Error:** `Invalid geometry` o `422 Validation Error`

**Solución:**
```bash
# Verificar que PostGIS esté instalado
psql $DATABASE_URL -c "SELECT PostGIS_Version()"

# Validar geometría antes de enviar
psql $DATABASE_URL -c "SELECT ST_IsValid(ST_GeomFromText('POLYGON((...))'))"
```

#### 4. Error de timeouts en pruebas

**Error:** Pruebas que tardan demasiado

**Solución:**
```python
# Aumentar timeout en pytest
@pytest.mark.e2e
@pytest.mark.timeout(30)  # 30 segundos máximo
async def test_mapa_catastral_lento():
    # test que puede tardar más
    pass
```

---

## 📝 Checklist de Pruebas E2E

### Pre-Pruebas

- [ ] Base de datos de pruebas configurada
- [ ] Usuarios de prueba creados
- [ ] Servidor API corriendo en puerto 8000
- [ ] Variables de entorno configuradas
- [ ] Dependencias de prueba instaladas

### Durante Pruebas

- [ ] Pruebas de salud (P0) ejecutadas primero
- [ ] Pruebas CRUD básicas (P0) ejecutadas
- [ ] Pruebas de integración (P1) ejecutadas
- [ ] Pruebas de edge cases (P2) ejecutadas
- [ ] Pruebas de flujos completos ejecutadas

### Post-Pruebas

- [ ] Reporte generado exitosamente
- [ ] Datos de prueba limpiados
- [ ] Fallas investigadas y documentadas
- [ ] Regresiones identificadas
- [ ] Métricas registradas

---

## 🎯 Matriz de Trazabilidad

### Requisitos → Casos de Prueba

| Requisito | Caso de Prueba | Endpoint API | Tabla BD |
|-----------|----------------|---------------|----------|
| Registro inmueble | IN-API-001 | POST /api/v1/inmuebles | inmuebles, propietarios |
| Código catastral | IN-API-001 | POST /api/v1/inmuebles | inmuebles, configuracion_sistema |
| Generación PDF | IN-API-021 | GET /api/v1/inmuebles/{id}/cedula | v_pdf_cedula_catastral |
| Mapa catastral | CA-API-001 | GET /api/v1/catastro/mapa | inmuebles |
| Gestión propietarios | PR-API-001 | POST /api/v1/propietarios | propietarios |
| Configuración | CF-API-001 | GET /api/v1/configuracion/catastral | configuracion_catastral |

---

## 🚀 Próximos Pasos

### Fase 1: Implementación Inmediata

1. **Crear estructura de directorios de pruebas**
2. **Implementar casos de prueba P0 (críticos)**
3. **Configurar pytest y fixtures**
4. **Implementar scripts de setup/cleanup**

### Fase 2: Expansión

1. **Implementar casos de prueba P1 (importantes)**
2. **Agregar pruebas de carga básicas**
3. **Implementar reportes automáticos**
4. **Integración con CI/CD**

### Fase 3: Optimización

1. **Implementar pruebas P2 (edge cases)**
2. **Optimizar tiempos de ejecución**
3. **Paralelización de pruebas**
4. **Mocking de servicios externos**

---

## 📚 Referencias

- [Documentación FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Documentación pytest](https://docs.pytest.org/)
- [Documentación httpx](https://www.python-httpx.org/)
- [Documentación Playwright](https://playwright.dev/python/)

---

## 🎉 Conclusión

Esta guía proporciona un framework completo para implementar pruebas E2E robustas para el sistema SRCM. Con estos casos de prueba y scripts, puedes asegurar la calidad del sistema antes de cada despliegue.

**Próximo paso recomendado:** Implementar los casos de prueba P0 (críticos) para comenzar inmediatamente con la validación del sistema.

---

**Versión:** 1.0  
**Mantenido por:** Equipo de Desarrollo SRCM  
**Última actualización:** 16 de septiembre de 2026
