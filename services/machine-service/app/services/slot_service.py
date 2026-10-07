from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.machine import Machine
from app.models.slot import Slot


def generate_daily_slots(
    db: Session,
    machine_id,
    date,
) -> list[Slot]:
    machine = db.scalar(
        select(Machine).where(Machine.id == machine_id)
    )

    if not machine:
        raise ValueError("Machine not found")

    if not machine.is_active:
        raise ValueError("Machine is inactive")

    slots = []

    start_time = datetime.combine(
        date,
        datetime.min.time().replace(hour=8),
    )

    for hour in range(14):
        slot_start = start_time + timedelta(hours=hour)
        slot_end = slot_start + timedelta(hours=1)

        existing_slot = db.scalar(
            select(Slot).where(
                Slot.machine_id == machine_id,
                Slot.slot_start_time == slot_start,
            )
        )

        if existing_slot:
            continue

        slot = Slot(
            machine_id=machine_id,
            slot_start_time=slot_start,
            slot_end_time=slot_end,
            status="available",
        )

        db.add(slot)
        slots.append(slot)

    db.commit()

    for slot in slots:
        db.refresh(slot)

    return slots


def get_slots_for_machine(
    db: Session,
    machine_id,
    date,
) -> list[Slot]:
    machine = db.scalar(
        select(Machine).where(Machine.id == machine_id)
    )

    if not machine:
        raise ValueError("Machine not found")

    start_time = datetime.combine(
        date,
        datetime.min.time(),
    )

    end_time = start_time + timedelta(days=1)

    return db.scalars(
        select(Slot)
        .where(
            Slot.machine_id == machine_id,
            Slot.slot_start_time >= start_time,
            Slot.slot_start_time < end_time,
        )
        .order_by(Slot.slot_start_time)
    ).all()

def get_slot_by_id(db: Session, slot_id) -> Slot:
    slot = db.scalar(
        select(Slot).where(Slot.id == slot_id)
    )

    if not slot:
        raise ValueError("Slot not found")

    machine = db.scalar(
        select(Machine).where(Machine.id == slot.machine_id)
    )

    if not machine:
        raise ValueError("Machine not found")

    if not machine.is_active:
        raise ValueError("Machine is inactive")

    return slot