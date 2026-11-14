from datetime import date

from fastapi import HTTPException


class BronirovalException(Exception):
    detail = "Какая-то ошибка"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)

class ObjectNotFoundException(BronirovalException):
    detail = "Объект не найден"

class HotelNotFoundException(ObjectNotFoundException):
    detail = "Отель не найден"

class RoomNotFoundException(ObjectNotFoundException):
    detail = "Номер не найден"

class AllRoomsBookedException(BronirovalException):
    detail = "Нет свободных номеров"

class ObjectAlreadyExists(BronirovalException):
    detail = "Похожий объект уже существует"

class UserAlreadyExistsException(ObjectAlreadyExists):
    detail = "Пользователь с такой почтой уже существует"

class UserEmailNotRegisteredException(BronirovalException):
    detail = "Пользователь с таким email не зарегистрирован"

class IncorrectPasswordException(BronirovalException):
    detail = "Пароль неверный"

class IncorrectTokenException(BronirovalException):
    detail = "Неверный токен"

class IncorrectDatesException(BronirovalException):
    detail = "Дата заезда не может быть позже даты выезда"


def date_to_after_date_from(date_from: date, date_to: date) -> None:
    if date_from >= date_to:
        raise IncorrectDatesException

class BronirovalHTTPException(HTTPException):
    status_code = 500
    detail = None

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)

class HotelNotFoundHTTPException(BronirovalHTTPException):
    status_code = 404
    detail = "Отель не найден"

class RoomNotFoundHTTPException(BronirovalHTTPException):
    status_code = 404
    detail = "Номер не найден"

class AllRoomsBookedHTTPException(BronirovalHTTPException):
    status_code = 409
    detail = "Нет свободных номеров"

class UserAlreadyExistsHTTPException(BronirovalHTTPException):
    status_code = 409
    detail = "Пользователь с такой почтой уже существует"

class UserEmailNotRegisteredHTTPException(BronirovalHTTPException):
    status_code = 401
    detail = "Пользователь с таким email не зарегистрирован"

class IncorrectPasswordHTTPException(BronirovalHTTPException):
    status_code = 401
    detail = "Пароль неверный"

class IncorrectTokenHTTPException(BronirovalHTTPException):
    status_code = 401
    detail = "Неверный токен"

class NoAccessTokenHTTPException(BronirovalHTTPException):
    status_code = 401
    detail = "Вы не предоставили токен доступа"

class IncorrectDatesHTTPException(BronirovalHTTPException):
    status_code = 422
    detail = "Дата заезда не может быть позже даты выезда"
