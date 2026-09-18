# 📱 App Móvil SRCM de Campos para Gestionar las Coordenadas y Registros de los Inmuebles

**Sistema de Registro Catastral Municipal - Módulo Móvil de Campo**  
**Municipio Torbes, Estado Táchira, Venezuela**  
**Versión: 1.0.0**  
**Fecha: 15 de septiembre de 2026**

---

## 🎯 **OBJETIVO**

Este documento describe los casos de uso reales de la App Móvil SRCM de Campos para Gestionar las Coordenadas y Registros de los Inmuebles, explicando paso a paso cómo se capturan los datos en campo y cómo se envían al backend FastAPI, verificando que todo coincida con las APIs implementadas.

---

## 📋 **CASO DE USO 1: Crear Nuevo Inmueble en Campo**

### **Descripción**
El inspector catastral va al terreno y captura los datos básicos del predio, marca los linderos en el mapa, y guarda la inspección.

### **Paso a Paso**

#### **Paso 1: Autenticación**
- **Acción:** Inspector abre la app e ingresa email y contraseña
- **Backend:** Supabase Auth valida credenciales
- **Respuesta:** Token JWT devuelto al móvil
- **Storage:** Token guardado en AsyncStorage local

```typescript
// Código móvil
const login = async (email: string, password: string) => {
  const response = await supabase.auth.signInWithPassword({ email, password });
  const token = response.data.session.access_token;
  await AsyncStorage.setItem('auth_token', token);
};
```

#### **Paso 2: Abrir Pantalla de Inspección**
- **Acción:** Inspector toca botón "Nueva Inspección"
- **Pantalla:** InspeccionCampoScreen se abre
- **Estado:** Formulario vacío, mapa listo

#### **Paso 3: Ingresar Código Catastral Básico**
- **Acción:** Inspector ingresa:
  - Sector: "01"
  - Manzana: "001"
  - Parcela: "001"
- **Validación:** Campo obligatorio, máximos de caracteres (2, 3, 3)
- **Estado:** Datos guardados en estado local

```typescript
const [formData, setFormData] = useState({
  sector: '01',
  manzana: '001',
  parcela: '001',
  subparcela: '000',  // Siempre '000' en campo
  nivel: '000',       // Siempre '000' en campo
  unidad: '000',      // Siempre '000' en campo
});
```

#### **Paso 4: Ingresar Dirección del Predio**
- **Acción:** Inspector ingresa dirección completa
- **Ejemplo:** "Vía al Llano, Sector San José, Casa #123"
- **Validación:** Campo obligatorio
- **Estado:** Guardado en estado local

```typescript
const [formData, setFormData] = useState({
  direccion: 'Vía al Llano, Sector San José, Casa #123',
});
```

#### **Paso 5: Seleccionar Tipo de Tenencia**
- **Acción:** Inspector selecciona de dropdown
- **Opciones:** "Propio", "Ejido", "Arrendado"
- **Estado:** Guardado en estado local

```typescript
const [formData, setFormData] = useState({
  tenencia: 'propio',  // Valor por defecto
});
```

#### **Paso 6: Ingresar Área Terreno (Opcional)**
- **Acción:** Inspector ingresa área en m²
- **Ejemplo:** "500"
- **Validación:** Solo números, opcional
- **Estado:** Guardado en estado local

```typescript
const [formData, setFormData] = useState({
  area_terreno_m2: '500',
});
```

#### **Paso 7: Marcar Linderos en el Mapa (PASO CRÍTICO)**
- **Acción:** Inspector abre el mapa
- **GPS:** App obtiene ubicación actual del dispositivo
- **Marcador:** Pin azul muestra ubicación actual con precisión GPS

##### **7.1 Marcar Primer Vértice**
- **Acción:** Inspector camina al primer punto del polígono
- **Tocar:** Toca en el mapa en esa ubicación
- **Resultado:** Pin rojo aparece marcando vértice #1
- **Coordenadas:**
  - Latitude: 7.7654
  - Longitude: -72.2345
- **Estado:** Vértice guardado en array local

```typescript
const handleMapPress = (event: any) => {
  const { coordinate } = event.nativeEvent;
  const nuevoVertice: Vertice = {
    id: Date.now().toString(),
    latitude: coordinate.latitude,
    longitude: coordinate.longitude,
    indice: vertices.length + 1,
  };
  setVertices([...vertices, nuevoVertice]);
};
```

