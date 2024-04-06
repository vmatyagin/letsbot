import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from person import get_full_users

app = FastAPI()


@app.get("/")
async def get_map_data():
    json_compatible_item_data = jsonable_encoder(get_full_users())

    return JSONResponse(content=json_compatible_item_data)


async def run_server():
    config = uvicorn.Config(app, log_level="info", proxy_headers=True, host="0.0.0.0",lifespan=)
    server = uvicorn.Server(config)

    await server.serve()
