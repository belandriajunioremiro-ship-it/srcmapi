# 📱 SRCM Mobile - App de Campo Catastral

**Sistema de Registro Catastral Municipal - Módulo Móvil de Campo**  
**Municipio Torbes, Estado Táchira, Venezuela**  
**Versión: 1.0.0**  
**Fecha: 15 de septiembre de 2026**

---

## 🎯 **INTRODUCCIÓN**

SRCM Mobile es la aplicación móvil **EXCLUSIVAMENTE DE CAMPO** para el Sistema de Registro Catastral Municipal del Municipio Torbes. Esta aplicación está diseñada para que los inspectores catastrales realicen trabajo de campo capturando linderos, vértices geodésicos y coordenadas GPS directamente desde dispositivos móviles en el terreno.

**IMPORTANTE:** Esta app NO tiene funcionalidades administrativas. Solo sirve para registrar inmuebles en campo.

### **Funcionalidades Únicas de Campo:**

- 🗺️ Marcar linderos en mapa interactivo
- 📍 Capturar coordenadas GPS de vértices
- 📋 Formulario simplificado de datos catastrales mínimos
- 📡 Sincronización offline (trabajar sin internet)
- 📸 Foto opcional del predio

---

## 🚀 **STACK TECNOLÓGICO SIMPLIFICADO**

### **Stack Principal**
- **Expo SDK 52+** - Framework de desarrollo React Native
- **TypeScript** - Type safety
- **React Native 0.76.7** - Versión estable

### **Mapas y GPS (CORAZÓN DE LA APP)**
- **@react-native-maps v1.11.0** - Mapas nativos con Google Maps
- **@react-native-community/geolocation v3.1.0** - GPS precisa del dispositivo

### **UI y Navegación**
- **NativeBase v4** - Componentes UI nativos simples
- **React Navigation v7+** - Navegación básica

### **Estado y Datos**
- **Zustand v4.5** - Estado global ligero
- **TanStack Query v5** - Caché HTTP y sincronización
- **expo-sqlite v14.0.0** - Base de datos local offline
- **@react-native-community/netinfo v11.0.0** - Detección de internet

### **Cámara (Opcional)**
- **expo-camera v15.0.0** - Captura de foto del predio

### **HTTP y Auth**
- **axios v1.7.9** - Cliente HTTP
- **@react-native-async-storage/async-storage** - Almacenamiento de token

---

## 📁 **ESTRUCTURA DE ARCHIVOS SIMPLIFICADA**

```
srcm-mobile/
├── app.json                      # Configuración Expo y permisos
├── package.json                  # Dependencias simplificadas
├── tsconfig.json                 # Configuración TypeScript
├── babel.config.js               # Configuración Babel
├── assets/                       # Imágenes, logos
│   ├── logo.png
│   └── icon.png
├── src/
│   ├── App.tsx                   # Punto de entrada
│   │
│   ├── api/                      # Conexión al backend FastAPI
│   │   ├── client.ts             # Cliente Axios con JWT
│   │   └── endpoints.ts          # Endpoints del backend
│   │
│   ├── store/                    # Estado global (Zustand)
│   │   ├── index.ts              # Store principal
│   │   └── inspeccionSlice.ts    # Estado de inspecciones
│   │
│   ├── navigation/               # Navegación React Navigation
│   │   ├── AppNavigator.tsx      # Navegador principal
│   │   └── types.ts              # Tipos de navegación
│   │
│   ├── screens/                  # SOLO 4 PANTALLAS
│   │   ├── LoginScreen.tsx               # Autenticación
│   │   ├── ListaInspeccionesScreen.tsx   # Lista de inspecciones pendientes
│   │   ├── InspeccionCampoScreen.tsx     # PANTALLA PRINCIPAL - Marcar linderos
│   │   └── SyncStatusScreen.tsx          # Estado de sincronización
│   │
│   ├── components/               # Componentes reutilizables
│   │   └── MapaLinderos.tsx              # COMPONENTE PRINCIPAL - Mapa de linderos
│   │
│   ├── hooks/                    # Custom hooks
│   │   ├── useAuth.tsx                    # Hook de autenticación
│   │   └── useLocation.tsx                # Hook de GPS
│   │
│   ├── services/                 # Servicios de negocio
│   │   ├── authService.ts                # Servicio de autenticación
│   │   ├── inmuebleService.ts             # Servicio de inmuebles
│   │   └── syncService.ts                 # Servicio de sincronización offline
│   │
│   ├── database/                 # Base de datos local (SQLite)
│   │   ├── init.ts                      # Inicialización
│   │   └── schema.ts                    # Esquema de BD local
│   │
│   └── utils/                    # Utilidades
│       ├── constants.ts                  # Constantes (URL backend, etc)
│       └── storage.ts                    # Almacenamiento local
```