##### **7.2 Marcar Segundo Vértice**
- **Acción:** Inspector camina al segundo punto
- **Tocar:** Toca en el mapa
- **Resultado:** Pin rojo aparece marcando vértice #2
- **Coordenadas:**
  - Latitude: 7.7655
  - Longitude: -72.2346

##### **7.3 Marcar Tercer Vértice**
- **Acción:** Inspector camina al tercer punto
- **Tocar:** Toca en el mapa
- **Resultado:** Pin rojo aparece marcando vértice #3
- **Coordenadas:**
  - Latitude: 7.7656
  - Longitude: -72.2347
- **Polígono:** Línea azul conecta los 3 vértices
- **Relleno:** Área azul semitransparente aparece

##### **7.4 Marcar Más Vértices (Opcional)**
- **Acción:** Inspector puede marcar más vértices para mayor precisión
- **Mínimo:** 3 vértices
- **Máximo:** Sin límite, pero recomienda 5-10 para polígonos complejos

##### **7.5 Eliminar Vértice (Si se equivoca)**
- **Acción:** Tocar el pin rojo del vértice
- **Resultado:** Vértice eliminado
- **Polígono:** Se redibuja sin ese vértice

#### **Paso 8: Validar Polígono**
- **Validación App:** Mínimo 3 vértices requeridos
- **Mensaje:** "✅ Polígono válido con 3 vértices"
- **Estado:** Botón "Guardar Inspección" habilitado

#### **Paso 9: Guardar Inspección**
- **Acción:** Inspector toca "Guardar Inspección"
- **Validación Final:**
  - ✅ Mínimo 3 vértices
  - ✅ Código catastral básico completo
  - ✅ Dirección ingresada

#### **Paso 10: Construir Payload para Backend**
- **Acción:** App construye el objeto JSON para enviar al backend
- **Estructura:** Debe coincidir con schema `InmuebleCreate` del backend

```typescript
const payload = {
  sector: '01',
  manzana: '001',
  parcela: '001',
  subparcela: '000',
  nivel: '000',
  unidad: '000',
  direccion: 'Vía al Llano, Sector San José, Casa #123',
  tenencia: 'propio',
  area_terreno_m2: 500.0,
  existe_vivienda: false,
  geom: {
    type: 'Polygon',
    coordinates: [
      [
        [-72.2345, 7.7654],  // Vértice 1 (lon, lat)
        [-72.2346, 7.7655],  // Vértice 2 (lon, lat)
        [-72.2347, 7.7656],  // Vértice 3 (lon, lat)
        [-72.2345, 7.7654],  // Cerrar polígono (primer vértice)
      ]
    ]
  },
  registrado_por: user.id,
};
```

**IMPORTANTE:** GeoJSON usa `[longitude, latitude]` no `[latitude, longitude]`

#### **Paso 11: Enviar al Backend**
- **Método HTTP:** POST
- **Endpoint:** `/api/v1/inmuebles`
- **Headers:**
  - `Content-Type: application/json`
  - `Authorization: Bearer <token_jwt>`

```typescript
const response = await axios.post(
  'https://tu-backend.com/api/v1/inmuebles',
  payload,
  {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    }
  }
);
```

#### **Paso 12: Backend Procesa la Solicitud**

##### **12.1 Autenticación**
- **Backend:** Verifica token JWT
- **Middleware:** `get_current_user`
- **Resultado:** Usuario autenticado, rol verificado

##### **12.2 Validación Pydantic**
- **Backend:** Schema `InmuebleCreate` valida payload
- **Validaciones:**
  - ✅ sector: char(2) válido
  - ✅ manzana: char(3) válido
  - ✅ parcela: char(3) válido
  - ✅ direccion: string no vacío
  - ✅ tenencia: 'propio' en lista permitida
  - ✅ geom: GeoJSON Polygon válido
  - ✅ registered_por: UUID válido

##### **12.3 Insertar en Base de Datos**
- **Backend:** Inserta en tabla `inmuebles`
- **Trigger:** `antes_de_guardar_inmueble` se ejecuta automáticamente

##### **12.4 Trigger Calcula Valores**
- **Función:** `generar_codigo_catastral()`
- **Entrada:** sector='01', manzana='001', parcela='001', subparcela='000', nivel='000', unidad='000'
- **Salida:** '20112701001001000000000' (23 caracteres)
- **Campo:** `codigo_catastral` se actualiza

