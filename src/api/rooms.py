from datetime import date

from fastapi import APIRouter, Body, Query

from src.api.dependencies import DBDep
from src.exception import (
    HotelNotFoundException,
    HotelNotFoundHTTPException,
    IncorrectDatesException,
    IncorrectDatesHTTPException,
    RoomNotFoundException,
    RoomNotFoundHTTPException,
)
from src.schemas.rooms import RoomAddRequest, RoomPatchRequest, RoomWithRels
from src.services.rooms import RoomService

router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get("/{hotel_id}/rooms")
async def get_rooms(
    hotel_id: int,
    db: DBDep,
    date_from: date = Query(openapi_examples={"example": {"value": "2024-08-01"}}),
    date_to: date = Query(openapi_examples={"example": {"value": "2024-08-10"}})
) -> list[RoomWithRels]:
    try:
        return await RoomService(db).get_filtered_by_time(hotel_id=hotel_id, date_from=date_from, date_to=date_to)
    except IncorrectDatesException:
        raise IncorrectDatesHTTPException from None


@router.get("/{hotel_id}/rooms/{room_id}")
async def get_room(
    hotel_id: int,
    room_id: int,
    db: DBDep
) -> RoomWithRels:
    try:
        return await RoomService(db).get_room(hotel_id, room_id)
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException from None


@router.post("/{hotel_id}/rooms")
async def create_room(
    hotel_id: int,
    db: DBDep,
    room_data: RoomAddRequest = Body()
):
    try:
        room = await RoomService(db).add_room(hotel_id, room_data)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException from None
    return {"status": "OK", "data": room}


@router.put("/{hotel_id}/rooms/{room_id}")
async def edit_room(
        hotel_id: int,
        room_id: int,
        room_data: RoomAddRequest,
        db: DBDep,
):
    await RoomService(db).edit_room(hotel_id, room_id, room_data)
    return {"status": "OK"}


@router.patch("/{hotel_id}/rooms/{room_id}")
async def partially_edit_room(
        hotel_id: int,
        room_id: int,
        room_data: RoomPatchRequest,
        db: DBDep,
):
    await RoomService(db).edit_room_partially(hotel_id, room_id, room_data)
    return {"status": "OK"}


@router.delete("/{hotel_id}/rooms/{room_id}")
async def delete_room(
    hotel_id: int,
    room_id: int,
    db: DBDep
):
    await RoomService(db).delete_room(hotel_id, room_id)
    return {"status": "OK"}
