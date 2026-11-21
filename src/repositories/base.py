import logging
from collections.abc import Sequence

from asyncpg import UniqueViolationError
from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError, NoResultFound

from src.database import Base
from src.exception import ObjectAlreadyExists, ObjectNotFoundException
from src.repositories.mappers.base import DataMapper


class BaseRepository[ModelType: Base, SchemaType: BaseModel]:
    model: type[ModelType]
    mapper: type[DataMapper[ModelType, SchemaType]]

    def __init__(self, session):
        self.session = session

    async def get_filtered(self, *filter, **filter_by) -> list[SchemaType]:
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(model) for model in result.scalars().all()]

    async def get_all(self, *args, **kwargs) -> list[SchemaType]:
        return await self.get_filtered()

    async def get_one_or_none(self, **filter_by) -> SchemaType | None:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model:
            return self.mapper.map_to_domain_entity(model)
        return None

    async def get_one(self, **filter_by) -> SchemaType:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        try:
            model = result.scalar_one()
        except NoResultFound:
            raise ObjectNotFoundException from None
        return self.mapper.map_to_domain_entity(model)

    async def add(self, data: BaseModel) -> SchemaType:
        try:
            add_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
            result = await self.session.execute(add_stmt)
            model = result.scalars().one()
            return self.mapper.map_to_domain_entity(model)
        except IntegrityError as ex:
            logging.exception(f"Не удалось добавить даннные в БД, входные данные {data}")
            if ex.orig is not None and isinstance(ex.orig.__cause__, UniqueViolationError):
                raise ObjectAlreadyExists from ex
            else:
                logging.exception(f"Незнакомая ошибка: yе удалось добавить даннные в БД, входные данные {data}")
                raise ex

    async def add_bulk(self, data: Sequence[BaseModel]) -> None:
        add_stmt = insert(self.model).values([item.model_dump() for item in data])
        await self.session.execute(add_stmt)

    async def edit(self, data: BaseModel, exclude_unset: bool = False, **filter_by) -> None:
        update_stmt = update(self.model).filter_by(**filter_by).values(**data.model_dump(exclude_unset=exclude_unset))
        await self.session.execute(update_stmt)

    async def delete(self, **filter_by) -> None:
        delete_stmt = delete(self.model).filter_by(**filter_by)
        await self.session.execute(delete_stmt)