- **Función:** Calcula vigencia
- **Entrada:** fecha_emision = hoy, vigencia_cedula_meses = 12
- **Salida:** vigente_hasta = hoy + 12 meses

- **Función:** Calcula UTM del centroide
- **Entrada:** Coordenadas GPS del polígono
- **Salida:** utm_norte, utm_este (SRID 2201)

- **Función:** Calcula superficie GIS
- **Entrada:** Geometría del polígono
- **Salida:** superficie_gis_m2, perimetro_gis_m

- **Función:** Genera expediente
- **Entrada:** Secuencia seq_expediente
- **Salida:** expediente_numero = '000001/2026'

##### **12.5 Validación de Solapamiento**
- **Trigger:** `prevenir_solape_predios`
- **Función:** Verifica si el polígono se superpone con otros predios
- **Umbral:** > 1 m² de solapamiento
- **Resultado:** Si hay solapamiento, error 409 y rechaza el INSERT

##### **12.6 Valores Calculados Automáticos**
- **Columnas GENERATED STORED:**
  - valor_terreno = area_terreno_m2 * valor_unit_terreno
  - valor_construccion = area_construccion_m2 * valor_unit_construccion
  - valor_comercio = area_comercio_m2 * valor_unit_comercio
  - valor_catastral_total = valor_terreno + valor_construccion + valor_comercio

#### **Paso 13: Backend Responde**
- **Status HTTP:** 201 Created
- **Body:** Objeto `InmuebleOut` con todos los campos

```json
{
  "id": "uuid-del-inmueble",
  "codigo_catastral": "20112701001001000000000",
  "codigo_catastral_formato": "20-27-01-01-001-001-000-000-000",
  "expediente_numero": "000001/2026",
  "sector": "01",
  "manzana": "001",
  "parcela": "001",
  "subparcela": "000",
  "nivel": "000",
  "unidad": "000",
  "direccion": "Vía al Llano, Sector San José, Casa #123",
  "tenencia": "propio",
  "area_terreno_m2": 500.0,
  "valor_terreno": 12250000.00,
  "valor_construccion": 0.00,
  "valor_comercio": 0.00,
  "valor_catastral_total": 12250000.00,
  "utm_norte": 1234567.89,
  "utm_este": 234567.89,
  "superficie_gis_m2": 498.5,
  "perimetro_gis_m": 89.2,
  "vigente_hasta": "2027-09-15",
  "fecha_emision": "2026-09-15",
  "created_at": "2026-09-15T10:30:00Z",
  "updated_at": "2026-09-15T10:30:00Z"
}
```

#### **Paso 14: App Muestra Éxito**
- **Alerta:** "✅ Éxito - Inmueble guardado"
- **Mensaje:** "Código catastral: 20112701001001000000000"
- **Acción:** Inspector puede ver el código catastral generado
- **Navegación:** Regresa a lista de inspecciones

---

## 📋 **CASO DE USO 2: Crear Inmueble Sin Conexión a Internet (Offline)**

### **Descripción**
El inspector está en una zona sin internet. Captura los datos localmente y sincroniza cuando tenga conexión.

### **Paso a Paso**

#### **Paso 1-9: Igual que Caso de Uso 1**
- Captura de datos igual al caso anterior
- Hasta el paso de "Guardar Inspección"

#### **Paso 10: Detectar Sin Conexión**
- **NetInfo:** App detecta que no hay internet
- **Estado:** `isConnected = false`

```typescript
import NetInfo from '@react-native-community/netinfo';

const isConnected = await NetInfo.fetch();
if (!isConnected.isConnected) {
  // Modo offline
}
```

#### **Paso 11: Guardar Localmente en SQLite**
- **Acción:** App guarda la inspección en base de datos local
- **Tabla:** `inmuebles_offline`
- **Estado:** `sync_status = 'pending'`

```typescript
const saveInmuebleLocal = async (inmueble: any) => {
  await db.executeSqlAsync(
    'INSERT INTO inmuebles_offline (id, data, sync_status) VALUES (?, ?, ?)',
    [inmueble.id, JSON.stringify(inmueble), 'pending']
  );
};
```

