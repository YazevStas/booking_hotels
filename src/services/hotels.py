from datetime import date

from src.api.dependencies import PaginationParams
from src.exception import HotelNotFoundException, ObjectNotFoundException, date_to_after_date_from
from src.schemas.hotels import Hotel, HotelAdd, HotelPatch
from src.services.base import BaseService


class HotelService(BaseService):

    async def get_filtered_by_time(
            self,
            pagination: PaginationParams,
            location: str | None,
            title: str | None,
            date_from: date,
            date_to: date,
    ) -> list[Hotel]:
        date_to_after_date_from(date_from, date_to)
        per_page = pagination.per_page or 5
        return await self.db.hotels.get_filtered_by_time(
            date_from=date_from,
            date_to=date_to,
            location=location,
            title=title,
            limit=per_page,
            offset=per_page * (pagination.page - 1),
        )

    async def get_hotel(self, hotel_id: int) -> Hotel:
        return await self.db.hotels.get_one(id=hotel_id)

    async def add_hotel(self, data: HotelAdd) -> Hotel:
        hotel = await self.db.hotels.add(data)
        await self.db.commit()
        return hotel

    async def edit_hotel(self, hotel_id: int, data: HotelAdd) -> None:
        await self.db.hotels.edit(data, id=hotel_id)
        await self.db.commit()

    async def edit_hotel_partially(self, hotel_id: int, data: HotelPatch) -> None:
        await self.db.hotels.edit(data, exclude_unset=True, id=hotel_id)
        await self.db.commit()

    async def delete_hotel(self, hotel_id: int) -> None:
        await self.db.hotels.delete(id=hotel_id)
        await self.db.commit()

    async def check_hotel_exists(self, hotel_id: int) -> None:
        try:
            await self.db.hotels.get_one(id=hotel_id)
        except ObjectNotFoundException:
            raise HotelNotFoundException from None