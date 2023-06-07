import base64
import gzip
from typing import List

from fastapi import APIRouter
from starlette.responses import JSONResponse

from db import *

router = APIRouter()


async def ungzip(base64_string):
    try:
        b = bytearray()
        b.extend(map(ord, base64_string))
        compressed_data = base64.b64decode(b)
        uncompressed_data = gzip.decompress(compressed_data).decode()
        return json.loads(uncompressed_data)
    except Exception as e:
        print(f'ungzip: {e}')
        print(base64_string)


# select?hashkey=pools-v2
@router.get("/pools")
async def pools(pool: str = None):
    items = None
    if pool:
        items = await redis.hgetall(pool)
    if items is None or len(items) < 1:
        return JSONResponse(status_code=404, content={
            "message": f"Не найден {pool}, примеры: pools-v2, pools-v3, pools_pancake, sushi_v2_pools"})
    return {pool: items}


@router.get("/replica")
async def replica(market: str = None, key: str = None):
    if market and key:
        items = await redis.hget(market, key)
        if items is None or len(items) < 1:
            return JSONResponse(status_code=404, content={
                "message": f"Не найден {market} - {key}"})
        items = await ungzip(items)
        print(items['bids'])
        items['bids'] = reversed(items['bids'])
        items['asks'] = reversed(list(reversed(items['asks'])))
        # print(items['bids'].reverse())
        return {market: {key: items}}
    elif market:
        items = await redis.hgetall(market)
        if items is None or len(items) < 1:
            return JSONResponse(status_code=404, content={
                "message": f"Не найден {market}, примеры: ascendexzip, bitruezip, bkexzip, gatezip, hitbtczip, hotbitzip, kucoinzip, mexczip"})
        else:
            unzip_items = {k: await ungzip(v) for k, v in items.items()}
            print(list(unzip_items.keys()))
        return {market: list(unzip_items.keys())}


@router.get("/settings")
async def settings():
    items = json.loads(await redis.get('settings'))
    if items is None:
        return JSONResponse(status_code=404, content={"message": f"Not found settings"})
    return {"settings": items}


@router.get("/timers")
async def settings():
    items = await redis.hgetall('timers')
    if items is None:
        return JSONResponse(status_code=404, content={"message": f"Not found timers"})
    return {"settings": items}
