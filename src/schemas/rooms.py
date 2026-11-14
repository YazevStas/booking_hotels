from pydantic import BaseModel, ConfigDict

from src.schemas.facilities import Facility


class RoomAddRequest(BaseModel):
    price: int
    description: str | None = None
    quantity: int
    title: str
    facilities_ids: list[int] = []

class RoomAdd(BaseModel):
    hotel_id: int
    price: int
    description: str | None = None
    quantity: int
    title: str


class Room(RoomAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)

class RoomWithRels(Room):
    facilities: list[Facility]

class RoomPatchRequest(BaseModel):
    price: int | None = None
    description: str | None = None
    quantity: int | None = None
    title: str | None = None
    facilities_ids: list[int] = []


class RoomPatch(BaseModel):
    hotel_id: int | None = None
    price: int | None = None
    description: str | None = None
    quantity: int | None = None
    title: str | None = None
    