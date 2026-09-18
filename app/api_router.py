from fastapi import APIRouter

from app.routers import catastro, configuracion, inmuebles, propietarios, usuarios

api_router = APIRouter()
api_router.include_router(inmuebles.router)
api_router.include_router(propietarios.router)
api_router.include_router(catastro.router)
api_router.include_router(configuracion.router)
api_router.include_router(usuarios.router)
