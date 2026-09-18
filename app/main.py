import logging

from fastapi import FastAPI, HTTPException, status
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


@app.get("/", tags=["Salud"])
def raiz():
    return {
        "servicio": settings.APP_NAME,
        "estado": "activo",
        "documentacion": "/docs",
    }


@app.get("/salud", tags=["Salud"])
def salud():
    """Endpoint simple de health-check (útil para Render/Railway/Fly.io)."""
    return {"status": "ok"}
