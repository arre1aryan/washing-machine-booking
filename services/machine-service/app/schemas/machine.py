from uuid import UUID

from pydantic import BaseModel


class MachineCreate(BaseModel):
    name: str
    location: str


class MachineResponse(BaseModel):
    id: UUID
    name: str
    location: str
    is_active: bool