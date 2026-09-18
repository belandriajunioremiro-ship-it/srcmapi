import os
import time
import random
import sys
import requests
from colorama import init, Fore, Style
from dotenv import load_dotenv

init(autoreset=True)
load_dotenv()
load_dotenv('.env.test')

API_URL = "https://srcmapi.onrender.com/api/v1"
TOKEN = os.getenv("TEST_AUTH_TOKEN")

if not TOKEN:
    print(Fore.RED + "\n[!] ERROR CRITICO: No se encontro TEST_AUTH_TOKEN en el archivo .env\n")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def step_print(step, msg, delay=0.5):
    print(Fore.CYAN + f"[{step}/7] " + Fore.WHITE + msg.ljust(42), end="", flush=True)
    time.sleep(delay)

def success_print(msg):
    print(Fore.GREEN + Style.BRIGHT + f" ✔ DONE" + Fore.RESET + f" | {msg}")

def fail_print(error):
    print(Fore.RED + Style.BRIGHT + f" ✘ ERROR\n   Detalle: {error}")
    sys.exit(1)

print("\n" + Fore.BLUE + Style.BRIGHT + "═" * 75)
print(Fore.BLUE + Style.BRIGHT + " " * 12 + "S.R.C.M. - INYECTOR & AUDITOR DE TABLAS (E2E)")
print(Fore.BLUE + Style.BRIGHT + "═" * 75)
print(Fore.WHITE + Style.BRIGHT + f" [>] DESTINO:  " + Fore.GREEN + API_URL)
print(Fore.WHITE + Style.BRIGHT + f" [>] OBJETIVO: " + Fore.YELLOW + "Poblar ABSOLUTAMENTE TODOS los campos del PDF")
print(Fore.BLUE + Style.BRIGHT + "═" * 75 + "\n")

rand_num = random.randint(1000, 9999)
cedula = f"V-999{rand_num}"
propietario_data = {
    "cedula_rif": cedula,
    "nombre": "Inversor Supremo",
    "apellido": f"Prueba{rand_num}",
    "telefono": "0414-5558899",
    "email": f"inversor_{rand_num}@alcaldia.gov.ve",
    "direccion": "Urbanización El Trigal, Avenida Principal"
}

step_print(1, "Creando 'propietarios' en BD")
resp_prop = requests.post(f"{API_URL}/propietarios", headers=HEADERS, json=propietario_data)
if resp_prop.status_code == 201:
    prop_id = resp_prop.json()["id"]
    success_print(f"Cédula: {Fore.YELLOW}{cedula}{Fore.RESET}")
else:
    fail_print(resp_prop.text)

offset_lon = random.uniform(-0.05, 0.05)
offset_lat = random.uniform(-0.05, 0.05)
parcela_num = f"{random.randint(100, 999)}"
manzana_num = f"{random.randint(10, 99):03d}"

# AQUI ESTA LA MAGIA: LLENANDO TODOS LOS CAMPOS POSIBLES DE LA BD
inmueble_data = {
    "propietario_id": prop_id,
    "direccion": f"Quinta Residencial Muestra #{rand_num}, Sector Privado",
    "sector": "06",
    "manzana": manzana_num,
    "parcela": parcela_num,
    "tenencia": "propio",
    
    # Documento de Propiedad
    "documento_tipo": "Registro Inmobiliario de Torbes",
    "documento_numero": f"DOC-{rand_num}",
    "documento_tomo": "Tomo IV",
    "documento_folio": "Folios 45 al 50",
    "documento_protocolo": "Primer Protocolo",
    "documento_fecha": "2018-05-14",
    
    # Linderos según Documento
    "lindero_norte_doc": "Calle Principal de la Urbanización",
    "lindero_norte_mts": 15.50,
    "lindero_sur_doc": "Parcela Colindante N° 08",
    "lindero_sur_mts": 15.50,
    "lindero_este_doc": "Avenida Los Cedros",
    "lindero_este_mts": 22.58,
    "lindero_oeste_doc": "Terreno Municipal Área Verde",
    "lindero_oeste_mts": 22.58,
    
    # Linderos según Topografía (Levantamiento real)
    "lindero_norte_top": "Calle Principal (Muro Perimetral)",
    "lindero_norte_top_mts": 15.55,
    "lindero_sur_top": "Parcela Colindante N° 08 (Cerca)",
    "lindero_sur_top_mts": 15.52,
    "lindero_este_top": "Avenida Los Cedros",
    "lindero_este_top_mts": 22.60,
    "lindero_oeste_top": "Terreno Municipal Área Verde",
    "lindero_oeste_top_mts": 22.55,
    
    # Servicios Básicos
    "aguas_blancas": True,
    "aguas_servidas": True,
    "electricidad": True,
    "contador": True,
    
    # Vivienda y Uso
    "existe_vivienda": True,
    "tipo_vivienda": "Quinta de dos niveles",
    "descripcion_uso": "Residencial - Comercial",
    "numero_plantas": 2,
    "uso_segun_zonificacion": "R3 - Residencial Mixto",
    
    # Características Físicas
    "via_acceso": "asfalto",
    "estructura_techo": "placa",
    "estructura_paredes": "bloque",
    "piso": "ceramica",
    "dormitorios": 5,
    "banos": 4,
    "sala": True,
    "cocina": True,
    "ambiente_otro": "Estacionamiento, Patio trasero y Local",
    "caracteristica_general": "aislada",
    "observaciones": "Levantamiento topográfico realizado con Drone RTK. Totalmente solvente con la administración tributaria municipal.",
    
    # Datos Fiscales y Recibos
    "numero_recibo": f"HACIENDA-{rand_num}",
    "fecha_recibo": "2026-09-18",
    
    # Avalúos (Cantidades en M2)
    "area_terreno_m2": 350.00,
    "valor_unit_terreno": 24500.00,
    "area_construccion_m2": 210.00,
    "valor_unit_construccion": 85400.00,
    "area_comercio_m2": 45.50,
    "valor_unit_comercio": 95000.00,
    
    # Coordenadas
    "geom": {
        "type": "Polygon",
        "coordinates": [[
            [-72.2450 + offset_lon, 7.7230 + offset_lat],
            [-72.2455 + offset_lon, 7.7230 + offset_lat],
            [-72.2455 + offset_lon, 7.7235 + offset_lat],
            [-72.2450 + offset_lon, 7.7230 + offset_lat]
        ]]
    }
}

