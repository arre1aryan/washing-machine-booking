import httpx

from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from datetime import date
from uuid import UUID

from app.config import MACHINE_SERVICE_URL, BOOKING_SERVICE_URL
from app.api.dependencies import (
    get_current_user,
    get_current_admin,
)

from app.core.cache import (
    availability_cache_key,
    get_availability_version,
    get_cached_availability,
    set_cached_availability,
)

from app.core.rate_limiter import check_booking_rate_limit


app = FastAPI(title="API Gateway")

security = HTTPBearer()

class BookingRequest(BaseModel):
    slot_id: UUID

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/machines")
def get_machines():
    try:
        response = httpx.get(
            f"{MACHINE_SERVICE_URL}/machines",
            timeout=5.0,
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Machine Service unavailable",
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Machine Service request failed",
        )

    return response.json()


@app.get("/availability")
def get_availability(
    machine_id: UUID,
    date: date,
):
    version = get_availability_version(machine_id)

    cache_key = None

    if version is not None:
        cache_key = availability_cache_key(
            machine_id,
            date.isoformat(),
            version,
        )

        cached = get_cached_availability(cache_key)

        if cached is not None:
            return cached
    try:
        slots_response = httpx.get(
            f"{MACHINE_SERVICE_URL}/machines/{machine_id}/slots",
            params={"date": date.isoformat()},
            timeout=5.0,
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Machine Service unavailable",
        )

    if slots_response.status_code != 200:
        raise HTTPException(
            status_code=slots_response.status_code,
            detail="Machine Service request failed",
        )

    slots = slots_response.json()

    if not slots:
        return []

    slot_ids = [slot["id"] for slot in slots]

    try:
        booked_response = httpx.get(
            f"{BOOKING_SERVICE_URL}/bookings/slots",
            params=[("slot_ids", slot_id) for slot_id in slot_ids],
            timeout=5.0,
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Booking Service unavailable",
        )

    if booked_response.status_code != 200:
        raise HTTPException(
            status_code=booked_response.status_code,
            detail="Booking Service request failed",
        )

    booked_slot_ids = set(booked_response.json())

    availability = [
        {
            **slot,
            "available": slot["id"] not in booked_slot_ids,
        }
        for slot in slots
    ]

    # Cache writes will be enabled after invalidation is integrated.
    # set_cached_availability(cache_key, availability)

    if cache_key is not None:
        latest_version = get_availability_version(machine_id)

        if latest_version == version:
            set_cached_availability(cache_key, availability)

    return availability

@app.post("/bookings", status_code=201)
def create_booking(
    booking_data: BookingRequest,
    current_user: dict = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    check_booking_rate_limit(current_user["id"])

    payload = {
        "slot_id": str(booking_data.slot_id),
    }

    try:
        response = httpx.post(
            f"{BOOKING_SERVICE_URL}/bookings",
            json=payload,
            headers={
                "Authorization": f"Bearer {credentials.credentials}",
            },
            timeout=5.0,
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Booking Service unavailable",
        )

    if response.status_code != 201:
        try:
            detail = response.json().get(
                "detail",
                "Booking Service request failed",
            )
        except ValueError:
            detail = "Booking Service request failed"

        raise HTTPException(
            status_code=response.status_code,
            detail=detail,
        )

    return response.json()


@app.get("/bookings/me")
def get_my_bookings(
    current_user: dict = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        response = httpx.get(
            f"{BOOKING_SERVICE_URL}/bookings/me",
            headers={
                "Authorization": f"Bearer {credentials.credentials}",
            },
            timeout=5.0,
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Booking Service unavailable",
        )

    if response.status_code != 200:
        try:
            detail = response.json().get(
                "detail",
                "Booking Service request failed",
            )
        except ValueError:
            detail = "Booking Service request failed"

        raise HTTPException(
            status_code=response.status_code,
            detail=detail,
        )

    return response.json()


@app.patch("/admin/machines/{machine_id}/status")
def update_machine_status(
    machine_id: UUID,
    is_active: bool,
    current_admin: dict = Depends(get_current_admin),
):
    try:
        response = httpx.patch(
            f"{MACHINE_SERVICE_URL}/machines/{machine_id}/status",
            params={"is_active": is_active},
            timeout=5.0,
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Machine Service unavailable",
        )

    if response.status_code != 200:
        try:
            detail = response.json().get(
                "detail",
                "Machine Service request failed",
            )
        except ValueError:
            detail = "Machine Service request failed"

        raise HTTPException(
            status_code=response.status_code,
            detail=detail,
        )

    return response.json()


@app.patch("/bookings/{booking_id}/cancel")
def cancel_my_booking(
    booking_id: UUID,
    current_user: dict = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        response = httpx.patch(
            f"{BOOKING_SERVICE_URL}/bookings/{booking_id}/cancel",
            headers={
                "Authorization": f"Bearer {credentials.credentials}",
            },
            timeout=5.0,
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Booking Service unavailable",
        )

    if response.status_code != 200:
        try:
            detail = response.json().get(
                "detail",
                "Booking cancellation failed",
            )
        except ValueError:
            detail = "Booking cancellation failed"

        raise HTTPException(
            status_code=response.status_code,
            detail=detail,
        )

    return response.json()