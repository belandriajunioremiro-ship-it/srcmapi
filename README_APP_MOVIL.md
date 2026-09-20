# 📱 SRCM Mobile — App de Inspección Catastral en Campo

Aplicación móvil oficial del **Sistema de Registro Catastral Municipal (SRCM)**.
Herramienta exclusiva de campo para inspectores y topógrafos de la Alcaldía del Municipio Torbes.

> **Función única:** Login, Registro de cuenta, Crear propietarios, Registrar inmuebles completos (linderos, servicios, características, GPS, fotos).

---

## 🎨 Design System

| Elemento | Valor |
|:--|:--|
| **Primario** | `#2563EB` (Azul Institucional) |
| **Fondo claro** | `#FFFFFF` / `#F3F4F6` |
| **Texto título** | `#111827` (Negro) |
| **Texto secundario** | `#4B5563` (Gris oscuro) |
| **Tipografía** | Nunito (Google Fonts) o sistema nativo |
| **Estilo** | Boxless, sombras suaves, botones amplios touch-friendly |

---

## 🛠️ Stack Tecnológico

| Categoría | Paquete | Función |
|:--|:--|:--|
| **Framework** | `react-native` + `expo` | Base de la app |
| **Navegación** | `@react-navigation/native` | Sistema de rutas |
| | `@react-navigation/native-stack` | Stack de pantallas |
| | `@react-navigation/bottom-tabs` | Tabs inferiores |
| **Auth** | `@supabase/supabase-js` | Login/Registro directo con Supabase |
| | `@react-native-async-storage/async-storage` | Persistir sesión JWT |
| **HTTP** | `axios` | Consumir API de Render |
| **Formularios** | `react-hook-form` | Gestión de formularios complejos |
| | `zod` + `@hookform/resolvers` | Validación de esquemas |
| **GPS** | `expo-location` | Capturar Lat/Lon del topógrafo |
| **Cámara/Fotos** | `expo-image-picker` | Tomar fotos de fachada |
| **Estilos** | `nativewind` + `tailwindcss` | Tailwind CSS en React Native |
| **Iconos** | `@expo/vector-icons` | Iconografía (viene con Expo) |
| **Notificaciones** | `react-native-toast-message` | Alertas visuales |
| **Splash/Loading** | `expo-splash-screen` | Pantalla de carga |
| **Seguridad** | `expo-secure-store` | Almacenar tokens de forma segura |
| **Fuentes** | `expo-font` + `@expo-google-fonts/nunito` | Tipografía Nunito |

---

## 📦 Comandos de Instalación (Copy-Paste)

### 1. Crear el proyecto
```bash
npx create-expo-app srcm-mobile --template blank
cd srcm-mobile
```

### 2. Navegación
```bash
npx expo install @react-navigation/native @react-navigation/native-stack @react-navigation/bottom-tabs react-native-screens react-native-safe-area-context
```

### 3. Supabase Auth + Almacenamiento seguro
```bash
npx expo install @supabase/supabase-js @react-native-async-storage/async-storage expo-secure-store
```

### 4. HTTP Client
```bash
npm install axios
```

### 5. Formularios y Validación
```bash
npm install react-hook-form zod @hookform/resolvers
```

### 6. Hardware (GPS + Cámara)
```bash
npx expo install expo-location expo-image-picker
```

### 7. Estilos (NativeWind / Tailwind)
```bash
npm install nativewind tailwindcss
npx tailwindcss init
```

### 8. UI Extras (Fuentes, Iconos, Toast, Splash)
```bash
npx expo install expo-font @expo-google-fonts/nunito expo-splash-screen react-native-toast-message
```

---

## 📂 Estructura de Carpetas y Archivos

