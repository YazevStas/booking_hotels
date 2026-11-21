from src.exception import ObjectNotFoundException, RoomNotFoundException, date_to_after_date_from
from src.schemas.bookings import Booking, BookingAdd, BookingAddRequest
from src.services.base import BaseService


class BookingService(BaseService):
    async def get_bookings(self) -> list[Booking]:
        return await self.db.bookings.get_all()

    async def get_my_bookings(self, user_id: int) -> list[Booking]:
        return await self.db.bookings.get_filtered(user_id=user_id)

    async def add_booking(self, user_id: int, data: BookingAddRequest) -> Booking:
        date_to_after_date_from(data.date_from, data.date_to)
        try:
            room = await self.db.rooms.get_one(id=data.room_id)
        except ObjectNotFoundException:
            raise RoomNotFoundException from None
        _booking_data = BookingAdd(
            user_id=user_id,
            **data.model_dump(),
            price=room.price,
        )
        booking = await self.db.bookings.add_booking(_booking_data, hotel_id=room.hotel_id)
        await self.db.commit()
        return booking
