import asyncio

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi_websocket_pubsub import PubSubEndpoint
from starlette.responses import HTMLResponse

from routes import pools, websock
from routes.websock import *

app = FastAPI()

origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

endpoint = PubSubEndpoint()
endpoint.register_route(app, path="/pubsub")

app.include_router(pools.router)

active_connections: List[WebSocket] = []


class ConnectionManager:
    def __init__(self):
        global active_connections
        self.active_connections = active_connections

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(e)
                print(self.active_connections)
                self.active_connections.remove(connection)
                print(self.active_connections)

    async def broadcast_bytes(self, message: bytes):
        for connection in self.active_connections:
            await connection.send_bytes(message)


manager = ConnectionManager()


@app.get("/")
def read_root():
    html_content = 'Exchanger API v1 <a href="/docs">docs</a>'
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/trigger")
async def trigger_events():
    # Upon request trigger an event
    while True:
        await endpoint.publish([f"triggered  {time.time()}"])
        await asyncio.sleep(1)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await timers(manager)
            await settings(manager)
            await last_block(manager)
            await profits(manager)
            await tickers_alert(manager)
            await transfers(manager)
            await wallets(manager)
            # data = await websocket.receive_text()
            # if data == 'sub replicas':
            #     asyncio.create_task(replicas_broadcast(manager))
            # await manager.send_personal_message(f"You wrote: {data}", websocket)
            # await manager.broadcast(f"Client says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client {websocket} left the chat")


async def run_server():
    config = uvicorn.Config("main:app", port=3080, host='0.0.0.0', log_level="info", reload=True)
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(run_server())
