#!/usr/bin/env python3
"""
Ejecutor de Pruebas E2E - SRCM
Script elegante para ejecutar y visualizar pruebas desde la línea de comandos
"""
import subprocess
import sys
import time
from datetime import datetime
from typing import List, Tuple

# Colores ANSI para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    """Imprime un encabezado elegante"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.END}")
    try:
        print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.END}")
    except:
        print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.END}\n")

def print_success(text: str):
    """Imprime texto en verde"""
    print(f"{Colors.GREEN}[OK] {text}{Colors.END}")

def print_error(text: str):
    """Imprime texto en rojo"""
    print(f"{Colors.RED}[ERROR] {text}{Colors.END}")

def print_info(text: str):
    """Imprime texto en azul"""
    print(f"{Colors.BLUE}[INFO] {text}{Colors.END}")

def print_warning(text: str):
    """Imprime texto en amarillo"""
    print(f"{Colors.YELLOW}[WARN] {text}{Colors.END}")

def print_progress_bar(current: int, total: int, width: int = 40):
    """Imprime una barra de progreso"""
    progress = current / total
    filled = int(width * progress)
    bar = '#' * filled + '-' * (width - filled)
    percent = int(progress * 100)
    print(f"\r[{Colors.GREEN}{bar}{Colors.END}] {percent}%", end='', flush=True)

def run_command(command: List[str], description: str) -> Tuple[bool, str]:
    """Ejecuta un comando y retorna el resultado"""
    print(f"\n{Colors.CYAN}→ {description}{Colors.END}")
    print(f"{Colors.BLUE}Comando: {' '.join(command)}{Colors.END}")
    
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
            print_error(f"Falló con código {result.returncode}")
            if result.stderr:
                print(f"{Colors.RED}Error: {result.stderr}{Colors.END}")
            return False, result.stdout
    except subprocess.TimeoutExpired:
        print_error("Tiempo de espera agotado")
        return False, ""
    except Exception as e:
        print_error(f"Error inesperado: {str(e)}")
        return False, ""

def print_summary(results: List[Tuple[str, bool, str]]):
    """Imprime un resumen elegante de los resultados"""
    print_header("RESUMEN DE EJECUCION")
    
    total = len(results)
    passed = sum(1 for _, success, _ in results if success)
    failed = total - passed
    
    print(f"{Colors.BOLD}Total de pruebas:{Colors.END} {total}")
    print(f"{Colors.GREEN}Exitosas:{Colors.END} {passed}")
    print(f"{Colors.RED}Fallidas:{Colors.END} {failed}")
    print(f"{Colors.CYAN}Porcentaje exito:{Colors.END} {int((passed/total)*100)}%")
    
    print(f"\n{Colors.BOLD}Detalle por prueba:{Colors.END}\n")
    
    for name, success, output in results:
        status = f"{Colors.GREEN}[PASS]{Colors.END}" if success else f"{Colors.RED}[FAIL]{Colors.END}"
        print(f"{status} {Colors.CYAN}{name}{Colors.END}")
        
        if not success and output:
            # Mostrar primeras líneas del error
            lines = output.split('\n')[:3]
            for line in lines:
                if line.strip():
                    print(f"  {Colors.RED}{line}{Colors.END}")
        print()

def main():
    """Función principal"""
    print_header("EJECUTOR DE PRUEBAS E2E - SRCM")
    
    print(f"{Colors.CYAN}Sistema de Registro Catastral Municipal{Colors.END}")
    print(f"{Colors.CYAN}Municipio Torbes, Estado Tachira, Venezuela{Colors.END}")
    print(f"{Colors.BLUE}Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    
    # Verificar que pytest está instalado
    print_info("Verificando dependencias...")
    try:
        import pytest
        print_success("pytest está instalado")
    except ImportError:
        print_error("pytest no está instalado. Ejecuta: pip install -r requirements-test.txt")
        sys.exit(1)
    
    # Menú de opciones
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
        print(f"  {Colors.CYAN}{option}{Colors.END}")
    
    choice = input(f"\n{Colors.YELLOW}Selecciona una opcion (0-9): {Colors.END}")
    
    # Mapeo de opciones a comandos
    test_commands = {
        "1": (["pytest", "tests/test_salud.py", "-v"], "Pruebas de Salud"),
        "2": (["pytest", "tests/test_sin_auth.py", "-v"], "Pruebas Sin Autenticación"),
        "3": (["pytest", "tests/test_bypass_auth.py", "-v"], "Pruebas con Bypass"),
        "4": (["pytest", "tests/test_configuracion.py", "-v"], "Pruebas de Configuración"),
        "5": (["pytest", "tests/test_propietarios.py", "-v"], "Pruebas de Propietarios"),
        "6": (["pytest", "tests/test_inmuebles.py", "-v"], "Pruebas de Inmuebles"),
        "7": (["pytest", "tests/test_catastro.py", "-v"], "Pruebas de Catastro"),
        "8": (["pytest", "tests/test_usuarios.py", "-v"], "Pruebas de Usuarios"),
        "9": (["pytest", "tests/", "-v"], "TODAS las pruebas")
    }
    
    if choice == "0":
        print_info("Saliendo...")
        sys.exit(0)
    
    if choice not in test_commands:
        print_error("Opción no válida")
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
                print(f"{Colors.GREEN}{line}{Colors.END}")
            elif 'FAILED' in line:
                print(f"{Colors.RED}{line}{Colors.END}")
            elif 'ERROR' in line:
                print(f"{Colors.RED}{line}{Colors.END}")
            elif 'SKIPPED' in line:
                print(f"{Colors.YELLOW}{line}{Colors.END}")
            elif '===' in line or '---' in line:
                print(f"{Colors.CYAN}{line}{Colors.END}")
            elif '%' in line and 'passed' in line:
                print(f"{Colors.BOLD}{Colors.GREEN}{line}{Colors.END}")
            else:
                print(line)
    
    # Resumen final
    print_header("RESULTADO FINAL")
    
    if success:
        print_success("Pruebas completadas exitosamente!")
    else:
        print_warning("Algunas pruebas fallaron. Revisa la salida arriba.")
    
    print(f"\n{Colors.BLUE}Para más detalles, ejecuta directamente:{Colors.END}")
    print(f"{Colors.CYAN}{' '.join(command)}{Colors.END}")
    
    print(f"\n{Colors.BLUE}Para ver la documentación:{Colors.END}")
    print(f"{Colors.CYAN}ver REPORTE_COMPLETO_PRUEBAS_E2E.md{Colors.END}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Ejecución interrumpida por el usuario{Colors.END}")
        sys.exit(0)
