# Guía de Ejecución de Pruebas E2E - SRCM

**Sistema de Registro Catastral Municipal - Municipio Torbes, Estado Táchira, Venezuela**

**Versión:** 2.5.0  
**Fecha:** 17 de septiembre de 2026  
**Backend:** FastAPI + Python 3.12+  
**Base de Datos:** PostgreSQL + PostGIS (Supabase)

---

## 📋 Índice

- [Introducción](#introducción)
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Configuración de Supabase](#configuración-de-supabase)
- [Variables de Entorno Necesarias](#variables-de-entorno-necesarias)
- [Conexión a Base de Datos](#conexión-a-base-de-datos)
- [Pruebas E2E a Ejecutar](#pruebas-e2e-a-ejecutar)
- [Flujo Completo de Pruebas](#flujo-completo-de-pruebas)
- [Ejecución de Pruebas](#ejecución-de-pruebas)
- [Verificación de Resultados](#verificación-de-resultados)

---

## 🎯 Introducción

Este documento describe cómo ejecutar las pruebas End-to-End (E2E) para el Sistema de Registro Catastral Municipal (SRCM). Las pruebas E2E validan el funcionamiento completo del sistema, desde la API hasta la base de datos, simulando el uso real de la aplicación.

### Alcance de las Pruebas

- **35 endpoints API** del sistema SRCM
- **7 tablas de base de datos** principales
- **Integración con Supabase** (autenticación y base de datos)
- **Generación de cédulas catastrales** en PDF
- **Funcionalidades geoespaciales** con PostGIS

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                   Cliente (Frontend/Móvil)                  │
└─────────────────────────────────────────────────────────────┘
                              │
                    HTTP/HTTPS Request
                              │
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (localhost:8000)               │
│  - 35 Endpoints REST API                                   │
│  - Autenticación JWT con Supabase Auth                     │
│  - Validación de datos con Pydantic                        │
└─────────────────────────────────────────────────────────────┘
                              │
                    SQLAlchemy ORM
                              │
┌─────────────────────────────────────────────────────────────┐
│         Supabase PostgreSQL + PostGIS Database             │
│  - 7 Tablas principales                                     │
│  - Triggers para código catastral                          │
│  - Funciones geoespaciales                                  │
│  - Índices para búsqueda                                    │
└─────────────────────────────────────────────────────────────┘
```

### Componentes Principales

1. **Backend FastAPI**: API REST con 35 endpoints
2. **Base de Datos Supabase**: PostgreSQL + PostGIS para datos geoespaciales
3. **Autenticación**: Supabase Auth con tokens JWT
4. **Storage**: Supabase Storage para archivos (fotos, PDFs)

---

## ⚙️ Configuración de Supabase

### 1. Crear Proyecto en Supabase

1. Accede a [Supabase](https://supabase.com)
2. Crea un nuevo proyecto con nombre: `srcm-pruebas`
3. Selecciona la región más cercana a tu ubicación
4. Espera a que el proyecto se inicialice (2-3 minutos)

### 2. Ejecutar Script SQL

1. Ve a **SQL Editor** en el panel de Supabase
2. Copia el contenido del archivo `srcm_supabase_completo.sql`
3. Pega el contenido en el editor SQL
4. Ejecuta el script (botón "Run")

Este script crea:
- 7 tablas principales (configuracion_catastral, configuracion_sistema, usuarios, propietarios, inmuebles, hitos_prediales, fotos_inmueble)
- Extensiones PostGIS y pgcrypto
- Triggers para generación automática de código catastral
- Índices para optimización de consultas
- Vistas para reportes y cédulas catastrales

### 3. Configurar Autenticación

1. Ve a **Authentication** > **Providers**
2. Habilita **Email** provider (ya viene habilitado por defecto)
3. Configura las URLs de redirección si es necesario

### 4. Configurar Storage

1. Ve a **Storage** > **Buckets**
2. Crea un nuevo bucket llamado: `catastro-archivos`
3. Configura como **Public** o **Private** según tus necesidades
4. Configura las políticas de acceso (RLS)

---

## 🔑 Variables de Entorno Necesarias

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

### Variables Obligatorias

```env
# ============================================================
# CONFIGURACIÓN DE APLICACIÓN
# ============================================================
APP_NAME=SRCM API - Pruebas E2E
APP_ENV=testing
DEBUG=true
API_V1_PREFIX=/api/v1

# ============================================================
# BASE DE DATOS SUPABASE
# ============================================================
# La encuentras en: Supabase → Project Settings → Database → Connection string
# Usa el modo "Session" (puerto 5432) para pruebas
DATABASE_URL=postgresql://postgres:TU_PASSWORD@db.TU_PROYECTO.supabase.co:5432/postgres

# ============================================================
# SUPABASE AUTH (AUTENTICACIÓN)
# ============================================================
# Supabase → Project Settings → API
SUPABASE_URL=https://TU_PROYECTO.supabase.co
SUPABASE_ANON_KEY=TU_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY=TU_SERVICE_ROLE_KEY
SUPABASE_JWT_SECRET=TU_JWT_SECRET

# ============================================================
# SEGURIDAD DE LA API
# ============================================================
# Genera una clave secreta con: python -c "import secrets; print(secrets.token_urlsafe(64))"
SECRET_KEY=TU_SECRET_KEY_GENERADO
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALGORITHM=HS256

# ============================================================
# CORS (ORIGENES PERMITIDOS)
# ============================================================
# Separados por coma, sin espacios
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:54545

# ============================================================
# STORAGE SUPABASE
# ============================================================
SUPABASE_STORAGE_BUCKET=catastro-archivos

# ============================================================
# CONFIGURACIÓN CATASTRAL
# ============================================================
# Debe coincidir con los valores en la base de datos
CODIGO_ESTADO=20
CODIGO_MUNICIPIO=27
CODIGO_PARROQUIA=01
SRID_UTM=2201
```

### Cómo Obtener las Credenciales de Supabase

1. **DATABASE_URL**:
   - Ve a `Project Settings` > `Database`
   - Copia la `Connection string` (modo Session)
   - Reemplaza `TU_PASSWORD` con tu contraseña de base de datos

2. **SUPABASE_URL**:
   - Ve a `Project Settings` > `API`
   - Copia el `Project URL`

3. **SUPABASE_ANON_KEY**:
   - En la misma sección `API`
   - Copia el `anon public key`

4. **SUPABASE_SERVICE_ROLE_KEY**:
   - En la misma sección `API`
   - Copia el `service_role key` (úsalo con cuidado, tiene acceso total)

5. **SUPABASE_JWT_SECRET**:
   - Ve a `Project Settings` > `API` > `JWT Settings`
   - Copia el `JWT Secret`

### Generar SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Copia el resultado y pégalo en la variable `SECRET_KEY`.

---

## 🔗 Conexión a Base de Datos

### Configuración de SQLAlchemy

El sistema usa SQLAlchemy ORM para conectarse a Supabase. La configuración está en `app/db/session.py`:

```python
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verifica conexiones antes de usarlas
    pool_size=5,         # Tamaño del pool de conexiones
    max_overflow=10,     # Conexiones adicionales cuando el pool está lleno
    connect_args={"options": "-c timezone=utc"},
    echo=settings.DEBUG and settings.APP_ENV == "development",
)
```

### Verificar Conexión

Para verificar que la conexión funciona correctamente:

```bash
# 1. Activa el entorno virtual
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 2. Instala dependencias
pip install -r requirements.txt

# 3. Ejecuta el servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 4. En otra terminal, verifica el health check
curl http://localhost:8000/salud
```

Si devuelve `{"status": "ok"}`, la conexión es exitosa.

### Tablas de Base de Datos

El sistema crea 7 tablas principales:

1. **configuracion_catastral**: Configuración catastral y datos institucionales
2. **configuracion_sistema**: Configuración del sistema para validación de códigos
3. **usuarios**: Usuarios del sistema (administradores e inspectores)
4. **propietarios**: Propietarios de inmuebles
5. **inmuebles**: Inmuebles catastrales (tabla principal)
6. **hitos_prediales**: Vértices GPS de polígonos
7. **fotos_inmueble**: URLs de fotos de inmuebles

---

## 🧪 Pruebas E2E a Ejecutar

### Categoría 1: Configuración y Salud (2 endpoints)

#### SC-001: Health Check
- **Endpoint**: `GET /salud`
- **Propósito**: Verificar que el servidor está activo
- **Respuesta esperada**: `{"status": "ok"}`
- **Prioridad**: P0 (Crítica)

#### SC-002: Raíz del sistema
- **Endpoint**: `GET /`
- **Propósito**: Verificar información básica del servicio
- **Respuesta esperada**: JSON con nombre del servicio y documentación
- **Prioridad**: P0 (Crítica)

### Categoría 2: Configuración Catastral (5 endpoints)

#### CC-001: Obtener configuración catastral
- **Endpoint**: `GET /api/v1/configuracion/catastral`
- **Propósito**: Obtener valores catastrales actuales
- **Validar**: Valores por m², vigencia, códigos geográficos
- **Prioridad**: P0 (Crítica)

#### CC-002: Actualizar configuración catastral
- **Endpoint**: `PATCH /api/v1/configuracion/catastral`
- **Propósito**: Actualizar valores catastrales
- **Validar**: Valores actualizados correctamente en BD
- **Prioridad**: P1 (Importante)

#### CC-003: Obtener configuración del sistema
- **Endpoint**: `GET /api/v1/configuracion/sistema`
- **Propósito**: Obtener configuración de validación de códigos
- **Validar**: Códigos coinciden con configuración catastral
- **Prioridad**: P0 (Crítica)

#### CC-004: Actualizar configuración del sistema
- **Endpoint**: `PATCH /api/v1/configuracion/sistema`
- **Propósito**: Actualizar códigos de validación
- **Validar**: Sincronización con configuración catastral
- **Prioridad**: P1 (Importante)

#### CC-005: Obtener configuración para PDF
- **Endpoint**: `GET /api/v1/configuracion/catastral/pdf-config`
- **Propósito**: Obtener datos institucionales para cédulas
- **Validar**: Datos de autoridades y notas legales
- **Prioridad**: P1 (Importante)

### Categoría 3: Propietarios (6 endpoints)

#### PR-001: Crear propietario
- **Endpoint**: `POST /api/v1/propietarios`
- **Propósito**: Registrar nuevo propietario
- **Validar**: Propietario creado con todos los campos
- **Prioridad**: P0 (Crítica)

#### PR-002: Listar propietarios
- **Endpoint**: `GET /api/v1/propietarios`
- **Propósito**: Listar propietarios con paginación
- **Validar**: Paginación funciona correctamente
- **Prioridad**: P0 (Crítica)

#### PR-003: Obtener propietario por ID
- **Endpoint**: `GET /api/v1/propietarios/{id}`
- **Propósito**: Obtener detalles de un propietario
- **Validar**: Todos los campos son correctos
- **Prioridad**: P0 (Crítica)

#### PR-004: Actualizar propietario
- **Endpoint**: `PATCH /api/v1/propietarios/{id}`
- **Propósito**: Actualizar datos de propietario
- **Validar**: Datos actualizados en BD
- **Prioridad**: P1 (Importante)

#### PR-005: Eliminar propietario
- **Endpoint**: `DELETE /api/v1/propietarios/{id}`
- **Propósito**: Eliminar propietario sin inmuebles
- **Validar**: Propietario eliminado de BD
- **Prioridad**: P1 (Importante)

#### PR-006: Listar inmuebles de propietario
- **Endpoint**: `GET /api/v1/propietarios/{id}/inmuebles`
- **Propósito**: Obtener inmuebles asociados a un propietario
- **Validar**: Lista correcta de inmuebles
- **Prioridad**: P1 (Importante)

### Categoría 4: Inmuebles (13 endpoints)

#### IN-001: Crear inmueble
- **Endpoint**: `POST /api/v1/inmuebles`
- **Propósito**: Crear nuevo inmueble catastral
- **Validar**: 
  - Código catastral generado automáticamente
  - Geometría almacenada correctamente
  - Valores calculados (terreno, construcción, total)
- **Prioridad**: P0 (Crítica)

#### IN-002: Listar inmuebles
- **Endpoint**: `GET /api/v1/inmuebles`
- **Propósito**: Listar inmuebles con filtros y paginación
- **Validar**:
  - Paginación funciona
  - Filtros (sector, tenencia, fechas) funcionan
  - Búsqueda por dirección/propietario funciona
- **Prioridad**: P0 (Crítica)

#### IN-003: Obtener inmueble por ID
- **Endpoint**: `GET /api/v1/inmuebles/{id}`
- **Propósito**: Obtener detalles completos de inmueble
- **Validar**: Todos los campos incluyendo geometría
- **Prioridad**: P0 (Crítica)

#### IN-004: Actualizar inmueble
- **Endpoint**: `PATCH /api/v1/inmuebles/{id}`
- **Propósito**: Actualizar datos de inmueble
- **Validar**: Datos actualizados, vigencia recalculada
- **Prioridad**: P1 (Importante)

#### IN-005: Eliminar inmueble
- **Endpoint**: `DELETE /api/v1/inmuebles/{id}`
- **Propósito**: Eliminar inmueble (solo admin)
- **Validar**: Inmueble eliminado de BD
- **Prioridad**: P1 (Importante)

#### IN-006: Generar cédula catastral PDF
- **Endpoint**: `GET /api/v1/inmuebles/{id}/cedula`
- **Propósito**: Generar y descargar PDF de cédula
- **Validar**: PDF generado correctamente
- **Prioridad**: P0 (Crítica)

#### IN-007: Obtener datos para cédula
- **Endpoint**: `GET /api/v1/inmuebles/{id}/cedula-datos`
- **Propósito**: Obtener datos para generar PDF en frontend
- **Validar**: Todos los datos necesarios presentes
- **Prioridad**: P1 (Importante)

#### IN-008: Agregar foto a inmueble
- **Endpoint**: `POST /api/v1/inmuebles/{id}/fotos`
- **Propósito**: Registrar URL de foto
- **Validar**: Foto asociada al inmueble
- **Prioridad**: P1 (Importante)

#### IN-009: Listar fotos de inmueble
- **Endpoint**: `GET /api/v1/inmuebles/{id}/fotos`
- **Propósito**: Listar todas las fotos de un inmueble
- **Validar**: Lista completa de fotos
- **Prioridad**: P1 (Importante)

#### IN-010: Eliminar foto de inmueble
- **Endpoint**: `DELETE /api/v1/inmuebles/{id}/fotos/{foto_id}`
- **Propósito**: Eliminar foto específica
- **Validar**: Foto eliminada de BD
- **Prioridad**: P2 (Normal)

#### IN-011: Agregar hito predial
- **Endpoint**: `POST /api/v1/inmuebles/{id}/hitos`
- **Propósito**: Agregar vértice GPS al polígono
- **Validar**: Hito creado con coordenadas correctas
- **Prioridad**: P1 (Importante)

#### IN-012: Listar hitos de inmueble
- **Endpoint**: `GET /api/v1/inmuebles/{id}/hitos`
- **Propósito**: Listar todos los hitos de un inmueble
- **Validar**: Lista ordenada por índice de vértice
- **Prioridad**: P1 (Importante)

#### IN-013: Eliminar hito predial
- **Endpoint**: `DELETE /api/v1/inmuebles/{id}/hitos/{hito_id}`
- **Propósito**: Eliminar hito específico
- **Validar**: Hito eliminado de BD
- **Prioridad**: P2 (Normal)

### Categoría 5: Catastro Geoespacial (5 endpoints)

#### CA-001: Obtener mapa catastral
- **Endpoint**: `GET /api/v1/catastro/mapa`
- **Propósito**: Obtener GeoJSON de todos los predios
- **Validar**: GeoJSON válido con geometrías correctas
- **Prioridad**: P0 (Crítica)

#### CA-002: Obtener estadísticas generales
- **Endpoint**: `GET /api/v1/catastro/estadisticas`
- **Propósito**: Obtener estadísticas del catastro
- **Validar**: Totales de inmuebles, áreas, valores
- **Prioridad**: P1 (Importante)

#### CA-003: Obtener predios por sector
- **Endpoint**: `GET /api/v1/catastro/por-sector`
- **Propósito**: Agrupar inmuebles por sector
- **Validar**: Agrupación correcta por sector
- **Prioridad**: P1 (Importante)

#### CA-004: Auditoría de solapamientos
- **Endpoint**: `GET /api/v1/catastro/solapamientos`
- **Propósito**: Detectar polígonos solapados
- **Validar**: Detección correcta de solapamientos
- **Prioridad**: P2 (Normal)

#### CA-005: Listar sectores disponibles
- **Endpoint**: `GET /api/v1/catastro/sectores`
- **Propósito**: Obtener lista de sectores
- **Validar**: Lista completa de sectores
- **Prioridad**: P1 (Importante)

### Categoría 6: Usuarios (4 endpoints)

#### US-001: Obtener perfil actual
- **Endpoint**: `GET /api/v1/usuarios/me`
- **Propósito**: Obtener datos del usuario autenticado
- **Validar**: Datos correctos del usuario actual
- **Prioridad**: P0 (Crítica)

#### US-002: Listar usuarios (admin)
- **Endpoint**: `GET /api/v1/usuarios`
- **Propósito**: Listar todos los usuarios (solo admin)
- **Validar**: Lista completa de usuarios
- **Prioridad**: P1 (Importante)

#### US-003: Cambiar rol de usuario (admin)
- **Endpoint**: `PATCH /api/v1/usuarios/{id}/rol`
- **Propósito**: Cambiar rol entre admin/inspector
- **Validar**: Rol actualizado correctamente
- **Prioridad**: P1 (Importante)

#### US-004: Activar/desactivar usuario (admin)
- **Endpoint**: `PATCH /api/v1/usuarios/{id}/estado`
- **Propósito**: Cambiar estado activo/inactivo
- **Validar**: Estado actualizado correctamente
- **Prioridad**: P1 (Importante)

---

## 🔄 Flujo Completo de Pruebas

### Escenario 1: Registro Completo de Inmueble

Este flujo prueba el proceso completo de registro de un inmueble catastral:

1. **Autenticación**
   - Iniciar sesión con usuario de pruebas
   - Obtener token JWT

2. **Verificar Configuración**
   - Obtener configuración catastral actual
   - Verificar que los códigos geográficos son correctos

3. **Crear Propietario**
   - Registrar nuevo propietario
   - Obtener ID del propietario creado

4. **Crear Inmueble**
   - Enviar datos del inmueble con geometría
   - Verificar código catastral generado
   - Verificar valores calculados

5. **Agregar Hitos Prediales**
   - Agregar vértices GPS del polígono
   - Verificar coordenadas UTM calculadas

6. **Agregar Fotos**
   - Registrar URLs de fotos del inmueble
   - Verificar asociación correcta

7. **Generar Cédula Catastral**
   - Solicitar generación de PDF
   - Verificar que el PDF se genera correctamente

8. **Consultar Inmueble**
   - Obtener detalles completos del inmueble
   - Verificar todos los datos

### Escenario 2: Consulta y Búsqueda

Este flujo prueba las funcionalidades de consulta y búsqueda:

1. **Listar Inmuebles**
   - Obtener lista paginada de inmuebles
   - Aplicar filtros por sector
   - Aplicar filtros por tenencia
   - Aplicar filtros por fechas
   - Usar búsqueda por dirección

2. **Mapa Catastral**
   - Obtener GeoJSON del mapa
   - Verificar geometrías válidas
   - Verificar propiedades de cada feature

3. **Estadísticas**
   - Obtener estadísticas generales
   - Obtener datos por sector
   - Verificar cálculos de áreas y valores

### Escenario 3: Gestión de Configuración

Este flujo prueba la gestión de configuración del sistema:

1. **Obtener Configuración**
   - Obtener configuración catastral
   - Obtener configuración del sistema
   - Verificar sincronización entre ambas

2. **Actualizar Configuración**
   - Actualizar valor m² terreno
   - Actualizar vigencia de cédulas
   - Actualizar datos institucionales
   - Verificar actualización en BD

3. **Validar Impacto**
   - Crear nuevo inmueble después de actualizar
   - Verificar que usa nuevos valores
   - Verificar cálculos correctos

---

## 🚀 Ejecución de Pruebas

### Método 1: Pruebas Manuales con Curl

#### Ejemplo: Health Check

```bash
curl -X GET http://localhost:8000/salud
```

#### Ejemplo: Crear Propietario

```bash
curl -X POST http://localhost:8000/api/v1/propietarios \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cedula_rif": "V-15123456",
    "nombre": "Juan",
    "apellido": "Pérez",
    "telefono": "0414-1234567",
    "email": "juan.perez@email.com",
    "direccion": "Calle Principal #123"
  }'
```

#### Ejemplo: Crear Inmueble

```bash
curl -X POST http://localhost:8000/api/v1/inmuebles \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "propietario_id": "UUID_DEL_PROPIETARIO",
    "direccion": "Calle de Prueba #456",
    "sector": "06",
    "manzana": "049",
    "parcela": "135",
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

### Método 2: Pruebas con Postman

1. Importa la colección de endpoints (si está disponible)
2. Configura la variable de entorno `base_url` = `http://localhost:8000`
3. Configura la variable `token` con tu token JWT
4. Ejecuta las pruebas en orden según el flujo

### Método 3: Pruebas Automatizadas con Python

Crea un archivo `test_e2e.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8000"
TOKEN = "YOUR_JWT_TOKEN"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_health_check():
    response = requests.get(f"{BASE_URL}/salud")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    print("✅ Health check exitoso")

def test_crear_propietario():
    data = {
        "cedula_rif": "V-15123456",
        "nombre": "Juan",
        "apellido": "Pérez",
        "telefono": "0414-1234567",
        "email": "juan.perez@email.com",
        "direccion": "Calle Principal #123"
    }
    response = requests.post(f"{BASE_URL}/api/v1/propietarios", 
                           headers=headers, json=data)
    assert response.status_code == 201
    propietario_id = response.json()["id"]
    print(f"✅ Propietario creado: {propietario_id}")
    return propietario_id

def test_crear_inmueble(propietario_id):
    data = {
        "propietario_id": propietario_id,
        "direccion": "Calle de Prueba #456",
        "sector": "06",
        "manzana": "049",
        "parcela": "135",
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
    }
    response = requests.post(f"{BASE_URL}/api/v1/inmuebles", 
                           headers=headers, json=data)
    assert response.status_code == 201
    inmueble = response.json()
    assert "codigo_catastral" in inmueble
    print(f"✅ Inmueble creado: {inmueble['codigo_catastral']}")
    return inmueble["id"]

if __name__ == "__main__":
    test_health_check()
    propietario_id = test_crear_propietario()
    inmueble_id = test_crear_inmueble(propietario_id)
    print("🎉 Pruebas E2E completadas exitosamente")
```

Ejecuta las pruebas:

```bash
python test_e2e.py
```

---

## ✅ Verificación de Resultados

### Verificación en Base de Datos

Usa el SQL Editor de Supabase para verificar:

```sql
-- Verificar propietario creado
SELECT * FROM propietarios WHERE cedula_rif = 'V-15123456';

-- Verificar inmueble creado
SELECT 
  codigo_catastral,
  direccion,
  valor_catastral_total,
  fecha_emision,
  vigente_hasta
FROM inmuebles 
WHERE direccion = 'Calle de Prueba #456';

-- Verificar geometría
SELECT 
  codigo_catastral,
  ST_AsGeoJSON(geom) as geometria,
  superficie_gis_m2,
  perimetro_gis_m
FROM inmuebles 
WHERE direccion = 'Calle de Prueba #456';

-- Verificar hitos prediales
SELECT * FROM hitos_prediales 
WHERE inmueble_id = 'UUID_DEL_INMUEBLE'
ORDER BY indice_vertice;

-- Verificar fotos
SELECT * FROM fotos_inmueble 
WHERE inmueble_id = 'UUID_DEL_INMUEBLE'
ORDER BY created_at;
```

### Verificación de Códigos Catastrales

El código catastral debe tener el formato: `20-27-01-06-049-135-000-000-000`

Donde:
- `20`: Estado Táchira
- `27`: Municipio Torbes
- `01`: Parroquia San Josecito
- `06`: Sector
- `049`: Manzana
- `135`: Parcela
- `000`: Subparcela
- `000`: Nivel
- `000`: Unidad

### Verificación de Valores Calculados

```sql
-- Verificar cálculo de valores
SELECT 
  area_terreno_m2,
  valor_unit_terreno,
  valor_terreno,
  area_construccion_m2,
  valor_unit_construccion,
  valor_construccion,
  valor_catastral_total,
  (area_terreno_m2 * valor_unit_terreno) as calculo_terreno,
  (area_construccion_m2 * valor_unit_construccion) as calculo_construccion
FROM inmuebles 
WHERE direccion = 'Calle de Prueba #456';
```

Los valores calculados deben coincidir con los valores almacenados.

---

## 📊 Reporte de Pruebas

### Formato de Reporte

```markdown
# Reporte de Ejecución de Pruebas E2E

**Fecha:** [FECHA]  
**Ejecutor:** [NOMBRE]  
**Ambiente:** Testing  
**Versión:** 2.5.0

## Resumen
- Total pruebas: 35
- Exitosas: [NUMERO]
- Fallidas: [NUMERO]
- Porcentaje éxito: [PORCENTAJE]%

## Detalle por Categoría

### Salud (2/2)
- ✅ SC-001: Health Check
- ✅ SC-002: Raíz del sistema

### Configuración Catastral (5/5)
- ✅ CC-001: Obtener configuración catastral
- ✅ CC-002: Actualizar configuración catastral
- ✅ CC-003: Obtener configuración del sistema
- ✅ CC-004: Actualizar configuración del sistema
- ✅ CC-005: Obtener configuración para PDF

### Propietarios (6/6)
- ✅ PR-001: Crear propietario
- ✅ PR-002: Listar propietarios
- ✅ PR-003: Obtener propietario por ID
- ✅ PR-004: Actualizar propietario
- ✅ PR-005: Eliminar propietario
- ✅ PR-006: Listar inmuebles de propietario

### Inmuebles (13/13)
- ✅ IN-001: Crear inmueble
- ✅ IN-002: Listar inmuebles
- ✅ IN-003: Obtener inmueble por ID
- ✅ IN-004: Actualizar inmueble
- ✅ IN-005: Eliminar inmueble
- ✅ IN-006: Generar cédula catastral PDF
- ✅ IN-007: Obtener datos para cédula
- ✅ IN-008: Agregar foto a inmueble
- ✅ IN-009: Listar fotos de inmueble
- ✅ IN-010: Eliminar foto de inmueble
- ✅ IN-011: Agregar hito predial
- ✅ IN-012: Listar hitos de inmueble
- ✅ IN-013: Eliminar hito predial

### Catastro Geoespacial (5/5)
- ✅ CA-001: Obtener mapa catastral
- ✅ CA-002: Obtener estadísticas generales
- ✅ CA-003: Obtener predios por sector
- ✅ CA-004: Auditoría de solapamientos
- ✅ CA-005: Listar sectores disponibles

### Usuarios (4/4)
- ✅ US-001: Obtener perfil actual
- ✅ US-002: Listar usuarios (admin)
- ✅ US-003: Cambiar rol de usuario (admin)
- ✅ US-004: Activar/desactivar usuario (admin)

## Incidencias Encontradas

[ID] - [Descripción] - [Severidad]

## Recomendaciones

[Recomendaciones para mejorar el sistema]
```

---

## 🔧 Troubleshooting

### Error: "Connection refused"

**Causa**: El servidor no está ejecutándose o el puerto es incorrecto.

**Solución**:
```bash
# Verificar que el servidor esté corriendo
curl http://localhost:8000/salud

# Si no responde, iniciar el servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Error: "Authentication failed"

**Causa**: Token JWT inválido o expirado.

**Solución**:
- Verifica que el token sea correcto
- Genera un nuevo token desde Supabase Auth
- Verifica que `SUPABASE_JWT_SECRET` sea correcto

### Error: "Database connection failed"

**Causa**: Credenciales de base de datos incorrectas.

**Solución**:
- Verifica `DATABASE_URL` en `.env`
- Verifica que la contraseña sea correcta
- Verifica que tu IP esté en los allowed hosts de Supabase

### Error: "Geometry is invalid"

**Causa**: El polígono GeoJSON no es válido.

**Solución**:
- Verifica que el polígono esté cerrado (primer y último punto iguales)
- Verifica que las coordenadas estén en formato correcto [lon, lat]
- Verifica que el polígono no se intersecte a sí mismo

### Error: "Código catastral duplicado"

**Causa**: Ya existe un inmueble con el mismo código catastral.

**Solución**:
- Verifica que la combinación sector-manzana-parcela sea única
- Usa diferentes valores para las pruebas

---

## 📝 Checklist de Preparación

Antes de ejecutar las pruebas, verifica:

- [ ] Proyecto de Supabase creado y configurado
- [ ] Script SQL ejecutado correctamente
- [ ] Bucket de Storage creado
- [ ] Archivo `.env` configurado con todas las variables
- [ ] Dependencias Python instaladas
- [ ] Entorno virtual activado
- [ ] Servidor FastAPI ejecutándose en puerto 8000
- [ ] Health check responde correctamente
- [ ] Token JWT válido obtenido
- [ ] Usuario de prueba creado en Supabase Auth

---

## 🎓 Conclusión

Esta guía proporciona un marco completo para ejecutar pruebas E2E del sistema SRCM. Las pruebas validan:

1. **Integración completa** entre frontend, backend y base de datos
2. **Funcionalidades críticas** del sistema catastral
3. **Conexión con Supabase** para autenticación y datos
4. **Generación de documentos** oficiales (cédulas catastrales)
5. **Funcionalidades geoespaciales** con PostGIS

Sigue este orden de ejecución y verifica los resultados en cada paso para asegurar la calidad del sistema antes del despliegue a producción.

---

**Sistema desarrollado para la Alcaldía del Municipio Torbes, Estado Táchira, Venezuela**
