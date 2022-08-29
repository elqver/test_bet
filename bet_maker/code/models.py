import enum

from sqlalchemy import Column, Integer, Numeric, Enum

from db.config import Base


class BetState(enum.Enum):
    NEW = 0
    WIN = 1
    LOSE = 2


class Bet(Base):
    __tablename__ = 'bm_bet'

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer)
    size = Column(Numeric(precision=12, scale=2))
    state = Column(Enum(BetState))
