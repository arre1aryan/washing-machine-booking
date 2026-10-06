import httpx
from fastapi import FastAPI, HTTPException

from datetime import date
from uuid import UUID

from app.config import MACHINE_SERVICE_URL, BOOKING_SERVICE_URL



app = FastAPI(title="API Gateway")


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

    return [
        {
            **slot,
            "available": slot["id"] not in booked_slot_ids,
        }
        for slot in slots
    ]