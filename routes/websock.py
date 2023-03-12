import asyncio
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from db import *


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


async def timers():
    while True:
        try:
            items = await redis.hgetall('timers')
            await manager.broadcast(f'"timers": {items}')
            await asyncio.sleep(1)
        except Exception as err:
            print('ws', err)


async def settings():
    while True:
        try:
            items = await redis.get('settings')
            await manager.broadcast(f'"settings": {items}')
            await asyncio.sleep(1)
        except Exception as err:
            print('ws', err)


async def last_block():
    while True:
        try:
            items = await redis.get('last_block')
            await manager.broadcast(f'"last_block": {items}')
            await asyncio.sleep(1)
        except Exception as err:
            print('last_block', err)


async def profits():
    while True:
        try:
            items = await redis.hgetall('profits')
            await manager.broadcast(f'"profits": {items}')
            await asyncio.sleep(1)
        except Exception as err:
            print('profits', err)
