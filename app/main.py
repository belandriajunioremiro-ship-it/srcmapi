import logging

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
import os
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware

from app.api_router import api_router
from app.core.config import settings
from app.services.cedula_service import generar_pdf_formato_vacio

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
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;500;600;700;800;900&display=swap');
            body { font-family: 'Nunito', sans-serif; background-color: #ffffff; }
        </style>
    </head>
    <body class="text-slate-900 min-h-screen flex flex-col bg-white">
        
        <!-- Main Content -->
        <main class="flex-grow flex flex-col items-center p-4 md:p-10 mt-2 md:mt-6 w-full">
            
            <!-- Hero Banner -->
            <div class="max-w-[1600px] w-full mb-16 flex justify-center">
                <img src="/static/logos/bannerarriba.jpg" alt="Sistema de Registro Catastral Municipal" class="w-full h-auto rounded-xl object-contain">
            </div>

            <div class="max-w-[1600px] w-full">
                <!-- Modulos del Sistema -->
                <div class="mb-20">
                    <h3 class="text-2xl font-extrabold text-slate-900 mb-10 flex items-center gap-3 justify-center md:justify-start">
                        <i class="fa-solid fa-cubes text-blue-600"></i> Arquitectura y Módulos Activos
                    </h3>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-20">
                        <!-- Módulo 1 -->
                        <div class="p-6 group hover:-translate-y-1 transition-transform duration-300">
                            <div class="text-blue-600 mb-6 w-14 h-14 flex items-center justify-center rounded-xl bg-slate-50 group-hover:bg-blue-600 group-hover:text-white transition-colors duration-300">
                                <i class="fa-solid fa-layer-group text-2xl"></i>
                            </div>
                            <h4 class="text-slate-900 font-bold mb-3 text-xl tracking-tight">Motor Espacial (GIS)</h4>
                            <p class="text-base text-slate-600 leading-relaxed font-medium">PostgreSQL + PostGIS. Prevención de solapes mediante Triggers (ST_Intersects). Manejo de Polígonos GeoJSON y SRID 2201 (REGVEN).</p>
                        </div>

                        <!-- Módulo 2 -->
                        <div class="p-6 group hover:-translate-y-1 transition-transform duration-300">
                            <div class="text-blue-600 mb-6 w-14 h-14 flex items-center justify-center rounded-xl bg-slate-50 group-hover:bg-blue-600 group-hover:text-white transition-colors duration-300">
                                <i class="fa-solid fa-file-pdf text-2xl"></i>
                            </div>
                            <h4 class="text-slate-900 font-bold mb-3 text-xl tracking-tight">Cédulas Catastrales</h4>
                            <p class="text-base text-slate-600 leading-relaxed font-medium">Generación automática de PDFs de la Cédula Catastral, cálculo de avalúos y generación de Códigos QR para verificación.</p>
                        </div>

                        <!-- Módulo 3 -->
                        <div class="p-6 group hover:-translate-y-1 transition-transform duration-300">
                            <div class="text-blue-600 mb-6 w-14 h-14 flex items-center justify-center rounded-xl bg-slate-50 group-hover:bg-blue-600 group-hover:text-white transition-colors duration-300">
                                <i class="fa-solid fa-user-shield text-2xl"></i>
                            </div>
                            <h4 class="text-slate-900 font-bold mb-3 text-xl tracking-tight">Auth & Supabase</h4>
                            <p class="text-base text-slate-600 leading-relaxed font-medium">Autenticación Stateless delegada a Supabase Auth. Validación rigurosa de firmas JWT (Algoritmo ES256) y RBAC.</p>
                        </div>

                        <!-- Módulo 4 -->
                        <div class="p-6 group hover:-translate-y-1 transition-transform duration-300">
                            <div class="text-blue-600 mb-6 w-14 h-14 flex items-center justify-center rounded-xl bg-slate-50 group-hover:bg-blue-600 group-hover:text-white transition-colors duration-300">
                                <i class="fa-solid fa-vial-circle-check text-2xl"></i>
                            </div>
                            <h4 class="text-slate-900 font-bold mb-3 text-xl tracking-tight">Calidad de Software</h4>
                            <p class="text-base text-slate-600 leading-relaxed font-medium">Validado al 100%. Suite E2E y Pruebas Unitarias. Validaciones estrictas Pydantic v2 sobre 35 Endpoints aislados.</p>
                        </div>
                    </div>

                    <!-- Botón de Acceso -->
                    <div class="py-12 flex flex-col md:flex-row items-center justify-between gap-8 mb-20 border-t border-slate-100">
                        <div class="text-center md:text-left max-w-3xl">
                            <h3 class="text-3xl font-extrabold text-slate-900 mb-3 tracking-tight">Portal para Desarrolladores</h3>
                            <p class="text-slate-600 text-lg mb-0 font-medium leading-relaxed">Accede a la especificación OpenAPI (Swagger UI). Podrás interactuar con los endpoints, leer los esquemas de la Base de Datos e inyectar tokens para pruebas de concepto.</p>
                        </div>
                        <div class="flex-shrink-0 mt-4 md:mt-0">
                            <a href="/docs" class="inline-flex items-center justify-center gap-3 px-10 py-4 bg-blue-600 hover:bg-blue-700 text-white text-lg font-bold rounded-xl transition-all duration-200 hover:-translate-y-1 shadow-md hover:shadow-lg shadow-blue-600/20">
                                <i class="fa-solid fa-code text-xl"></i>
                                Abrir Swagger UI
                            </a>
                        </div>
                    </div>

                    <!-- Formato Cédula Catastral -->
                    <div class="py-12 flex flex-col md:flex-row items-center justify-between gap-8 mb-20 border-t border-slate-100">
                        <div class="text-center md:text-left max-w-3xl">
                            <h3 class="text-3xl font-extrabold text-slate-900 mb-3 tracking-tight">Formato de Cédula Catastral</h3>
                            <p class="text-slate-600 text-lg mb-0 font-medium leading-relaxed">Descarga el formato oficial de la Cédula Catastral en PDF, completamente en blanco (sin datos de inmueble ni propietario), listo para impresión o llenado manual.</p>
                        </div>
                        <div class="flex-shrink-0 mt-4 md:mt-0">
                            <a href="/cedula-formato-vacio" class="inline-flex items-center justify-center gap-3 px-10 py-4 bg-white hover:bg-slate-50 text-blue-600 border-2 border-blue-600 text-lg font-bold rounded-xl transition-all duration-200 hover:-translate-y-1 shadow-md hover:shadow-lg shadow-blue-600/10">
                                <i class="fa-solid fa-file-pdf text-xl"></i>
                                Generar Cédula Catastral sin datos
                            </a>
                        </div>
                    </div>

                    <!-- Stack Tecnológico -->
                    <div class="pt-16 pb-16 text-center border-t border-slate-100 flex justify-center">
                        <img src="/static/logos/bannerabajo.jpg" alt="Stack Tecnológico" class="w-full max-w-[1400px] h-auto object-contain">
                    </div>

                </div>
            </div>
        </main>

        <!-- Footer -->
        <footer class="py-8 mt-auto border-t border-slate-100">
            <div class="max-w-[1600px] mx-auto px-6 text-center text-sm text-slate-500 font-semibold tracking-wide">
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


@app.get("/cedula-formato-vacio", tags=["Salud"])
def cedula_formato_vacio():
    """Genera y descarga el PDF del formato de Cédula Catastral SIN datos (en blanco)."""
    pdf_bytes = generar_pdf_formato_vacio()
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="Formato_Cedula_Catastral_SIN_DATOS.pdf"'
        },
    )
