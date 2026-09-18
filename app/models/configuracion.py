from datetime import datetime
from typing import Optional

from sqlalchemy import CHAR, DateTime, Integer, Numeric, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ConfiguracionCatastral(Base):
    """Fila única (id=1) con los parámetros catastrales y valores de m²."""

    __tablename__ = "configuracion_catastral"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, default=1)
    codigo_estado: Mapped[str] = mapped_column(CHAR(2), nullable=False)
    codigo_municipio: Mapped[str] = mapped_column(CHAR(2), nullable=False)
    codigo_parroquia: Mapped[str] = mapped_column(CHAR(2), nullable=False)
    nombre_estado: Mapped[str] = mapped_column(String, nullable=False)
    nombre_municipio: Mapped[str] = mapped_column(String, nullable=False)
    nombre_parroquia: Mapped[str] = mapped_column(String, nullable=False)
    ordenanza_referencia: Mapped[Optional[str]] = mapped_column(String)
    srid_utm: Mapped[int] = mapped_column(Integer, nullable=False)
    valor_m2_terreno: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    valor_m2_construccion: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    valor_m2_comercio: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    alicuota_impuesto: Mapped[float] = mapped_column(Numeric(6, 5), nullable=False)
    vigencia_cedula_meses: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Campos institucionales para cédula catastral (v2.5)
    rif_alcaldia: Mapped[str] = mapped_column(String, nullable=False)
    direccion_institucional: Mapped[str] = mapped_column(String, nullable=False)
    nombre_maxima_autoridad: Mapped[str] = mapped_column(String, nullable=False)
    cargo_maxima_autoridad: Mapped[str] = mapped_column(String, nullable=False)
    texto_acta_maxima_autoridad: Mapped[str] = mapped_column(String, nullable=False)
    nombre_director_catastro: Mapped[str] = mapped_column(String, nullable=False)
    cargo_director_catastro: Mapped[str] = mapped_column(String, nullable=False)
    texto_resolucion_director: Mapped[str] = mapped_column(String, nullable=False)
    notas_legales: Mapped[str] = mapped_column(String, nullable=False)


class ConfiguracionSistema(Base):
    """Fila única (id=1) usada por el trigger de validación del código."""

    __tablename__ = "configuracion_sistema"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    estado_codigo: Mapped[str] = mapped_column(String(2), nullable=False)
    municipio_codigo: Mapped[str] = mapped_column(String(2), nullable=False)
    parroquia_codigo: Mapped[str] = mapped_column(String(2), nullable=False)
    nombre_municipio: Mapped[str] = mapped_column(String, nullable=False)
