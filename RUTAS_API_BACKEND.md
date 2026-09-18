# Rutas API Backend - SRCM

Documentación completa de las rutas API del Sistema de Registro Catastral Municipal (SRCM) para el Municipio Torbes, Estado Táchira.

**Base URL:** `http://localhost:8000` (o tu dominio en producción)
**API Prefix:** `/api/v1`
**Autenticación:** Bearer Token (JWT de Supabase Auth)

---

## 📋 Tabla de Contenidos

- [Autenticación](#autenticación)
- [Rutas Generales](#rutas-generales)
- [Inmuebles](#inmuebles)
- [Propietarios](#propietarios)
- [Catastro](#catastro)
- [Usuarios](#usuarios)
- [Códigos de Estado HTTP](#códigos-de-estado-http)

---

## 🔐 Autenticación

Todas las rutas (excepto `/` y `/salud`) requieren autenticación mediante JWT token emitido por Supabase Auth.

### Headers de Autenticación
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Roles de Usuario
- **inspector**: Acceso a operaciones estándar (crear, leer, actualizar)
- **administrador**: Acceso completo incluyendo operaciones destructivas (eliminar, cambiar roles, ver solapamientos)

### Obtener Token
El token se obtiene al hacer login/signup en Supabase Auth (desde el frontend o usando Supabase JS SDK).

---

## 🏠 Rutas Generales

### GET `/`
Información básica del servicio.

**Respuesta:**
```json
{
  "servicio": "SRCM API",
  "estado": "activo",
  "documentacion": "/docs"
}
```

---

### GET `/salud`
Health-check simple para monitoreo del servicio.

**Respuesta:**
```json
{
  "status": "ok"
}
```

---

## 🏢 Inmuebles

### POST `/api/v1/inmuebles`
Crear un nuevo inmueble en el catastro.

**Autenticación:** Requerida (cualquier rol)
**Rol requerido:** inspector o administrador

**Body:**
```json
{
  "sector": "01",
  "manzana": "001",
  "parcela": "001",
  "subparcela": "000",
  "nivel": "000",
  "unidad": "000",
  "propietario_id": "uuid-del-propietario",
  "direccion": "Vía al Llano, Sector San José",
  "documento_tipo": "Título de Propiedad",
  "documento_numero": "12345",
  "documento_tomo": "I",
  "documento_folio": "100",
  "documento_protocolo": "01",
  "documento_fecha": "2020-01-15",
  "tenencia": "propio",
  "lindero_norte_doc": "Colinda con terreno de Juan Pérez",
  "lindero_norte_mts": 25.5,
  "lindero_sur_doc": "Colinda con quebrada seca",
  "lindero_sur_mts": 30.0,
  "lindero_este_doc": "Colinda con camino vecinal",
  "lindero_este_mts": 20.0,
  "lindero_oeste_doc": "Colinda con terreno de María González",
  "lindero_oeste_mts": 28.0,
  "lindero_norte_top": "Vértice GPS 1",
  "lindero_norte_top_mts": 26.0,
  "lindero_sur_top": "Vértice GPS 2",
  "lindero_sur_top_mts": 31.0,
  "lindero_este_top": "Vértice GPS 3",
  "lindero_este_top_mts": 21.0,
  "lindero_oeste_top": "Vértice GPS 4",
  "lindero_oeste_top_mts": 29.0,
  "aguas_blancas": true,
  "aguas_servidas": true,
  "electricidad": true,
  "contador": true,
  "existe_vivienda": true,
  "tipo_vivienda": "casa",
  "descripcion_uso": "residencial",
  "numero_plantas": 1,
  "uso_segun_zonificacion": "residencial",
  "area_terreno_m2": 500.0,
  "valor_unit_terreno": 24500.00,
  "area_construccion_m2": 120.0,
  "valor_unit_construccion": 85400.00,
  "area_comercio_m2": 0.0,
  "valor_unit_comercio": 95000.00,
  "via_acceso": "asfalto",
  "estructura_techo": "placa",
  "estructura_paredes": "bloque",
  "piso": "ceramica",
  "dormitorios": 3,
  "banos": 2,
  "sala": true,
  "cocina": true,
  "ambiente_otro": "comedor",
  "caracteristica_general": "aislada",
  "observaciones": "Inmueble en buen estado",
  "fecha_emision": "2024-01-15",
  "fecha_recibo": "2024-01-15",
  "numero_recibo": "REC-2024-001",
  "geom": {
    "type": "Polygon",
    "coordinates": [[
      [-72.2345, 7.7654],
      [-72.2346, 7.7655],
      [-72.2347, 7.7654],
      [-72.2346, 7.7653],
      [-72.2345, 7.7654]
    ]]
  }
}
```

**Respuesta (201 Created):**
```json
{
  "id": "uuid-del-inmueble",
  "codigo_catastral": "20112701001001000000000",
  "codigo_catastral_formato": "20-27-01-01-001-001-000-000-000",
  "expediente_numero": "000001/2024",
  "sector": "01",
  "manzana": "001",
  "parcela": "001",
  "subparcela": "000",
  "nivel": "000",
  "unidad": "000",
  "propietario_id": "uuid-del-propietario",
  "direccion": "Vía al Llano, Sector San José",
  "valor_terreno": 12250000.00,
  "valor_construccion": 10248000.00,
  "valor_comercio": 0.00,
  "valor_catastral_total": 22498000.00,
  "utm_norte": 1234567.89,
  "utm_este": 234567.89,
  "superficie_gis_m2": 498.5,
  "perimetro_gis_m": 89.2,
  "fecha_emision": "2024-01-15",
  "vigente_hasta": "2025-01-15",
  "estado_sync": "synced",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Errores:**
- `422 Unprocessable Entity`: Geometría inválida
- `409 Conflict`: Solape topológico con otro predio o código catastral duplicado

---

### GET `/api/v1/inmuebles`
Listar inmuebles con paginación avanzada, filtros múltiples, búsqueda y ordenamiento.

**Autenticación:** Requerida (cualquier rol)

**Query Parameters:**
- `pagina` (int, default: 1) - Número de página
- `por_pagina` (int, default: 25, max: 100) - Elementos por página
- `sector` (string, opcional) - Filtrar por sector catastral
- `tenencia` (string, opcional) - Filtrar por tipo de tenencia (propio, ejido, arrendado)
- `q` (string, opcional) - Búsqueda parcial por dirección o datos del propietario
- `fecha_desde` (string, opcional) - Filtrar inmuebles creados desde esta fecha (YYYY-MM-DD)
- `fecha_hasta` (string, opcional) - Filtrar inmuebles creados hasta esta fecha (YYYY-MM-DD)
- `vigente` (boolean, opcional) - Filtrar por vigencia de la cédula (true=vigentes, false=vencidos)
- `ordenar_por` (string, default: "created_at") - Campo de ordenamiento (created_at, codigo_catastral, direccion, valor_catastral_total, fecha_emision, sector)
- `orden` (string, default: "desc") - Dirección de ordenamiento (asc, desc)

**Ejemplos:**
```http
# Básico con paginación
GET /api/v1/inmuebles?pagina=1&por_pagina=10

# Con filtros sectoriales
GET /api/v1/inmuebles?sector=01&tenencia=propio

# Con búsqueda
GET /api/v1/inmuebles?q=Los+Almendros

# Con filtros por fechas
GET /api/v1/inmuebles?fecha_desde=2024-01-01&fecha_hasta=2024-12-31

# Solo cédulas vigentes
GET /api/v1/inmuebles?vigente=true

# Ordenado por valor catastral (mayor a menor)
GET /api/v1/inmuebles?ordenar_por=valor_catastral_total&orden=desc

# Combinado completo
GET /api/v1/inmuebles?pagina=1&por_pagina=20&sector=01&q=casa&vigente=true&ordenar_por=fecha_emision&orden=desc
```

**Respuesta:**
```json
{
  "total": 150,
  "pagina": 1,
  "por_pagina": 10,
  "resultados": [
    {
      "id": "uuid-del-inmueble",
      "codigo_catastral": "20112701001001000000000",
      "codigo_catastral_formato": "20-27-01-01-001-001-000-000-000",
      "direccion": "Vía al Llano, Sector San José",
      "sector": "01",
      "tenencia": "propio",
      "existe_vivienda": true,
      "valor_catastral_total": 22498000.00,
      "vigente_hasta": "2025-01-15",
      "estado_sync": "synced"
    }
  ]
}
```

**Notas:**
- La búsqueda `q` usa índices trigram para rendimiento óptimo
- Los filtros de fecha aceptan formato ISO 8601 (YYYY-MM-DD)
- El parámetro `vigente` compara con la fecha actual automáticamente
- Campos de ordenamiento disponibles optimizados con índices correspondientes

---

### GET `/api/v1/inmuebles/{inmueble_id}`
Obtener detalles completos de un inmueble específico.

**Autenticación:** Requerida (cualquier rol)

**Parámetros de ruta:**
- `inmueble_id` (UUID) - ID del inmueble

**Respuesta:**
```json
{
  "id": "uuid-del-inmueble",
  "codigo_catastral": "20112701001001000000000",
  "codigo_catastral_formato": "20-27-01-01-001-001-000-000-000",
  "expediente_numero": "000001/2024",
  "sector": "01",
  "manzana": "001",
  "parcela": "001",
  "subparcela": "000",
  "nivel": "000",
  "unidad": "000",
  "propietario_id": "uuid-del-propietario",
  "propietario": {
    "id": "uuid-del-propietario",
    "cedula_rif": "V-12345678",
    "nombre": "Juan",
    "apellido": "Pérez",
    "telefono": "+58-276-1234567",
    "email": "juan@example.com",
    "direccion": "Dirección del propietario"
  },
  "direccion": "Vía al Llano, Sector San José",
  "documento_tipo": "Título de Propiedad",
  "documento_numero": "12345",
  "documento_tomo": "I",
  "documento_folio": "100",
  "documento_protocolo": "01",
  "documento_fecha": "2020-01-15",
  "tenencia": "propio",
  "lindero_norte_doc": "Colinda con terreno de Juan Pérez",
  "lindero_norte_mts": 25.5,
  "lindero_sur_doc": "Colinda con quebrada seca",
  "lindero_sur_mts": 30.0,
  "lindero_este_doc": "Colinda con camino vecinal",
  "lindero_este_mts": 20.0,
  "lindero_oeste_doc": "Colinda con terreno de María González",
  "lindero_oeste_mts": 28.0,
  "lindero_norte_top": "Vértice GPS 1",
  "lindero_norte_top_mts": 26.0,
  "lindero_sur_top": "Vértice GPS 2",
  "lindero_sur_top_mts": 31.0,
  "lindero_este_top": "Vértice GPS 3",
  "lindero_este_top_mts": 21.0,
  "lindero_oeste_top": "Vértice GPS 4",
  "lindero_oeste_top_mts": 29.0,
  "aguas_blancas": true,
  "aguas_servidas": true,
  "electricidad": true,
  "contador": true,
  "existe_vivienda": true,
  "tipo_vivienda": "casa",
  "descripcion_uso": "residencial",
  "numero_plantas": 1,
  "uso_segun_zonificacion": "residencial",
  "area_terreno_m2": 500.0,
  "valor_unit_terreno": 24500.00,
  "area_construccion_m2": 120.0,
  "valor_unit_construccion": 85400.00,
  "area_comercio_m2": 0.0,
  "valor_unit_comercio": 95000.00,
  "valor_terreno": 12250000.00,
  "valor_construccion": 10248000.00,
  "valor_comercio": 0.00,
  "valor_catastral_total": 22498000.00,
  "via_acceso": "asfalto",
  "estructura_techo": "placa",
  "estructura_paredes": "bloque",
  "piso": "ceramica",
  "dormitorios": 3,
  "banos": 2,
  "sala": true,
  "cocina": true,
  "ambiente_otro": "comedor",
  "caracteristica_general": "aislada",
  "observaciones": "Inmueble en buen estado",
  "geom": {
    "type": "Polygon",
    "coordinates": [[
      [-72.2345, 7.7654],
      [-72.2346, 7.7655],
      [-72.2347, 7.7654],
      [-72.2346, 7.7653],
      [-72.2345, 7.7654]
    ]]
  },
  "utm_norte": 1234567.89,
  "utm_este": 234567.89,
  "superficie_gis_m2": 498.5,
  "perimetro_gis_m": 89.2,
  "fecha_emision": "2024-01-15",
  "fecha_recibo": "2024-01-15",
  "numero_recibo": "REC-2024-001",
  "vigente_hasta": "2025-01-15",
  "estado_sync": "synced",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Errores:**
- `404 Not Found`: Inmueble no encontrado

---

### PATCH `/api/v1/inmuebles/{inmueble_id}`
Actualizar un inmueble existente (solo los campos enviados).

**Autenticación:** Requerida (cualquier rol)

**Parámetros de ruta:**
- `inmueble_id` (UUID) - ID del inmueble

**Body (todos los campos opcionales):**
```json
{
  "propietario_id": "nuevo-uuid-propietario",
  "direccion": "Nueva dirección actualizada",
  "documento_tipo": "Nuevo tipo de documento",
  "documento_numero": "54321",
  "documento_tomo": "II",
  "documento_folio": "200",
  "documento_protocolo": "02",
  "documento_fecha": "2021-06-20",
  "tenencia": "arrendado",
  "contrato_arrendamiento_num": "CTR-2024-001",
  "contrato_arrendamiento_fecha": "2024-01-01",
  "area_terreno_m2": 550.0,
  "valor_unit_terreno": 25000.00,
  "area_construccion_m2": 130.0,
  "valor_unit_construccion": 86000.00,
  "area_comercio_m2": 50.0,
  "valor_unit_comercio": 96000.00,
  "existe_vivienda": true,
  "tipo_vivienda": "casa",
  "descripcion_uso": "mixto",
  "numero_plantas": 2,
  "uso_segun_zonificacion": "residencial",
  "observaciones": "Observaciones actualizadas",
  "fecha_emision": "2024-06-15",
  "fecha_recibo": "2024-06-15",
  "numero_recibo": "REC-2024-002",
  "geom": {
    "type": "Polygon",
    "coordinates": [[
      [-72.2345, 7.7654],
      [-72.2346, 7.7655],
      [-72.2347, 7.7654],
      [-72.2346, 7.7653],
      [-72.2345, 7.7654]
    ]]
  }
}
```

**Respuesta:** Objeto Inmueble actualizado (igual que GET)

**Errores:**
- `404 Not Found`: Inmueble no encontrado
- `422 Unprocessable Entity`: Geometría inválida
- `409 Conflict`: Solape topológico o conflicto de datos

---

### DELETE `/api/v1/inmuebles/{inmueble_id}`
Eliminar un inmueble del catastro.

**Autenticación:** Requerida
**Rol requerido:** administrador

**Parámetros de ruta:**
- `inmueble_id` (UUID) - ID del inmueble

**Respuesta:** 204 No Content

**Errores:**
- `404 Not Found`: Inmueble no encontrado
- `403 Forbidden`: Usuario no tiene rol de administrador

---

### GET `/api/v1/inmuebles/{inmueble_id}/cedula`
Descargar la cédula catastral en PDF.

**Autenticación:** Requerida (cualquier rol)

**Parámetros de ruta:**
- `inmueble_id` (UUID) - ID del inmueble

**Respuesta:** Archivo PDF (application/pdf)
- Content-Disposition: attachment; filename="cedula_catastral_{uuid}.pdf"

**Errores:**
- `404 Not Found`: Inmueble no encontrado

---

### POST `/api/v1/inmuebles/{inmueble_id}/hitos`
Agregar un hito predial (vértice GPS del polígono).

**Autenticación:** Requerida (cualquier rol)

**Parámetros de ruta:**
- `inmueble_id` (UUID) - ID del inmueble

**Body:**
```json
{
  "indice_vertice": 1,
  "descripcion": "Vértice 1 - Esquina noroeste",
  "lat": 7.7654,
  "lon": -72.2345,
  "foto_url": "https://storage.supabase.co/bucket/foto.jpg"
}
```

**Respuesta (201 Created):**
```json
{
  "id": "uuid-del-hito",
  "inmueble_id": "uuid-del-inmueble",
  "indice_vertice": 1,
  "descripcion": "Vértice 1 - Esquina noroeste",
  "lat": 7.7654,
  "lon": -72.2345,
  "utm_norte": 1234567.89,
  "utm_este": 234567.89,
  "foto_url": "https://storage.supabase.co/bucket/foto.jpg",
  "created_at": "2024-01-15T10:35:00Z"
}
```

**Errores:**
- `404 Not Found`: Inmueble no encontrado
- `409 Conflict`: Índice de vértice duplicado para el mismo inmueble

---

### GET `/api/v1/inmuebles/{inmueble_id}/hitos`
Listar todos los hitos prediales de un inmueble.

**Autenticación:** Requerida (cualquier rol)

**Parámetros de ruta:**
- `inmueble_id` (UUID) - ID del inmueble

**Respuesta:**
```json
[
  {
    "id": "uuid-del-hito-1",
    "inmueble_id": "uuid-del-inmueble",
    "indice_vertice": 1,
    "descripcion": "Vértice 1 - Esquina noroeste",
    "lat": 7.7654,
    "lon": -72.2345,
    "utm_norte": 1234567.89,
    "utm_este": 234567.89,
    "foto_url": "https://storage.supabase.co/bucket/foto1.jpg",
    "created_at": "2024-01-15T10:35:00Z"
  },
  {
    "id": "uuid-del-hito-2",
    "inmueble_id": "uuid-del-inmueble",
    "indice_vertice": 2,
    "descripcion": "Vértice 2 - Esquina noreste",
    "lat": 7.7655,
    "lon": -72.2346,
    "utm_norte": 1234568.89,
    "utm_este": 234568.89,
    "foto_url": "https://storage.supabase.co/bucket/foto2.jpg",
    "created_at": "2024-01-15T10:36:00Z"
  }
]
```

---

### POST `/api/v1/inmuebles/{inmueble_id}/fotos`
Agregar una foto del inmueble.

**Autenticación:** Requerida (cualquier rol)

**Parámetros de ruta:**
- `inmueble_id` (UUID) - ID del inmueble

**Body:**
```json
{
  "url": "https://storage.supabase.co/bucket/foto-inmueble.jpg",
  "descripcion": "Fachada principal del inmueble"
}
```

**Respuesta (201 Created):**
```json
{
  "id": "uuid-de-la-foto",
  "inmueble_id": "uuid-del-inmueble",
  "url": "https://storage.supabase.co/bucket/foto-inmueble.jpg",
  "descripcion": "Fachada principal del inmueble",
  "created_at": "2024-01-15T10:40:00Z"
}
```

---

### GET `/api/v1/inmuebles/{inmueble_id}/fotos`
Listar todas las fotos de un inmueble.

**Autenticación:** Requerida (cualquier rol)

**Parámetros de ruta:**
- `inmueble_id` (UUID) - ID del inmueble

**Respuesta:**
```json
[
  {
    "id": "uuid-de-la-foto-1",
    "inmueble_id": "uuid-del-inmueble",
    "url": "https://storage.supabase.co/bucket/foto1.jpg",
    "descripcion": "Fachada principal",
    "created_at": "2024-01-15T10:40:00Z"
  },
  {
    "id": "uuid-de-la-foto-2",
    "inmueble_id": "uuid-del-inmueble",
    "url": "https://storage.supabase.co/bucket/foto2.jpg",
    "descripcion": "Interior sala",
    "created_at": "2024-01-15T10:41:00Z"
  }
]
```

---

## 👥 Propietarios

### POST `/api/v1/propietarios`
Crear un nuevo propietario.

**Autenticación:** Requerida (cualquier rol)

**Body:**
```json
{
  "cedula_rif": "V-12345678",
  "nombre": "Juan",
  "apellido": "Pérez",
  "telefono": "+58-276-1234567",
  "email": "juan.perez@example.com",
  "direccion": "Calle Principal, #123, San Josecito"
}
```

**Respuesta (201 Created):**
```json
{
  "id": "uuid-del-propietario",
  "cedula_rif": "V-12345678",
  "nombre": "Juan",
  "apellido": "Pérez",
  "telefono": "+58-276-1234567",
  "email": "juan.perez@example.com",
  "direccion": "Calle Principal, #123, San Josecito",
  "created_at": "2024-01-15T10:20:00Z"
}
```

**Errores:**
- `409 Conflict`: Cédula/RIF duplicado

---

### GET `/api/v1/propietarios`
Listar propietarios con paginación, búsqueda y ordenamiento.

**Autenticación:** Requerida (cualquier rol)

**Query Parameters:**
- `pagina` (int, default: 1) - Número de página
- `por_pagina` (int, default: 25, max: 100) - Elementos por página
- `q` (string, opcional) - Búsqueda parcial por nombre, apellido o cédula/RIF
- `ordenar_por` (string, default: "nombre") - Campo de ordenamiento (nombre, apellido, cedula_rif, created_at)
- `orden` (string, default: "asc") - Dirección de ordenamiento (asc, desc)

**Ejemplos:**
```http
# Básico con paginación
GET /api/v1/propietarios?pagina=1&por_pagina=10

# Con búsqueda
GET /api/v1/propietarios?q=Pérez

# Ordenado por apellido descendente
GET /api/v1/propietarios?ordenar_por=apellido&orden=desc

# Ordenado por fecha de creación
GET /api/v1/propietarios?ordenar_por=created_at&orden=desc

# Combinado
GET /api/v1/propietarios?pagina=1&por_pagina=20&q=González&ordenar_por=nombre&orden=asc
```

**Respuesta:**
```json
{
  "total": 150,
  "pagina": 1,
  "por_pagina": 10,
  "resultados": [
    {
      "id": "uuid-del-propietario-1",
      "cedula_rif": "V-12345678",
      "nombre": "Juan",
      "apellido": "Pérez",
      "telefono": "+58-276-1234567",
      "email": "juan.perez@example.com",
      "direccion": "Calle Principal, #123, San Josecito",
      "created_at": "2024-01-15T10:20:00Z"
    },
    {
      "id": "uuid-del-propietario-2",
      "cedula_rif": "V-87654321",
      "nombre": "María",
      "apellido": "Pérez",
      "telefono": "+58-276-7654321",
      "email": "maria.perez@example.com",
      "direccion": "Avenida Bolívar, #456, San Josecito",
      "created_at": "2024-01-15T10:25:00Z"
    }
  ]
}
```

**Notas:**
- La búsqueda `q` usa índices trigram para rendimiento óptimo
- Campos de ordenamiento disponibles optimizados con índices correspondientes
- Respuesta paginada permite navegación eficiente en interfaces frontend

---

### GET `/api/v1/propietarios/{propietario_id}`
Obtener detalles de un propietario específico.

**Autenticación:** Requerida (cualquier rol)

**Parámetros de ruta:**
- `propietario_id` (UUID) - ID del propietario

**Respuesta:** Objeto Propietario completo

**Errores:**
- `404 Not Found`: Propietario no encontrado

---

### PATCH `/api/v1/propietarios/{propietario_id}`
Actualizar un propietario existente.

**Autenticación:** Requerida (cualquier rol)

**Parámetros de ruta:**
- `propietario_id` (UUID) - ID del propietario

**Body (todos los campos opcionales):**
```json
{
  "telefono": "+58-276-9999999",
  "email": "nuevo.email@example.com",
  "direccion": "Nueva dirección actualizada"
}
```

**Respuesta:** Objeto Propietario actualizado

**Errores:**
- `404 Not Found`: Propietario no encontrado
- `409 Conflict`: Cédula/RIF duplicado

---

### DELETE `/api/v1/propietarios/{propietario_id}`
Eliminar un propietario.

**Autenticación:** Requerida
**Rol requerido:** administrador

**Parámetros de ruta:**
- `propietario_id` (UUID) - ID del propietario

**Respuesta:** 204 No Content

**Errores:**
- `404 Not Found`: Propietario no encontrado
- `403 Forbidden`: Usuario no tiene rol de administrador
- `409 Conflict`: No se puede eliminar porque tiene inmuebles registrados (ON DELETE RESTRICT)

---

## 🗺️ Catastro

### GET `/api/v1/catastro/mapa`
Obtener el mapa catastral en formato GeoJSON.

**Autenticación:** Requerida (cualquier rol)

**Query Parameters (todos opcionales, para bbox):**
- `min_lon` (float) - Longitud mínima del área visible
- `min_lat` (float) - Latitud mínima del área visible
- `max_lon` (float) - Longitud máxima del área visible
- `max_lat` (float) - Latitud máxima del área visible

**Ejemplo con bbox:**
```http
GET /api/v1/catastro/mapa?min_lon=-72.25&min_lat=7.70&max_lon=-72.15&max_lat=7.80
```

**Ejemplo sin bbox (carga todo):**
```http
GET /api/v1/catastro/mapa
```

**Respuesta (GeoJSON FeatureCollection):**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-72.2345, 7.7654],
          [-72.2346, 7.7655],
          [-72.2347, 7.7654],
          [-72.2346, 7.7653],
          [-72.2345, 7.7654]
        ]]
      },
      "properties": {
        "id": "uuid-del-inmueble",
        "codigo": "20-27-01-01-001-001-000-000-000",
        "direccion": "Vía al Llano, Sector San José",
        "sector": "01",
        "superficie": 498.5
      }
    }
  ]
}
```

---

### GET `/api/v1/catastro/estadisticas`
Obtener estadísticas generales del catastro.

**Autenticación:** Requerida (cualquier rol)

**Respuesta:**
```json
{
  "total_predios": 1250,
  "superficie_total_m2": 625000.50,
  "valor_catastral_total": 15250000000.00,
  "predios_con_vivienda": 980,
  "valor_promedio_por_predio": 12200000.00,
  "por_tenencia": {
    "propio": 1100,
    "ejido": 100,
    "arrendado": 50
  },
  "por_sector": {
    "01": 450,
    "02": 380,
    "03": 420
  }
}
```

---

### GET `/api/v1/catastro/por-sector`
Obtener predios agrupados por sector catastral.

**Autenticación:** Requerida (cualquier rol)

**Uso:** Análisis estadístico por sector, distribución de trabajo de inspectores, planificación urbana por zona, reportes administrativos.

**Respuesta:**
```json
{
  "01": {
    "total_predios": 450,
    "superficie_total_m2": 225000.00,
    "valor_catastral_total": 5490000000.00
  },
  "02": {
    "total_predios": 380,
    "superficie_total_m2": 190000.00,
    "valor_catastral_total": 4636000000.00
  },
  "03": {
    "total_predios": 420,
    "superficie_total_m2": 210000.00,
    "valor_catastral_total": 5124000000.00
  }
}
```

**Campos de respuesta:**
- `total_predios`: Cantidad de inmuebles en el sector
- `superficie_total_m2`: Suma de superficies GIS de todos los predios del sector
- `valor_catastral_total`: Suma de valores catastrales de todos los predios del sector

---

### GET `/api/v1/catastro/solapamientos`
Detectar predios con solapamientos topológicos (auditoría).

**Autenticación:** Requerida
**Rol requerido:** administrador

**Respuesta:**
```json
[
  {
    "codigo_catastral_1": "20112701001001000000000",
    "codigo_catastral_2": "20112701001002000000000",
    "area_solape_m2": 15.5
  }
]
```

**Nota:** En condiciones normales esto debe devolver una lista vacía, ya que el trigger `prevenir_solape_predios` bloquea el guardado de polígonos superpuestos.

---

## 👤 Usuarios

### GET `/api/v1/usuarios/me`
Obtener el perfil del usuario autenticado actualmente.

**Autenticación:** Requerida (cualquier rol)

**Respuesta:**
```json
{
  "id": "uuid-del-usuario",
  "cedula": "V-12345678",
  "nombre": "Juan",
  "apellido": "Pérez",
  "rol": "inspector",
  "activo": true,
  "created_at": "2024-01-01T08:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

**Errores:**
- `404 Not Found`: Perfil no encontrado (se crea automáticamente al hacer signup en Supabase Auth)

---

### GET `/api/v1/usuarios`
Listar todos los usuarios del sistema.

**Autenticación:** Requerida
**Rol requerido:** administrador

**Respuesta:**
```json
[
  {
    "id": "uuid-del-usuario-1",
    "cedula": "V-12345678",
    "nombre": "Juan",
    "apellido": "Pérez",
    "rol": "administrador",
    "activo": true,
    "created_at": "2024-01-01T08:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z"
  },
  {
    "id": "uuid-del-usuario-2",
    "cedula": "V-87654321",
    "nombre": "María",
    "apellido": "González",
    "rol": "inspector",
    "activo": true,
    "created_at": "2024-01-02T09:00:00Z",
    "updated_at": "2024-01-10T14:00:00Z"
  }
]
```

**Errores:**
- `403 Forbidden`: Usuario no tiene rol de administrador

---

### PATCH `/api/v1/usuarios/{usuario_id}/rol`
Cambiar el rol de un usuario.

**Autenticación:** Requerida
**Rol requerido:** administrador

**Parámetros de ruta:**
- `usuario_id` (UUID) - ID del usuario

**Body:**
```json
{
  "rol": "administrador"
}
```

**Valores permitidos para `rol`: `administrador`, `inspector`

**Respuesta:** Objeto Usuario actualizado

**Errores:**
- `404 Not Found`: Usuario no encontrado
- `403 Forbidden`: Usuario no tiene rol de administrador

---

## 📊 Códigos de Estado HTTP

### 2xx - Success
- `200 OK`: Solicitud exitosa
- `201 Created`: Recurso creado exitosamente
- `204 No Content`: Solicitud exitosa sin contenido en la respuesta (usualmente DELETE)

### 4xx - Client Error
- `400 Bad Request`: Solicitud mal formada
- `401 Unauthorized`: No autenticado o token inválido
- `403 Forbidden`: Autenticado pero sin permisos suficientes
- `404 Not Found`: Recurso no encontrado
- `409 Conflict`: Conflicto de datos (duplicados, restricciones de integridad)
- `422 Unprocessable Entity`: Datos inválidos o validación fallida

### 5xx - Server Error
- `500 Internal Server Error`: Error interno del servidor
- `503 Service Unavailable`: Servicio no disponible temporalmente

---

## 🔧 Herramientas de Documentación

### Swagger UI
Documentación interactiva con posibilidad de probar las rutas directamente:
```
http://localhost:8000/docs
```

### ReDoc
Documentación alternativa con diseño más limpio:
```
http://localhost:8000/redoc
```

---

## 📝 Notas Importantes

1. **Autenticación**: Todas las rutas (excepto `/` y `/salud`) requieren token JWT válido en el header `Authorization`.

2. **Código Catastral**: Se genera automáticamente en el backend mediante triggers de PostgreSQL. No se debe enviar ni modificar manualmente.

3. **Geometría**: Las coordenadas deben estar en WGS84 (EPSG:4326) para el polígono `geom`. El sistema calcula automáticamente las coordenadas UTM (REGVEN).

4. **Valores Catastrales**: Los valores (terreno, construcción, comercio) se calculan automáticamente como `área × valor_unitario`. Solo se envían las áreas y valores unitarios.

5. **Solapamientos**: El sistema previene automáticamente solapamientos mayores a 1m² entre predios mediante triggers de PostGIS.

6. **Paginación**: Para listados grandes, siempre usar parámetros `pagina` y `por_pagina` para optimizar el rendimiento.

7. **Búsqueda**: Los parámetros de búsqueda `q` usan índices de texto completo (pg_trgm) para búsquedas parciales eficientes.

8. **Roles**: Las operaciones destructivas (DELETE) y de auditoría requieren rol de `administrador`.

---

## 📞 Soporte

Para issues o preguntas sobre la API, consultar:
- Documentación técnica del proyecto: `/docs`
- README principal del proyecto
- Soporte del equipo de desarrollo SRCM

---

**Última actualización:** Enero 2024
**Versión de la API:** 1.0.0
**Versión del SQL:** v2.5 Completa