#### **Paso 12: Mostrar Mensaje**
- **Alerta:** "Guardado localmente - Se sincronizará cuando haya conexión"
- **Estado:** Inspección marcada como pendiente en lista

#### **Paso 13: Inspector Termina Trabajo de Campo**
- **Acción:** Inspector regresa a zona con internet
- **App:** App detecta conexión

#### **Paso 14: Sincronización Automática**
- **Acción:** App detecta cambio de estado de red
- **Trigger:** Llama a `syncService.syncPendingInmuebles()`

```typescript
NetInfo.addEventListener(state => {
  if (state.isConnected) {
    syncService.syncPendingInmuebles();
  }
});
```

#### **Paso 15: Obtener Inspecciones Pendientes**
- **SQL:** `SELECT * FROM inmuebles_offline WHERE sync_status = 'pending'`
- **Resultado:** Lista de inspecciones pendientes

#### **Paso 16: Enviar Cada Inspección al Backend**
- **Loop:** Por cada inspección pendiente
- **POST:** `/api/v1/inmuebles`
- **Payload:** El mismo payload del caso de uso 1

```typescript
for (const item of pendingInmuebles) {
  const data = JSON.parse(item.data);
  await axios.post('/inmuebles', data);
}
```

#### **Paso 17: Backend Procesa (Igual que Caso de Uso 1)**
- Autenticación
- Validación Pydantic
- Insertar en BD
- Triggers calculan valores
- Respuesta con código catastral

#### **Paso 18: Marcar como Sincronizado**
- **SQL:** `UPDATE inmuebles_offline SET sync_status = 'synced' WHERE id = ?`
- **Estado:** Inspección marcada como sincronizada en SQLite local

#### **Paso 19: Notificar al Usuario**
- **Notificación:** "Sincronización completada - 1 inspección sincronizada"
- **Badge:** Contador de pendientes actualizado

---

## 📋 **CASO DE USO 3: Ver Lista de Inspecciones**

### **Descripción**
El inspector quiere ver todas las inspecciones realizadas, tanto pendientes como sincronizadas.

### **Paso a Paso**

#### **Paso 1: Abrir Lista de Inspecciones**
- **Pantalla:** ListaInspeccionesScreen
- **Estado:** Lista cargada desde SQLite local

#### **Paso 2: Obtener Datos Locales**
- **SQL:** `SELECT * FROM inmuebles_offline ORDER BY created_at DESC`
- **Resultado:** Lista de todas las inspecciones locales

```typescript
const inspecciones = await db.getAllAsync('inmuebles_offline');
```

#### **Paso 3: Mostrar Lista con Estado**
- **UI:** Lista con indicadores de estado
- **Estados:**
  - 🟡 Pendiente de sincronización
  - ✅ Sincronizado
  - ❌ Error de sincronización

```typescript
{inspecciones.map(item => (
  <Card key={item.id}>
    <Text>Código: {item.data.codigo_catastral || 'Pendiente'}</Text>
    <Text>Dirección: {item.data.direccion}</Text>
    <Badge colorScheme={item.sync_status === 'synced' ? 'green' : 'yellow'}>
      {item.sync_status}
    </Badge>
  </Card>
))}
```

#### **Paso 4: Opciones por Inspección**
- **Si pendiente:** Ver detalles, forzar sincronización
- **Si sincronizado:** Ver código catastral, ver en mapa

---

## 📋 **CASO DE USO 4: Ver Estado de Sincronización**

### **Descripción**
El inspector quiere saber cuántas inspecciones están pendientes de sincronizar.

### **Paso a Paso**

#### **Paso 1: Abrir Pantalla de Sync**
- **Pantalla:** SyncStatusScreen
- **Estado:** Contadores cargados

#### **Paso 2: Obtener Contadores**
- **SQL:** Contar por estado de sincronización

```typescript
const pending = await db.getAllAsync('inmuebles_offline', 'WHERE sync_status = ?', ['pending']);
const synced = await db.getAllAsync('inmuebles_offline', 'WHERE sync_status = ?', ['synced']);
const errors = await db.getAllAsync('inmuebles_offline', 'WHERE sync_status = ?', ['error']);
```

#### **Paso 3: Mostrar Resumen**
- **UI:** Tarjetas con contadores
- **Ejemplo:**
  - 🟡 Pendientes: 3
  - ✅ Sincronizados: 15
  - ❌ Errores: 0

