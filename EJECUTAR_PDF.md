# SRCM Backend - Comandos y Archivos Editables

## Iniciar el servidor

```bash
.venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API disponible en: `http://localhost:8000/docs`

---

## Generar PDF de prueba (sin servidor)

```bash
.venv\Scripts\python.exe test_pdf_prueba.py
.venv\Scripts\python.exe test_pdf_prueba.py --n 1
.venv\Scripts\python.exe test_pdf_prueba.py --n 5
```

Los PDFs se guardan en `pdfs_prueba/`.

---

## Generar PDF via API (con servidor corriendo)

```
GET /api/v1/inmuebles/{inmueble_id}/cedula
```

Ejemplo con curl:

```bash
curl -o cedula.pdf http://localhost:8000/api/v1/inmuebles/TU-UUID-AQUI/cedula
```

---

## Verificar cantidad de paginas del PDF

```bash
.venv\Scripts\python.exe -c "from PyPDF2 import PdfReader; from pathlib import Path; p=list(Path('pdfs_prueba').iterdir())[0]; r=PdfReader(str(p)); print(f'{p.name}: {len(r.pages)} paginas')"
```

---

## Poblar la base de datos con datos de prueba

```bash
.venv\Scripts\python.exe scripts/seed_datos_realistas.py
```

---

## Crear usuario administrador

```bash
.venv\Scripts\python.exe scripts/crear_admin.py
```

---

## Instalar dependencias

```bash
.venv\Scripts\pip.exe install -r requirements.txt
```

Requiere **GTK3 Runtime** para WeasyPrint (Windows):
https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases

---

## Variables de entorno (.env)

Crear archivo `.env` en la raiz del proyecto:

```env
DATABASE_URL=postgresql+psycopg2://usuario:password@host:5432/basededatos
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
SUPABASE_JWT_SECRET=...
SECRET_KEY=tu-clave-secreta
CORS_ORIGINS=http://localhost:3000
```

---

## Archivos editables para modificar el PDF

### Plantilla HTML (lo mas importante)

| Archivo | Descripcion |
|---------|-------------|
| `app/templates/cedula_catastral.html` | Plantilla completa del PDF (2 paginas). Aqui se cambian textos, layout, logos, tamaños, colores, firmas, tablas |

### Logos e imagenes

| Archivo | Descripcion |
|---------|-------------|
| `static/logos/escudotachira.png` | Escudo del Estado Tachira (header izquierdo) |
| `static/logos/escudotorbes.png` | Escudo del Municipio Torbes (header derecho) |
| `static/logos/escudovenezuela.png` | Escudo de Venezuela |
| `static/logos/logoalcaldia.png` | Logo de la Alcaldia (pie de pagina 1) |

### Logica y filtros

| Archivo | Descripcion |
|---------|-------------|
| `app/services/cedula_service.py` | Servicio que genera el PDF. Filtros Jinja2 (`fmt_money`, `fmt_area`, `fmt_mts`, `fmt_num`), generacion de QR, consulta a la vista `v_pdf_cedula_catastral` |
| `test_pdf_prueba.py` | Script de prueba con datos realistas de Torbes (nombres, sectores, linderos, etc.) |

### Backend - Rutas API

| Archivo | Descripcion |
|---------|-------------|
| `app/routers/inmuebles.py` | Endpoints de inmuebles + endpoint `GET /{id}/cedula` que devuelve el PDF |
| `app/routers/catastro.py` | Mapa catastral, estadisticas, solapamientos |
| `app/routers/propietarios.py` | CRUD de propietarios |
| `app/routers/usuarios.py` | Autenticacion y usuarios |

### Backend - Modelos y schemas

| Archivo | Descripcion |
|---------|-------------|
| `app/models/inmueble.py` | Modelo SQLAlchemy del inmueble |
| `app/models/propietario.py` | Modelo del propietario |
| `app/schemas/inmueble.py` | Schemas Pydantic (entrada/salida API) |
| `app/services/inmueble_service.py` | Logica de negocio de inmuebles |
| `app/services/inmueble_mapper.py` | Mapeo modelo -> schema de respuesta |

### Configuracion

| Archivo | Descripcion |
|---------|-------------|
| `app/core/config.py` | Configuracion central (lee `.env`): DATABASE_URL, claves, CORS, codigo catastral por defecto |
| `app/core/security.py` | JWT, hash de contrasenas |
| `app/core/deps.py` | Dependencias FastAPI (auth, db session) |
| `app/db/session.py` | Conexion a PostgreSQL/Supabase |

### Base de datos

| Archivo | Descripcion |
|---------|-------------|
| `srcm_supabase_completo.sql` | Schema SQL v2.5 completo (tablas, vistas, triggers, funciones PostGIS) |
| `scripts/seed_datos_realistas.py` | Poblador de BD con datos realistas de Torbes |
| `scripts/crear_admin.py` | Crea usuario administrador |

---

## Estructura del PDF (cedula_catastral.html)

```
Pagina 1 - Certificacion formal
  +-- Header: escudos + nombre institucion + RIF
  +-- Direccion y telefonos
  +-- Titulo: "CEDULA CATASTRAL"
  +-- Cuerpo: texto legal de certificacion (propietario, cedula, direccion, areas, valor)
  +-- Linderos: Norte / Sur / Este / Oeste (documento + metros)
  +-- Disclaimer legal (borde rojo)
  +-- Fecha de emision
  +-- Firmas (Alcaldesa + Directora de Catastro)
  +-- Pie: direccion + logo alcaldia

Pagina 2 - Tablas tecnicas
  +-- Header: escudos + nombre institucion
  +-- Bloque superior: tipo documento + codigo catastral + expediente + vigencia
  +-- Tabla propietario
  +-- Tabla ubicacion
  +-- Tabla terreno y construccion
  +-- Tabla servicios
  +-- Tabla linderos topograficos
  +-- Tabla valoracion
  +-- Tabla documento / tenencia
  +-- QR + sello
```

---

## Clases CSS principales del PDF

| Clase | Uso |
|-------|-----|
| `.header` / `.emblem` / `.header-center` | Encabezado con escudos |
| `.hc-1` a `.hc-5` | Lineas de texto del header |
| `.inst-info` | Direccion y telefonos |
| `.cert-title` | "CEDULA CATASTRAL" |
| `.cert-body` | Texto legal de certificacion |
| `.cert-linderos` / `.cert-lin-row` | Linderos del inmueble |
| `.cert-disclaimer` | Disclaimer legal (borde rojo) |
| `.cert-fecha` | Fecha de emision |
| `.sigs` / `.sig` / `.sig-line` | Firmas |
| `.foot-bar` / `.foot-logo` | Pie de pagina 1 |
| `.upper-block` / `.doc-type` / `.code-box` | Bloque superior pagina 2 |
| `.data-table` / `.data-section` | Tablas tecnicas pagina 2 |
| `.ribbon-corner` / `.ribbon-corner-br` | Esquinas tricolores venezolanas |
| `.watermark` | Marca de agua (escudo) |
