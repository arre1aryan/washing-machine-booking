import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Index, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class Booking(Base):
    __tablename__ = "bookings"

    __table_args__ = (
    Index(
        "uq_booking_confirmed_slot",
        "slot_id",
        unique=True,
        postgresql_where=text("status = 'confirmed'"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        nullable=False,
    )

    slot_id: Mapped[uuid.UUID] = mapped_column(
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="confirmed",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )