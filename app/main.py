import logging

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware

from app.api_router import api_router
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("srcm")

app = FastAPI(
    title="SRCM API - Sistema de Registro Catastral Municipal - 35 Endpoints",
    description=(
        "**API REST completa del Sistema de Registro Catastral Municipal (SRCM)**\n\n"
        "**Municipio Torbes, Estado Táchira, Venezuela**\n\n"
        "Esta API profesional permite la gestión completa del catastro municipal, incluyendo:\n\n"
        "🏢 **Gestión de Inmuebles:** Creación, lectura, actualización y eliminación de predios catastrales\n"
        "👥 **Gestión de Propietarios:** Registro y administración de propietarios de inmuebles\n"
        "🗺️ **Catastro Geoespacial:** Mapa interactivo GeoJSON, estadísticas y auditoría topológica\n"
        "⚙️ **Configuración Catastral:** Gestión de valores por m², vigencia de cédulas y datos institucionales\n"
        "👤 **Gestión de Usuarios:** Control de roles y estado de inspectores y administradores\n"
        "📄 **Cédulas Catastrales:** Generación automática de PDFs con código QR\n\n"
        "**Características Técnicas:**\n\n"
        "✅ **35 Endpoints** completamente implementados\n"
        "✅ **Autenticación JWT** con Supabase Auth\n"
        "✅ **Base de datos PostgreSQL + PostGIS** para datos geoespaciales\n"
        "✅ **Cálculo automático** de códigos catastrales, valores y coordenadas UTM\n"
        "✅ **Validación de solapamientos** topológicos para prevenir errores\n"
        "✅ **Sincronización offline** para trabajo de campo\n\n"
        "**Código Catastral:** Formato de 23 caracteres (EE-MM-PP-SSS-MAA-PAA-SPAA-NAA-UAA)\n"
        "**UTM SRID:** 2201 (REGVEN - UTM 18N)\n"
        "**Versión:** 2.5 Completa"
    ),
    version="2.5.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {
            "name": "Salud",
            "description": "Endpoints de health-check y estado del sistema"
        },
        {
            "name": "Inmuebles",
            "description": "Gestión completa de inmuebles catastrales, fotos y hitos prediales"
        },
        {
            "name": "Propietarios",
            "description": "Gestión de propietarios de inmuebles catastrales"
        },
        {
            "name": "Catastro",
            "description": "Funciones geoespaciales, mapa catastral y estadísticas"
        },
        {
            "name": "Configuración",
            "description": "Gestión de configuración catastral y del sistema"
        },
        {
            "name": "Usuarios",
            "description": "Gestión de usuarios, roles y permisos"
        }
    ],

)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.exception_handler(HTTPException)
async def log_http_exceptions(request, exc: HTTPException):
    if exc.status_code >= 500:
        logger.error("Error %s en %s: %s", exc.status_code, request.url, exc.detail)
    return await http_exception_handler(request, exc)