---

## 🗺️ **COMPONENTE PRINCIPAL: MAPA DE LINDEROS**

Este es el componente más importante de la app. Permite marcar vértices del polígono del predio tocando en el mapa.

```typescript
// src/components/MapaLinderos.tsx
import React, { useState, useEffect, useRef } from 'react';
import { View, StyleSheet, Text, TouchableOpacity } from 'react-native';
import MapView, { Polygon, Marker, PROVIDER_GOOGLE } from 'react-native-maps';
import Geolocation from '@react-native-community/geolocation';

interface Vertice {
  id: string;
  latitude: number;
  longitude: number;
  indice: number;
}

interface MapaLinderosProps {
  onVerticesChange: (vertices: Vertice[]) => void;
  vertices: Vertice[];
}

export const MapaLinderos: React.FC<MapaLinderosProps> = ({ 
  onVerticesChange, 
  vertices 
}) => {
  const [currentLocation, setCurrentLocation] = useState<{ latitude: number; longitude: number } | null>(null);
  const [gpsAccuracy, setGpsAccuracy] = useState<number | null>(null);
  const mapRef = useRef<MapView>(null);

  useEffect(() => {
    // Obtener ubicación actual con alta precisión
    Geolocation.getCurrentPosition(
      (position) => {
        setCurrentLocation({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        });
        setGpsAccuracy(position.coords.accuracy);
      },
      (error) => console.error('Error GPS:', error),
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 10000 }
    );
  }, []);

  const handleMapPress = (event: any) => {
    const { coordinate } = event.nativeEvent;
    const nuevoVertice: Vertice = {
      id: Date.now().toString(),
      latitude: coordinate.latitude,
      longitude: coordinate.longitude,
      indice: vertices.length + 1,
    };
    onVerticesChange([...vertices, nuevoVertice]);
  };

  const handleVerticeRemove = (verticeId: string) => {
    onVerticesChange(vertices.filter((v: Vertice) => v.id !== verticeId));
  };

  const handleCenterOnLocation = () => {
    if (currentLocation) {
      mapRef.current?.animateToRegion({
        latitude: currentLocation.latitude,
        longitude: currentLocation.longitude,
        latitudeDelta: 0.002,
        longitudeDelta: 0.002,
      });
    }
  };

  return (
    <View style={styles.container}>
      <MapView
        ref={mapRef}
        style={styles.map}
        provider={PROVIDER_GOOGLE}
        initialRegion={{
          latitude: 7.7654,
          longitude: -72.2345,
          latitudeDelta: 0.01,
          longitudeDelta: 0.01,
        }}
        onPress={handleMapPress}
      >
        {/* Marcador de ubicación actual */}
        {currentLocation && (
          <Marker
            coordinate={{
              latitude: currentLocation.latitude,
              longitude: currentLocation.longitude,
            }}
            title="Mi Ubicación"
            description={`Precisión GPS: ${gpsAccuracy?.toFixed(1)}m`}
            pinColor="blue"
          />
        )}

        {/* Vértices marcados */}
        {vertices.map((vertice: Vertice) => (
          <Marker
            key={vertice.id}
            coordinate={{
              latitude: vertice.latitude,
              longitude: vertice.longitude,
            }}
            title={`Vértice ${vertice.indice}`}
            onPress={() => handleVerticeRemove(vertice.id)}
            pinColor="red"
          />
        ))}

        {/* Polígono del predio */}
        {vertices.length >= 3 && (
          <Polygon
            coordinates={vertices.map((v: Vertice) => ({
              latitude: v.latitude,
              longitude: v.longitude,
            }))}
            fillColor="rgba(0, 123, 255, 0.3)"
            strokeColor="blue"
            strokeWidth={2}
          />
        )}
      </MapView>

      {/* Controles flotantes */}
      <View style={styles.controls}>
        <TouchableOpacity style={styles.button} onPress={handleCenterOnLocation}>
          <Text style={styles.buttonText}>📍 Mi Ubicación</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.button} onPress={() => onVerticesChange([])}>
          <Text style={styles.buttonText}>🗑️ Limpiar</Text>
        </TouchableOpacity>
      </View>

      {/* Info de GPS */}
      {gpsAccuracy && (
        <View style={styles.gpsInfo}>
          <Text style={styles.gpsText}>
            Precisión GPS: {gpsAccuracy.toFixed(1)}m
            {gpsAccuracy < 5 ? ' ✅ Excelente' : gpsAccuracy < 10 ? ' ⚠️ Buena' : ' ❌ Baja'}
          </Text>
        </View>
      )}

      {/* Contador de vértices */}
      <View style={styles.counter}>
        <Text style={styles.counterText}>Vértices: {vertices.length}</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  map: {
    flex: 1,
  },
  controls: {
    position: 'absolute',
    bottom: 30,
    left: 20,
    right: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 12,
    borderRadius: 8,
    minWidth: 120,
  },
  buttonText: {
    color: 'white',
    fontWeight: 'bold',
    textAlign: 'center',
  },
  gpsInfo: {
    position: 'absolute',
    top: 20,
    left: 20,
    right: 20,
    backgroundColor: 'rgba(0,0,0,0.7)',
    padding: 10,
    borderRadius: 8,
  },
  gpsText: {
    color: 'white',
    fontSize: 12,
  },
  counter: {
    position: 'absolute',
    top: 70,
    right: 20,
    backgroundColor: 'rgba(0,0,0,0.7)',
    padding: 8,
    borderRadius: 8,
  },
  counterText: {
    color: 'white',
    fontWeight: 'bold',
  },
});
```