```
srcm-mobile/
├── App.js                                    # Punto de entrada, proveedores de contexto
├── app.json                                  # Config Expo (permisos GPS, cámara, nombre)
├── tailwind.config.js                        # Config de NativeWind / Tailwind
├── babel.config.js                           # Config Babel (plugin NativeWind)
│
├── src/
│   │
│   ├── config/
│   │   ├── supabase.js                       # Cliente Supabase (URL + anon key)
│   │   ├── api.js                            # Instancia Axios con baseURL e interceptor JWT
│   │   └── constants.js                      # Colores, URLs, textos reutilizables
│   │
│   ├── contexts/
│   │   └── AuthContext.js                    # Context API para sesión del usuario
│   │
│   ├── navigation/
│   │   ├── AppNavigator.js                   # Decide: AuthStack o MainStack según sesión
│   │   ├── AuthStack.js                      # Stack: Login → Registro
│   │   └── MainStack.js                      # Stack: Dashboard → Wizard de Registro
│   │
│   ├── screens/
│   │   ├── auth/
│   │   │   ├── LoginScreen.js                # Pantalla de inicio de sesión
│   │   │   └── RegisterScreen.js             # Pantalla de crear cuenta
│   │   │
│   │   ├── home/
│   │   │   └── DashboardScreen.js            # Menú principal (Nuevo Registro, Historial)
│   │   │
│   │   └── registro/
│   │       ├── Paso1_PropietarioScreen.js    # Cédula, nombre, apellido, teléfono, email
│   │       ├── Paso2_DocumentoScreen.js      # Documento de propiedad + Linderos según documento
│   │       ├── Paso3_CaracteristicasScreen.js # Servicios, edificación, linderos topográficos
│   │       ├── Paso4_AvaluoScreen.js         # Áreas m², valores unitarios, zonificación
│   │       ├── Paso5_GPSFotosScreen.js       # Captura GPS (expo-location) + Cámara
│   │       └── Paso6_ResumenScreen.js        # Vista previa completa antes de enviar
│   │
│   ├── components/
│   │   ├── ui/
│   │   │   ├── Button.js                     # Botón primario/secundario reutilizable
│   │   │   ├── Input.js                      # Input de texto con label y error
│   │   │   ├── Switch.js                     # Toggle para booleanos (Electricidad SI/NO)
│   │   │   ├── Select.js                     # Picker/Dropdown (tipo vivienda, tenencia)
│   │   │   └── StepIndicator.js              # Barra de progreso del Wizard (Paso 1 de 6)
│   │   │
│   │   ├── LinderoInput.js                   # Componente para 1 lindero (descripción + metros)
│   │   ├── LinderoGroup.js                   # Grupo de 4 linderos (Norte/Sur/Este/Oeste)
│   │   ├── GPSCapture.js                     # Botón + display de coordenadas capturadas
│   │   └── PhotoCapture.js                   # Botón de cámara + preview de foto
│   │
│   ├── services/
│   │   ├── authService.js                    # signIn(), signUp(), signOut() con Supabase
│   │   ├── propietarioService.js             # crearPropietario(), buscarPropietario()
│   │   ├── inmuebleService.js                # crearInmueble(), listarInmuebles()
│   │   ├── hitoService.js                    # agregarHito() con coordenadas GPS
│   │   ├── fotoService.js                    # subirFoto() con URL de imagen
│   │   └── locationService.js                # getCurrentPosition() con alta precisión
│   │
│   ├── hooks/
│   │   ├── useAuth.js                        # Hook para consumir AuthContext
│   │   └── useLocation.js                    # Hook para captura GPS con estado de carga
│   │
│   ├── validations/
│   │   ├── propietarioSchema.js              # Esquema Zod para validar propietario
│   │   ├── inmuebleSchema.js                 # Esquema Zod para validar inmueble completo
│   │   └── loginSchema.js                    # Esquema Zod para login/registro
│   │
│   └── utils/
│       ├── formatters.js                     # Formatear moneda (Bs), fechas, cédula
│       └── storage.js                        # Helpers para SecureStore (guardar/leer token)
```

---

## 📱 Flujo de Pantallas (Wizard de 6 Pasos)

