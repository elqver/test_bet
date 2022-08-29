import enum

from sqlalchemy import Column, Integer, Numeric, DateTime, Enum

from db.config import Base


class EventState(enum.Enum):
    NEW = 1
    FINISHED_WIN = 2
    FINISHED_LOSE = 3


class Event(Base):
    __tablename__ = 'lp_event'

    id = Column(Integer, primary_key=True)
    coefficient = Column(Numeric(precision=5, scale=2))
    deadline = Column(DateTime)
    state = Column(Enum(EventState))
