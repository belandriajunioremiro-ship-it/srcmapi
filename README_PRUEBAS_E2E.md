# 🚀 S.R.C.M. - Auditoría y Certificación E2E (Producción)

Este documento detalla los scripts y comandos oficiales para validar el correcto funcionamiento del backend del **Sistema de Registro Catastral Municipal (SRCM)**, desplegado en **Render** y conectado a la base de datos **Supabase (PostgreSQL + PostGIS)**.

Durante esta fase, se certificó con un **100% de éxito (74/74 pruebas pasadas)** la API en la nube, validando seguridad JWT, motor geográfico (PostGIS) y generación de Cédulas Catastrales en PDF institucionales.

---

## 🛠️ Requisito Previo (Comandos de Ejecución)
Dado que a veces el entorno virtual (.venv) en Windows bloquea los ejecutables, los siguientes comandos utilizan la **ruta absoluta global de Python 3.12**. Asegúrate de estar dentro de la carpeta srcm (cd Desktop\srcm) antes de ejecutarlos.

---

### 1. Validación Visual Completa de la API (CLI Profesional)
Ejecuta el script visualizador para auditar todos los endpoints con una interfaz en consola estilizada. Valida Auth, rutas, conexión a Supabase y devuelve un informe detallado de éxito.

**Comando (CMD / PowerShell):**
`cmd
"C:\Users\Reactjs\AppData\Local\Programs\Python\Python312\python.exe" validar_produccion.py
`

### 2. Inyector de Datos Muestra y Descarga de PDF
Este script inyecta un expediente falso **100% completo** en producción. Simula el trabajo de un inspector: crea el propietario, dibuja el polígono GIS, enlaza hitos, adjunta fotos, y rellena los linderos, servicios y características físicas. 
Al final de la inyección, el script consulta la base de datos y **descarga el PDF final de la Cédula Catastral** directamente a tu carpeta.

**Comando (CMD / PowerShell):**
`cmd
"C:\Users\Reactjs\AppData\Local\Programs\Python\Python312\python.exe" generar_datos_muestra.py
`

### 3. Prueba de Hacker: Solapamientos Geoespaciales (PostGIS)
Script de validación topológica. Intenta registrar un terreno de forma legal, y luego intenta forzar una inyección de un segundo terreno ilegal que choca físicamente con el primero. Comprueba que el Trigger prevenir_solape_predios aborte la transacción inmediatamente devolviendo el área exacta de choque.

**Comando (CMD / PowerShell):**
`cmd
"C:\Users\Reactjs\AppData\Local\Programs\Python\Python312\python.exe" prueba_solapamiento.py
`

### 4. Ejecución Maestra Clásica (Pytest E2E)
Si se desea correr la suite original completa sin las interfaces visuales, comprobando la integridad de los 76 casos de prueba técnicos (incluyendo bypass de auth, reportes unitarios y salud del servidor).

**Comandos (CMD):**
`cmd
set BASE_URL=https://srcmapi.onrender.com
.venv\Scripts\pytest.exe tests/ -v
`

**Comandos (PowerShell):**
`powershell
$env:BASE_URL="https://srcmapi.onrender.com"
.venv\Scripts\pytest.exe tests/ -v
`

---
*Documentación generada automáticamente para la Alcaldía del Municipio Torbes, Táchira - Venezuela. (v2.5)*