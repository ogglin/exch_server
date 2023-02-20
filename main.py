import asyncio
from typing import Union

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse

from routes import pools

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


async def run_server():
    config = uvicorn.Config("main:app", port=8080, host='0.0.0.0', log_level="info", reload=True)
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(run_server())
