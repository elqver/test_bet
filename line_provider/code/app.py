import sys
from typing import List

from fastapi import FastAPI, Path, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from cruds import get_event_by_id, insert_event, get_events_by_ids, \
    change_event_state, get_available_events
from db.config import get_session
from models import EventState
from schemas import Event, EventRepr

logger.remove()
logger.add(sys.stdout, level="DEBUG")

app = FastAPI()


@app.get('/event/available', response_model=list[EventRepr])
async def get_events_before_deadline(adb: AsyncSession = Depends(get_session)):
    res = await get_available_events(adb)
    logger.debug(res)
    return res


@app.get('/event/{id}', response_model=EventRepr)
async def get_event(id: int = Path(default=None),
                    adb: AsyncSession = Depends(get_session)):
    logger.debug(f'{id=}')
    event = await get_event_by_id(adb, id)
    logger.debug(f'{event=}')
    if event is None:
        raise HTTPException(status_code=404,
                            detail={
                                'message': 'no event found',
                                'id': id
                            })
    return EventRepr.from_orm(event)


@app.get('/event', response_model=list[EventRepr])
async def get_events(ids: List[int] = Query(default=[]),
                     adb: AsyncSession = Depends(get_session)):
    res = await get_events_by_ids(adb, ids)
    logger.debug(res)
    return res


@app.put('/event/{id}/win', response_model=EventRepr)
async def set_event_win(id: int = Path(default=None),
                        adb: AsyncSession = Depends(get_session)):
    result = await change_event_state(adb, id, EventState.FINISHED_WIN)
    return EventRepr.from_orm(result)


@app.put('/event/{id}/lose', response_model=EventRepr)
async def set_event_lose(id: int = Path(default=None),
                         adb: AsyncSession = Depends(get_session)):
    result = await change_event_state(adb, id, EventState.FINISHED_LOSE)
    return EventRepr.from_orm(result)


@app.post('/event', response_model=EventRepr)
async def create_event(event: Event, adb: AsyncSession = Depends(get_session)):
    logger.debug(f'{event=}')
    res = EventRepr.from_orm(await insert_event(adb, event))
    await adb.commit()
    return res
