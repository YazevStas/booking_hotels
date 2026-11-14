import typing

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if typing.TYPE_CHECKING:
    from src.models.facilities import FacilitiesORM

class RoomsORM(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    price: Mapped[int]
    description: Mapped[str | None]
    quantity: Mapped[int]
    title: Mapped[str]

    facilities: Mapped[list["FacilitiesORM"]] = relationship(
        back_populates="rooms",
        secondary="rooms_facilities",
    )