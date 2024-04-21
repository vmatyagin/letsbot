"""Сервер Telegram бота. Точка входа."""

import logging
import sys
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from routes import root_router

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    logger.info("🚀 Starting application")
    from bot import start_telegram

    await start_telegram()
    yield
    logger.info("⛔ Stopping application")


app = FastAPI(lifespan=lifespan)
app.include_router(root_router)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8345,
        proxy_headers=True,
        log_level="info",
    )