---

## 📱 **PANTALLA PRINCIPAL: INSPECCIÓN EN CAMPO**

Esta es la pantalla principal donde el inspector captura los datos del predio en el terreno.

```typescript
// src/screens/InspeccionCampoScreen.tsx
import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, Alert, TouchableOpacity } from 'react-native';
import { Text, Input, Button, Select, Heading } from 'native-base';
import { MapaLinderos } from '../components/MapaLinderos';
import { inmuebleService } from '../services/inmuebleService';
import { useAuth } from '../hooks/useAuth';

interface Vertice {
  id: string;
  latitude: number;
  longitude: number;
  indice: number;
}

export const InspeccionCampoScreen: React.FC = () => {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    sector: '',
    manzana: '',
    parcela: '',
    direccion: '',
    tenencia: 'propio',
    area_terreno_m2: '',
    existe_vivienda: false,
  });

  const [vertices, setVertices] = useState<Vertice[]>([]);
  const [isSaving, setIsSaving] = useState(false);

  const handleGuardar = async () => {
    // Validaciones
    if (vertices.length < 3) {
      Alert.alert('Error', 'Debes marcar al menos 3 vértices para el polígono');
      return;
    }

    if (!formData.sector || !formData.manzana || !formData.parcela) {
      Alert.alert('Error', 'Debes ingresar código sector, manzana y parcela');
      return;
    }

    if (!formData.direccion) {
      Alert.alert('Error', 'Debes ingresar la dirección del predio');
      return;
    }

    setIsSaving(true);

    try {
      // Construir GeoJSON del polígono
      const coordinates = vertices.map((v) => [v.longitude, v.latitude]);
      const geom = {
        type: 'Polygon',
        coordinates: [coordinates],
      };

      // Crear inmueble en backend
      const inmueble = await inmuebleService.create({
        sector: formData.sector,
        manzana: formData.manzana,
        parcela: formData.parcela,
        subparcela: '000',
        nivel: '000',
        unidad: '000',
        direccion: formData.direccion,
        tenencia: formData.tenencia,
        area_terreno_m2: formData.area_terreno_m2 ? parseFloat(formData.area_terreno_m2) : null,
        existe_vivienda: formData.existe_vivienda,
        geom,
        registrado_por: user.id,
      });

      Alert.alert(
        '✅ Éxito',
        `Inmueble guardado\nCódigo catastral: ${inmueble.codigo_catastral}`,
        [
          {
            text: 'OK',
            onPress: () => navigation.goBack(),
          },
        ]
      );
    } catch (error) {
      Alert.alert('❌ Error', 'No se pudo guardar el inmueble. Verifica tu conexión.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView style={styles.formScroll}>
        <Heading size="lg" style={styles.title}>
          🗺️ Inspección en Campo
        </Heading>

        {/* Formulario simplificado */}
        <View style={styles.formSection}>
          <Text style={styles.sectionTitle}>Código Catastral Básico</Text>

          <View style={styles.row}>
            <View style={styles.col}>
              <Text style={styles.label}>Sector (2 dígitos)</Text>
              <Input
                placeholder="01"
                value={formData.sector}
                onChangeText={(text) => setFormData({ ...formData, sector: text })}
                maxLength={2}
                keyboardType="numeric"
              />
            </View>

            <View style={styles.col}>
              <Text style={styles.label}>Manzana (3 dígitos)</Text>
              <Input
                placeholder="001"
                value={formData.manzana}
                onChangeText={(text) => setFormData({ ...formData, manzana: text })}
                maxLength={3}
                keyboardType="numeric"
              />
            </View>

            <View style={styles.col}>
              <Text style={styles.label}>Parcela (3 dígitos)</Text>
              <Input
                placeholder="001"
                value={formData.parcela}
                onChangeText={(text) => setFormData({ ...formData, parcela: text })}
                maxLength={3}
                keyboardType="numeric"
              />
            </View>
          </View>

          <Text style={styles.label}>Dirección del Predio *</Text>
          <Input
            placeholder="Ej: Vía al Llano, Sector San José, Casa #123"
            value={formData.direccion}
            onChangeText={(text) => setFormData({ ...formData, direccion: text })}
          />

          <Text style={styles.label}>Tipo de Tenencia</Text>
          <Select
            selectedValue={formData.tenencia}
            onValueChange={(value) => setFormData({ ...formData, tenencia: value })}
          >
            <Select.Item label="Propio" value="propio" />
            <Select.Item label="Ejido" value="ejido" />
            <Select.Item label="Arrendado" value="arrendado" />
          </Select>

          <Text style={styles.label}>Área Terreno (m²)</Text>
          <Input
            placeholder="Ej: 500"
            value={formData.area_terreno_m2}
            onChangeText={(text) => setFormData({ ...formData, area_terreno_m2: text })}
            keyboardType="numeric"
          />

          <TouchableOpacity
            style={styles.checkbox}
            onPress={() => setFormData({ ...formData, existe_vivienda: !formData.existe_vivienda })}
          >
            <Text style={styles.checkboxText}>
              {formData.existe_vivienda ? '✅' : '⬜'} Existe vivienda en el predio
            </Text>
          </TouchableOpacity>
        </View>

        {/* Mapa de linderos */}
        <View style={styles.mapSection}>
          <Text style={styles.sectionTitle}>
            Marcar Linderos del Predio ({vertices.length} vértices)
          </Text>
          <Text style={styles.subtitle}>
            Toca en el mapa para marcar cada vértice del polígono
          </Text>

          <View style={styles.mapContainer}>
            <MapaLinderos
              vertices={vertices}
              onVerticesChange={setVertices}
            />
          </View>

          {vertices.length >= 3 && (
            <View style={styles.successMessage}>
              <Text style={styles.successText}>
                ✅ Polígono válido con {vertices.length} vértices
              </Text>
            </View>
          )}
        </View>
      </ScrollView>

      {/* Botón flotante de guardar */}
      <View style={styles.saveButton}>
        <Button
          onPress={handleGuardar}
          isLoading={isSaving}
          isDisabled={vertices.length < 3}
          size="lg"
        >
          💾 Guardar Inspección
        </Button>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  formScroll: {
    flex: 1,
    padding: 16,
  },
  title: {
    marginBottom: 20,
    color: '#333',
  },
  formSection: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 12,
    color: '#333',
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  col: {
    flex: 1,
    marginHorizontal: 4,
  },
  label: {
    fontSize: 14,
    fontWeight: '500',
    marginBottom: 4,
    color: '#333',
  },
  checkbox: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
  },
  checkboxText: {
    fontSize: 14,
    color: '#333',
  },
  mapSection: {
    backgroundColor: 'white',
    padding: 16,
    borderRadius: 12,
    marginBottom: 80,
  },
  mapContainer: {
    height: 400,
    borderRadius: 12,
    overflow: 'hidden',
    marginBottom: 12,
  },
  successMessage: {
    backgroundColor: '#d4edda',
    padding: 12,
    borderRadius: 8,
  },
  successText: {
    color: '#155724',
    fontWeight: 'bold',
    textAlign: 'center',
  },
  saveButton: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    padding: 16,
    backgroundColor: 'white',
    borderTopWidth: 1,
    borderTopColor: '#ddd',
  },
});
```

