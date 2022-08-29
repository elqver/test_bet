import datetime
import sys
import time
from typing import Optional

import httpx
from fastapi import FastAPI, Path, HTTPException, Depends, Query
from loguru import logger
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from cruds import insert_bet, select_bets
from db.config import get_session
from models import BetState
from schemas import BetRepr, Bet, TimeModel

logger.remove()
logger.add(sys.stdout, level="DEBUG")

app = FastAPI()


# TODO: add redis cache here instead
pool_timeout = datetime.timedelta(seconds=10)
available_events = None
last_available_pull: datetime.datetime.now() - pool_timeout


@app.get('/events')
async def get_events():
    if datetime.datetime.now() >= last_available_pull + pool_timeout:
        async with AsyncClient() as client:
            r: httpx.Response = await client.get(
                'http://line-provider/event/available')
            available_events = r.json()
    return available_events


# TODO: add redis cache here
@app.post('/bet', response_model=BetRepr)
async def create_bet(bet: Bet, adb: AsyncSession = Depends(get_session)):
    async with AsyncClient() as client:
        r: httpx.Response = await client.get(
            f'http://line-provider/event/{bet.event_id}')
        if r.status_code == 404:
            raise HTTPException(status_code=404,
                                detail={
                                    'message': 'no event found',
                                    'id': bet.event_id
                                })
        json_response = r.json()
        if json_response['state'] != 1:
            raise HTTPException(status_code=400,
                                detail={
                                    'message': 'event already has a result',
                                    'event': json_response
                                })
        if datetime.datetime.fromisoformat(
                json_response['deadline']) < datetime.datetime.now():
            raise HTTPException(status_code=400,
                                detail={
                                    'message': 'deadline violation',
                                    'event': json_response
                                })
    orm_bet = await insert_bet(adb, bet)
    response = BetRepr.from_orm(orm_bet)
    await adb.commit()
    return response


# TODO: add redis cache here
@app.get('/bets', response_model=list[BetRepr])
async def get_bets(ids: Optional[list[int]] = Query(default=None),
                   offset: int = 0,
                   limit: Optional[int] = None,
                   adb: AsyncSession = Depends(get_session)):
    bets = await select_bets(adb, ids, offset, limit)
    events_to_update: list[int] = list(
        {b.event_id
         for b in bets if b.state == BetState.NEW})

    async with AsyncClient() as client:
        r: httpx.Response = await client.get('http://line-provider/event',
                                             params={'ids': events_to_update})
        resp = r.json()
        events_update = {ev['id']: ev['state'] for ev in resp}

    for b in bets:
        if b.event_id in events_update:
            b.state = {0: BetState.NEW,
                       1: BetState.WIN,
                       2: BetState.LOSE}[events_update[b.event_id]]
            adb.add(b)
    await adb.commit()

    return [BetRepr.from_orm(b) for b in bets]
