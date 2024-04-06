import logging
from typing import Annotated

from fastapi import APIRouter, Header
from aiogram import types
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from person import get_full_users
from bot import bot, dp
from config import WEBHOOK_PATH, WEBHOOK_SECRET

logger = logging.getLogger(__name__)


root_router = APIRouter(
    prefix="",
    tags=["root"],
    responses={404: {"description": "Not found"}},
)


@root_router.get("/surfbot")
async def root() -> dict:
    json_compatible_item_data = jsonable_encoder(get_full_users())

    return JSONResponse(content=json_compatible_item_data)


@root_router.post(WEBHOOK_PATH)
async def bot_webhook(
    update: dict,
    x_telegram_bot_api_secret_token: Annotated[str | None, Header()] = None,
) -> None | dict:
    """Register webhook endpoint for telegram bot"""
    if x_telegram_bot_api_secret_token != WEBHOOK_SECRET:
        logger.error("Wrong secret token !")
        return {"status": "error", "message": "Wrong secret token !"}
    telegram_update = types.Update(**update)
    await dp.feed_webhook_update(bot=bot, update=telegram_update)