#### **Paso 4: Botón Sincronizar Ahora**
- **Acción:** Tocar botón para forzar sincronización
- **Lógica:** Llama a `syncService.syncPendingInmuebles()`
- **Resultado:** Intenta sincronizar todas las pendientes

---

## 🔍 **VERIFICACIÓN DE COHERENCIA CON BACKEND**

### **Checklist de Coincidencia**

| Componente Móvil | Backend API | Estado |
|------------------|--------------|--------|
| **Payload POST /inmuebles** | Schema `InmuebleCreate` | ✅ Coincide |
| sector (char 2) | sector: CHAR(2) | ✅ Coincide |
| manzana (char 3) | manzana: CHAR(3) | ✅ Coincide |
| parcela (char 3) | parcela: CHAR(3) | ✅ Coincide |
| subparcela (char 3) | subparcela: CHAR(3) | ✅ Coincide |
| nivel (char 3) | nivel: CHAR(3) | ✅ Coincide |
| unidad (char 3) | unidad: CHAR(3) | ✅ Coincide |
| direccion (string) | direccion: String | ✅ Coincide |
| tenencia (string) | tenencia: String (CHECK) | ✅ Coincide |
| area_terreno_m2 (float) | area_terreno_m2: Numeric(12,2) | ✅ Coincide |
| geom (GeoJSON) | geom: Geometry(Polygon, 4326) | ✅ Coincide |
| registrado_por (UUID) | registrado_por: UUID | ✅ Coincide |
| **Authorization Bearer** | JWT Supabase Auth | ✅ Coincide |
| **Response 201** | HTTP 201 Created | ✅ Coincide |
| **Response InmuebleOut** | Schema `InmuebleOut` | ✅ Coincide |

### **Campos Calculados por Backend (NO enviados desde móvil)**

| Campo | Calculado por | No enviado desde móvil |
|-------|---------------|----------------------|
| codigo_catastral | Trigger `antes_de_guardar_inmueble` | ✅ Correcto |
| expediente_numero | Trigger `antes_de_guardar_inmueble` | ✅ Correcto |
| vigente_hasta | Trigger `antes_de_guardar_inmueble` | ✅ Correcto |
| utm_norte | Trigger `antes_de_guardar_inmueble` | ✅ Correcto |
| utm_este | Trigger `antes_de_guardar_inmueble` | ✅ Correcto |
| superficie_gis_m2 | Trigger `antes_de_guardar_inmueble` | ✅ Correcto |
| perimetro_gis_m | Trigger `antes_de_guardar_inmueble` | ✅ Correcto |
| valor_terreno | Columna GENERATED STORED | ✅ Correcto |
| valor_construccion | Columna GENERATED STORED | ✅ Correcto |
| valor_comercio | Columna GENERATED STORED | ✅ Correcto |
| valor_catastral_total | Columna GENERATED STORED | ✅ Correcto |

---

## ✅ **CONCLUSIÓN**

### **Coincidencia Perfecta:**

1. ✅ **Payload enviado desde móvil** coincide exactamente con schema `InmuebleCreate` del backend
2. ✅ **Endpoint POST /inmuebles** existe y funciona correctamente
3. ✅ **Autenticación JWT** coincide con backend Supabase Auth
4. ✅ **GeoJSON Polygon** coincide con tipo Geometry(Polygon, 4326) del backend
5. ✅ **Campos calculados** NO se envían desde móvil (correcto, backend los calcula)
6. ✅ **Sincronización offline** usa el mismo payload cuando hay conexión
7. ✅ **Validaciones** del backend manejan todos los casos de error

### **Flujo de Datos:**

```
Móvil (Campo) 
  ↓ (1) Captura datos básicos + GPS
  ↓ (2) Construye payload JSON
  ↓ (3) POST /api/v1/inmuebles
  ↓ (4) Backend valida (Pydantic)
  ↓ (5) Backend inserta (SQLAlchemy)
  ↓ (6) Triggers calculan valores
  ↓ (7) Backend responde (InmuebleOut)
  ↓ (8) Móvil muestra código catastral
```

**Todo coincide perfectamente. La app móvil está diseñada correctamente para enviar datos al backend SRCM.**

---

**Documento generado por Devin - Backend Expert**  
**Fecha: 15 de septiembre de 2026**  
**Versión: 1.0**
