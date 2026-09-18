#!/usr/bin/env python3
"""
SRCM API - Sistema de Registro Catastral Municipal
Modulo de Informacion y Despliegue Profesional
Municipio Torbes, Estado Tachira, Venezuela
"""

import os
import sys
from datetime import datetime

# Colores ANSI para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_header():
    """Imprime el encabezado principal"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("=" * 80)
    print(" " * 20 + "SRCM API - Sistema de Registro Catastral Municipal")
    print(" " * 28 + "Municipio Torbes, Estado Tachira, Venezuela")
    print(" " * 30 + "Version 2.5.0 - 15 de septiembre de 2026")
    print("=" * 80)
    print(f"{Colors.END}\n")

def print_section(title):
    """Imprime un titulo de seccion"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}>>> {title} {Colors.END}")
    print(f"{Colors.BLUE}{'-' * 80}{Colors.END}\n")

def print_statistic(label, value, color=Colors.GREEN):
    """Imprime una estadistica con formato"""
    print(f"{Colors.CYAN}  {label:.<60} {color}{value}{Colors.END}")

def print_endpoint(method, path, description):
    """Imprime un endpoint con formato"""
    color_map = {
        'GET': Colors.GREEN,
        'POST': Colors.BLUE,
        'PATCH': Colors.YELLOW,
        'DELETE': Colors.RED
    }
    color = color_map.get(method, Colors.WHITE)
    print(f"  {color}{method:6}{Colors.END}  {Colors.CYAN}{path:45}{Colors.END}  {Colors.WHITE}{description}{Colors.END}")

