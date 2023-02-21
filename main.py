import asyncio

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse

from routes import pools
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

app.include_router(pools.router)


@app.get("/")
def read_root():
    html_content = 'Exchanger API v1 <a href="/docs">docs</a>'
    return HTMLResponse(content=html_content, status_code=200)


@app.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client left the chat")


async def run_server():
    asyncio.create_task(timers())
    asyncio.create_task(settings())
    asyncio.create_task(last_block())
    asyncio.create_task(profits())
    config = uvicorn.Config("main:app", port=3080, host='0.0.0.0', log_level="info", reload=True)
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(run_server())
