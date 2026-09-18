# SRCM Backend - Sistema de Registro Catastral Municipal

**Sistema de Registro Catastral Municipal para el Municipio Torbes, Estado Táchira, Venezuela**

Backend API REST desarrollado con FastAPI, PostgreSQL + PostGIS (Supabase) y generación de cédulas catastrales en PDF.

## 📋 Índice

- [Características](#características)
- [Requisitos Previos](#requisitos-previos)
- [Instalación Local](#instalación-local)
- [Configuración](#configuración)
- [Ejecución](#ejecución)
- [Despliegue en Render](#despliegue-en-render)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Documentación API](#documentación-api)
- [Troubleshooting](#troubleshooting)

## ✨ Características

- **Código Catastral Automático**: Generación automática de códigos catastrales según normativa venezolana (23 caracteres)
- **Cédulas Catastrales PDF**: Generación de documentos oficiales en PDF desde el backend
- **Mapa Catastral**: Geometría de predios con PostGIS y GeoJSON
- **Gestión de Inmuebles**: CRUD completo con validaciones topológicas
- **Gestión de Propietarios**: Registro y búsqueda de propietarios
- **Autenticación**: Integración con Supabase Auth
- **Roles de Usuario**: Administrador e Inspector
- **Auditoría**: Control de cambios y topología de predios

## 🔧 Requisitos Previos

### Software Necesario

- **Python 3.12+** (recomendado 3.12)
- **Git**
- **Supabase Account** (para base de datos y autenticación)

### Dependencias del Sistema

#### ⚠️ GTK3 Runtime (Solo para Windows - Requerido para PDFs)

Para generar cédulas catastrales en PDF, WeasyPrint requiere GTK3 runtime en Windows:

**Opción 1: Instalación en Windows (RECOMENDADA)**
1. Descarga el instalador desde: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
2. Ejecuta el instalador (no requiere configuración especial)
3. Reinicia tu terminal

> **¿Es seguro?** Sí, GTK3 runtime es 100% seguro. Es similar a instalar .NET Framework o Visual C++ redistributable. Solo añade librerías necesarias para renderizar PDFs. Se puede desinstalar completamente si lo deseas.

**Opción 2: WSL2 (Alternativa sin tocar Windows)**
- Instala WSL2 con Ubuntu
- Instala las librerías de Linux dentro de WSL2
- Corre el backend desde WSL2

**Opción 3: Omitir PDFs por ahora**
- El resto de la API funciona perfectamente sin GTK3
- Puedes instalar GTK3 más tarde si necesitas generar PDFs

## 📦 Instalación Local

### 1. Clonar el Repositorio

```bash
git clone <tu-repositorio>
cd srcm-backend
```

### 2. Crear Entorno Virtual

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Supabase

1. Crea un proyecto en [Supabase](https://supabase.com)
2. Ve a Settings > API y copia:
   - Project URL
   - anon public key
   - service_role key
3. Ve a Settings > Database y copia:
   - Connection string (URI)
4. Ejecuta el script SQL en Supabase SQL Editor:
   ```bash
   # Copia el contenido de srcm_supabase_completo.sql
   # Pégalo en el SQL Editor de Supabase
   # Ejecuta el script
   ```

### 5. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# Aplicación
APP_NAME=SRCM API
APP_ENV=development
DEBUG=True
API_V1_PREFIX=/api/v1

# Base de datos (Supabase)
DATABASE_URL=postgresql://postgres:[password]@[project-ref].supabase.co:5432/postgres

# Supabase Auth
SUPABASE_URL=https://[project-ref].supabase.co
SUPABASE_ANON_KEY=[anon-key]
SUPABASE_SERVICE_ROLE_KEY=[service-role-key]
SUPABASE_JWT_SECRET=[jwt-secret]

# Seguridad
SECRET_KEY=[genera-una-clave-secreta]
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALGORITHM=HS256

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Storage
SUPABASE_STORAGE_BUCKET=catastro-archivos

# Configuración catastral
CODIGO_ESTADO=20
CODIGO_MUNICIPIO=27
CODIGO_PARROQUIA=01
SRID_UTM=2201
```

**Generar SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 🚀 Ejecución

### Modo Desarrollo

```bash
# Activar entorno virtual
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Ejecutar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en:
- **API**: http://localhost:8000
- **Documentación (Swagger)**: http://localhost:8000/docs
- **Documentación (ReDoc)**: http://localhost:8000/redoc

### Verificar Instalación

```bash
# Health check
curl http://localhost:8000/salud

# Debe retornar: {"status": "ok"}
```

## 🌐 Despliegue en Render

### Archivos a Subir

**OBLIGATORIOS:**
```
srcm-backend/
├── app/                    # Todo el código de la aplicación
├── requirements.txt         # Dependencias
├── .env                    # Variables de entorno (producción)
├── Procfile                # Configuración de Render
└── srcm_supabase_completo.sql  # Para ejecutar en Supabase
```

**NO subir:**
- `.venv/` (Render crea su propio entorno)
- Archivos en `.gitignore`
- Scripts de desarrollo

### Crear Procfile

Crea un archivo `Procfile` en la raíz:

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Configuración en Render

1. **Crear Web Service**
   - Connect GitHub repository
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

2. **Variables de Entorno**
   - Agrega todas las variables del `.env` en Render
   - Usa valores de producción (no valores de desarrollo)

3. **Base de Datos**
   - Ejecuta `srcm_supabase_completo.sql` en Supabase producción
   - Configura `DATABASE_URL` con la URI de producción

### ¿Dará problemas en Render?

**NO** porque:
- ✅ Python 3.12 está soportado en Render
- ✅ FastAPI está optimizado para servicios en la nube
- ✅ WeasyPrint funciona en Render (Linux tiene GTK3 nativo)
- ✅ Supabase es compatible con cualquier hosting

## 📁 Estructura del Proyecto

```
srcm-backend/
├── app/
│   ├── core/                 # Configuración y seguridad
│   │   ├── config.py         # Configuración central
│   │   ├── deps.py           # Dependencias de inyección
│   │   └── security.py       # Autenticación y JWT
│   ├── db/                   # Base de datos
│   │   └── session.py        # Sesión de SQLAlchemy
│   ├── models/               # Modelos ORM
│   │   ├── inmueble.py
│   │   ├── propietario.py
│   │   ├── usuario.py
│   │   ├── foto.py
│   │   └── hito.py
│   ├── routers/              # Endpoints API
│   │   ├── inmuebles.py      # CRUD inmuebles
│   │   ├── propietarios.py   # CRUD propietarios
│   │   ├── catastro.py       # Mapa y estadísticas
│   │   └── usuarios.py       # Gestión de usuarios
│   ├── schemas/              # Esquemas Pydantic
│   │   ├── inmueble.py
│   │   ├── propietario.py
│   │   ├── usuario.py
│   │   ├── foto.py
│   │   └── hito.py
│   ├── services/             # Lógica de negocio
│   │   ├── inmueble_service.py
│   │   ├── propietario_service.py
│   │   ├── catastro_service.py
│   │   ├── cedula_service.py # Generación PDF
│   │   └── geo_service.py    # Geometría y coordenadas
│   ├── utils/                # Utilidades
│   │   ├── catastro_codigo.py # Generador de códigos
│   │   └── db_errors.py      # Manejo de errores
│   ├── api_router.py         # Router principal
│   └── main.py               # Entry point
├── requirements.txt          # Dependencias Python
├── .env                     # Variables de entorno
├── Procfile                 # Configuración Render
└── srcm_supabase_completo.sql # Script SQL
```

## 📚 Documentación API

Una vez ejecutado el servidor, accede a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints Principales

**Total: 35 endpoints implementados**

#### Inmuebles (13 endpoints)
- `POST /api/v1/inmuebles` - Crear inmueble
- `GET /api/v1/inmuebles` - Listar inmuebles (paginación, filtros)
- `GET /api/v1/inmuebles/{id}` - Obtener inmueble
- `PATCH /api/v1/inmuebles/{id}` - Actualizar inmueble
- `DELETE /api/v1/inmuebles/{id}` - Eliminar inmueble
- `GET /api/v1/inmuebles/{id}/cedula` - Descargar cédula catastral PDF
- `GET /api/v1/inmuebles/{id}/cedula-datos` - Obtener datos para cédula (frontend)
- `POST /api/v1/inmuebles/{id}/fotos` - Agregar foto
- `GET /api/v1/inmuebles/{id}/fotos` - Listar fotos
- `DELETE /api/v1/inmuebles/{id}/fotos/{foto_id}` - Eliminar foto
- `POST /api/v1/inmuebles/{id}/hitos` - Agregar hito predial
- `GET /api/v1/inmuebles/{id}/hitos` - Listar hitos
- `DELETE /api/v1/inmuebles/{id}/hitos/{hito_id}` - Eliminar hito

#### Propietarios (6 endpoints)
- `POST /api/v1/propietarios` - Crear propietario
- `GET /api/v1/propietarios` - Listar propietarios
- `GET /api/v1/propietarios/{id}` - Obtener propietario
- `PATCH /api/v1/propietarios/{id}` - Actualizar propietario
- `DELETE /api/v1/propietarios/{id}` - Eliminar propietario
- `GET /api/v1/propietarios/{id}/inmuebles` - Listar inmuebles de propietario

#### Catastro (5 endpoints)
- `GET /api/v1/catastro/mapa` - Mapa catastral (GeoJSON)
- `GET /api/v1/catastro/estadisticas` - Estadísticas generales
- `GET /api/v1/catastro/por-sector` - Predios por sector
- `GET /api/v1/catastro/solapamientos` - Auditoría topológica
- `GET /api/v1/catastro/sectores` - Listar sectores disponibles

#### Configuración (5 endpoints)
- `GET /api/v1/configuracion/catastral` - Obtener configuración catastral
- `PATCH /api/v1/configuracion/catastral` - Actualizar configuración catastral
- `GET /api/v1/configuracion/sistema` - Obtener configuración del sistema
- `PATCH /api/v1/configuracion/sistema` - Actualizar configuración del sistema
- `GET /api/v1/configuracion/catastral/pdf-config` - Configuración para PDF

#### Usuarios (4 endpoints)
- `GET /api/v1/usuarios/me` - Perfil actual
- `GET /api/v1/usuarios` - Listar usuarios (admin)
- `PATCH /api/v1/usuarios/{id}/rol` - Cambiar rol (admin)
- `PATCH /api/v1/usuarios/{id}/estado` - Activar/desactivar usuario (admin)

#### Salud (2 endpoints)
- `GET /` - Raíz del sistema
- `GET /salud` - Health check

## 🔍 Troubleshooting

### Error: "cannot load library 'libgobject-2.0-0'"

**Solución:** Instala GTK3 Runtime en Windows
1. Descarga desde: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
2. Ejecuta el instalador
3. Reinicia terminal

### Error: "Connection refused" al conectar a Supabase

**Solución:**
- Verifica que `DATABASE_URL` sea correcta
- Revisa que tu IP esté en los allowed hosts de Supabase
- Verifica que las credenciales sean correctas

### Error: "Module not found"

**Solución:**
```bash
# Asegúrate de estar en el entorno virtual
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Reinstala dependencias
pip install -r requirements.txt
```

### Error: PDF no se genera

**Solución:**
- Verifica que GTK3 Runtime esté instalado
- Reinicia el terminal después de instalar GTK3
- Ejecuta el script de prueba: `python test_pdf_prueba.py`

### Error: CORS en el frontend

**Solución:**
- Verifica `CORS_ORIGINS` en `.env`
- Agrega la URL de tu frontend
- Ejemplo: `CORS_ORIGINS=http://localhost:3000,http://localhost:5173`

## 📖 Documentación Adicional

Para más detalles sobre flujos de trabajo y uso de la API, consulta:

- **[FLUJOS_DE_TRABAJO.md](FLUJOS_DE_TRABAJO.md)** - Guía completa de flujos de trabajo con ejemplos visuales

## 🤝 Soporte

Para problemas o preguntas:
- Revisa la documentación en `/docs`
- Verifica el troubleshooting arriba
- Consulta los logs del servidor para errores detallados

## 📄 Licencia

Sistema desarrollado para la Alcaldía del Municipio Torbes, Estado Táchira, Venezuela.
