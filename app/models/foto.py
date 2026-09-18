import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class FotoInmueble(Base):
    __tablename__ = "fotos_inmueble"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    inmueble_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("inmuebles.id", ondelete="CASCADE")
    )
    url: Mapped[str] = mapped_column(String, nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    inmueble: Mapped["Inmueble"] = relationship(back_populates="fotos")  # noqa: F821
