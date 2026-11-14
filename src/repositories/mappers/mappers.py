from src.models.bookings import BookingsORM
from src.models.facilities import FacilitiesORM, RoomsFacilitiesORM
from src.models.hotels import HotelsORM
from src.models.rooms import RoomsORM
from src.models.users import UsersORM
from src.repositories.mappers.base import DataMapper
from src.schemas.bookings import Booking
from src.schemas.facilities import Facility, RoomFacility
from src.schemas.hotels import Hotel
from src.schemas.rooms import Room, RoomWithRels
from src.schemas.users import User


class HotelDataMapper(DataMapper[HotelsORM, Hotel]):
    db_model = HotelsORM
    schema = Hotel

class RoomDataMapper(DataMapper[RoomsORM, Room]):
    db_model = RoomsORM
    schema = Room

class RoomDataWithRelsMapper(DataMapper[RoomsORM, RoomWithRels]):
    db_model = RoomsORM
    schema = RoomWithRels

class UserDataMapper(DataMapper[UsersORM, User]):
    db_model = UsersORM
    schema = User

class BookingDataMapper(DataMapper[BookingsORM, Booking]):
    db_model = BookingsORM
    schema = Booking

class FacilityDataMapper(DataMapper[FacilitiesORM, Facility]):
    db_model = FacilitiesORM
    schema = Facility

class RoomFacilityDataMapper(DataMapper[RoomsFacilitiesORM, RoomFacility]):
    db_model = RoomsFacilitiesORM
    schema = RoomFacility