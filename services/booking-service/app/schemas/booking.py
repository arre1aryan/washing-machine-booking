from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class BookingCreate(BaseModel):
    user_id: UUID
    slot_id: UUID


class BookingResponse(BaseModel):
    id: UUID
    user_id: UUID
    slot_id: UUID
    status: str
    created_at: datetime