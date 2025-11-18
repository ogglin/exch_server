import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from routes.websock import *
app = FastAPI()

# Разрешить CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================
#   Connection Manager — подписки / рассылка
# =====================================================

class ConnectionManager:
    def __init__(self):
        # { websocket: {"timers", "settings", ...} }
        self.connections = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections[websocket] = set()

    def disconnect(self, websocket: WebSocket):
        if websocket in self.connections:
            del self.connections[websocket]

    def subscribe(self, websocket: WebSocket, channel: str):
        self.connections[websocket].add(channel)

    def unsubscribe(self, websocket: WebSocket, channel: str):
        self.connections[websocket].discard(channel)

    def subscribers(self, channel: str):
        return [
            ws for ws, subs in self.connections.items()
            if channel in subs
        ]

    async def broadcast(self, channel: str, message):
        dead = []

        for ws in self.subscribers(channel):
            try:
                # FastAPI автоматически сериализует dict в JSON
                await ws.send_json({channel: message})
            except WebSocketDisconnect:
                dead.append(ws)
            except Exception as e:
                print(f"Send failed but ws kept alive: {e}")

        for ws in dead:
            self.disconnect(ws)


manager = ConnectionManager()


# =====================================================
#   Обработчики — вызываются только если есть подписчики
# =====================================================

async def timers(manager):
    if not manager.subscribers("timers"):
        return
    await manager.broadcast("timers", await get_timers_data())


async def settings(manager):
    if not manager.subscribers("settings"):
        return
    await manager.broadcast("settings", await get_settings_data())


async def last_block(manager):
    if not manager.subscribers("last_block"):
        return
    await manager.broadcast("last_block", await get_last_block_data())


async def profits(manager):
    if not manager.subscribers("profits"):
        return
    await manager.broadcast("profits", await get_profits_data())


async def tickers_alert(manager):
    if not manager.subscribers("tickers_alert"):
        return
    await manager.broadcast("tickers_alert", await get_tickers_alert_data())


async def transfers(manager):
    if not manager.subscribers("transfers"):
        return
    await manager.broadcast("transfers", await get_transfers_data())


async def new_transfers(manager):
    if not manager.subscribers("new_transfers"):
        return
    await manager.broadcast("new_transfers", await get_new_transfers_data())


async def wallets(manager):
    if not manager.subscribers("wallets"):
        return
    await manager.broadcast("wallets", await get_wallets_data())


# =====================================================
#   Producer — общий фон рассылающий обновления
# =====================================================

async def producer(manager: ConnectionManager):
    while True:
        await asyncio.gather(
            timers(manager),
            settings(manager),
            last_block(manager),
            profits(manager),
            tickers_alert(manager),
            transfers(manager),
            new_transfers(manager),
            wallets(manager)
        )
        await asyncio.sleep(0.2)


# =====================================================
#   WebSocket consumer — подписки / отписки
# =====================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            msg = await websocket.receive_text()
            parts = msg.split()
            if len(parts) != 2:
                continue

            cmd, channel = parts
            if cmd == "sub":
                manager.subscribe(websocket, channel)

            elif cmd == "unsub":
                manager.unsubscribe(websocket, channel)

    except WebSocketDisconnect:
        manager.disconnect(websocket)


# =====================================================
#   Запуск сервера
# =====================================================

# @app.on_event("startup")
# async def start_background_tasks():
#     asyncio.create_task(producer(manager))

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server startup...")
    asyncio.create_task(producer(manager))
    yield
    print("Server shutdown...")

app.router.lifespan_context = lifespan


def run_server():
    uvicorn.run("main:app", host="0.0.0.0", port=30080, reload=True)


if __name__ == "__main__":
    run_server()
