from fastapi import APIRouter, Response

from src.api.dependencies import DBDep, UserIdDep
from src.exception import (
    IncorrectPasswordException,
    IncorrectPasswordHTTPException,
    UserAlreadyExistsException,
    UserAlreadyExistsHTTPException,
    UserEmailNotRegisteredException,
    UserEmailNotRegisteredHTTPException,
)
from src.schemas.users import User, UserRequestAdd
from src.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


@router.post("/register")
async def register_user(
    data: UserRequestAdd,
    db: DBDep,
):
    try:
        await AuthService(db).register_user(data)
    except UserAlreadyExistsException:
        raise UserAlreadyExistsHTTPException from None
    return {"status": "OK"}


@router.post("/login")
async def login_user(
    data: UserRequestAdd,
    response: Response,
    db: DBDep,
):
    try:
        access_token = await AuthService(db).login_user(data)
    except UserEmailNotRegisteredException:
        raise UserEmailNotRegisteredHTTPException from None
    except IncorrectPasswordException:
        raise IncorrectPasswordHTTPException from None
    response.set_cookie("access_token", access_token)
    return {"access_token": access_token}


@router.get("/me")
async def get_me(
    user_id: UserIdDep,
    db: DBDep,
) -> User | None:
    return await AuthService(db).get_me(user_id)


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"status": "OK"}