```
┌─────────────┐     ┌──────────────┐
│   LOGIN     │────▶│  DASHBOARD   │
│  REGISTRO   │     │  (Menú)      │
└─────────────┘     └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  PASO 1      │  Propietario: Cédula, Nombre, Apellido, Teléfono, Email
                    └──────┬───────┘
                    ┌──────▼───────┐
                    │  PASO 2      │  Documento: Tipo, Número, Tomo, Folio, Protocolo, Fecha
                    │              │  Linderos Según Documento: N/S/E/O + metros
                    └──────┬───────┘
                    ┌──────▼───────┐
                    │  PASO 3      │  Servicios: Agua, Electricidad, Contador (toggles)
                    │              │  Edificación: Tipo vivienda, Techo, Paredes, Piso
                    │              │  Linderos Según Topografía: N/S/E/O + metros
                    └──────┬───────┘
                    ┌──────▼───────┐
                    │  PASO 4      │  Avalúos: Área terreno m², Valor unit, Área construcción
                    │              │  Área comercio, Zonificación, Plantas
                    └──────┬───────┘
                    ┌──────▼───────┐
                    │  PASO 5      │  [CAPTURAR GPS] → expo-location (Lat/Lon)
                    │              │  [TOMAR FOTO]   → expo-image-picker (Fachada)
                    └──────┬───────┘
                    ┌──────▼───────┐
                    │  PASO 6      │  Resumen completo → Confirmar → Enviar al Backend
                    └──────────────┘
```

---

## 🌐 Mapa Completo de Endpoints a Consumir

**Base URL:** `https://srcmapi.onrender.com/api/v1`
**Header obligatorio:** `Authorization: Bearer <TOKEN_SUPABASE>`

### Autenticación (Directo con Supabase SDK — No pasa por el backend)

| Acción | Método Supabase | Campos |
|:--|:--|:--|
| **Login** | `supabase.auth.signInWithPassword()` | `email` (req), `password` (req) |
| **Registro** | `supabase.auth.signUp()` | `email` (req), `password` (req) |
| **Cerrar sesión** | `supabase.auth.signOut()` | — |
| **Sesión actual** | `supabase.auth.getSession()` | — (devuelve `access_token`) |

> ⚠️ La confirmación de email está **desactivada** en Supabase. La cuenta se activa al instante.

---

### Propietarios — `POST /api/v1/propietarios`

Crea un nuevo propietario (dueño del terreno). Se ejecuta en el **Paso 1** del Wizard.

| Campo | Tipo | Requerido | Ejemplo |
|:--|:--|:--|:--|
| `cedula_rif` | `string` (5-20 chars) | ✅ Sí | `"V-12345678"` |
| `nombre` | `string` (min 1) | ✅ Sí | `"Juan Carlos"` |
| `apellido` | `string` (min 1) | ✅ Sí | `"Pérez López"` |
| `telefono` | `string \| null` | ❌ No | `"0414-5551234"` |
| `email` | `email \| null` | ❌ No | `"juan@correo.com"` |
| `direccion` | `string \| null` | ❌ No | `"Av. Principal, San Josecito"` |

**Respuesta:** `201 Created` → `PropietarioOut` (incluye `id: UUID` generado).

---

### Inmuebles — `POST /api/v1/inmuebles`

Crea el registro catastral completo. Se ejecuta en el **Paso 6** (al confirmar el resumen). Es el payload más grande de la API.

#### Identificación y Ubicación Catastral

| Campo | Tipo | Requerido | Ejemplo |
|:--|:--|:--|:--|
| `propietario_id` | `UUID` | ❌ No | `"7e5846d2-6639-..."` |
| `direccion` | `string` (min 1) | ✅ Sí | `"Quinta El Trigal #45"` |
| `sector` | `string` (2 chars) | ✅ Sí | `"06"` |
| `manzana` | `string` (3 chars) | ✅ Sí | `"049"` |
| `parcela` | `string` (3 chars) | ✅ Sí | `"232"` |
| `subparcela` | `string` (3 chars) | ❌ No | `"000"` (default) |
| `nivel` | `string` (3 chars) | ❌ No | `"000"` (default) |
| `unidad` | `string` (3 chars) | ❌ No | `"000"` (default) |
| `tenencia` | `string` | ❌ No | `"propio"` / `"ejido"` / `"arrendado"` |

#### Documento de Propiedad (Transcripción del papel viejo)

