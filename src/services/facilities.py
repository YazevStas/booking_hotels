from src.schemas.facilities import Facility, FacilityAdd
from src.services.base import BaseService


class FacilityService(BaseService):
    async def get_facilities(self) -> list[Facility]:
        return await self.db.facilities.get_all()

    async def create_facility(self, data: FacilityAdd) -> Facility:
        facility = await self.db.facilities.add(data)
        await self.db.commit()
        return facility