---

## 🔌 **INTEGRACIÓN CON BACKEND FASTAPI**

### **Cliente API Simplificado**

```typescript
// src/api/client.ts
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_BASE_URL } from '../utils/constants';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token JWT
apiClient.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default apiClient;
```

### **Endpoints del Backend**

```typescript
// src/api/endpoints.ts
import apiClient from './client';

export const inmuebleService = {
  create: async (data: any) => {
    const response = await apiClient.post('/inmuebles', data);
    return response.data;
  },
};
```

---

## 🔄 **SINCRONIZACIÓN OFFLINE**

```typescript
// src/services/syncService.ts
import * as SQLite from 'expo-sqlite';
import { inmuebleService } from '../api/endpoints';

const db = SQLite.openDatabase('srcm_offline.db');

export const syncService = {
  saveInmuebleLocal: async (inmueble: any) => {
    await db.transactionAsync(async (tx) => {
      await tx.executeSqlAsync(
        'INSERT OR REPLACE INTO inmuebles_offline (id, data, sync_status) VALUES (?, ?, ?)',
        [inmueble.id, JSON.stringify(inmueble), 'pending']
      );
    });
  },

  syncPendingInmuebles: async () => {
    const pending = await db.getAllAsync('inmuebles_offline', 'WHERE sync_status = ?', ['pending']);
    
    for (const item of pending) {
      try {
        const data = JSON.parse(item.data);
        await inmuebleService.create(data);
        
        await db.executeSqlAsync(
          'UPDATE inmuebles_offline SET sync_status = ? WHERE id = ?',
          ['synced', item.id]
        );
      } catch (error) {
        await db.executeSqlAsync(
          'UPDATE inmuebles_offline SET sync_status = ? WHERE id = ?',
          ['error', item.id]
        );
      }
    }
  },
};
```