| Campo | Tipo | Requerido | Ejemplo |
|:--|:--|:--|:--|
| `documento_tipo` | `string \| null` | ❌ No | `"Registro Inmobiliario de Torbes"` |
| `documento_numero` | `string \| null` | ❌ No | `"DOC-2658"` |
| `documento_tomo` | `string \| null` | ❌ No | `"Tomo IV"` |
| `documento_folio` | `string \| null` | ❌ No | `"Folios 45 al 50"` |
| `documento_protocolo` | `string \| null` | ❌ No | `"Primer Protocolo"` |
| `documento_fecha` | `date (YYYY-MM-DD)` | ❌ No | `"2018-05-14"` |

#### Linderos Según Documento (Lo que dice el papel viejo)

| Campo | Tipo | Requerido | Ejemplo |
|:--|:--|:--|:--|
| `lindero_norte_doc` | `string \| null` | ❌ No | `"Calle Principal de la Urbanización"` |
| `lindero_norte_mts` | `float \| null` | ❌ No | `15.50` |
| `lindero_sur_doc` | `string \| null` | ❌ No | `"Parcela Colindante N° 08"` |
| `lindero_sur_mts` | `float \| null` | ❌ No | `15.50` |
| `lindero_este_doc` | `string \| null` | ❌ No | `"Avenida Los Cedros"` |
| `lindero_este_mts` | `float \| null` | ❌ No | `22.58` |
| `lindero_oeste_doc` | `string \| null` | ❌ No | `"Terreno Municipal Área Verde"` |
| `lindero_oeste_mts` | `float \| null` | ❌ No | `22.58` |

#### Linderos Según Levantamiento Topográfico (Lo que el inspector mide en campo)

| Campo | Tipo | Requerido | Ejemplo |
|:--|:--|:--|:--|
| `lindero_norte_top` | `string \| null` | ❌ No | `"Calle Principal (Muro Perimetral)"` |
| `lindero_norte_top_mts` | `float \| null` | ❌ No | `15.55` |
| `lindero_sur_top` | `string \| null` | ❌ No | `"Parcela Colindante N° 08 (Cerca)"` |
| `lindero_sur_top_mts` | `float \| null` | ❌ No | `15.52` |
| `lindero_este_top` | `string \| null` | ❌ No | `"Avenida Los Cedros"` |
| `lindero_este_top_mts` | `float \| null` | ❌ No | `22.60` |
| `lindero_oeste_top` | `string \| null` | ❌ No | `"Terreno Municipal Área Verde"` |
| `lindero_oeste_top_mts` | `float \| null` | ❌ No | `22.55` |

#### Servicios de Factibilidad

| Campo | Tipo | Requerido | Default |
|:--|:--|:--|:--|
| `aguas_blancas` | `bool` | ❌ No | `false` |
| `aguas_servidas` | `bool` | ❌ No | `false` |
| `electricidad` | `bool` | ❌ No | `false` |
| `contador` | `bool` | ❌ No | `false` |

#### Edificación y Uso

| Campo | Tipo | Requerido | Ejemplo |
|:--|:--|:--|:--|
| `existe_vivienda` | `bool` | ❌ No | `true` |
| `tipo_vivienda` | `string \| null` | ❌ No | `"Quinta de dos niveles"` |
| `descripcion_uso` | `string` | ❌ No | `"residencial"` (default) |
| `numero_plantas` | `int \| null` | ❌ No | `2` |
| `uso_segun_zonificacion` | `string \| null` | ❌ No | `"R3 - Residencial Mixto"` |

#### Características Físicas del Inmueble

| Campo | Tipo | Requerido | Ejemplo |
|:--|:--|:--|:--|
| `via_acceso` | `string \| null` | ❌ No | `"asfalto"` |
| `estructura_techo` | `string \| null` | ❌ No | `"placa"` |
| `estructura_paredes` | `string \| null` | ❌ No | `"bloque"` |
| `piso` | `string \| null` | ❌ No | `"ceramica"` |
| `dormitorios` | `int \| null` | ❌ No | `5` |
| `banos` | `int \| null` | ❌ No | `4` |
| `sala` | `bool` | ❌ No | `true` |
| `cocina` | `bool` | ❌ No | `true` |
| `ambiente_otro` | `string \| null` | ❌ No | `"Estacionamiento, Patio trasero"` |
| `caracteristica_general` | `string \| null` | ❌ No | `"aislada"` |
| `observaciones` | `string \| null` | ❌ No | `"Levantamiento con Drone RTK"` |

