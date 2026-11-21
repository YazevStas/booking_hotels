from datetime import date

from src.exception import (
    ObjectNotFoundException,
    RoomNotFoundException,
    date_to_after_date_from,
)
from src.schemas.facilities import RoomFacilityAdd
from src.schemas.rooms import Room, RoomAdd, RoomAddRequest, RoomPatch, RoomPatchRequest, RoomWithRels
from src.services.base import BaseService
from src.services.hotels import HotelService


class RoomService(BaseService):
    async def get_filtered_by_time(
        self,
        hotel_id: int,
        date_from: date,
        date_to: date,
    ) -> list[RoomWithRels]:
        date_to_after_date_from(date_from, date_to)
        return await self.db.rooms.get_filtered_by_time(hotel_id=hotel_id, date_from=date_from, date_to=date_to)

    async def get_room(self, hotel_id: int, room_id: int) -> RoomWithRels:
        return await self.db.rooms.get_one_with_rels(id=room_id, hotel_id=hotel_id)

    async def add_room(self, hotel_id: int, data: RoomAddRequest) -> Room:
        await HotelService(self.db).check_hotel_exists(hotel_id)
        _room_data = RoomAdd(hotel_id=hotel_id, **data.model_dump())
        room = await self.db.rooms.add(_room_data)
        rooms_facilities_data = [RoomFacilityAdd(room_id=room.id, facility_id=f_id) for f_id in data.facilities_ids]
        if rooms_facilities_data:
            await self.db.rooms_facilities.add_bulk(rooms_facilities_data)
        await self.db.commit()
        return room

    async def edit_room(self, hotel_id: int, room_id: int, data: RoomAddRequest) -> None:
        await HotelService(self.db).check_hotel_exists(hotel_id)
        await self.check_room_exists(hotel_id, room_id)
        _room_data = RoomAdd(hotel_id=hotel_id, **data.model_dump())
        await self.db.rooms.edit(_room_data, id=room_id)
        await self.db.rooms_facilities.set_room_facilities(room_id=room_id, facilities_ids=data.facilities_ids)
        await self.db.commit()

    async def edit_room_partially(self, hotel_id: int, room_id: int, data: RoomPatchRequest) -> None:
        await HotelService(self.db).check_hotel_exists(hotel_id)
        await self.check_room_exists(hotel_id, room_id)
        _room_data_dict = data.model_dump(exclude_unset=True)
        _room_data = RoomPatch(hotel_id=hotel_id, **_room_data_dict)
        await self.db.rooms.edit(_room_data, exclude_unset=True, id=room_id, hotel_id=hotel_id)
        if "facilities_ids" in _room_data_dict:
            await self.db.rooms_facilities.set_room_facilities(
                room_id=room_id, facilities_ids=_room_data_dict["facilities_ids"]
            )
        await self.db.commit()

    async def delete_room(self, hotel_id: int, room_id: int) -> None:
        await HotelService(self.db).check_hotel_exists(hotel_id)
        await self.check_room_exists(hotel_id, room_id)
        await self.db.rooms_facilities.delete(room_id=room_id)
        await self.db.rooms.delete(id=room_id, hotel_id=hotel_id)
        await self.db.commit()

    async def check_room_exists(self, hotel_id: int, room_id: int) -> None:
        try:
            await self.db.rooms.get_one(id=room_id, hotel_id=hotel_id)
        except ObjectNotFoundException:
            raise RoomNotFoundException from None
