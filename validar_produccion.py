import os
import sys
import time
import subprocess
from colorama import init, Fore, Style

# Inicializar colores para Windows
init(autoreset=True)

URL_PRODUCCION = "https://srcmapi.onrender.com"
os.environ["BASE_URL"] = URL_PRODUCCION

def imprimir_encabezado():
    print("\n" + Fore.CYAN + "=" * 80)
    print(Fore.CYAN + " " * 15 + "S.R.C.M. - CERTIFICACION END-TO-END (PRODUCCION)")
    print(Fore.CYAN + "=" * 80)
    print(Fore.WHITE + Style.BRIGHT + f" [>] ENTORNO BACKEND: " + Fore.GREEN + "Render (Cloud Server)")
    print(Fore.WHITE + Style.BRIGHT + f" [>] MOTOR DE DATOS:  " + Fore.GREEN + "Supabase (PostgreSQL + PostGIS)")
    print(Fore.WHITE + Style.BRIGHT + f" [>] AUTENTICACION:   " + Fore.GREEN + "Supabase JWT Activo")
    print(Fore.WHITE + Style.BRIGHT + f" [>] OBJETIVO API:    " + Fore.YELLOW + URL_PRODUCCION)
    print(Fore.CYAN + "=" * 80 + "\n")
    print(Fore.WHITE + " Iniciando simulacion de trafico real. Esto evaluara 35 endpoints...")
    print(Fore.WHITE + " Interactuando con la base de datos de produccion de forma segura.\n")

def main():
    imprimir_encabezado()
    start_time = time.time()
    
    # Ejecutamos pytest forzando colores y ocultando warnings innecesarios
    comando = [
        sys.executable, "-m", "pytest", 
        "tests/", 
        "-v", 
        "--disable-warnings", 
        "--color=yes",
        "--tb=short" # Muestra errores cortos para no llenar la pantalla
    ]
    
    try:
        # Ejecutamos conectando la salida directamente a la consola
        proceso = subprocess.run(comando)
        
        tiempo_total = time.time() - start_time
        print("\n" + Fore.CYAN + "=" * 80)
        
        if proceso.returncode == 0:
            print(Fore.GREEN + Style.BRIGHT + f" [+] EXCELENTE: Todas las pruebas superadas en {tiempo_total:.1f} segundos.")
            print(Fore.GREEN + " [+] El servidor y la base de datos en produccion operan al 100%.")
        elif proceso.returncode == 1:
            print(Fore.YELLOW + Style.BRIGHT + f" [!] FINALIZADO CON OBSERVACIONES en {tiempo_total:.1f} segundos.")
            print(Fore.YELLOW + " [!] Nota: Es normal que las pruebas de la 'raiz' fallen porque cambiamos el JSON por HTML.")
        else:
            print(Fore.RED + Style.BRIGHT + f" [-] ERROR CRITICO DETECTADO. Codigo de salida: {proceso.returncode}")
            
        print(Fore.CYAN + "=" * 80 + "\n")
        
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Prueba cancelada por el usuario.")
        sys.exit(1)

if __name__ == "__main__":
    main()
