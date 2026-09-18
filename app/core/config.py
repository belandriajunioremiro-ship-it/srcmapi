"""
Configuración central de la aplicación.

Todos los valores se leen desde variables de entorno (archivo .env en
desarrollo, variables reales de entorno en producción). Nunca se
hardcodean credenciales aquí.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Aplicación ---
    APP_NAME: str = "SRCM API"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # --- Base de datos (Supabase Postgres + PostGIS) ---
    DATABASE_URL: str

    # --- Supabase Auth ---
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_JWT_SECRET: str

    # --- Seguridad propia de la API (si emites tus propios tokens) ---
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    # --- CORS ---
    CORS_ORIGINS: str = "http://localhost:3000"

    # --- Storage ---
    SUPABASE_STORAGE_BUCKET: str = "catastro-archivos"

    # --- Configuración catastral por defecto ---
    # Debe coincidir siempre con las filas de configuracion_catastral /
    # configuracion_sistema en la base de datos. Se usa como respaldo /
    # valor de referencia en el backend (p. ej. para validaciones rápidas
    # sin ir a la BD), pero la fuente de verdad sigue siendo la BD.
    CODIGO_ESTADO: str = "20"
    CODIGO_MUNICIPIO: str = "27"
    CODIGO_PARROQUIA: str = "01"
    SRID_UTM: int = 2201

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> "Settings":
    """Cachea la configuración para no releer el .env en cada request."""
    return Settings()


settings = get_settings()
