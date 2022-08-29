import datetime
import decimal

from pydantic import BaseModel

from models import BetState


class TimeModel(BaseModel):
    time: datetime.datetime


class Bet(BaseModel):
    event_id: int
    size: decimal.Decimal
    state: BetState


class BetRepr(Bet):
    id: int

    class Config:
        orm_mode = True
