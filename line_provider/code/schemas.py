import datetime
import decimal

from pydantic import BaseModel, root_validator

from models import EventState


class BaseModelUtcDateTime(BaseModel):

    @root_validator(pre=False)
    def datetime_normalizer(cls, values):
        for field, value in values.items():
            if isinstance(value, datetime.datetime) and value.tzinfo:
                values[field] = value.replace(tzinfo=None)

        return values


class Event(BaseModelUtcDateTime):
    coefficient: decimal.Decimal
    deadline: datetime.datetime
    state: EventState


class EventRepr(Event):
    id: int

    class Config:
        orm_mode = True
