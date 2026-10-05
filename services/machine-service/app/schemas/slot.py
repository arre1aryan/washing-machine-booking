from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SlotResponse(BaseModel):
    id: UUID
    machine_id: UUID
    slot_start_time: datetime
    slot_end_time: datetime
    status: str