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
        items = {}
        if pool == 'pools-v2' or pool == 'pools-v3':
            for k, v in (await old_redis.hgetall(pool)).items():
                items[k] = json.loads(v.replace('True', 'true').replace('False', 'false'))
        else:
            for k, v in (await redis.hgetall(pool)).items():
                items[k] = json.loads(v)
    if items is None:
        return JSONResponse(status_code=404, content={"message": f"Not found {pool}"})
    return {pool: items}


@router.get("/replica")
async def replica(market: str = None):
    items = None
    if market:
        items = {}
        for k, v in (await redis.hgetall(market)).items():
            items[k] = json.loads(v)
    if items is None:
        return JSONResponse(status_code=404, content={"message": f"Not found {market}"})
    return {market: items}


@router.get("/settings")
async def settings():
    items = json.loads(await redis.get('settings'))
    if items is None:
        return JSONResponse(status_code=404, content={"message": f"Not found settings"})
    return {"settings": items}
