from typing import List

from fastapi import APIRouter
from starlette.responses import JSONResponse

from db import *

router = APIRouter()


# select?hashkey=pools-v2
@router.get("/pools")
async def pools(pool: str = None):
    items = None
    if pool:
        # items = {}
        if pool == 'pools-v2' or pool == 'pools-v3' or pool == 'sushi_v2_pools':
            items = await old_redis.hgetall(pool)
            # for k, v in (await old_redis.hgetall(pool)).items():
            #     items[k] = json.loads(v.replace('True', 'true').replace('False', 'false'))
        else:
            items = await redis.hgetall(pool)
            # for k, v in (await redis.hgetall(pool)).items():
            #     items[k] = json.loads(v)
    if items is None or len(items) < 1:
        return JSONResponse(status_code=404, content={
            "message": f"Не найден {pool}, примеры: pools-v2, pools-v3, pools_pancake, sushi_v2_pools"})
    return {pool: items}


@router.get("/replica")
async def replica(market: str = None):
    items = None
    if market:
        items = await redis.hgetall(market)
        # for k, v in (await redis.hgetall(market)).items():
        #     items[k] = json.loads(v.replace("'", '"'))
    if items is None or len(items) < 1:
        return JSONResponse(status_code=404, content={
            "message": f"Не найден {market}, примеры: ascendex, bitrue, bkex, gate, hitbtc, hotbit, kucoin, mxc"})
    return {market: items}


@router.get("/settings")
async def settings():
    items = json.loads(await redis.get('settings'))
    if items is None:
        return JSONResponse(status_code=404, content={"message": f"Not found settings"})
    return {"settings": items}


@router.get("/timers")
async def settings():
    items = await old_redis.hgetall('timers')
    if items is None:
        return JSONResponse(status_code=404, content={"message": f"Not found timers"})
    return {"settings": items}
