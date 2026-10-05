import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class Slot(Base):
    __tablename__ = "slots"

    __table_args__ = (
        UniqueConstraint(
            "machine_id",
            "slot_start_time",
            name="uq_machine_slot_start",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    machine_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("machines.id"),
        nullable=False,
    )

    slot_start_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    slot_end_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="available",
        nullable=False,
    )