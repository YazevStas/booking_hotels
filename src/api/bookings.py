from fastapi import APIRouter

from src.api.dependencies import DBDep, UserIdDep
from src.exception import (
    AllRoomsBookedException,
    AllRoomsBookedHTTPException,
    IncorrectDatesException,
    IncorrectDatesHTTPException,
    RoomNotFoundException,
    RoomNotFoundHTTPException,
)
from src.schemas.bookings import Booking, BookingAddRequest
from src.services.bookings import BookingService

router = APIRouter(prefix="/bookings", tags=["Бронирование"])


@router.get("")
async def get_bookings(db: DBDep) -> list[Booking]:
    return await BookingService(db).get_bookings()


@router.get("/me")
async def get_my_bookings(user_id: UserIdDep, db: DBDep) -> list[Booking]:
    return await BookingService(db).get_my_bookings(user_id)


@router.post("")
async def add_booking(user_id: UserIdDep, db: DBDep, booking_data: BookingAddRequest):
    try:
        booking = await BookingService(db).add_booking(user_id, booking_data)
    except IncorrectDatesException:
        raise IncorrectDatesHTTPException from None
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException from None
    except AllRoomsBookedException:
        raise AllRoomsBookedHTTPException from None

    return {"status": "OK", "data": booking}
