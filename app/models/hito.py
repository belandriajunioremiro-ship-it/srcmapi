import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class HitoPredial(Base):
    """Vértices GPS del polígono de un inmueble (linderos en campo)."""

    __tablename__ = "hitos_prediales"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    inmueble_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("inmuebles.id", ondelete="CASCADE")
    )
    indice_vertice: Mapped[int] = mapped_column(Integer, nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String)
    lat: Mapped[float] = mapped_column(Numeric(10, 7), nullable=False)
    lon: Mapped[float] = mapped_column(Numeric(10, 7), nullable=False)
    # Calculados por el trigger antes_de_guardar_hito (ST_Transform a REGVEN)
    utm_norte: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    utm_este: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    foto_url: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    inmueble: Mapped["Inmueble"] = relationship(back_populates="hitos")  # noqa: F821
