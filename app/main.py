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
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
            body { font-family: 'Inter', sans-serif; background-color: #f8fafc; }
            .bg-pattern {
                background-image: radial-gradient(#cbd5e1 1px, transparent 1px);
                background-size: 24px 24px;
            }
        </style>
    </head>
    <body class="text-slate-800 min-h-screen flex flex-col bg-pattern">
        
        <!-- Header Institucional -->
        <header class="bg-[#0f172a] text-white py-5 shadow-lg border-b-4 border-yellow-500">
            <div class="max-w-5xl mx-auto px-6 flex flex-col md:flex-row items-center gap-4">
                <div class="w-14 h-14 bg-white rounded-full flex items-center justify-center text-[#0f172a] text-2xl shadow-inner">
                    <i class="fa-solid fa-landmark"></i>
                </div>
                <div class="text-center md:text-left">
                    <h2 class="text-xs font-semibold tracking-widest text-slate-300 uppercase mb-1">República Bolivariana de Venezuela</h2>
                    <h1 class="text-2xl font-bold tracking-tight">Alcaldía del Municipio Torbes</h1>
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="flex-grow flex items-center justify-center p-6">
            <div class="max-w-4xl w-full bg-white rounded-2xl shadow-xl overflow-hidden border border-slate-200">
                
                <!-- Banner Title -->
                <div class="bg-slate-50 border-b border-slate-200 p-8 text-center relative overflow-hidden">
                    <!-- Subtle background decoration -->
                    <div class="absolute -right-10 -top-10 text-slate-200 opacity-20 text-[150px]">
                        <i class="fa-solid fa-map"></i>
                    </div>
                    <div class="relative z-10">
                        <div class="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-blue-100 text-blue-700 mb-5 shadow-sm border border-blue-200">
                            <i class="fa-solid fa-map-location-dot text-4xl"></i>
                        </div>
                        <h2 class="text-3xl font-extrabold text-[#0f172a] mb-2 tracking-tight">Sistema de Registro Catastral Municipal</h2>
                        <p class="text-slate-500 text-lg font-medium">Plataforma Central de Servicios (API SRCM)</p>
                    </div>
                </div>

                <!-- Info Grid -->
                <div class="p-8 md:p-10">
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10 text-left">
                        <div class="bg-slate-50 p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition duration-300">
                            <div class="text-emerald-600 mb-4 bg-emerald-100 w-12 h-12 flex items-center justify-center rounded-lg"><i class="fa-solid fa-database text-xl"></i></div>
                            <h3 class="text-[#0f172a] font-bold text-lg mb-2">Estado Activo</h3>
                            <p class="text-sm text-slate-600 leading-relaxed">Conexión estable con PostgreSQL + PostGIS. Triggers de validación topológica en línea.</p>
                        </div>
                        <div class="bg-slate-50 p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition duration-300">
                            <div class="text-blue-600 mb-4 bg-blue-100 w-12 h-12 flex items-center justify-center rounded-lg"><i class="fa-solid fa-shield-halved text-xl"></i></div>
                            <h3 class="text-[#0f172a] font-bold text-lg mb-2">Seguridad JWT</h3>
                            <p class="text-sm text-slate-600 leading-relaxed">Capa de autenticación estricta con firmas criptográficas ES256 administradas por Supabase.</p>
                        </div>
                        <div class="bg-slate-50 p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition duration-300">
                            <div class="text-purple-600 mb-4 bg-purple-100 w-12 h-12 flex items-center justify-center rounded-lg"><i class="fa-solid fa-network-wired text-xl"></i></div>
                            <h3 class="text-[#0f172a] font-bold text-lg mb-2">35 Endpoints</h3>
                            <p class="text-sm text-slate-600 leading-relaxed">Servicios REST completos para la auditoría, registro y consulta geoespacial de predios.</p>
                        </div>
                    </div>

                    <!-- Action Button -->
                    <div class="text-center bg-blue-50/50 p-8 rounded-2xl border border-blue-100">
                        <h4 class="text-[#0f172a] font-bold mb-4">Acceso a Desarrolladores</h4>
                        <a href="/docs" class="inline-flex items-center justify-center gap-3 px-8 py-4 bg-[#0f172a] hover:bg-blue-900 text-white text-lg font-semibold rounded-xl shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all duration-200">
                            <i class="fa-solid fa-file-code"></i>
                            Ingresar a la Documentación Oficial
                        </a>
                        <p class="mt-5 text-sm text-slate-500 max-w-lg mx-auto">
                            <i class="fa-solid fa-circle-info text-blue-500 mr-1"></i>
                            La interfaz Swagger permite realizar consultas en tiempo real. Se requiere un Token JWT válido para mutaciones de datos.
                        </p>
                    </div>
                </div>
            </div>
        </main>

        <!-- Footer -->
        <footer class="bg-white border-t border-slate-200 py-8 text-center text-sm text-slate-500">
            <p class="font-semibold text-slate-700 mb-1">Versión del Sistema: 2.5.0 &bull; Dirección de Catastro</p>
            <p>&copy; 2026 Alcaldía del Municipio Torbes. Todos los derechos reservados.</p>
        </footer>
    </body>
    </html>
    """
    return html_content


@app.get("/salud", tags=["Salud"])
def salud():
    """Endpoint simple de health-check (útil para Render/Railway/Fly.io)."""
    return {"status": "ok"}
