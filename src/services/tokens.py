from datetime import UTC, datetime, timedelta

import jwt

from src.config import settings
from src.exception import IncorrectTokenException


class TokenService:
    """Работа с JWT. База данных не нужна, поэтому не наследуется от BaseService."""

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode |= {"exp": expire}
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        except jwt.exceptions.InvalidTokenError:
            raise IncorrectTokenException from None
