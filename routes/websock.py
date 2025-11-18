import asyncio
import gzip
from typing import List

from db import *


async def get_timers_data():
    try:
        return await redis.hgetall('timers')
    except Exception as err:
        return err


async def get_settings_data():
    try:
        return await redis.get('settings')
    except Exception as err:
        return err


async def get_last_block_data():
    try:
        return await redis.get('last_block')
    except Exception as err:
        return err


async def get_profits_data():
    try:
        items = await redis.hgetall('profits')
        if len(json.dumps(items)) > 0:
            return items
    except Exception as err:
        return err


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


async def get_tickers_alert_data():
    try:
        return await redis.hgetall('ticks_alerts')
    except Exception as e:
        return e


async def get_transfers_data():
    try:
        return await redis.hgetall('transfers')
    except Exception as err:
        return err


async def get_new_transfers_data():
    try:
        return await redis.hgetall('new_transfers')
    except Exception as err:
        return err


async def get_wallets_data():
    try:
        return await redis.hgetall('wallets_checked')
    except Exception as err:
        return err
