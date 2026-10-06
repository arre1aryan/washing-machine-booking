import httpx

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from uuid import UUID

from app.models.booking import Booking
from app.schemas.booking import BookingCreate
from app.core.config import settings


def create_booking(db: Session, booking_data: BookingCreate) -> Booking:
    existing_booking = db.scalar(
        select(Booking).where(
            Booking.slot_id == booking_data.slot_id,
            Booking.status == "confirmed",
        )
    )

    if existing_booking:
        raise ValueError("Slot is already booked")

    slot = get_slot_details(booking_data.slot_id)

    requested_start = slot["slot_start_time"]
    requested_end = slot["slot_end_time"]

    user_bookings = db.scalars(
        select(Booking).where(
            Booking.user_id == booking_data.user_id,
            Booking.status == "confirmed",
        )
    ).all()

    for existing in user_bookings:
        existing_slot = get_slot_details(existing.slot_id)

        if (
            existing_slot["slot_end_time"] == requested_start
            or existing_slot["slot_start_time"] == requested_end
        ):
            raise ValueError(
                "You cannot book consecutive slots"
            )

    booking = Booking(
        user_id=booking_data.user_id,
        slot_id=booking_data.slot_id,
        status="confirmed",
    )

    db.add(booking)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("Slot is already booked")
    
    db.refresh(booking)

    return booking

def get_slot_details(slot_id):
    response = httpx.get(
        f"{settings.machine_service_url}/slots/{slot_id}"
    )

    if response.status_code == 404:
        raise ValueError("Slot not found")

    if response.status_code != 200:
        raise ValueError("Machine Service unavailable")

    return response.json()

def get_user_bookings(db: Session, user_id) -> list[Booking]:
    return db.scalars(
        select(Booking).where(
            Booking.user_id == user_id,
            Booking.status == "confirmed",
        ).order_by(Booking.created_at.desc())
    ).all()


def get_booked_slot_ids(
    db: Session,
    slot_ids: list[UUID],
) -> list[UUID]:
    return db.scalars(
        select(Booking.slot_id).where(
            Booking.slot_id.in_(slot_ids),
            Booking.status == "confirmed",
        )
    ).all()