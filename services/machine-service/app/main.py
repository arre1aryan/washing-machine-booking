from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from datetime import date
from uuid import UUID

from app.schemas.slot import SlotResponse
from app.services.slot_service import (
    generate_daily_slots,
    get_slots_for_machine,
    get_slot_by_id,
)

from app.core.database import SessionLocal
from app.schemas.machine import MachineCreate, MachineResponse
from app.services.machine_service import (
    create_machine,
    get_machines,
    set_machine_status,
)


app = FastAPI(title="Machine Service")


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.post("/machines", response_model=MachineResponse, status_code=201)
def create_machine_endpoint(
    machine_data: MachineCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_machine(db, machine_data)
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )


@app.get("/machines", response_model=list[MachineResponse])
def list_machines(db: Session = Depends(get_db)):
    return get_machines(db)

@app.post(
    "/machines/{machine_id}/slots/generate",
    response_model=list[SlotResponse],
)
def generate_slots(
    machine_id: UUID,
    date: date,
    db: Session = Depends(get_db),
):
    try:
        return generate_daily_slots(db, machine_id, date)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@app.get(
    "/machines/{machine_id}/slots",
    response_model=list[SlotResponse],
)
def get_machine_slots(
    machine_id: UUID,
    date: date,
    db: Session = Depends(get_db),
):
    try:
        return get_slots_for_machine(db, machine_id, date)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@app.get("/slots/{slot_id}", response_model=SlotResponse)
def get_slot(slot_id: UUID, db: Session = Depends(get_db)):
    try:
        return get_slot_by_id(db, slot_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.patch("/machines/{machine_id}/status", response_model=MachineResponse)
def update_machine_status(
    machine_id: UUID,
    is_active: bool,
    db: Session = Depends(get_db),
):
    try:
        return set_machine_status(
            db,
            machine_id,
            is_active,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )