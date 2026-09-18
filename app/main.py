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
        <title>SRCM API - Backend Catastral</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .bg-grid {
                background-size: 40px 40px;
                background-image: linear-gradient(to right, rgba(255, 255, 255, 0.05) 1px, transparent 1px),
                                  linear-gradient(to bottom, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
            }
            .glow-text {
                text-shadow: 0 0 20px rgba(59, 130, 246, 0.5);
            }
        </style>
    </head>
    <body class="bg-slate-900 bg-grid min-h-screen flex items-center justify-center font-sans text-slate-300 relative overflow-hidden">
        
        <!-- Elementos decorativos de fondo -->
        <div class="absolute top-0 left-0 w-full h-full overflow-hidden -z-10 pointer-events-none">
            <div class="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] rounded-full bg-blue-600/20 blur-[120px]"></div>
            <div class="absolute bottom-[0%] -right-[10%] w-[40%] h-[40%] rounded-full bg-emerald-600/20 blur-[100px]"></div>
        </div>

        <div class="max-w-3xl w-full p-8 relative z-10">
            
            <!-- Tarjeta Principal -->
            <div class="bg-slate-800/60 backdrop-blur-xl rounded-3xl p-10 shadow-2xl border border-slate-700/50 text-center transform transition-all hover:scale-[1.01] duration-300">
                
                <div class="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-blue-500/10 text-blue-400 mb-6 border border-blue-500/20">
                    <i class="fa-solid fa-map-location-dot text-4xl"></i>
                </div>

                <h1 class="text-4xl md:text-5xl font-extrabold text-white mb-4 tracking-tight glow-text">
                    SRCM <span class="text-blue-500">API</span>
                </h1>
                <h2 class="text-xl md:text-2xl font-medium text-slate-400 mb-8">
                    Sistema de Registro Catastral Municipal
                </h2>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-10 text-left">
                    <div class="bg-slate-900/50 p-4 rounded-2xl border border-slate-700/50">
                        <div class="text-emerald-400 mb-2"><i class="fa-solid fa-server text-xl"></i></div>
                        <h3 class="text-white font-bold mb-1">Estado</h3>
                        <p class="text-sm text-slate-400">Servicio en línea (PostgreSQL + PostGIS)</p>
                    </div>
                    <div class="bg-slate-900/50 p-4 rounded-2xl border border-slate-700/50">
                        <div class="text-purple-400 mb-2"><i class="fa-solid fa-shield-halved text-xl"></i></div>
                        <h3 class="text-white font-bold mb-1">Seguridad</h3>
                        <p class="text-sm text-slate-400">Protegido por Supabase JWT (ES256)</p>
                    </div>
                    <div class="bg-slate-900/50 p-4 rounded-2xl border border-slate-700/50">
                        <div class="text-blue-400 mb-2"><i class="fa-solid fa-code text-xl"></i></div>
                        <h3 class="text-white font-bold mb-1">Endpoints</h3>
                        <p class="text-sm text-slate-400">35 Rutas REST disponibles</p>
                    </div>
                </div>

                <div class="flex flex-col sm:flex-row gap-4 justify-center">
                    <a href="/docs" class="group relative px-8 py-4 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl shadow-lg shadow-blue-500/30 transition-all duration-200 flex items-center justify-center gap-3">
                        <span>Documentación Swagger</span>
                        <i class="fa-solid fa-arrow-right group-hover:translate-x-1 transition-transform"></i>
                    </a>
                    <a href="/redoc" class="px-8 py-4 bg-slate-700 hover:bg-slate-600 text-white font-bold rounded-xl transition-all duration-200 flex items-center justify-center gap-3">
                        <i class="fa-solid fa-book"></i>
                        <span>ReDoc View</span>
                    </a>
                </div>

            </div>
            
            <div class="text-center mt-8 text-slate-500 text-sm">
                <p>Versión 2.5.0 &bull; Desarrollado con FastAPI y Python &bull; Alcaldía de Torbes</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content


@app.get("/salud", tags=["Salud"])
def salud():
    """Endpoint simple de health-check (útil para Render/Railway/Fly.io)."""
    return {"status": "ok"}
