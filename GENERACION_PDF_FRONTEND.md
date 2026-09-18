# Generación de Cédulas Catastrales desde Frontend

Documentación completa para desarrolladores frontend sobre cómo generar cédulas catastrales PDF utilizando la API del SRCM.

## 📋 Índice

- [Visión General](#visión-general)
- [Arquitectura de Generación de PDFs](#arquitectura-de-generación-de-pdfs)
- [Endpoints Disponibles](#endpoints-disponibles)
- [Autenticación](#autenticación)
- [Flujo de Trabajo Completo](#flujo-de-trabajo-completo)
- [Implementación en React](#implementación-en-react)
- [Implementación en Vue.js](#implementación-en-vuejs)
- [Implementación en Angular](#implementación-en-angular)
- [Ejemplos de Código](#ejemplos-de-código)
- [Estructura de Datos](#estructura-de-datos)
- [Personalización del PDF](#personalización-del-pdf)
- [Manejo de Errores](#manejo-de-errores)
- [Optimización y Performance](#optimización-y-performance)
- [Preguntas Frecuentes](#preguntas-frecuentes)

---

## 🎯 Visión General

El SRCM ofrece **dos opciones** para generar cédulas catastrales en PDF:

### Opción 1: Generación desde Backend (Recomendada para descarga directa)
- **Endpoint:** `GET /api/v1/inmuebles/{id}/cedula`
- **Ventaja:** Más seguro, el cliente no puede alterar los valores
- **Uso ideal:** Descarga directa del PDF sin personalización

### Opción 2: Generación desde Frontend (Recomendada para personalización)
- **Endpoint:** `GET /api/v1/inmuebles/{id}/cedula-datos`
- **Endpoint complementario:** `GET /api/v1/configuracion/catastral/pdf-config`
- **Ventaja:** Flexibilidad total en diseño y personalización
- **Uso ideal:** Aplicaciones con diseño personalizado, vista previa, múltiples formatos

---

## 🏗️ Arquitectura de Generación de PDFs

```
┌─────────────────┐
│   Frontend      │
│  (React/Vue)    │
└────────┬────────┘
         │
         │ 1. Solicitar datos
         ▼
┌─────────────────┐
│   API SRCM      │
│  /cedula-datos  │
└────────┬────────┘
         │
         │ 2. JSON con datos
         ▼
┌─────────────────┐
│  Frontend       │
│  @react-pdf     │
└────────┬────────┘
         │
         │ 3. Generar PDF
         ▼
┌─────────────────┐
│   PDF Final     │
│  Personalizado  │
└─────────────────┘
```

---

## 🔌 Endpoints Disponibles

### 1. Obtener Datos de Cédula Catastral

**Endpoint:** `GET /api/v1/inmuebles/{inmueble_id}/cedula-datos`

**Autenticación:** Requiere token JWT válido

**Parámetros:**
- `inmueble_id` (UUID): ID del inmueble en la URL

**Response (200 OK):**
```json
{
  "inmueble_id": "uuid-del-inmueble",
  "codigo_catastral": "20270106049135000000000",
  
  "e": "20",
  "m": "27", 
  "p": "01",
  "s": "06",
  "ma": "049",
  "pa": "135",
  "sp": "000",
  "n": "000",
  "u": "000",
  
  "expediente_numero": "EXP-2024-0001",
  "numero_recibo": "REC-2024-001",
  "fecha_recibo": "2024-01-10",
  "fecha_emision": "2024-01-15",
  "vigente_hasta": "2025-01-15",
  
  "cedula_rif": "V-15.234.567",
  "propietario_nombre": "Juan Pérez",
  
  "direccion": "Calle Principal, Sector San José",
  "documento_tipo": "Documento Público",
  "documento_numero": "1234",
  "documento_tomo": "1",
  "documento_folio": "456",
  "documento_protocolo": "789",
  "documento_fecha": "2020-05-20",
  "tenencia": "propio",
  
  "lindero_norte_doc": "Calle Principal",
  "lindero_norte_mts": 50.5,
  "lindero_sur_doc": "Quebrada Seca",
  "lindero_sur_mts": 45.0,
  "lindero_este_doc": "Terreno de Pérez",
  "lindero_este_mts": 60.0,
  "lindero_oeste_doc": "Calle Secundaria",
  "lindero_oeste_mts": 55.0,
  
  "lindero_norte_top": "Punto GPS N-1",
  "lindero_norte_top_mts": 51.0,
  "lindero_sur_top": "Punto GPS S-1",
  "lindero_sur_top_mts": 46.0,
  "lindero_este_top": "Punto GPS E-1",
  "lindero_este_top_mts": 61.0,
  "lindero_oeste_top": "Punto GPS W-1",
  "lindero_oeste_top_mts": 56.0,
  
  "aguas_blancas": true,
  "aguas_servidas": true,
  "electricidad": true,
  "contador": true,
  
  "existe_vivienda": true,
  "tipo_vivienda": "Casa",
  "descripcion_uso": "Vivienda familiar",
  "numero_plantas": 2,
  "uso_segun_zonificacion": "Residencial",
  
  "area_terreno_m2": 150.50,
  "valor_unit_terreno": 83.06,
  "valor_terreno": 12500.00,
  "area_construccion_m2": 120.00,
  "valor_unit_construccion": 95.00,
  "valor_construccion": 11400.00,
  "area_comercio_m2": 0.00,
  "valor_unit_comercio": 0.00,
  "valor_comercio": 0.00,
  "valor_catastral_total": 23900.00,
  
  "via_acceso": "Asfaltada",
  "estructura_techo": "Lámina",
  "estructura_paredes": "Bloque",
  "piso": "Cerámica",
  "dormitorios": 3,
  "banos": 2,
  "sala": 1,
  "cocina": 1,
  "ambiente_otro": 0,
  "caracteristica_general": "Buena conservación",
  "observaciones": "Sin observaciones",
  
  "utm_norte": 1125000.00,
  "utm_este": 525000.00,
  
  "nombre_estado": "Táchira",
  "nombre_municipio": "Torbes",
  "nombre_parroquia": "San Josécito",
  "rif_alcaldia": "G-20000123-4",
  "direccion_institucional": "Av. Principal, Edificio Alcaldía, San Josécito",
  
  "nombre_maxima_autoridad": "Ing. Carlos Rodríguez",
  "cargo_maxima_autoridad": "Alcalde del Municipio Torbes",
  "texto_acta_maxima_autoridad": "Acta N° 001-2024 del Consejo Municipal",
  "nombre_director_catastro": "Lic. Ana Martínez",
  "cargo_director_catastro": "Directora de Catastro",
  "texto_resolucion_director": "Resolución N° DC-2024-001",
  "notas_legales": "Este documento es válido para todos los efectos legales. La información contenida es responsabilidad de la Alcaldía del Municipio Torbes."
}
```

**Error (404 Not Found):**
```json
{
  "detail": "Inmueble no encontrado"
}
```

**Error (404 Not Found - Datos de cédula):**
```json
{
  "detail": "Datos de cédula no encontrados"
}
```

---

### 2. Obtener Configuración Institucional para PDF (Opcional)

**Endpoint:** `GET /api/v1/configuracion/catastral/pdf-config`

**⚠️ NOTA IMPORTANTE:** Este endpoint es **opcional** para generar PDFs desde el frontend. La vista `v_pdf_cedula_catastral` ya incluye todos los datos institucionales necesarios. Este endpoint es útil principalmente para:
- Cache de configuración (evitar cargarla con cada inmueble)
- Formularios de administración
- Obtener configuración sin datos de un inmueble específico

**Autenticación:** Requiere token JWT válido

**Response (200 OK):**
```json
{
  "nombre_estado": "Táchira",
  "nombre_municipio": "Torbes",
  "nombre_parroquia": "San Josécito",
  "rif_alcaldia": "G-20000123-4",
  "direccion_institucional": "Av. Principal, Edificio Alcaldía, San Josécito",
  "nombre_maxima_autoridad": "Ing. Carlos Rodríguez",
  "cargo_maxima_autoridad": "Alcalde del Municipio Torbes",
  "texto_acta_maxima_autoridad": "Acta N° 001-2024 del Consejo Municipal",
  "nombre_director_catastro": "Lic. Ana Martínez",
  "cargo_director_catastro": "Directora de Catastro",
  "texto_resolucion_director": "Resolución N° DC-2024-001",
  "notas_legales": "Este documento es válido para todos los efectos legales. La información contenida es responsabilidad de la Alcaldía del Municipio Torbes."
}
```

**Error (404 Not Found):**
```json
{
  "detail": "Configuración catastral no encontrada. Ejecuta el script SQL."
}
```

---

## 🔐 Autenticación

Todos los endpoints requieren autenticación JWT mediante el header `Authorization`:

```javascript
const token = localStorage.getItem('token'); // o tu método de almacenamiento

const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
};
```

---

## 🔄 Flujo de Trabajo Completo

### Paso 1: Obtener Token de Autenticación
```javascript
// Login con Supabase Auth
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'usuario@ejemplo.com',
  password: 'contraseña'
});

const token = data.session.access_token;
```

### Paso 2: Obtener Datos del Inmueble (Incluye configuración)
```javascript
const obtenerDatosCedula = async (inmuebleId) => {
  const response = await fetch(`https://api.srcm.ve/api/v1/inmuebles/${inmuebleId}/cedula-datos`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (!response.ok) {
    throw new Error('Error al obtener datos de la cédula');
  }
  
  const datos = await response.json();
  return datos;
};
```

### Paso 3: Generar PDF con los Datos (Opcional: Cache de configuración)

⚠️ **NOTA:** Los datos institucionales ya vienen incluidos en la respuesta del paso 2. Solo necesitas este paso si quieres cachear la configuración por separado.

```javascript
const obtenerConfiguracionPDF = async () => {
  const response = await fetch('https://api.srcm.ve/api/v1/configuracion/catastral/pdf-config', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const config = await response.json();
  return config;
};
```

### Paso 4: Generar PDF con los Datos
```javascript
import { PDFDownloadLink, Document, Page, Text, View } from '@react-pdf/renderer';

const CedulaCatastral = ({ datos, config }) => (
  <Document>
    <Page size="A4">
      <View>
        <Text>Cédula Catastral</Text>
        <Text>{config.nombre_estado}</Text>
        <Text>{config.nombre_municipio}</Text>
        <Text>Código: {datos.codigo_catastral}</Text>
        <Text>Propietario: {datos.propietario_nombre}</Text>
        {/* Más contenido */}
      </View>
    </Page>
  </Document>
);
```

---

## ⚛️ Implementación en React

### Instalación de Dependencias

```bash
npm install @react-pdf/renderer
# o
yarn add @react-pdf/renderer
```

### Componente Completo

```jsx
import React, { useState, useEffect } from 'react';
import { PDFDownloadLink, Document, Page, Text, View, StyleSheet, Image } from '@react-pdf/renderer';

const styles = StyleSheet.create({
  page: {
    padding: 30,
    fontFamily: 'Helvetica',
  },
  header: {
    marginBottom: 20,
    borderBottom: '2 solid #000',
    paddingBottom: 10,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 14,
    textAlign: 'center',
    marginBottom: 5,
  },
  section: {
    marginBottom: 15,
  },
  sectionTitle: {
    fontSize: 12,
    fontWeight: 'bold',
    marginBottom: 8,
    backgroundColor: '#f0f0f0',
    padding: 5,
  },
  row: {
    flexDirection: 'row',
    marginBottom: 5,
  },
  label: {
    fontSize: 10,
    fontWeight: 'bold',
    width: '40%',
  },
  value: {
    fontSize: 10,
    width: '60%',
  },
  footer: {
    position: 'absolute',
    bottom: 30,
    left: 30,
    right: 30,
    textAlign: 'center',
    fontSize: 8,
    borderTop: '1 solid #000',
    paddingTop: 10,
  },
});

const CedulaCatastralPDF = ({ datos }) => (
  <Document>
    <Page size="A4" style={styles.page}>
      {/* Header Institucional */}
      <View style={styles.header}>
        <Text style={styles.title}>CÉDULA CATASTRAL</Text>
        <Text style={styles.subtitle}>{datos.nombre_estado} - {datos.nombre_municipio}</Text>
        <Text style={styles.subtitle}>{datos.nombre_parroquia}</Text>
        <Text style={styles.subtitle}>RIF: {datos.rif_alcaldia}</Text>
      </View>

      {/* Datos del Inmueble */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>DATOS DEL INMUEBLE</Text>
        <View style={styles.row}>
          <Text style={styles.label}>Código Catastral:</Text>
          <Text style={styles.value}>{datos.codigo_catastral}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Expediente:</Text>
          <Text style={styles.value}>{datos.expediente_numero}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Dirección:</Text>
          <Text style={styles.value}>{datos.direccion}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Tenencia:</Text>
          <Text style={styles.value}>{datos.tenencia.toUpperCase()}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Superficie Terreno:</Text>
          <Text style={styles.value}>{datos.area_terreno_m2.toFixed(2)} m²</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Superficie Construcción:</Text>
          <Text style={styles.value}>{datos.area_construccion_m2.toFixed(2)} m²</Text>
        </View>
      </View>

      {/* Valores Catastrales */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>VALORES CATASTRALES</Text>
        <View style={styles.row}>
          <Text style={styles.label}>Valor Total:</Text>
          <Text style={styles.value}>Bs. {datos.valor_catastral_total.toFixed(2)}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Valor Terreno:</Text>
          <Text style={styles.value}>Bs. {datos.valor_terreno.toFixed(2)}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Valor Construcción:</Text>
          <Text style={styles.value}>Bs. {datos.valor_construccion.toFixed(2)}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Valor m² Terreno:</Text>
          <Text style={styles.value}>Bs. {datos.valor_unit_terreno.toFixed(2)}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Valor m² Construcción:</Text>
          <Text style={styles.value}>Bs. {datos.valor_unit_construccion.toFixed(2)}</Text>
        </View>
      </View>

      {/* Datos del Propietario */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>DATOS DEL PROPIETARIO</Text>
        <View style={styles.row}>
          <Text style={styles.label}>Nombre:</Text>
          <Text style={styles.value}>{datos.propietario_nombre}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Cédula/RIF:</Text>
          <Text style={styles.value}>{datos.cedula_rif}</Text>
        </View>
      </View>

      {/* Documento Legal */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>DOCUMENTO LEGAL</Text>
        <View style={styles.row}>
          <Text style={styles.label}>Tipo:</Text>
          <Text style={styles.value}>{datos.documento_tipo}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Número:</Text>
          <Text style={styles.value}>{datos.documento_numero}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Fecha:</Text>
          <Text style={styles.value}>{new Date(datos.documento_fecha).toLocaleDateString('es-VE')}</Text>
        </View>
      </View>

      {/* Linderos según Documento */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>LINDEROS (DOCUMENTO)</Text>
        <View style={styles.row}>
          <Text style={styles.label}>Norte:</Text>
          <Text style={styles.value}>{datos.lindero_norte_doc} ({datos.lindero_norte_mts} m)</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Sur:</Text>
          <Text style={styles.value}>{datos.lindero_sur_doc} ({datos.lindero_sur_mts} m)</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Este:</Text>
          <Text style={styles.value}>{datos.lindero_este_doc} ({datos.lindero_este_mts} m)</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Oeste:</Text>
          <Text style={styles.value}>{datos.lindero_oeste_doc} ({datos.lindero_oeste_mts} m)</Text>
        </View>
      </View>

      {/* Linderos según Topografía */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>LINDEROS (TOPOGRAFÍA)</Text>
        <View style={styles.row}>
          <Text style={styles.label}>Norte:</Text>
          <Text style={styles.value}>{datos.lindero_norte_top} ({datos.lindero_norte_top_mts} m)</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Sur:</Text>
          <Text style={styles.value}>{datos.lindero_sur_top} ({datos.lindero_sur_top_mts} m)</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Este:</Text>
          <Text style={styles.value}>{datos.lindero_este_top} ({datos.lindero_este_top_mts} m)</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Oeste:</Text>
          <Text style={styles.value}>{datos.lindero_oeste_top} ({datos.lindero_oeste_top_mts} m)</Text>
        </View>
      </View>

      {/* Servicios */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>SERVICIOS</Text>
        <View style={styles.row}>
          <Text style={styles.label}>Aguas Blancas:</Text>
          <Text style={styles.value}>{datos.aguas_blancas ? 'Sí' : 'No'}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Aguas Servidas:</Text>
          <Text style={styles.value}>{datos.aguas_servidas ? 'Sí' : 'No'}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Electricidad:</Text>
          <Text style={styles.value}>{datos.electricidad ? 'Sí' : 'No'}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Contador:</Text>
          <Text style={styles.value}>{datos.contador ? 'Sí' : 'No'}</Text>
        </View>
      </View>

      {/* Vivienda */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>VIVIENDA</Text>
        <View style={styles.row}>
          <Text style={styles.label}>Existe Vivienda:</Text>
          <Text style={styles.value}>{datos.existe_vivienda ? 'Sí' : 'No'}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Tipo:</Text>
          <Text style={styles.value}>{datos.tipo_vivienda}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Uso:</Text>
          <Text style={styles.value}>{datos.descripcion_uso}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Plantas:</Text>
          <Text style={styles.value}>{datos.numero_plantas}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Dormitorios:</Text>
          <Text style={styles.value}>{datos.dormitorios}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label">Baños:</Text>
          <Text style={styles.value">{datos.banos}</Text>
        </View>
      </View>

      {/* Características Físicas */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>CARACTERÍSTICAS FÍSICAS</Text>
        <View style={styles.row}>
          <Text style={styles.label}>Vía de Acceso:</Text>
          <Text style={styles.value">{datos.via_acceso}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Techo:</Text>
          <Text style={styles.value}>{datos.estructura_techo}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Paredes:</Text>
          <Text style={styles.value}>{datos.estructura_paredes}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Piso:</Text>
          <Text style={styles.value}>{datos.piso}</Text>
        </View>
      </View>

      {/* Vigencia */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>VIGENCIA</Text>
        <View style={styles.row}>
          <Text style={styles.label}>Fecha Emisión:</Text>
          <Text style={styles.value}>{new Date(datos.fecha_emision).toLocaleDateString('es-VE')}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Válido Hasta:</Text>
          <Text style={styles.value}>{new Date(datos.vigente_hasta).toLocaleDateString('es-VE')}</Text>
        </View>
      </View>

      {/* Coordenadas */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>COORDENADAS UTM</Text>
        <View style={styles.row}>
          <Text style={styles.label}>UTM Norte:</Text>
          <Text style={styles.value}>{datos.utm_norte.toFixed(2)}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>UTM Este:</Text>
          <Text style={styles.value}>{datos.utm_este.toFixed(2)}</Text>
        </View>
      </View>

      {/* Observaciones */}
      {datos.observaciones && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>OBSERVACIONES</Text>
          <Text style={styles.value}>{datos.observaciones}</Text>
        </View>
      )}

      {/* Footer */}
      <View style={styles.footer}>
        <Text>{datos.nombre_maxima_autoridad} - {datos.cargo_maxima_autoridad}</Text>
        <Text>{datos.texto_acta_maxima_autoridad}</Text>
        <Text>{datos.nombre_director_catastro} - {datos.cargo_director_catastro}</Text>
        <Text>{datos.texto_resolucion_director}</Text>
        <Text>{datos.notas_legales}</Text>
      </View>
    </Page>
  </Document>
);

const GeneradorCedula = ({ inmuebleId }) => {
  const [datos, setDatos] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const cargarDatos = async () => {
      try {
        setLoading(true);
        
        // Cargar datos del inmueble (ya incluye configuración institucional)
        const datosResponse = await fetch(`/api/v1/inmuebles/${inmuebleId}/cedula-datos`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        if (!datosResponse.ok) {
          throw new Error('Error al cargar datos del inmueble');
        }
        
        const datosData = await datosResponse.json();
        setDatos(datosData);
        
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    cargarDatos();
  }, [inmuebleId]);

  if (loading) return <div>Cargando datos de la cédula...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!datos) return <div>No hay datos disponibles</div>;

  return (
    <div>
      <h3>Generar Cédula Catastral</h3>
      <PDFDownloadLink
        document={<CedulaCatastralPDF datos={datos} />}
        fileName={`cedula_catastral_${datos.codigo_catastral}.pdf`}
      >
        {({ loading }) => (
          <button disabled={loading}>
            {loading ? 'Generando PDF...' : 'Descargar Cédula PDF'}
          </button>
        )}
      </PDFDownloadLink>
    </div>
  );
};

export default GeneradorCedula;
```

---

## 💻 Implementación en Vue.js

### Instalación de Dependencias

```bash
npm install @react-pdf/renderer
# o
yarn add @react-pdf/renderer
```

### Componente Vue.js

```vue
<template>
  <div>
    <h3>Generar Cédula Catastral</h3>
    
    <div v-if="loading">Cargando datos de la cédula...</div>
    <div v-else-if="error">Error: {{ error }}</div>
    <div v-else-if="!datos">No hay datos disponibles</div>
    
    <div v-else>
      <button @click="generarPDF" :disabled="generando">
        {{ generando ? 'Generando PDF...' : 'Descargar Cédula PDF' }}
      </button>
    </div>
  </div>
</template>

<script>
import { pdf } from '@react-pdf/renderer';
import CedulaCatastralPDF from './CedulaCatastralPDF';

export default {
  name: 'GeneradorCedula',
  props: {
    inmuebleId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      datos: null,
      loading: true,
      error: null,
      generando: false
    };
  },
  async mounted() {
    await this.cargarDatos();
  },
  methods: {
    async cargarDatos() {
      try {
        this.loading = true;
        
        // Cargar datos del inmueble (ya incluye configuración institucional)
        const datosResponse = await fetch(`/api/v1/inmuebles/${this.inmuebleId}/cedula-datos`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        if (!datosResponse.ok) {
          throw new Error('Error al cargar datos del inmueble');
        }
        
        this.datos = await datosResponse.json();
        
      } catch (err) {
        this.error = err.message;
      } finally {
        this.loading = false;
      }
    },
    
    async generarPDF() {
      try {
        this.generando = true;
        
        const doc = CedulaCatastralPDF({ datos: this.datos });
        const asPdf = pdf(doc);
        const blob = await asPdf.toBlob();
        
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `cedula_catastral_${this.datos.codigo_catastral}.pdf`;
        link.click();
        
        URL.revokeObjectURL(url);
        
      } catch (err) {
        console.error('Error generando PDF:', err);
        alert('Error al generar el PDF');
      } finally {
        this.generando = false;
      }
    }
  }
};
</script>
```

---

## 🅰️ Implementación en Angular

### Instalación de Dependencias

```bash
npm install @react-pdf/renderer
# o
yarn add @react-pdf/renderer
```

### Servicio Angular

```typescript
// cedula.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class CedulaService {
  private apiUrl = 'https://api.srcm.ve/api/v1';
  
  constructor(private http: HttpClient) {}
  
  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('token');
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }
  
  obtenerConfiguracionPDF(): Observable<any> {
    return this.http.get(
      `${this.apiUrl}/configuracion/catastral/pdf-config`,
      { headers: this.getHeaders() }
    );
  }
  
  obtenerDatosCedula(inmuebleId: string): Observable<any> {
    return this.http.get(
      `${this.apiUrl}/inmuebles/${inmuebleId}/cedula-datos`,
      { headers: this.getHeaders() }
    );
  }
}
```

### Componente Angular

```typescript
// generador-cedula.component.ts
import { Component, OnInit } from '@angular/core';
import { CedulaService } from './cedula.service';
import { pdf } from '@react-pdf/renderer';
import CedulaCatastralPDF from './CedulaCatastralPDF';

@Component({
  selector: 'app-generador-cedula',
  template: `
    <div>
      <h3>Generar Cédula Catastral</h3>
      
      <div *ngIf="loading">Cargando datos de la cédula...</div>
      <div *ngIf="error">Error: {{ error }}</div>
      <div *ngIf="!datos">No hay datos disponibles</div>
      
      <div *ngIf="datos">
        <button 
          (click)="generarPDF()" 
          [disabled]="generando">
          {{ generando ? 'Generando PDF...' : 'Descargar Cédula PDF' }}
        </button>
      </div>
    </div>
  `
})
export class GeneradorCedulaComponent implements OnInit {
  datos: any = null;
  loading = true;
  error: string | null = null;
  generando = false;
  
  constructor(
    private cedulaService: CedulaService,
    @Inject('inmuebleId') private inmuebleId: string
  ) {}
  
  async ngOnInit() {
    await this.cargarDatos();
  }
  
  async cargarDatos() {
    try {
      this.loading = true;
      
      // Cargar datos del inmueble (ya incluye configuración institucional)
      this.datos = await this.cedulaService.obtenerDatosCedula(this.inmuebleId).toPromise();
      
    } catch (err) {
      this.error = err.message;
    } finally {
      this.loading = false;
    }
  }
  
  async generarPDF() {
    try {
      this.generando = true;
      
      const doc = CedulaCatastralPDF({ datos: this.datos });
      const asPdf = pdf(doc);
      const blob = await asPdf.toBlob();
      
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `cedula_catastral_${this.datos.codigo_catastral}.pdf`;
      link.click();
      
      URL.revokeObjectURL(url);
      
    } catch (err) {
      console.error('Error generando PDF:', err);
      alert('Error al generar el PDF');
    } finally {
      this.generando = false;
    }
  }
}
```

---

## 📝 Ejemplos de Código

### Ejemplo Básico con Fetch

```javascript
async function generarCedula(inmuebleId) {
  const token = localStorage.getItem('token');
  
  try {
    // Obtener datos
    const response = await fetch(`/api/v1/inmuebles/${inmuebleId}/cedula-datos`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (!response.ok) {
      throw new Error('Error al obtener datos');
    }
    
    const datos = await response.json();
    console.log('Datos de la cédula:', datos);
    
    // Aquí usarías los datos para generar el PDF
    // con tu librería favorita (@react-pdf/renderer, jsPDF, etc.)
    
  } catch (error) {
    console.error('Error:', error);
  }
}
```

### Ejemplo con Axios

```javascript
import axios from 'axios';

async function generarCedula(inmuebleId) {
  const token = localStorage.getItem('token');
  
  try {
    const response = await axios.get(`/api/v1/inmuebles/${inmuebleId}/cedula-datos`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    const datos = response.data;
    console.log('Datos de la cédula:', datos);
    
    // Generar PDF con los datos
    
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}
```

---

## 📊 Estructura de Datos

### Campos Completos de la Respuesta (60+ campos)

La vista `v_pdf_cedula_catastral` contiene todos los datos necesarios para generar la cédula catastral completa.

#### Identificación y Código Catastral
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `inmueble_id` | UUID | ID único del inmueble |
| `codigo_catastral` | String | Código catastral sin formato (23 caracteres) |
| `e, m, p` | String | Bloques del código: Estado, Municipio, Parroquia |
| `s, ma, pa, sp, n, u` | String | Bloques del código: Sector, Manzana, Parcela, Subparcela, Nivel, Unidad |

#### Expediente y Fechas
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `expediente_numero` | String | Número de expediente |
| `numero_recibo` | String | Número de recibo de pago |
| `fecha_recibo` | Date | Fecha del recibo |
| `fecha_emision` | Date | Fecha de emisión de la cédula |
| `vigente_hasta` | Date | Fecha de vigencia de la cédula |

#### Datos del Propietario
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `cedula_rif` | String | Cédula de identidad o RIF del propietario |
| `propietario_nombre` | String | Nombre completo del propietario |

#### Datos del Inmueble y Documento Legal
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `direccion` | String | Dirección completa del inmueble |
| `documento_tipo` | String | Tipo de documento legal |
| `documento_numero` | String | Número de documento |
| `documento_tomo` | String | Tomo del documento |
| `documento_folio` | String | Folio del documento |
| `documento_protocolo` | String | Protocolo del documento |
| `documento_fecha` | Date | Fecha del documento |
| `tenencia` | String | Tipo de tenencia (propio, ejido, arrendado) |

#### Linderos según Documento
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `lindero_norte_doc` | String | Descripción lindero norte (documento) |
| `lindero_norte_mts` | Float | Metros lindero norte (documento) |
| `lindero_sur_doc` | String | Descripción lindero sur (documento) |
| `lindero_sur_mts` | Float | Metros lindero sur (documento) |
| `lindero_este_doc` | String | Descripción lindero este (documento) |
| `lindero_este_mts` | Float | Metros lindero este (documento) |
| `lindero_oeste_doc` | String | Descripción lindero oeste (documento) |
| `lindero_oeste_mts` | Float | Metros lindero oeste (documento) |

#### Linderos según Levantamiento Topográfico
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `lindero_norte_top` | String | Descripción lindero norte (topográfico) |
| `lindero_norte_top_mts` | Float | Metros lindero norte (topográfico) |
| `lindero_sur_top` | String | Descripción lindero sur (topográfico) |
| `lindero_sur_top_mts` | Float | Metros lindero sur (topográfico) |
| `lindero_este_top` | String | Descripción lindero este (topográfico) |
| `lindero_este_top_mts` | Float | Metros lindero este (topográfico) |
| `lindero_oeste_top` | String | Descripción lindero oeste (topográfico) |
| `lindero_oeste_top_mts` | Float | Metros lindero oeste (topográfico) |

#### Factibilidad de Servicios
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `aguas_blancas` | Boolean | Servicio de aguas blancas disponible |
| `aguas_servidas` | Boolean | Servicio de aguas servidas disponible |
| `electricidad` | Boolean | Servicio eléctrico disponible |
| `contador` | Boolean | Tiene contador instalado |

#### Vivienda y Uso
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `existe_vivienda` | Boolean | Existe vivienda en el predio |
| `tipo_vivienda` | String | Tipo de vivienda (casa, apartamento, etc.) |
| `descripcion_uso` | String | Descripción del uso del inmueble |
| `numero_plantas` | Integer | Número de plantas de la construcción |
| `uso_segun_zonificacion` | String | Uso según zonificación municipal |

#### Áreas y Valores Catastrales
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `area_terreno_m2` | Float | Área del terreno en m² |
| `valor_unit_terreno` | Float | Valor unitario por m² de terreno |
| `valor_terreno` | Float | Valor total del terreno |
| `area_construccion_m2` | Float | Área de construcción en m² |
| `valor_unit_construccion` | Float | Valor unitario por m² de construcción |
| `valor_construccion` | Float | Valor total de la construcción |
| `area_comercio_m2` | Float | Área comercial en m² |
| `valor_unit_comercio` | Float | Valor unitario por m² comercial |
| `valor_comercio` | Float | Valor total comercial |
| `valor_catastral_total` | Float | Valor catastral total |

#### Características Físicas
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `via_acceso` | String | Tipo de vía de acceso |
| `estructura_techo` | String | Material del techo |
| `estructura_paredes` | String | Material de las paredes |
| `piso` | String | Material del piso |
| `dormitorios` | Integer | Número de dormitorios |
| `banos` | Integer | Número de baños |
| `sala` | Integer | Número de salas |
| `cocina` | Integer | Número de cocinas |
| `ambiente_otro` | Integer | Otros ambientes |
| `caracteristica_general` | String | Características generales |
| `observaciones` | String | Observaciones adicionales |

#### Coordenadas
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `utm_norte` | Float | Coordenada UTM Norte (SRID: 2201) |
| `utm_este` | Float | Coordenada UTM Este (SRID: 2201) |

#### Datos Institucionales (Incluidos en la vista)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `nombre_estado` | String | Nombre del estado (Táchira) |
| `nombre_municipio` | String | Nombre del municipio (Torbes) |
| `nombre_parroquia` | String | Nombre de la parroquia |
| `rif_alcaldia` | String | RIF de la alcaldía |
| `direccion_institucional` | String | Dirección de la alcaldía |

#### Datos de Firmas (Incluidos en la vista)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `nombre_maxima_autoridad` | String | Nombre de la máxima autoridad |
| `cargo_maxima_autoridad` | String | Cargo de la máxima autoridad |
| `texto_acta_maxima_autoridad` | String | Texto del acta de autoridad |
| `nombre_director_catastro` | String | Nombre del director de catastro |
| `cargo_director_catastro` | String | Cargo del director de catastro |
| `texto_resolucion_director` | String | Texto de la resolución |
| `notas_legales` | String | Notas legales del documento |

---

## 🎨 Personalización del PDF

### Usar CSS Personalizado

```javascript
const styles = StyleSheet.create({
  page: {
    padding: 30,
    backgroundColor: '#ffffff',
  },
  header: {
    backgroundColor: '#003366',
    color: '#ffffff',
    padding: 20,
    marginBottom: 20,
  },
  logo: {
    width: 100,
    height: 100,
    marginBottom: 10,
  },
  // ... más estilos
});
```

### Agregar Imágenes

```javascript
import { Image } from '@react-pdf/renderer';

const Logo = () => (
  <Image 
    src="/logo-alcaldia.png" 
    style={{ width: 100, height: 100 }} 
  />
);
```

### Agregar Código QR

```javascript
import QRCode from 'qrcode';

const generarQR = async (codigoCatastral) => {
  const qrDataUrl = await QRCode.toDataURL(codigoCatastral);
  return qrDataUrl;
};

// En el componente
const [qrCode, setQrCode] = useState(null);

useEffect(() => {
  generarQR(datos.codigo_catastral).then(setQrCode);
}, [datos.codigo_catastral]);
```

---

## ⚠️ Manejo de Errores

### Errores Comunes

```javascript
try {
  const response = await fetch(`/api/v1/inmuebles/${inmuebleId}/cedula-datos`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (response.status === 401) {
    // Token expirado o inválido
    throw new Error('Sesión expirada. Por favor inicia sesión nuevamente.');
  }
  
  if (response.status === 404) {
    // Inmueble no encontrado
    throw new Error('Inmueble no encontrado en el sistema.');
  }
  
  if (response.status === 403) {
    // Sin permisos
    throw new Error('No tienes permisos para acceder a este inmueble.');
  }
  
  const datos = await response.json();
  
} catch (error) {
  console.error('Error:', error);
  // Mostrar mensaje al usuario
}
```

### Validación de Datos

```javascript
const validarDatosCedula = (datos) => {
  if (!datos.codigo_catastral) {
    throw new Error('Código catastral no disponible');
  }
  
  if (!datos.propietario_nombre) {
    throw new Error('Datos del propietario incompletos');
  }
  
  if (!datos.valor_catastral_total) {
    throw new Error('Valores catastrales no disponibles');
  }
  
  return true;
};
```

---

## ⚡ Optimización y Performance

### Cache de Configuración

```javascript
// Cache simple en memoria
let configCache = null;
let configCacheTime = null;

const obtenerConfiguracionConCache = async () => {
  const CACHE_DURATION = 24 * 60 * 60 * 1000; // 24 horas
  
  if (configCache && configCacheTime && (Date.now() - configCacheTime < CACHE_DURATION)) {
    return configCache;
  }
  
  const response = await fetch('/api/v1/configuracion/catastral/pdf-config', {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  });
  
  configCache = await response.json();
  configCacheTime = Date.now();
  
  return configCache;
};
```

### Lazy Loading de PDF

```javascript
const VistaPreviaCedula = ({ inmuebleId }) => {
  const [mostrarPDF, setMostrarPDF] = useState(false);
  
  return (
    <div>
      <button onClick={() => setMostrarPDF(true)}>
        Ver Vista Previa
      </button>
      
      {mostrarPDF && (
        <CedulaCatastralPDF inmuebleId={inmuebleId} />
      )}
    </div>
  );
};
```

---

## ❓ Preguntas Frecuentes

### ¿Puedo personalizar el diseño del PDF?
**Sí.** Al generar el PDF desde el frontend, tienes control total sobre el diseño usando CSS y componentes de @react-pdf/renderer.

### ¿Los datos son seguros?
**Sí.** Los datos provienen directamente del backend y no pueden ser alterados por el cliente. El frontend solo los presenta visualmente.

### ¿Necesito llamar al endpoint de configuración?
**No necesariamente.** La vista `v_pdf_cedula_catastral` ya incluye todos los datos institucionales necesarios. El endpoint de configuración es opcional y útil principalmente para cache o formularios de administración.

### ¿Cuántos campos devuelve la API?
**Más de 60 campos** organizados en categorías: identificación, expediente, propietario, documento legal, linderos (documento y topográfico), servicios, vivienda, áreas y valores, características físicas, coordenadas, y datos institucionales.

### ¿Puedo generar múltiples cédulas a la vez?
**Sí.** Puedes hacer múltiples llamadas a la API y generar un PDF combinado con todas las cédulas.

### ¿Qué pasa si cambio la configuración institucional?
**Los cambios se reflejan automáticamente** en la próxima generación de PDF, ya que la configuración se obtiene dinámicamente del backend en cada llamada.

### ¿Necesito instalar alguna librería especial?
**Solo @react-pdf/renderer** para React, o la librería equivalente para tu framework.

### ¿Puedo usar esto sin React?
**Sí.** Puedes usar otras librerías como jsPDF, pdfmake, o generar el PDF completamente en el backend.

### ¿Los datos de la vista incluyen coordenadas lat/long?
**No.** La vista devuelve coordenadas UTM (utm_norte, utm_este) en el sistema SRID:2201. Si necesitas lat/long, debes convertirlas en el frontend o usar el endpoint regular del inmueble.

---

## 📚 Recursos Adicionales

- [Documentación de @react-pdf/renderer](https://react-pdf.org/)
- [API Documentation SRCM](http://localhost:8000/docs)
- [Supabase Auth Documentation](https://supabase.com/docs/guides/auth)

---

## 🤝 Soporte

Para problemas o preguntas específicas sobre la implementación:
- Revisa la documentación de la API en `/docs`
- Verifica los logs del servidor para errores detallados
- Contacta al equipo de desarrollo del SRCM

---

**Versión:** 1.0  
**Fecha:** 16 de septiembre de 2026  
**Mantenido por:** Equipo de Desarrollo SRCM