---

## 📦 **PACKAGE.JSON SIMPLIFICADO**

```json
{
  "name": "srcm-mobile",
  "version": "1.0.0",
  "main": "node_modules/expo/AppEntry.js",
  "scripts": {
    "start": "expo start",
    "android": "expo start --android",
    "ios": "expo start --ios",
    "build:android": "eas build -p android"
  },
  "dependencies": {
    "expo": "~52.0.0",
    "react": "18.3.1",
    "react-native": "0.76.7",
    "native-base": "^4.0.0",
    "@react-navigation/native": "^7.0.0",
    "@react-navigation/native-stack": "^7.0.0",
    "@tanstack/react-query": "^5.0.0",
    "zustand": "^4.5.0",
    "axios": "^1.7.9",
    "@react-native-maps/maps": "^1.11.0",
    "@react-native-community/geolocation": "^3.1.0",
    "expo-camera": "~15.0.0",
    "expo-sqlite": "~14.0.0",
    "@react-native-community/netinfo": "^11.0.0",
    "@react-native-async-storage/async-storage": "^1.23.0"
  },
  "devDependencies": {
    "@babel/core": "^7.25.0",
    "@types/react": "~18.3.0",
    "typescript": "^5.5.0"
  }
}
```

---

## 🔐 **PERMISOS NECESSARIOS**

