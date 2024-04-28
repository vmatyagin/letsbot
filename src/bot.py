"""Настройка конфигурации бота"""

import logging
from aiogram import Bot, Dispatcher
from config import BASE_WEBHOOK_URL, TELEGRAM_BOT_TOKEN, WEBHOOK_PATH, WEBHOOK_SECRET
from middlewares import AccessMiddleware
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, WebhookInfo
from aiogram.fsm.context import FSMContext
from middlewares import AccessMiddleware
from filters import PrivateFilter
from bot_routes import register_router, admin_router, main_router
from person import Person, delete_person

logger = logging.getLogger(__name__)

dp = Dispatcher()
bot = Bot(TELEGRAM_BOT_TOKEN)

dp.message.outer_middleware(AccessMiddleware())

dp.include_routers(
    admin_router,
    register_router,
    main_router,
)


@dp.message(PrivateFilter(), Command(commands=["clear"]))
async def clear(message: Message, state: FSMContext):
    await state.clear()

    await message.answer("Очищено", reply_markup=ReplyKeyboardRemove())


@dp.message(PrivateFilter(), Command(commands=["remove_me"]))
async def remove_me(message: Message, person: Person, state: FSMContext):
    await state.clear()
    delete_person(user_pk=person["id"])
    await message.answer("Прощай", reply_markup=ReplyKeyboardRemove())


async def set_webhook(bot: Bot) -> None:
    # Check and set webhook for Telegram
    # await bot.delete_webhook(True)
    # await dp.start_polling(bot)
    # return

    async def check_webhook() -> WebhookInfo | None:
        try:
            webhook_info = await bot.get_webhook_info()
            return webhook_info
        except Exception as e:
            logger.error(f"Can't get webhook info - {e}")
            return

    current_webhook_info = await check_webhook()
    logger.debug(f"Current bot info: {current_webhook_info}")
    try:
        await bot.set_webhook(
            f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}",
            secret_token=WEBHOOK_SECRET,
            drop_pending_updates=True,
        )

        logger.debug(f"Updated bot info: {await check_webhook()}")
    except Exception as e:
        logger.error(f"Can't set webhook - {e}")


async def set_bot_commands_menu(bot: Bot) -> None:
    commands = [
        # BotCommand(command="/me", description="О тебе"),
        # BotCommand(command="/start", description="📋 Меню"),
        # BotCommand(command="/location", description="📍 Локации"),
        # BotCommand(command="/new_location", description="Для создания локации"),
        # BotCommand(command="/name", description="Изменение имени"),
        # BotCommand(command="/status", description="Изменение семейного статуса"),
        # BotCommand(command="/about", description="Изменение информации о себе"),
    ]
    try:
        await bot.set_my_commands(commands)
    except Exception as e:
        logger.error(f"Can't set commands - {e}")


async def start_telegram():
    await set_webhook(bot)
    await set_bot_commands_menu(bot)
