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

print("\n" + Fore.RED + Style.BRIGHT + "═" * 75)
print(Fore.RED + Style.BRIGHT + " " * 15 + "S.R.C.M. - AUDITOR DE SOLAPAMIENTOS (POSTGIS)")
print(Fore.RED + Style.BRIGHT + "═" * 75)
print(Fore.WHITE + Style.BRIGHT + f" [>] OBJETIVO: " + Fore.YELLOW + "Forzar una colisión geoespacial ilegal en la base de datos")
print(Fore.RED + Style.BRIGHT + "═" * 75 + "\n")

# Usar un punto aleatorio muy lejano para no chocar con las pruebas anteriores
lon_base = -72.3000 + random.uniform(-0.01, 0.01)
lat_base = 7.8000 + random.uniform(-0.01, 0.01)

# Polígono A (100x100 aprox)
coords_a = [[
    [lon_base, lat_base],
    [lon_base + 0.0010, lat_base],
    [lon_base + 0.0010, lat_base + 0.0010],
    [lon_base, lat_base + 0.0010],
    [lon_base, lat_base]
]]

# Polígono B (Desplazado apenas la mitad, solapará fuertemente con A)
coords_b = [[
    [lon_base + 0.0005, lat_base + 0.0005],
    [lon_base + 0.0015, lat_base + 0.0005],
    [lon_base + 0.0015, lat_base + 0.0015],
    [lon_base + 0.0005, lat_base + 0.0015],
    [lon_base + 0.0005, lat_base + 0.0005]
]]

# Crear Propietario Víctima
cedula = f"V-999{random.randint(1000, 9999)}"
resp_prop = requests.post(f"{API_URL}/propietarios", headers=HEADERS, json={
    "cedula_rif": cedula, "nombre": "Víctima", "apellido": "Solapamiento",
    "telefono": "000", "direccion": "X"
})
prop_id = resp_prop.json()["id"]

# Intentar Registrar Terreno A
print(Fore.CYAN + "[1/2] " + Fore.WHITE + "Registrando el Terreno A (Legal)...")
inmueble_a = {
    "propietario_id": prop_id,
    "direccion": "Terreno Original A",
    "sector": "06", "manzana": "001", "parcela": "001", "tenencia": "propio",
    "geom": {"type": "Polygon", "coordinates": coords_a}
}
resp_a = requests.post(f"{API_URL}/inmuebles", headers=HEADERS, json=inmueble_a)
if resp_a.status_code == 201:
    cod_a = resp_a.json()["codigo_catastral"]
    print(Fore.GREEN + f"      ✔ DONE | Terreno A registrado correctamente. Código: {cod_a}\n")
else:
    print(Fore.RED + f"      ✘ Error registrando A: {resp_a.text}\n")
    sys.exit(1)

# Intentar Registrar Terreno B (Ilegal)
time.sleep(1)
print(Fore.CYAN + "[2/2] " + Fore.WHITE + "Atención: Intentando registrar Terreno B encima del Terreno A...")
print(Fore.YELLOW + "      >> Enviando transacción maliciosa a la base de datos...")
time.sleep(1)

inmueble_b = {
    "propietario_id": prop_id,
    "direccion": "Terreno Ilegal B (Solapado)",
    "sector": "06", "manzana": "001", "parcela": "002", "tenencia": "propio",
    "geom": {"type": "Polygon", "coordinates": coords_b}
}
resp_b = requests.post(f"{API_URL}/inmuebles", headers=HEADERS, json=inmueble_b)

print("\n" + Fore.RED + Style.BRIGHT + "═" * 75)
if resp_b.status_code != 201:
    print(Fore.GREEN + Style.BRIGHT + " [+] EXCELENTE. EL MOTOR POSTGIS BLOQUEO EL REGISTRO CON ESTE MENSAJE:")
    print(Fore.WHITE + " " + resp_b.text)
else:
    print(Fore.RED + " [!] PELIGRO: El terreno se registró y no debería haberlo hecho.")
print(Fore.RED + Style.BRIGHT + "═" * 75 + "\n")