```json
// app.json
{
  "expo": {
    "name": "SRCM Mobile",
    "slug": "srcm-mobile",
    "plugins": [
      [
        "expo-location",
        {
          "locationAlwaysAndWhenInUsePermission": "Allow app to access your location"
        }
      ],
      [
        "expo-camera",
        {
          "cameraPermission": "Allow app to access your camera"
        }
      ]
    ],
    "android": {
      "permissions": [
        "ACCESS_FINE_LOCATION",
        "ACCESS_COARSE_LOCATION",
        "CAMERA",
        "INTERNET"
      ]
    }
  }
}
```

---

## 🎯 **FLUJO DE TRABAJO EN CAMPO**

### **1. Login**
- Usuario ingresa email y contraseña
- Autenticación con Supabase Auth
- Guardar token JWT localmente

### **2. Lista de Inspecciones**
- Ver inspecciones pendientes de sincronizar
- Ver inspecciones ya sincronizadas
- Botón para crear nueva inspección

### **3. Inspección en Campo (PANTALLA PRINCIPAL)**
- Ingresar código catastral básico (sector, manzana, parcela)
- Ingresar dirección del predio
- Seleccionar tipo de tenencia
- Ingresar área terreno
- Abrir mapa de linderos
- Tocar en el mapa para marcar vértices (mínimo 3)
- Ver polígono formado en tiempo real
- Ver precisión GPS
- Guardar inspección

### **4. Sincronización**
- App detecta conexión a internet
- Sincroniza inspecciones pendientes automáticamente
- Confirma éxito de sincronización

---

## 🚀 **COMANDOS PARA CREAR PROYECTO**

```bash
# Crear proyecto Expo
npx create-expo-app srcm-mobile --template blank-typescript

# Navegar al proyecto
cd srcm-mobile

# Instalar dependencias
npm install

# Instalar librerías principales
npm install native-base @react-navigation/native @tanstack/react-query zustand axios
npm install @react-native-maps/maps @react-native-community/geolocation
npm install expo-camera expo-sqlite @react-native-community/netinfo
npm install @react-native-async-storage/async-storage

# Iniciar desarrollo
npm start
```

---

## 📝 **DATOS MÍNIMOS REQUERIDOS**

### **Solo estos datos se capturan en campo:**

1. **Código Catastral Básico**
   - Sector (2 dígitos)
   - Manzana (3 dígitos)
   - Parcela (3 dígitos)

2. **Datos del Predio**
   - Dirección completa
   - Tipo de tenencia (propio/ejido/arrendado)
   - Área terreno m²
   - ¿Existe vivienda? (si/no)

3. **Coordenadas GPS (Automático del mapa)**
   - Latitud y longitud de cada vértice
   - Mínimo 3 vértices para polígono válido

4. **Foto (Opcional)**
   - Una foto del predio

**Todo lo demás (valor catastral, linderos documento, datos institucionales, etc.) se completa en la parte web administrativa.**

---

## 🎉 **RESUMEN FINAL**

### **App de Campo SRCM Mobile:**

- ✅ **Solo 4 pantallas** (Login, Lista, Inspección, Sync)
- ✅ **1 componente principal** (MapaLinderos)
- ✅ **Datos mínimos** (solo lo necesario para campo)
- ✅ **Mapa interactivo** para marcar linderos
- ✅ **GPS del dispositivo** para coordenadas
- ✅ **Sincronización offline** para trabajar sin internet
- ✅ **Sin funcionalidades administrativas**

**Esta app es EXCLUSIVAMENTE para trabajo de campo.**

---

**Documento actualizado por Devin - Backend Expert**  
**Fecha: 15 de septiembre de 2026**  
**Versión: 2.0 (Simplificado - Solo Campo)**
