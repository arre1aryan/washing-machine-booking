from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.schemas.booking import BookingCreate, BookingResponse
from app.api.dependencies import get_current_user
from app.services.booking_service import (
    create_booking,
    get_user_bookings,
    get_booked_slot_ids,
    cancel_booking,
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
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        user_id = UUID(current_user["id"])
        return create_booking(db, booking_data, user_id)

    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@app.get("/bookings/slots")
def get_booked_slots(
    slot_ids: list[UUID] = Query(...),
    db: Session = Depends(get_db),
):
    return get_booked_slot_ids(db, slot_ids)


@app.get("/bookings/me", response_model=list[BookingResponse])
def list_my_bookings(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = UUID(current_user["id"])
    return get_user_bookings(db, user_id)


@app.patch(
    "/bookings/{booking_id}/cancel",
    response_model=BookingResponse,
)
def cancel_booking_endpoint(
    booking_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return cancel_booking(
            db,
            booking_id,
            UUID(current_user["id"]),
        )

    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))