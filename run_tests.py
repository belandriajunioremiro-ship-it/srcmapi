#!/usr/bin/env python3
"""
Ejecutor de Pruebas E2E - SRCM
Script elegante para ejecutar pruebas desde CMD
"""
import subprocess
import sys
import time
from datetime import datetime

def print_header(text):
    """Imprime un encabezado elegante"""
    print("\n" + "=" * 60)
    print(text.center(60))
    print("=" * 60 + "\n")

def print_success(text):
    """Imprime texto en verde"""
    print(f"[OK] {text}")

def print_error(text):
    """Imprime texto en rojo"""
    print(f"[ERROR] {text}")

def print_info(text):
    """Imprime texto en azul"""
    print(f"[INFO] {text}")

def print_warning(text):
    """Imprime texto en amarillo"""
    print(f"[WARN] {text}")

def run_command(command, description):
    """Ejecuta un comando y retorna el resultado"""
    print(f"\n-> {description}")
    print(f"Comando: {' '.join(command)}")
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print_success("Completado exitosamente")
            return True, result.stdout
        else:
            print_error(f"Fallo con codigo {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False, result.stdout
    except subprocess.TimeoutExpired:
        print_error("Tiempo de espera agotado")
        return False, ""
    except Exception as e:
        print_error(f"Error inesperado: {str(e)}")
        return False, ""

def main():
    """Funcion principal"""
    print_header("EJECUTOR DE PRUEBAS E2E - SRCM")
    
    print("Sistema de Registro Catastral Municipal")
    print("Municipio Torbes, Estado Tachira, Venezuela")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar que pytest esta instalado
    print_info("Verificando dependencias...")
    try:
        import pytest
        print_success("pytest esta instalado")
    except ImportError:
        print_error("pytest no esta instalado. Ejecuta: pip install -r requirements-test.txt")
        sys.exit(1)
    
    # Menu de opciones
    print_header("SELECCIONA EL TIPO DE PRUEBAS")
    
    options = [
        "1. Pruebas de Salud (Health Check)",
        "2. Pruebas Sin Autenticacion",
        "3. Pruebas con Bypass de Auth",
        "4. Pruebas de Configuracion",
        "5. Pruebas de Propietarios",
        "6. Pruebas de Inmuebles",
        "7. Pruebas de Catastro",
        "8. Pruebas de Usuarios",
        "9. TODAS las pruebas",
        "0. Salir"
    ]
    
    for option in options:
        print(f"  {option}")
    
    # Verificar si se paso argumento
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        try:
            choice = input("\nSelecciona una opcion (0-9): ")
        except EOFError:
            # Ejecucion automatica: usar opcion 1 por defecto
            print_info("Ejecucion automatica: Pruebas de Salud")
            choice = "1"
    
    # Mapeo de opciones a comandos
    test_commands = {
        "1": (["pytest", "tests/test_salud.py", "-v", "--disable-warnings"], "Pruebas de Salud"),
        "2": (["pytest", "tests/test_sin_auth.py", "-v", "--disable-warnings"], "Pruebas Sin Autenticacion"),
        "3": (["pytest", "tests/test_bypass_auth.py", "-v", "--disable-warnings"], "Pruebas con Bypass"),
        "4": (["pytest", "tests/test_configuracion.py", "-v", "--disable-warnings"], "Pruebas de Configuracion"),
        "5": (["pytest", "tests/test_propietarios.py", "-v", "--disable-warnings"], "Pruebas de Propietarios"),
        "6": (["pytest", "tests/test_inmuebles.py", "-v", "--disable-warnings"], "Pruebas de Inmuebles"),
        "7": (["pytest", "tests/test_catastro.py", "-v", "--disable-warnings"], "Pruebas de Catastro"),
        "8": (["pytest", "tests/test_usuarios.py", "-v", "--disable-warnings"], "Pruebas de Usuarios"),
        "9": (["pytest", "tests/", "-v", "--disable-warnings"], "TODAS las pruebas")
    }
    
    if choice == "0":
        print_info("Saliendo...")
        sys.exit(0)
    
    if choice not in test_commands:
        print_error("Opcion no valida")
        print_info("Uso: python run_tests.py [1-9]")
        sys.exit(1)
    
    command, description = test_commands[choice]
    
    print_header(f"EJECUTANDO: {description}")
    
    # Ejecutar las pruebas
    success, output = run_command(command, description)
    
    # Imprimir salida formateada
    if output:
        print_header("SALIDA DE PRUEBAS")
        
        # Colorear la salida
        lines = output.split('\n')
        for line in lines:
            if 'PASSED' in line:
                print(f"[PASS] {line}")
            elif 'FAILED' in line:
                print(f"[FAIL] {line}")
            elif 'ERROR' in line:
                print(f"[ERROR] {line}")
            elif 'SKIPPED' in line:
                print(f"[SKIP] {line}")
            elif '===' in line or '---' in line:
                print(line)
            elif '%' in line and 'passed' in line:
                print(f"*** {line} ***")
            else:
                print(line)
    
    # Resumen final
    print_header("RESULTADO FINAL")
    
    if success:
        print_success("Pruebas completadas exitosamente!")
    else:
        print_warning("Algunas pruebas fallaron. Revisa la salida arriba.")
    
    print(f"\nPara mas detalles, ejecuta directamente:")
    print(f"{' '.join(command)}")
    
    print(f"\nPara ver la documentacion:")
    print(f"ver REPORTE_COMPLETO_PRUEBAS_E2E.md")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nEjecucion interrumpida por el usuario")
        sys.exit(0)
