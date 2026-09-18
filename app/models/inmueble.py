import uuid
from datetime import date, datetime
from typing import Optional

from geoalchemy2 import Geometry
from sqlalchemy import (
    Boolean,
    CHAR,
    Computed,
    Date,
    DateTime,
    FetchedValue,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Inmueble(Base):
    """
    Tabla principal del catastro. Varias columnas son calculadas por
    triggers de PostgreSQL (ver script SQL, sección 11.5
    antes_de_guardar_inmueble) y NO deben enviarse en un INSERT/UPDATE
    desde el backend:

        - codigo_catastral   (generado a partir de sector/manzana/parcela/...)
        - expediente_numero  (autogenerado si viene NULL)
        - vigente_hasta      (calculado desde fecha_emision + vigencia)
        - superficie_gis_m2 / perimetro_gis_m / utm_norte / utm_este
        - valor_terreno / valor_construccion / valor_comercio /
          valor_catastral_total (columnas GENERATED ALWAYS AS ... STORED)

    El backend solo necesita insertar/actualizar `geom` y los campos de
    negocio; después de guardar, se hace `db.refresh(obj)` para traer los
    valores calculados por la BD.
    """

    __tablename__ = "inmuebles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # --- Código catastral (bloques) ---
    sector: Mapped[str] = mapped_column(CHAR(2), nullable=False)
    manzana: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    parcela: Mapped[str] = mapped_column(CHAR(3), nullable=False)
    subparcela: Mapped[str] = mapped_column(CHAR(3), nullable=False, default="000")
    nivel: Mapped[str] = mapped_column(CHAR(3), nullable=False, default="000")
    unidad: Mapped[str] = mapped_column(CHAR(3), nullable=False, default="000")
    codigo_catastral: Mapped[Optional[str]] = mapped_column(
        CHAR(23), unique=True, nullable=True,
        server_default=FetchedValue(),
    )  # calculado por trigger
    expediente_numero: Mapped[Optional[str]] = mapped_column(
        String, nullable=True,
        server_default=FetchedValue(),
    )

    # --- Propietario ---
    propietario_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("propietarios.id", ondelete="RESTRICT")
    )
    propietario: Mapped[Optional["Propietario"]] = relationship(  # noqa: F821
        back_populates="inmuebles"
    )
    direccion: Mapped[str] = mapped_column(String, nullable=False)

    # --- Documento de propiedad ---
    documento_tipo: Mapped[Optional[str]] = mapped_column(String)
    documento_numero: Mapped[Optional[str]] = mapped_column(String)
    documento_tomo: Mapped[Optional[str]] = mapped_column(String)
    documento_folio: Mapped[Optional[str]] = mapped_column(String)
    documento_protocolo: Mapped[Optional[str]] = mapped_column(String)
    documento_fecha: Mapped[Optional[date]] = mapped_column(Date)

    # --- Tenencia ---
    tenencia: Mapped[str] = mapped_column(String, nullable=False, default="propio")
    contrato_arrendamiento_num: Mapped[Optional[str]] = mapped_column(String)
    contrato_arrendamiento_fecha: Mapped[Optional[date]] = mapped_column(Date)

    # --- Linderos según documento ---
    lindero_norte_doc: Mapped[Optional[str]] = mapped_column(String)
    lindero_norte_mts: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    lindero_sur_doc: Mapped[Optional[str]] = mapped_column(String)
    lindero_sur_mts: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    lindero_este_doc: Mapped[Optional[str]] = mapped_column(String)
    lindero_este_mts: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    lindero_oeste_doc: Mapped[Optional[str]] = mapped_column(String)
    lindero_oeste_mts: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))

    # --- Linderos según levantamiento topográfico / GPS ---
    lindero_norte_top: Mapped[Optional[str]] = mapped_column(String)
    lindero_norte_top_mts: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    lindero_sur_top: Mapped[Optional[str]] = mapped_column(String)
    lindero_sur_top_mts: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    lindero_este_top: Mapped[Optional[str]] = mapped_column(String)
    lindero_este_top_mts: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    lindero_oeste_top: Mapped[Optional[str]] = mapped_column(String)
    lindero_oeste_top_mts: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))

    # --- Factibilidad de servicios ---
    aguas_blancas: Mapped[bool] = mapped_column(Boolean, default=False)
    aguas_servidas: Mapped[bool] = mapped_column(Boolean, default=False)
    electricidad: Mapped[bool] = mapped_column(Boolean, default=False)
    contador: Mapped[bool] = mapped_column(Boolean, default=False)

    # --- Vivienda / uso ---
    existe_vivienda: Mapped[bool] = mapped_column(Boolean, default=False)
    tipo_vivienda: Mapped[Optional[str]] = mapped_column(String)
    descripcion_uso: Mapped[str] = mapped_column(String, default="residencial")
    numero_plantas: Mapped[Optional[int]] = mapped_column(Integer)
    uso_segun_zonificacion: Mapped[Optional[str]] = mapped_column(String)

    # --- Áreas y valores unitarios (entrada) ---
    area_terreno_m2: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    valor_unit_terreno: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    area_construccion_m2: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    valor_unit_construccion: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    area_comercio_m2: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    valor_unit_comercio: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))

    # --- Valores calculados (GENERATED ALWAYS AS ... STORED — solo lectura) ---
    # Computed() le dice a SQLAlchemy que NO los incluya en INSERT/UPDATE
    # y los traiga de vuelta vía RETURNING automáticamente.
    valor_terreno: Mapped[Optional[float]] = mapped_column(
        Numeric(18, 2),
        Computed("COALESCE(area_terreno_m2, 0) * COALESCE(valor_unit_terreno, 0)", persisted=True),
    )
    valor_construccion: Mapped[Optional[float]] = mapped_column(
        Numeric(18, 2),
        Computed("COALESCE(area_construccion_m2, 0) * COALESCE(valor_unit_construccion, 0)", persisted=True),
    )
    valor_comercio: Mapped[Optional[float]] = mapped_column(
        Numeric(18, 2),
        Computed("COALESCE(area_comercio_m2, 0) * COALESCE(valor_unit_comercio, 0)", persisted=True),
    )
    valor_catastral_total: Mapped[Optional[float]] = mapped_column(
        Numeric(18, 2),
        Computed(
            "COALESCE(area_terreno_m2, 0) * COALESCE(valor_unit_terreno, 0)"
            " + COALESCE(area_construccion_m2, 0) * COALESCE(valor_unit_construccion, 0)"
            " + COALESCE(area_comercio_m2, 0) * COALESCE(valor_unit_comercio, 0)",
            persisted=True,
        ),
    )

    # --- Características físicas ---
    via_acceso: Mapped[Optional[str]] = mapped_column(String)
    estructura_techo: Mapped[Optional[str]] = mapped_column(String)
    estructura_paredes: Mapped[Optional[str]] = mapped_column(String)
    piso: Mapped[Optional[str]] = mapped_column(String)
    dormitorios: Mapped[Optional[int]] = mapped_column(Integer)
    banos: Mapped[Optional[int]] = mapped_column(Integer)
    sala: Mapped[bool] = mapped_column(Boolean, default=False)
    cocina: Mapped[bool] = mapped_column(Boolean, default=False)
    ambiente_otro: Mapped[Optional[str]] = mapped_column(String)
    caracteristica_general: Mapped[Optional[str]] = mapped_column(String)

    observaciones: Mapped[Optional[str]] = mapped_column(String)

    # --- Geoespacial ---
    # SRID 4326 (lat/lon, WGS84) — igual que la columna `geom` en el script SQL.
    geom = mapped_column(Geometry(geometry_type="POLYGON", srid=4326), nullable=False)
    utm_norte: Mapped[Optional[float]] = mapped_column(
        Numeric(12, 2), server_default=FetchedValue(),
    )
    utm_este: Mapped[Optional[float]] = mapped_column(
        Numeric(12, 2), server_default=FetchedValue(),
    )
    superficie_gis_m2: Mapped[Optional[float]] = mapped_column(
        Numeric(12, 2), server_default=FetchedValue(),
    )
    perimetro_gis_m: Mapped[Optional[float]] = mapped_column(
        Numeric(12, 2), server_default=FetchedValue(),
    )

    registrado_por: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    estado_sync: Mapped[str] = mapped_column(String, default="synced")
    fecha_emision: Mapped[date] = mapped_column(Date, server_default=func.current_date())
    vigente_hasta: Mapped[Optional[date]] = mapped_column(
        Date, server_default=FetchedValue(),
    )

    # Campos para cédula catastral (v2.5)
    fecha_recibo: Mapped[date] = mapped_column(Date, server_default=func.current_date())
    numero_recibo: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    hitos: Mapped[list["HitoPredial"]] = relationship(  # noqa: F821
        back_populates="inmueble", cascade="all, delete-orphan"
    )
    fotos: Mapped[list["FotoInmueble"]] = relationship(  # noqa: F821
        back_populates="inmueble", cascade="all, delete-orphan"
    )

    # NOTA: codigo_catastral, expediente_numero, vigente_hasta,
    # superficie_gis_m2, perimetro_gis_m, utm_norte, utm_este y los 4
    # campos "valor_*" son calculados por triggers/columnas GENERATED
    # de Postgres. Los schemas Pydantic de creación (InmuebleCreate) NO
    # incluyen estos campos, así que SQLAlchemy nunca intenta escribirlos;
    # se leen de vuelta con `db.refresh(obj)` después del INSERT.
