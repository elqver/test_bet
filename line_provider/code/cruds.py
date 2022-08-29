import datetime
from typing import Optional

from fastapi import HTTPException
from loguru import logger
from sqlalchemy import select, insert, literal_column, update
from sqlalchemy.ext.asyncio import AsyncSession

from models import Event as ORMEvent, EventState
from schemas import Event


async def get_events_by_ids(adb: AsyncSession,
                            ids: list[int]) -> list[ORMEvent]:
    logger.debug(f'{ids=}')
    return (await adb.execute(select(ORMEvent).filter(ORMEvent.id.in_(ids))
                              )).scalars().all()


async def get_event_by_id(adb: AsyncSession,
                          target_id: int) -> Optional[ORMEvent]:
    logger.debug(f'{target_id=}')
    return (await
            adb.execute(select(ORMEvent).filter(ORMEvent.id == target_id)
                        )).scalars().first()


async def insert_event(adb: AsyncSession, event: Event) -> ORMEvent:
    target_event = ORMEvent(**event.dict())
    adb.add(target_event)
    await adb.flush()
    await adb.refresh(target_event)
    return target_event


async def change_event_state(adb: AsyncSession, id: int,
                             state: EventState) -> ORMEvent:
    target_event = await get_event_by_id(adb, id)
    if target_event is None:
        raise HTTPException(status_code=404,
                            detail={
                                'message': 'no event found',
                                'id': id
                            })
    if target_event.state != EventState.NEW.value:
        raise HTTPException(status_code=400,
                            detail={
                                'message': 'event already ended',
                                'id': id,
                                'status': target_event.state
                            })
    target_event.state = state
    adb.add(target_event)
    await adb.commit()
    return target_event


async def get_available_events(adb: AsyncSession) -> list[ORMEvent]:
    stmt = select(ORMEvent).filter(
        ORMEvent.deadline > datetime.datetime.now()).filter(
            ORMEvent.state == EventState.NEW)
    return (await adb.execute(stmt)).scalars().all()
