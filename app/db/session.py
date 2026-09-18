"""
Motor y sesión de SQLAlchemy contra Supabase (PostgreSQL + PostGIS).

Notas sobre pooling con Supabase:
- Si usas la cadena de conexión "Session" (puerto 5432), el pool normal
  de SQLAlchemy funciona sin problema.
- Si usas "Transaction pooler" (pgbouncer, puerto 6543) — recomendado en
  producción/serverless — hay que deshabilitar el pool de sentencias
  preparadas del lado del driver, por eso se pasa
  `prepare_threshold=None` a psycopg2 vía connect_args cuando aplica.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

_is_pgbouncer = ":6543" in settings.DATABASE_URL

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # evita usar conexiones muertas tras inactividad
    pool_size=5,
    max_overflow=10,
    connect_args={"options": "-c timezone=utc"},
    echo=settings.DEBUG and settings.APP_ENV == "development",
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base declarativa para todos los modelos ORM."""

    pass


def get_db():
    """Dependency de FastAPI: entrega una sesión y la cierra al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