def main():
    """Funcion principal"""
    # Limpiar pantalla
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Imprimir encabezado
    print_header()
    
    # Informacion General
    print_section("INFORMACION GENERAL")
    print_statistic("Nombre del Sistema", "SRCM API - Sistema de Registro Catastral Municipal")
    print_statistic("Institucion", "Alcaldia de Torbes")
    print_statistic("Ubicacion", "Estado Tachira, Venezuela")
    print_statistic("Version", "2.5.0 (Completa)")
    print_statistic("Framework", "FastAPI")
    print_statistic("Base de Datos", "PostgreSQL + PostGIS (Supabase)")
    print_statistic("Autenticacion", "Supabase Auth (JWT)")
    print_statistic("Coordenadas", "WGS84 (EPSG:4326) / UTM 18N (SRID:2201)")
    
    # Estadisticas del Sistema
    print_section("ESTADISTICAS DEL SISTEMA")
    print_statistic("Total de Endpoints", "35", Colors.YELLOW)
    print_statistic("Endpoints Inmuebles", "13", Colors.GREEN)
    print_statistic("Endpoints Propietarios", "6", Colors.GREEN)
    print_statistic("Endpoints Catastro", "5", Colors.GREEN)
    print_statistic("Endpoints Configuracion", "5", Colors.GREEN)
    print_statistic("Endpoints Usuarios", "4", Colors.GREEN)
    print_statistic("Endpoints Salud", "2", Colors.GREEN)
    print_statistic("Tablas de Base de Datos", "7", Colors.GREEN)
    print_statistic("Funciones SQL", "8", Colors.GREEN)
    print_statistic("Triggers SQL", "7", Colors.GREEN)
    print_statistic("Indices Optimizados", "11", Colors.GREEN)
    
    # Endpoints por Modulo
    print_section("ENDPOINTS POR MODULO")
    
    print(f"\n{Colors.BOLD}{Colors.YELLOW}  [INMUEBLES] 13 endpoints{Colors.END}")
    print_endpoint("POST", "/api/v1/inmuebles", "Crear inmueble")
    print_endpoint("GET", "/api/v1/inmuebles", "Listar inmuebles (paginado + filtros)")
    print_endpoint("GET", "/api/v1/inmuebles/{id}", "Obtener inmueble")
    print_endpoint("PATCH", "/api/v1/inmuebles/{id}", "Actualizar inmueble")
    print_endpoint("DELETE", "/api/v1/inmuebles/{id}", "Eliminar inmueble")
    print_endpoint("GET", "/api/v1/inmuebles/{id}/cedula", "Descargar PDF cedula")
    print_endpoint("GET", "/api/v1/inmuebles/{id}/cedula-datos", "Obtener datos cedula (frontend)")
    print_endpoint("POST", "/api/v1/inmuebles/{id}/fotos", "Agregar foto")
    print_endpoint("GET", "/api/v1/inmuebles/{id}/fotos", "Listar fotos")
    print_endpoint("DELETE", "/api/v1/inmuebles/{id}/fotos/{foto_id}", "Eliminar foto")
    print_endpoint("POST", "/api/v1/inmuebles/{id}/hitos", "Agregar hito")
    print_endpoint("GET", "/api/v1/inmuebles/{id}/hitos", "Listar hitos")
    print_endpoint("DELETE", "/api/v1/inmuebles/{id}/hitos/{hito_id}", "Eliminar hito")
    
    print(f"\n{Colors.BOLD}{Colors.YELLOW}  [PROPIETARIOS] 6 endpoints{Colors.END}")
    print_endpoint("POST", "/api/v1/propietarios", "Crear propietario")
    print_endpoint("GET", "/api/v1/propietarios", "Listar propietarios")
    print_endpoint("GET", "/api/v1/propietarios/{id}", "Obtener propietario")
    print_endpoint("PATCH", "/api/v1/propietarios/{id}", "Actualizar propietario")
    print_endpoint("DELETE", "/api/v1/propietarios/{id}", "Eliminar propietario")
    print_endpoint("GET", "/api/v1/propietarios/{id}/inmuebles", "Listar inmuebles de propietario")
    
    print(f"\n{Colors.BOLD}{Colors.YELLOW}  [CATASTRO] 5 endpoints{Colors.END}")
    print_endpoint("GET", "/api/v1/catastro/mapa", "Mapa catastral GeoJSON")
    print_endpoint("GET", "/api/v1/catastro/estadisticas", "Estadisticas generales")
    print_endpoint("GET", "/api/v1/catastro/por-sector", "Predios por sector")
    print_endpoint("GET", "/api/v1/catastro/solapamientos", "Auditoria topologica")
    print_endpoint("GET", "/api/v1/catastro/sectores", "Sectores disponibles")
    
    print(f"\n{Colors.BOLD}{Colors.YELLOW}  [CONFIGURACION] 5 endpoints{Colors.END}")
    print_endpoint("GET", "/api/v1/configuracion/catastral", "Obtener configuracion catastral")
    print_endpoint("PATCH", "/api/v1/configuracion/catastral", "Actualizar configuracion catastral")
    print_endpoint("GET", "/api/v1/configuracion/sistema", "Obtener configuracion del sistema")
    print_endpoint("PATCH", "/api/v1/configuracion/sistema", "Actualizar configuracion del sistema")
    print_endpoint("GET", "/api/v1/configuracion/catastral/pdf-config", "Configuracion para PDF")
    
    print(f"\n{Colors.BOLD}{Colors.YELLOW}  [USUARIOS] 4 endpoints{Colors.END}")
    print_endpoint("GET", "/api/v1/usuarios/me", "Perfil del usuario actual")
    print_endpoint("GET", "/api/v1/usuarios", "Listar usuarios")
    print_endpoint("PATCH", "/api/v1/usuarios/{id}/rol", "Cambiar rol")
    print_endpoint("PATCH", "/api/v1/usuarios/{id}/estado", "Activar/desactivar usuario")
    
    print(f"\n{Colors.BOLD}{Colors.YELLOW}  [SALUD] 2 endpoints{Colors.END}")
    print_endpoint("GET", "/", "Raiz del sistema")
    print_endpoint("GET", "/salud", "Health check del sistema")
    
    # Caracteristicas Tecnicas
    print_section("CARACTERISTICAS TECNICAS")
    print_statistic("Generacion Codigo Catastral", "Automatica (23 caracteres)", Colors.GREEN)
    print_statistic("Calculo Valores Catastrales", "Automatico (columnas GENERATED)", Colors.GREEN)
    print_statistic("Conversion Coordenadas UTM", "Automatica (trigger)", Colors.GREEN)
    print_statistic("Validacion Solapamientos", "Automatica (trigger)", Colors.GREEN)
    print_statistic("Generacion PDF Cedula", "Backend (WeasyPrint + Jinja2)", Colors.GREEN)
    print_statistic("Codigo QR en PDF", "Backend (qrcode)", Colors.GREEN)
    print_statistic("Busqueda Parcial", "Indices trigram (pg_trgm)", Colors.GREEN)
    print_statistic("Mapa GeoJSON", "PostGIS (ST_AsGeoJSON)", Colors.GREEN)
    print_statistic("Paginacion", "SQL (LIMIT/OFFSET)", Colors.GREEN)
    print_statistic("Autenticacion", "JWT Bearer Token", Colors.GREEN)
    print_statistic("Autorizacion", "Roles (inspector/administrador)", Colors.GREEN)
    
    # Informacion de Acceso
    print_section("INFORMACION DE ACCESO")
    print_statistic("URL Local", "http://localhost:8000", Colors.YELLOW)
    print_statistic("Documentacion Swagger", "http://localhost:8000/docs", Colors.YELLOW)
    print_statistic("Documentacion ReDoc", "http://localhost:8000/redoc", Colors.YELLOW)
    print_statistic("OpenAPI JSON", "http://localhost:8000/openapi.json", Colors.YELLOW)
    print_statistic("Health Check", "http://localhost:8000/salud", Colors.YELLOW)
    
    # Codigo Catastral
    print_section("CODIGO CATASTRAL")
    print(f"{Colors.CYAN}  Formato: {Colors.YELLOW}EE-MM-PP-SSS-MAA-PAA-SPAA-NAA-UAA{Colors.END}")
    print(f"{Colors.CYAN}  Total:   {Colors.YELLOW}23 caracteres{Colors.END}")
    print(f"{Colors.CYAN}  Estado:  {Colors.GREEN}20 (Tachira){Colors.END}")
    print(f"{Colors.CYAN}  Municipio: {Colors.GREEN}27 (Torbes){Colors.END}")
    print(f"{Colors.CYAN}  Parroquia: {Colors.GREEN}01 (San Josecito){Colors.END}")
    print(f"{Colors.CYAN}  UTM SRID: {Colors.GREEN}2201 (REGVEN - UTM 18N){Colors.END}")
    
    # Pie de pagina
    print(f"\n{Colors.BOLD}{Colors.GREEN}")
    print("=" * 80)
    print(" " * 25 + "SISTEMA COMPLETO Y LISTO PARA PRODUCCION")
    print(" " * 28 + "35 Endpoints Implementados")
    print(" " * 22 + "Documentacion: http://localhost:8000/docs")
    print("=" * 80)
    print(f"{Colors.END}\n")
    
    print(f"{Colors.YELLOW}  Para iniciar el servidor:{Colors.END}")
    print(f"  {Colors.CYAN}python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload{Colors.END}\n")

if __name__ == "__main__":
    main()
