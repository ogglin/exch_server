import asyncio
import gzip
from typing import List

from fastapi import WebSocket

from db import *


async def timers(manager):
    # while True:
    try:
        items = await redis.hgetall('timers')
        await manager.broadcast(f'"timers": {items}')
        await asyncio.sleep(.1)
    except Exception as err:
        print('ws', err)


async def settings(manager):
    # while True:
    try:
        items = await redis.get('settings')
        await manager.broadcast(f'"settings": {items}')
        await asyncio.sleep(.1)
    except Exception as err:
        print('ws', err)


async def last_block(manager):
    # while True:
    try:
        items = await redis.get('last_block')
        await manager.broadcast(f'"last_block": {items}')
        await asyncio.sleep(.1)
    except Exception as err:
        print('last_block', err)


async def profits(manager):
    length = 0
    # while True:
    try:
        items = await redis.hgetall('profits')
        for k, val in items.items():
            profs = json.loads(val)
            for prof in profs:
                if 'SIPHER' in str(prof):
                    # print(prof)
                    pass
                    # print(prof['market'], prof['usd_profit'])

        if length != len(json.dumps(items)):
            await manager.broadcast(f'"profits": {items}')
        await asyncio.sleep(.1)
    except Exception as err:
        print('profits', err)


async def h_get_all(hkey):
    while True:
        try:
            msg = await redis.hgetall(hkey)
            jdata = {f'{hkey}': msg}
            return jdata
        except Exception as err:
            print('error h_get_all:', err)


async def replicas_broadcast(manager):
    try:
        while True:
            a_tasks = [
                h_get_all('ascendex'),
                h_get_all('bitrue'),
                h_get_all('bkex'),
                h_get_all('gate'),
                h_get_all('hitbtc'),
                h_get_all('hotbit'),
                h_get_all('mxc'),
                h_get_all('kucoin')
            ]
            data = await asyncio.gather(*a_tasks)
            result = {}
            for d in data:
                for k, v in d.items():
                    result[k] = v
            compressed_data = gzip.compress(json.dumps(result).encode("utf-8"))
            await manager.broadcast_bytes(compressed_data)
    except Exception as exp:
        print('replicas_broadcast error:', exp)
        manager.disconnect()
        await manager.broadcast(f"Client #{manager.disconnect} left the chat")


async def tickers_alert(manager):
    try:
        items = await redis.hgetall('ticks_alerts')
        await manager.broadcast(f'"ticks_alerts": {items}')
    except Exception as e:
        print('ticks_alerts', e)


async def transfers(manager):
    try:
        items = await redis.hgetall('transfers')
        await manager.broadcast(f'"transfers": {items}')
    except Exception as e:
        print('transfers', e)


async def new_transfers(manager):
    try:
        items = await redis.hgetall('new_transfers')
        await manager.broadcast(f'"new_transfers": {items}')
    except Exception as e:
        print('new_transfers', e)


async def wallets(manager):
    try:
        items = await redis.hgetall('wallets_checked')
        await manager.broadcast(f'"wallets": {items}')
    except Exception as e:
        print('wallets_checked', e)
