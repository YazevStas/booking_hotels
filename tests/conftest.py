# ruff: noqa: E402
import json
from unittest import mock

import pytest
from httpx import ASGITransport, AsyncClient


def empty_cache(*args, **kwargs):
    def wrapper(func):
        return func
    return wrapper

mock.patch("fastapi_cache.decorator.cache", empty_cache).start()

from src.api.dependencies import get_db
from src.config import settings
from src.database import Base, async_session_maker_null_pool, engine_null_pool
from src.main import app
from src.schemas.hotels import HotelAdd
from src.schemas.rooms import RoomAdd
from src.utils.db_manager import DBManager


@pytest.fixture(scope="session", autouse=True)
def check_mode():
    assert settings.MODE == "TEST"

async def get_db_null_pool():
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        yield db

@pytest.fixture(scope="function", autouse=True)
async def db():
    async for db in get_db_null_pool():
        yield db

app.dependency_overrides[get_db] = get_db_null_pool

@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_mode):
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    with open("tests/mock_hotels.json") as file_hotels:
        hotels_json = json.load(file_hotels)
    with open("tests/mock_rooms.json") as file_rooms:
        rooms_json = json.load(file_rooms)

    hotels = [HotelAdd.model_validate(hotel) for hotel in hotels_json]
    rooms = [RoomAdd.model_validate(room) for room in rooms_json]

    async with DBManager(session_factory=async_session_maker_null_pool) as db_:
        await db_.hotels.add_bulk(hotels)
        await db_.rooms.add_bulk(rooms)
        await db_.commit()

@pytest.fixture(scope="session")
async def ac():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as ac:
        yield ac

@pytest.fixture(scope="session", autouse=True)
async def register_user(setup_database, ac):
    await ac.post(
        "auth/register",
        json={
            "email": "kot@pes.ru",
            "password": "1234"
        }
    )

@pytest.fixture(scope="session")
async def authenticated_ac(register_user, ac):
    await ac.post(
        "auth/login",
        json={
            "email": "kot@pes.ru",
            "password": "1234"
        }
    )
    assert ac.cookies["access_token"]
    yield ac

@pytest.fixture(scope="module")
async def delete_all_bookings():
    async for _db in get_db_null_pool():
        await _db.bookings.delete()
        await _db.commit()