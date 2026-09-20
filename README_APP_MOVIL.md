# 📱 S.R.C.M. Mobile - App de Inspección en Campo (React Native + Expo)

Este documento define la arquitectura, estructura y flujo de la aplicación móvil oficial del **Sistema de Registro Catastral Municipal (SRCM)**. 
Es una herramienta **exclusiva de campo** diseñada para los inspectores y topógrafos de la Alcaldía.

## 🎯 Objetivo de la App
Permitir a los inspectores registrar inmuebles directamente desde el terreno, capturando coordenadas GPS, fotos de fachadas, características físicas y transcribiendo los datos de los documentos antiguos. 

---

## 🎨 Diseño UI/UX (Design System)
Minimalista, profesional y de alto contraste para visibilidad bajo el sol.
- **Color Principal (Primario):** Azul Institucional (#2563EB o similar a Tailwind lue-600).
- **Fondos (Background):** Blanco puro (#FFFFFF) y grises muy claros (#F3F4F6) para separar tarjetas.
- **Textos (Tipografía):** Negro (#111827) para títulos y gris oscuro (#4B5563) para subtítulos. Letra *Nunito* o sistema nativo.
- **Estilo:** *Boxless* (sin cajas marcadas), uso de sombras suaves, botones amplios (touch-friendly).

---

## 🛠️ Stack Tecnológico y Paquetes Clave (Expo Go)
Para garantizar la mejor experiencia, fluidez y acceso al hardware del teléfono:

1. **Framework:** React Native con Expo Go (Fácil desarrollo y despliegue rápido).
2. **Navegación:** @react-navigation/native y @react-navigation/native-stack.
3. **Autenticación:** @supabase/supabase-js (Login/Registro directo con Supabase. *Nota: Confirmación por email desactivada*).
4. **Peticiones HTTP:** xios (Para consumir la API de Render srcmapi.onrender.com).
5. **Hardware (GPS y Cámara):** 
   - expo-location (Para obtener Lat/Lon exacta del topógrafo).
   - expo-camera o expo-image-picker (Para fotos de la fachada).
6. **Formularios complejos:** eact-hook-form + yup o zod (Para validar los cientos de campos antes de enviar).
7. **Estilos:** 
ativewind (Tailwind CSS para React Native) o StyleSheet nativo.

---

## 📂 Estructura de Carpetas Propuesta

`	ext
srcm-mobile/
├── App.js                   # Punto de entrada y proveedor de Contextos
├── app.json                 # Configuración de Expo (Permisos GPS/Cámara)
├── src/
│   ├── api/                 # Configuración de Axios y endpoints del backend
│   ├── auth/                # Configuración del cliente Supabase
│   ├── components/          # Componentes UI reutilizables (Botones, Inputs, Modales)
│   ├── navigation/          # AppNavigator (AuthStack vs MainStack)
│   ├── screens/             # Pantallas completas de la app
│   │   ├── auth/            # LoginScreen.js, RegisterScreen.js
│   │   ├── home/            # DashboardScreen.js (Menú principal)
│   │   └── registro/        # Wizard de Registro (Paso 1, Paso 2, etc.)
│   ├── services/            # Lógica de negocio (Cámara, GPS, envío de datos)
│   └── utils/               # Helpers, validaciones y constantes de colores
`

---

## 📱 Flujo de Pantallas y Formularios (El "Wizard")

Dado que un registro tiene muchos datos, se debe dividir en un **Wizard (Formulario por pasos)** para no abrumar al inspector en la pantalla pequeña del teléfono.

### 1. Módulo de Autenticación (Auth)
- **Login:** Correo y contraseña.
- **Registro:** Crear cuenta (Solo para nuevos inspectores). *La cuenta se activa inmediatamente sin pedir verificación de email.*

### 2. Paso 1: Propietarios (Y Co-propietarios)
- Inputs: Cédula/RIF, Nombres, Apellidos, Teléfono, Correo.
- *Nota de Arquitectura:* La base de datos actual vincula 1 propietario principal. La app permitirá registrar al "Propietario Principal" y en un futuro soportará agregar un array de co-propietarios.

### 3. Paso 2: Datos del Documento (Transcripción manual)
- Se transcriben los datos del papel viejo: Número, Tomo, Folios, Fecha, Protocolo.
- **Linderos Según Documento:** Inputs de texto para transcribir literalmente lo que dice el papel (Norte, Sur, Este, Oeste y sus medidas en metros).

### 4. Paso 3: Características Físicas y Topografía (Trabajo de Campo)
- **Linderos Según Topografía:** Lo que el inspector está viendo (Ej: Norte: Muro Perimetral 15.55mts).
- **Servicios:** Switches (Toggle) para Aguas Blancas, Aguas Servidas, Electricidad.
- **Edificación:** Tipo de vivienda, Pisos, Estructura de techo (Placa/Zinc), Paredes, Habitaciones.

### 5. Paso 4: Hardware (Geometría y Fotos)
- **Captura GPS:** Botón grande [CAPTURAR COORDENADA ACTUAL]. Usa expo-location con alta precisión para obtener Lat/Lon.
- **Cámara:** Tomar foto de la fachada.

---

## 🌐 Endpoints del Backend a Consumir (API Render)

La App Móvil actuará únicamente como cliente. Toda la lógica pesada (PostGIS, generación de Códigos Catastrales y PDFs) ocurre en el backend.

| Acción | Método | Endpoint (FastAPI) | Payload Principal |
| :--- | :--- | :--- | :--- |
| **Autenticación** | POST | *Directo vía Supabase SDK* | email, password |
| **1. Crear Dueño** | POST | /api/v1/propietarios | cedula_rif, 
ombre, pellido, 	elefono |
| **2. Crear Ficha** | POST | /api/v1/inmuebles | propietario_id, linderos_doc, linderos_top, caracteristicas, servicios, geom (Polígono básico o centroide) |
| **3. Anexar GPS**| POST | /api/v1/inmuebles/{id}/hitos | lat, lon (Capturados del teléfono) |
| **4. Subir Foto** | POST | /api/v1/inmuebles/{id}/fotos | Imagen en Base64 o Multipart form-data |

> **Nota de Seguridad:** Todas las peticiones al backend (Axios) deben incluir el Header Authorization: Bearer <TOKEN_SUPABASE>.

---
*Documentación estratégica creada para el desarrollo del cliente móvil SRCM.*