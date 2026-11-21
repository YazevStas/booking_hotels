from passlib.context import CryptContext

from src.exception import (
    IncorrectPasswordException,
    ObjectAlreadyExists,
    UserAlreadyExistsException,
    UserEmailNotRegisteredException,
)
from src.schemas.users import User, UserAdd, UserRequestAdd
from src.services.base import BaseService
from src.services.tokens import TokenService


class AuthService(BaseService):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    async def register_user(self, data: UserRequestAdd) -> None:
        hashed_password = self.hash_password(data.password)
        new_user_data = UserAdd(email=data.email, hashed_password=hashed_password)
        try:
            await self.db.users.add(new_user_data)
        except ObjectAlreadyExists:
            raise UserAlreadyExistsException from None
        await self.db.commit()

    async def login_user(self, data: UserRequestAdd) -> str:
        user = await self.db.users.get_user_with_hashed_password(email=data.email)
        if not user:
            raise UserEmailNotRegisteredException
        if not self.verify_password(data.password, user.hashed_password):
            raise IncorrectPasswordException
        return TokenService().create_access_token({"user_id": user.id})

    async def get_me(self, user_id: int) -> User | None:
        return await self.db.users.get_one_or_none(id=user_id)
