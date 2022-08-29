from typing import Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from schemas import Bet
from models import Bet as ORMBet


async def insert_bet(adb: AsyncSession, bet: Bet) -> ORMBet:
    target = ORMBet(**bet.dict())
    adb.add(target)
    await adb.flush()
    await adb.refresh(target)
    return target


async def select_bets(adb: AsyncSession,
                   ids: Optional[list[int]] = None,
                   offset: int = 0,
                   limit: Optional[int] = None) -> list[ORMBet]:
    stmt = select(ORMBet)
    if ids is not None:
        stmt.filter(ORMBet._in(ids))
    if offset:
        stmt.offset(offset)
    if limit is not None:
        stmt.limit(limit)
    res = (await adb.execute(stmt)).scalars().all()
    return res