@app.get("/", tags=["Salud"], response_class=HTMLResponse)
def raiz():
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Catastro Municipal - Alcaldía de Torbes</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <!-- FontAwesome para librería de iconos completa -->
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
            body { font-family: 'Inter', sans-serif; background-color: #f8fafc; }
            .bg-pattern {
                background-image: radial-gradient(#cbd5e1 1px, transparent 1px);
                background-size: 24px 24px;
            }
        </style>
    </head>
    <body class="text-slate-800 min-h-screen flex flex-col bg-pattern">
        
        <!-- Header Institucional -->
        <header class="bg-[#0f172a] text-white py-4 shadow-lg border-b-4 border-yellow-500 sticky top-0 z-50">
            <div class="max-w-6xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
                <div class="flex items-center gap-4">
                    <div class="w-14 h-14 bg-white rounded-full flex items-center justify-center text-[#0f172a] text-2xl shadow-inner border-2 border-slate-200">
                        <i class="fa-solid fa-building-columns"></i>
                    </div>
                    <div class="text-center md:text-left">
                        <h2 class="text-xs font-semibold tracking-widest text-slate-400 uppercase mb-0.5">República Bolivariana de Venezuela</h2>
                        <h1 class="text-xl font-bold tracking-tight">Alcaldía del Municipio Torbes</h1>
                    </div>
                </div>
                <div class="hidden md:flex gap-4">
                    <span class="px-3 py-1 bg-emerald-500/20 text-emerald-400 rounded-full text-sm font-semibold border border-emerald-500/30 flex items-center gap-2">
                        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> Sistema en línea
                    </span>
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="flex-grow flex items-center justify-center p-4 md:p-8">
            <div class="max-w-6xl w-full bg-white rounded-2xl shadow-xl overflow-hidden border border-slate-200">
                
                <!-- Hero Banner -->
                <div class="bg-gradient-to-br from-slate-50 to-slate-100 border-b border-slate-200 p-8 md:p-12 relative overflow-hidden flex flex-col md:flex-row items-center gap-8">
                    <div class="absolute -right-10 -bottom-10 text-slate-200 opacity-30 text-[200px] pointer-events-none">
                        <i class="fa-solid fa-map-marked-alt"></i>
                    </div>
                    
                    <div class="flex-shrink-0 relative z-10">
                        <div class="w-28 h-28 rounded-3xl bg-blue-600 text-white flex items-center justify-center shadow-lg shadow-blue-600/30">
                            <i class="fa-solid fa-satellite text-5xl"></i>
                        </div>
                    </div>
                    
                    <div class="relative z-10 text-center md:text-left">
                        <div class="inline-block px-3 py-1 bg-blue-100 text-blue-700 font-semibold text-xs rounded-full mb-3 uppercase tracking-wider">
                            API RESTful v2.5.0
                        </div>
                        <h2 class="text-3xl md:text-4xl font-extrabold text-[#0f172a] mb-3 tracking-tight">Sistema de Registro Catastral Municipal</h2>
                        <p class="text-slate-600 text-lg max-w-2xl">Plataforma central del motor catastral (SRCM). Gestiona propiedades, valida geometría topológica y emite documentación oficial automatizada.</p>
                    </div>
                </div>

                <!-- Modulos del Sistema (Extraídos del README) -->
                <div class="p-8 md:p-12">
                    <h3 class="text-xl font-bold text-slate-800 mb-6 flex items-center gap-2">
                        <i class="fa-solid fa-cubes text-blue-600"></i> Arquitectura y Módulos Activos
                    </h3>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
                        
                        <!-- Módulo 1 -->
                        <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition group">
                            <div class="text-blue-600 mb-4 bg-blue-50 w-12 h-12 flex items-center justify-center rounded-lg group-hover:bg-blue-600 group-hover:text-white transition">
                                <i class="fa-solid fa-layer-group text-xl"></i>
                            </div>
                            <h4 class="text-[#0f172a] font-bold mb-2">Motor Espacial (GIS)</h4>
                            <p class="text-sm text-slate-600">PostgreSQL + PostGIS. Prevención de solapes mediante Triggers (ST_Intersects). Manejo de Polígonos GeoJSON y SRID 2201 (REGVEN).</p>
                        </div>

                        <!-- Módulo 2 -->
                        <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition group">
                            <div class="text-emerald-600 mb-4 bg-emerald-50 w-12 h-12 flex items-center justify-center rounded-lg group-hover:bg-emerald-600 group-hover:text-white transition">
                                <i class="fa-solid fa-file-pdf text-xl"></i>
                            </div>
                            <h4 class="text-[#0f172a] font-bold mb-2">Cédulas Catastrales</h4>
                            <p class="text-sm text-slate-600">Generación automática de PDFs de la Cédula Catastral, cálculo de avalúos y generación de Códigos QR para verificación.</p>
                        </div>

                        <!-- Módulo 3 -->
                        <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition group">
                            <div class="text-purple-600 mb-4 bg-purple-50 w-12 h-12 flex items-center justify-center rounded-lg group-hover:bg-purple-600 group-hover:text-white transition">
                                <i class="fa-solid fa-user-shield text-xl"></i>
                            </div>
                            <h4 class="text-[#0f172a] font-bold mb-2">Auth & Supabase</h4>
                            <p class="text-sm text-slate-600">Autenticación Stateless delegada a Supabase Auth. Validación rigurosa de firmas JWT (Algoritmo ES256) y RBAC.</p>
                        </div>

                        <!-- Módulo 4 -->
                        <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition group">
                            <div class="text-amber-600 mb-4 bg-amber-50 w-12 h-12 flex items-center justify-center rounded-lg group-hover:bg-amber-600 group-hover:text-white transition">
                                <i class="fa-solid fa-vial-circle-check text-xl"></i>
                            </div>
                            <h4 class="text-[#0f172a] font-bold mb-2">Calidad de Software</h4>
                            <p class="text-sm text-slate-600">Validado al 100%. Suite E2E y Pruebas Unitarias. Validaciones estrictas Pydantic v2 sobre 35 Endpoints aislados.</p>
                        </div>
                    </div>

                    <!-- Botón de Acceso -->
                    <div class="bg-slate-900 rounded-2xl p-8 md:p-10 flex flex-col md:flex-row items-center justify-between gap-6 shadow-2xl relative overflow-hidden">
                        <!-- BG elements -->
                        <div class="absolute right-0 top-0 w-64 h-64 bg-blue-600/10 rounded-full blur-3xl"></div>
                        
                        <div class="relative z-10 text-center md:text-left max-w-2xl">
                            <h3 class="text-2xl font-bold text-white mb-2">Portal para Desarrolladores</h3>
                            <p class="text-slate-400 mb-0">Accede a la especificación OpenAPI (Swagger UI). Podrás interactuar con los endpoints, leer los esquemas de la Base de Datos e inyectar tokens para pruebas de concepto.</p>
                        </div>
                        <div class="relative z-10 flex-shrink-0">
                            <a href="/docs" class="inline-flex items-center justify-center gap-3 px-8 py-4 bg-blue-600 hover:bg-blue-500 text-white text-lg font-bold rounded-xl shadow-lg shadow-blue-900/50 transition-all duration-200 hover:-translate-y-1">
                                <i class="fa-solid fa-code"></i>
                                Abrir Swagger UI
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </main>

        <!-- Footer -->
        <footer class="bg-white border-t border-slate-200 py-6 mt-auto">
            <div class="max-w-6xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center text-sm text-slate-500">
                <p class="font-medium text-slate-700 mb-2 md:mb-0">SRCM &bull; Dirección de Catastro Municipal</p>
                <div class="flex items-center gap-4">
                    <p>&copy; 2026 Alcaldía del Municipio Torbes. Todos los derechos reservados.</p>
                </div>
            </div>
        </footer>
    </body>
    </html>
    """
    return html_content


@app.get("/salud", tags=["Salud"])
def salud():
    """Endpoint simple de health-check (útil para Render/Railway/Fly.io)."""
    return {"status": "ok"}