step_print(2, "Inyectando Inmueble con DATOS COMPLETOS.")
resp_inm = requests.post(f"{API_URL}/inmuebles", headers=HEADERS, json=inmueble_data)
if resp_inm.status_code == 201:
    inm_id = resp_inm.json()["id"]
    cod_catastral = resp_inm.json()["codigo_catastral"]
    success_print(f"Código: {Fore.YELLOW}{cod_catastral}{Fore.RESET}")
else:
    fail_print(resp_inm.text)

hito_data = {
    "indice_vertice": 1,
    "lat": 7.7230 + offset_lat,
    "lon": -72.2450 + offset_lon,
    "descripcion": "Vértice Nor-Este Muestra"
}
step_print(3, "Insertando 'hitos_prediales' (UTM)")
resp_hito = requests.post(f"{API_URL}/inmuebles/{inm_id}/hitos", headers=HEADERS, json=hito_data)
if resp_hito.status_code == 201:
    success_print("Vértice PostGIS enlazado.")
else:
    fail_print(resp_hito.text)

foto_data = {
    "url": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750",
    "descripcion": "Fachada Frontal de Muestra"
}
step_print(4, "Guardando 'fotos_inmueble'")
resp_foto = requests.post(f"{API_URL}/inmuebles/{inm_id}/fotos", headers=HEADERS, json=foto_data)
if resp_foto.status_code == 201:
    success_print("Media adjuntada al expediente.")
else:
    fail_print(resp_foto.text)

step_print(5, "Consultando 'configuracion_catastral'")
resp_cfg = requests.get(f"{API_URL}/configuracion/catastral", headers=HEADERS)
if resp_cfg.status_code == 200:
    val_terreno = resp_cfg.json().get("valor_m2_terreno", 0)
    alcaldesa = resp_cfg.json().get("nombre_maxima_autoridad", "")
    success_print(f"M2: {Fore.YELLOW}{val_terreno} Bs{Fore.RESET} | Autoridad: {Fore.YELLOW}{alcaldesa}{Fore.RESET}")
else:
    fail_print(resp_cfg.text)

step_print(6, "Extrayendo 'v_pdf_cedula_catastral'")
resp_cedula_datos = requests.get(f"{API_URL}/inmuebles/{inm_id}/cedula-datos", headers=HEADERS)
if resp_cedula_datos.status_code == 200:
    total = resp_cedula_datos.json().get("valor_catastral_total", 0)
    success_print(f"Avalúo total: {Fore.YELLOW}{total:,.2f} Bs{Fore.RESET}")
else:
    fail_print(resp_cedula_datos.text)

step_print(7, "Generando PDF ULTRA COMPLETO final...")
resp_pdf = requests.get(f"{API_URL}/inmuebles/{inm_id}/cedula", headers=HEADERS)
if resp_pdf.status_code == 200:
    pdf_filename = f"Cedula_Completa_{cod_catastral}.pdf"
    with open(pdf_filename, "wb") as f:
        f.write(resp_pdf.content)
    success_print(f"Guardado como: {Fore.YELLOW}{pdf_filename}{Fore.RESET}")
else:
    fail_print(f"Error generando PDF: {resp_pdf.text}")

print("\n" + Fore.GREEN + Style.BRIGHT + "═" * 75)
print(Fore.GREEN + Style.BRIGHT + " [+] AUDITORIA Y FLUJO DE DATOS COMPLETADOS CON EXITO.")
print(Fore.GREEN + Style.BRIGHT + "═" * 75)
print(Fore.WHITE + " -> Tablas afectadas: " + Fore.CYAN + "propietarios, inmuebles, hitos_prediales, fotos_inmueble")
print(Fore.WHITE + " -> Tablas leídas:    " + Fore.CYAN + "configuracion_catastral, configuracion_sistema")
print(Fore.WHITE + " -> Vistas armadas:   " + Fore.CYAN + "v_pdf_cedula_catastral")
print(Fore.WHITE + "\n " + Fore.YELLOW + "REVISA TU CARPETA" + Fore.WHITE + ": Acabamos de descargar un PDF con el 100% de las tablas llenas.")
print(Fore.WHITE + "\n Todo el sistema Relacional + Geoespacial esta enlazado y perfecto.\n")