#### Avalúos (Valores en Bolívares por m²)

| Campo | Tipo | Requerido | Ejemplo |
|:--|:--|:--|:--|
| `area_terreno_m2` | `float \| null` | ❌ No | `350.00` |
| `valor_unit_terreno` | `float \| null` | ❌ No | `24500.00` |
| `area_construccion_m2` | `float \| null` | ❌ No | `210.00` |
| `valor_unit_construccion` | `float \| null` | ❌ No | `85400.00` |
| `area_comercio_m2` | `float \| null` | ❌ No | `45.50` |
| `valor_unit_comercio` | `float \| null` | ❌ No | `95000.00` |

> 💡 **Campos calculados automáticamente por PostgreSQL (NO enviar):**
> `valor_terreno`, `valor_construccion`, `valor_comercio`, `valor_catastral_total` — Se calculan con `GENERATED ALWAYS AS (...) STORED`.
> `superficie_gis_m2`, `perimetro_gis_m`, `utm_norte`, `utm_este` — Calculados por Triggers PostGIS.
> `codigo_catastral`, `expediente_numero` — Generados por Triggers.

#### Geometría GIS (Polígono del terreno)

| Campo | Tipo | Requerido | Ejemplo |
|:--|:--|:--|:--|
| `geom` | `GeoJSON Polygon` | ✅ Sí | Ver abajo |

```json
{
  "type": "Polygon",
  "coordinates": [[
    [-72.2450, 7.7230],
    [-72.2455, 7.7230],
    [-72.2455, 7.7235],
    [-72.2450, 7.7230]
  ]]
}
```

#### Recibo / Fiscal

| Campo | Tipo | Requerido | Ejemplo |
|:--|:--|:--|:--|
| `fecha_emision` | `date \| null` | ❌ No | `"2026-09-18"` |
| `fecha_recibo` | `date \| null` | ❌ No | `"2026-09-18"` |
| `numero_recibo` | `string \| null` | ❌ No | `"HACIENDA-2658"` |

**Respuesta:** `201 Created` → `InmuebleOut` (incluye `id`, `codigo_catastral` generado, campos calculados).

---

### Hitos Prediales — `POST /api/v1/inmuebles/{inmueble_id}/hitos`

Registra un vértice GPS capturado por el teléfono del inspector. Se ejecuta en el **Paso 5**.

| Campo | Tipo | Requerido | Ejemplo |
|:--|:--|:--|:--|
| `indice_vertice` | `int` (≥ 0) | ✅ Sí | `1` |
| `lat` | `float` (-90 a 90) | ✅ Sí | `7.7230` |
| `lon` | `float` (-180 a 180) | ✅ Sí | `-72.2450` |
| `descripcion` | `string \| null` | ❌ No | `"Vértice Nor-Este"` |
| `foto_url` | `string \| null` | ❌ No | `"https://..."` |

**Respuesta:** `201 Created` → `HitoPredialOut` (incluye coordenadas UTM calculadas por PostGIS).

---

### Fotos del Inmueble — `POST /api/v1/inmuebles/{inmueble_id}/fotos`

Registra una foto de la fachada. Se ejecuta en el **Paso 5**.

| Campo | Tipo | Requerido | Ejemplo |
|:--|:--|:--|:--|
| `url` | `string` | ✅ Sí | `"https://storage.supabase.co/..."` |
| `descripcion` | `string \| null` | ❌ No | `"Fachada Frontal"` |

**Respuesta:** `201 Created` → `FotoInmuebleOut`.

---

### Endpoints de Consulta (Lectura)

Estos endpoints se usan para buscar propietarios existentes, listar inmuebles previos y obtener la configuración del sistema.

