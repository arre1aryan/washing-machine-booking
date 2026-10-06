from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.schemas.booking import BookingCreate, BookingResponse
from app.services.booking_service import (
    create_booking,
    get_user_bookings,
    get_booked_slot_ids,
)


app = FastAPI(title="Booking Service")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/bookings", response_model=BookingResponse, status_code=201)
def create_booking_endpoint(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_booking(db, booking_data)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@app.get("/bookings/slots")
def get_booked_slots(
    slot_ids: list[UUID] = Query(...),
    db: Session = Depends(get_db),
):
    return get_booked_slot_ids(db, slot_ids)


@app.get("/bookings/{user_id}", response_model=list[BookingResponse])
def list_user_bookings(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    return get_user_bookings(db, user_id)