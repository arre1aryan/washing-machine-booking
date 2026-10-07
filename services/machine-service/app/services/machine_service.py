from sqlalchemy import select
from sqlalchemy.orm import Session

from uuid import UUID

from app.models.machine import Machine
from app.schemas.machine import MachineCreate


def create_machine(db: Session, machine_data: MachineCreate) -> Machine:
    existing_machine = db.scalar(
        select(Machine).where(Machine.name == machine_data.name)
    )

    if existing_machine:
        raise ValueError("Machine already exists")

    machine = Machine(
        name=machine_data.name,
        location=machine_data.location,
    )

    db.add(machine)
    db.commit()
    db.refresh(machine)

    return machine


def get_machines(db: Session) -> list[Machine]:
    return db.scalars(
        select(Machine).order_by(Machine.name)
    ).all()


def set_machine_status(
    db: Session,
    machine_id: UUID,
    is_active: bool,
) -> Machine:
    machine = db.get(Machine, machine_id)

    if not machine:
        raise ValueError("Machine not found")

    machine.is_active = is_active

    db.commit()
    db.refresh(machine)

    return machine