| Acción | Método | Endpoint | Uso en la App |
|:--|:--|:--|:--|
| Buscar propietarios | `GET` | `/api/v1/propietarios?q=pérez` | Autocompletar al escribir cédula |
| Obtener propietario | `GET` | `/api/v1/propietarios/{id}` | Ver detalle del dueño |
| Listar inmuebles | `GET` | `/api/v1/inmuebles?pagina=1` | Historial de registros |
| Obtener inmueble | `GET` | `/api/v1/inmuebles/{id}` | Ver ficha completa |
| Listar hitos | `GET` | `/api/v1/inmuebles/{id}/hitos` | Ver vértices GPS guardados |
| Listar fotos | `GET` | `/api/v1/inmuebles/{id}/fotos` | Ver fotos del expediente |
| Config catastral | `GET` | `/api/v1/configuracion/catastral` | Obtener valores m² vigentes |
| Perfil usuario | `GET` | `/api/v1/usuarios/me` | Mostrar nombre e info del inspector |
| Descargar PDF | `GET` | `/api/v1/inmuebles/{id}/cedula` | Descargar cédula catastral (binario PDF) |

---

### Tabla Resumen — Endpoints que Usa la App Móvil

| # | Paso | Método | Endpoint | Descripción |
|:--|:--|:--|:--|:--|
| 1 | Auth | — | `supabase.auth.signInWithPassword()` | Login |
| 2 | Auth | — | `supabase.auth.signUp()` | Crear cuenta |
| 3 | 1 | `POST` | `/api/v1/propietarios` | Crear propietario |
| 4 | 1 | `GET` | `/api/v1/propietarios?q=...` | Buscar propietario existente |
| 5 | 6 | `POST` | `/api/v1/inmuebles` | Crear inmueble (payload completo) |
| 6 | 5 | `POST` | `/api/v1/inmuebles/{id}/hitos` | Registrar vértice GPS |
| 7 | 5 | `POST` | `/api/v1/inmuebles/{id}/fotos` | Subir foto de fachada |
| 8 | — | `GET` | `/api/v1/usuarios/me` | Perfil del inspector |
| 9 | — | `GET` | `/api/v1/configuracion/catastral` | Valores m² oficiales |
| 10 | — | `GET` | `/api/v1/inmuebles/{id}/cedula` | Descargar PDF de cédula |

---

## 🔐 Seguridad — Flujo de Autenticación

```
[App Móvil]                      [Supabase Auth]               [Backend Render]
    │                                   │                              │
    │── signInWithPassword() ──────────▶│                              │
    │◀── access_token (JWT ES256) ──────│                              │
    │                                   │                              │
    │── GET /api/v1/inmuebles ─────────────────────────────────────────▶│
    │   Header: Authorization: Bearer <token>                          │
    │                                   │                              │
    │                                   │◀── Valida firma JWT (ES256) ─│
    │◀── 200 OK { resultados: [...] } ─────────────────────────────────│
```

1. La app se autentica **directamente** con Supabase (nunca envía la contraseña al backend).
2. Supabase devuelve un `access_token` (JWT firmado con ES256).
3. La app guarda ese token en `expo-secure-store`.
4. Todas las peticiones a la API de Render incluyen el header `Authorization: Bearer <token>`.
5. El backend valida la firma del JWT sin contactar a Supabase (stateless).

---

## ⚙️ Configuración de `app.json` (Permisos)

```json
{
  "expo": {
    "name": "SRCM Mobile",
    "slug": "srcm-mobile",
    "version": "1.0.0",
    "orientation": "portrait",
    "plugins": [
      [
        "expo-location",
        {
          "locationAlwaysAndWhenInUsePermission": "SRCM necesita acceso a tu ubicación GPS para registrar las coordenadas del terreno."
        }
      ],
      [
        "expo-image-picker",
        {
          "photosPermission": "SRCM necesita acceso a tu galería para adjuntar fotos de fachadas.",
          "cameraPermission": "SRCM necesita acceso a tu cámara para fotografiar inmuebles."
        }
      ]
    ],
    "android": {
      "permissions": [
        "ACCESS_FINE_LOCATION",
        "ACCESS_COARSE_LOCATION",
        "CAMERA"
      ]
    }
  }
}
```

---

*Documentación técnica completa para el desarrollo de SRCM Mobile v1.0 — Alcaldía del Municipio Torbes, Táchira, Venezuela.*