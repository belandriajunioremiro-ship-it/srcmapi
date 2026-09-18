import logging

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
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

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


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
        <title>Catastro Municipal - SRCM API</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <!-- FontAwesome para iconos generales -->
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <!-- Devicon para logos de tecnologías -->
        <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/devicon.min.css" />
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
        
        <!-- Main Content -->
        <main class="flex-grow flex items-center justify-center p-4 md:p-8 mt-4 md:mt-8">
            <div class="max-w-6xl w-full bg-white rounded-3xl shadow-2xl overflow-hidden border border-slate-200">
                
                <!-- Hero Banner -->
                <div class="bg-gradient-to-br from-[#0f172a] to-blue-900 border-b border-slate-700 p-8 md:p-14 relative overflow-hidden flex flex-col items-center text-center">
                    <!-- Decoración geométrica -->
                    <div class="absolute -right-10 -bottom-10 text-blue-500 opacity-10 text-[250px] pointer-events-none transform rotate-12">
                        <i class="fa-solid fa-map-marked-alt"></i>
                    </div>
                    
                    <div class="relative z-10">
                        <div class="inline-block px-4 py-1.5 bg-blue-500/20 text-blue-300 font-bold text-xs rounded-full mb-6 uppercase tracking-widest border border-blue-500/30">
                            API RESTful v2.5.0
                        </div>
                        <h2 class="text-3xl md:text-5xl font-extrabold text-white mb-6 tracking-tight flex flex-col md:flex-row items-center justify-center gap-4">
                            <span class="w-16 h-16 rounded-2xl bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/30 text-white text-3xl">
                                <i class="fa-solid fa-location-crosshairs"></i>
                            </span>
                            Sistema de Registro Catastral Municipal
                        </h2>
                        <p class="text-blue-100/80 text-lg max-w-3xl leading-relaxed mx-auto">Plataforma central del motor catastral (SRCM). Gestiona propiedades, valida geometría topológica y emite documentación oficial automatizada para la Alcaldía del Municipio Torbes.</p>
                    </div>
                </div>

                <!-- Modulos del Sistema -->
                <div class="p-8 md:p-12">
                    <h3 class="text-xl font-bold text-slate-800 mb-6 flex items-center gap-2">
                        <i class="fa-solid fa-cubes text-blue-600"></i> Arquitectura y Módulos Activos
                    </h3>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
                        <!-- Módulo 1 -->
                        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-xl transition-all duration-300 group hover:-translate-y-1">
                            <div class="text-blue-600 mb-4 bg-blue-50 w-14 h-14 flex items-center justify-center rounded-xl group-hover:bg-blue-600 group-hover:text-white transition-colors">
                                <i class="fa-solid fa-layer-group text-2xl"></i>
                            </div>
                            <h4 class="text-[#0f172a] font-bold mb-2">Motor Espacial (GIS)</h4>
                            <p class="text-sm text-slate-600 leading-relaxed">PostgreSQL + PostGIS. Prevención de solapes mediante Triggers (ST_Intersects). Manejo de Polígonos GeoJSON y SRID 2201 (REGVEN).</p>
                        </div>

                        <!-- Módulo 2 -->
                        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-xl transition-all duration-300 group hover:-translate-y-1">
                            <div class="text-emerald-600 mb-4 bg-emerald-50 w-14 h-14 flex items-center justify-center rounded-xl group-hover:bg-emerald-600 group-hover:text-white transition-colors">
                                <i class="fa-solid fa-file-pdf text-2xl"></i>
                            </div>
                            <h4 class="text-[#0f172a] font-bold mb-2">Cédulas Catastrales</h4>
                            <p class="text-sm text-slate-600 leading-relaxed">Generación automática de PDFs de la Cédula Catastral, cálculo de avalúos y generación de Códigos QR para verificación.</p>
                        </div>

                        <!-- Módulo 3 -->
                        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-xl transition-all duration-300 group hover:-translate-y-1">
                            <div class="text-purple-600 mb-4 bg-purple-50 w-14 h-14 flex items-center justify-center rounded-xl group-hover:bg-purple-600 group-hover:text-white transition-colors">
                                <i class="fa-solid fa-user-shield text-2xl"></i>
                            </div>
                            <h4 class="text-[#0f172a] font-bold mb-2">Auth & Supabase</h4>
                            <p class="text-sm text-slate-600 leading-relaxed">Autenticación Stateless delegada a Supabase Auth. Validación rigurosa de firmas JWT (Algoritmo ES256) y RBAC.</p>
                        </div>

                        <!-- Módulo 4 -->
                        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-xl transition-all duration-300 group hover:-translate-y-1">
                            <div class="text-amber-600 mb-4 bg-amber-50 w-14 h-14 flex items-center justify-center rounded-xl group-hover:bg-amber-600 group-hover:text-white transition-colors">
                                <i class="fa-solid fa-vial-circle-check text-2xl"></i>
                            </div>
                            <h4 class="text-[#0f172a] font-bold mb-2">Calidad de Software</h4>
                            <p class="text-sm text-slate-600 leading-relaxed">Validado al 100%. Suite E2E y Pruebas Unitarias. Validaciones estrictas Pydantic v2 sobre 35 Endpoints aislados.</p>
                        </div>
                    </div>

                    <!-- Botón de Acceso -->
                    <div class="bg-slate-50 border border-slate-200 rounded-2xl p-8 md:p-10 flex flex-col md:flex-row items-center justify-between gap-6 relative overflow-hidden mb-12">
                        <div class="relative z-10 text-center md:text-left max-w-2xl">
                            <h3 class="text-2xl font-bold text-[#0f172a] mb-2">Portal para Desarrolladores</h3>
                            <p class="text-slate-600 mb-0">Accede a la especificación OpenAPI (Swagger UI). Podrás interactuar con los endpoints, leer los esquemas de la Base de Datos e inyectar tokens para pruebas de concepto.</p>
                        </div>
                        <div class="relative z-10 flex-shrink-0">
                            <a href="/docs" class="inline-flex items-center justify-center gap-3 px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white text-lg font-bold rounded-xl shadow-lg shadow-blue-600/30 transition-all duration-200 hover:-translate-y-1">
                                <i class="fa-solid fa-code"></i>
                                Abrir Swagger UI
                            </a>
                        </div>
                    </div>

                    <!-- Stack Tecnológico -->
                    <div class="border-t border-slate-100 pt-10 text-center">
                        <h4 class="text-sm font-bold text-slate-400 uppercase tracking-widest mb-8">Stack Tecnológico y Herramientas</h4>
                        <div class="flex flex-wrap justify-center items-center gap-6 md:gap-10 opacity-90 hover:opacity-100 transition-opacity">
                            
                            <div class="flex flex-col items-center gap-2 group cursor-default">
                                <img src="/static/logos/fastapi.png" alt="FastAPI" class="w-12 h-12 object-contain group-hover:scale-110 transition-transform drop-shadow-sm">
                                <span class="text-xs font-semibold text-slate-500">FastAPI</span>
                            </div>

                            <div class="flex flex-col items-center gap-2 group cursor-default">
                                <img src="/static/logos/PostgreSQL-Logo.png" alt="PostgreSQL" class="w-12 h-12 object-contain group-hover:scale-110 transition-transform drop-shadow-sm">
                                <span class="text-xs font-semibold text-slate-500">PostgreSQL</span>
                            </div>

                            <div class="flex flex-col items-center gap-2 group cursor-default">
                                <img src="/static/logos/posgist.jpg" alt="PostGIS" class="w-12 h-12 object-contain rounded-lg group-hover:scale-110 transition-transform shadow-sm">
                                <span class="text-xs font-semibold text-slate-500">PostGIS</span>
                            </div>

                            <div class="flex flex-col items-center gap-2 group cursor-default">
                                <img src="/static/logos/supabase.webp" alt="Supabase" class="w-12 h-12 object-contain group-hover:scale-110 transition-transform drop-shadow-sm">
                                <span class="text-xs font-semibold text-slate-500">Supabase</span>
                            </div>

                            <div class="flex flex-col items-center gap-2 group cursor-default">
                                <img src="/static/logos/Pydantic.png" alt="Pydantic" class="w-12 h-12 object-contain group-hover:scale-110 transition-transform drop-shadow-sm">
                                <span class="text-xs font-semibold text-slate-500">Pydantic</span>
                            </div>

                            <div class="flex flex-col items-center gap-2 group cursor-default">
                                <img src="/static/logos/SQLAlchemy.jpg" alt="SQLAlchemy" class="w-12 h-12 object-contain rounded-lg group-hover:scale-110 transition-transform shadow-sm">
                                <span class="text-xs font-semibold text-slate-500">SQLAlchemy</span>
                            </div>

                            <div class="flex flex-col items-center gap-2 group cursor-default">
                                <img src="/static/logos/Psycopg2.png" alt="Psycopg2" class="w-12 h-12 object-contain group-hover:scale-110 transition-transform drop-shadow-sm">
                                <span class="text-xs font-semibold text-slate-500">Psycopg2</span>
                            </div>

                            <div class="flex flex-col items-center gap-2 group cursor-default">
                                <img src="/static/logos/ReportLab.avif" alt="ReportLab" class="w-12 h-12 object-contain rounded-lg group-hover:scale-110 transition-transform shadow-sm">
                                <span class="text-xs font-semibold text-slate-500">ReportLab</span>
                            </div>

                            <div class="flex flex-col items-center gap-2 group cursor-default">
                                <img src="/static/logos/geopandas.png" alt="GeoPandas" class="w-12 h-12 object-contain group-hover:scale-110 transition-transform drop-shadow-sm">
                                <span class="text-xs font-semibold text-slate-500">GeoPandas</span>
                            </div>

                            <div class="flex flex-col items-center gap-2 group cursor-default">
                                <img src="/static/logos/PyJWT.jpg" alt="PyJWT" class="w-12 h-12 object-contain rounded-lg group-hover:scale-110 transition-transform shadow-sm">
                                <span class="text-xs font-semibold text-slate-500">PyJWT</span>
                            </div>
                            
                            <div class="flex flex-col items-center gap-2 group cursor-default">
                                <img src="/static/logos/Qrcode.jpg" alt="QR Code" class="w-12 h-12 object-contain rounded-lg group-hover:scale-110 transition-transform shadow-sm">
                                <span class="text-xs font-semibold text-slate-500">QRCode</span>
                            </div>

                            <div class="flex flex-col items-center gap-2 group cursor-default">
                                <img src="/static/logos/pytest.png" alt="Pytest" class="w-12 h-12 object-contain group-hover:scale-110 transition-transform drop-shadow-sm">
                                <span class="text-xs font-semibold text-slate-500">Pytest</span>
                            </div>

                        </div>
                    </div>

                </div>
            </div>
        </main>

        <!-- Footer -->
        <footer class="py-6 mt-auto">
            <div class="max-w-6xl mx-auto px-6 text-center text-sm text-slate-500 font-medium">
                <p>&copy; 2026 Alcaldía del Municipio Torbes. Dirección de Catastro. Todos los derechos reservados.</p>
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
