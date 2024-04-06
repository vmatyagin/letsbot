"""Настройка конфигурации бота"""

import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config import BASE_WEBHOOK_URL, TELEGRAM_BOT_TOKEN, WEBHOOK_PATH, WEBHOOK_SECRET
from middlewares import AccessMiddleware
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    KeyboardButton,
    ReplyKeyboardRemove,
    BotCommand,
    CallbackQuery,
    WebhookInfo,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardMarkup, InlineKeyboardBuilder
from middlewares import AccessMiddleware
from filters import PrivateFilter
from person import (
    Person,
    PersonStatusLangs,
    update_person,
    insert_location,
    PersonStatus,
    get_user_locations,
    get_location_by_id,
    delete_location_by_id,
)

logger = logging.getLogger(__name__)

dp = Dispatcher()
bot = Bot(TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.HTML)

dp.message.middleware(AccessMiddleware())


class Form(StatesGroup):
    name = State()
    about = State()
    status = State()
    location = State()
    new_location = State()


@dp.message(PrivateFilter(), CommandStart())
async def send_welcome(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        f"Привет, серфер!!\n \n"
        "Чтобы изменить информацию себе, введи одну из команд:\n"
        "/name, для изменении имени\n"
        "/location, для изменении локации \n"
        "/status, для изменении семейного статуса \n"
        "/about, для изменении информации о себе \n\n"
        "/me, чтобы получить информацию о себе\n"
    )


@dp.message(PrivateFilter(), Command(commands=["me"]))
async def get_me(message: Message, person: Person, state: FSMContext):
    await state.clear()

    name = person.get("name", "")
    status = PersonStatusLangs.get(
        PersonStatus(person.get("family_status", PersonStatus.UNSET))
    )
    about = person.get("about", "")

    answer = f"Имя -- {name}\nСемейный статус -- {status}\nО тебе -- {about}"

    if person["is_admin"]:
        answer += "\nТы админ"

    await message.answer(answer, reply_markup=ReplyKeyboardRemove())


@dp.message(PrivateFilter(), Command(commands=["name"]))
async def change_name(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Form.name)

    await message.answer("Хорошо, пришли в ответ новое имя")


@dp.message(PrivateFilter(), Form.name)
async def process_name(message: Message, person: Person, state: FSMContext) -> None:
    if len(message.text.strip()) < 2:
        await message.answer(f"Слишком короткое имя")
        return

    await state.clear()
    update_person(id=person["id"], field="name", value=message.text)
    await message.answer("Сохранено")


@dp.message(PrivateFilter(), Command(commands=["about"]))
async def change_name(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Form.about)

    await message.answer(
        "Пришли в ответ информацию, которую хотел бы рассказать о себе"
    )


@dp.message(PrivateFilter(), Form.about)
async def process_name(message: Message, person: Person, state: FSMContext) -> None:
    await state.clear()
    update_person(id=person["id"], field="about", value=message.text)
    await message.answer("Сохранено")


@dp.message(PrivateFilter(), Command(commands=["new_location"]))
async def change_name(message: Message, state: FSMContext):
    await state.clear()

    await state.set_state(Form.new_location)

    await message.answer("Пришли название локации или как-нибудь обзови точку)")


async def create_status_keyboard(message: Message, text: str):

    keyboard_list = []
    for status in PersonStatusLangs:
        keyboard_list.append([KeyboardButton(text=PersonStatusLangs[status])])

    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard_list, resize_keyboard=True, one_time_keyboard=True
    )

    await message.answer(
        text,
        reply_markup=keyboard,
    )


@dp.message(PrivateFilter(), Command(commands=["status"]))
async def change_status(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Form.status)

    await create_status_keyboard(message, "Выбери статус")


@dp.message(PrivateFilter(), Form.status)
async def process_status(message: Message, person: Person, state: FSMContext) -> None:

    new_status: str | None = None
    for status, text in PersonStatusLangs.items():
        if text == message.text:
            new_status = status.value
            break

    if not new_status:
        await create_status_keyboard(message, "Выбери статус")
        return

    await state.clear()

    update_person(id=person["id"], field="family_status", value=new_status)
    await message.answer("Сохранено", reply_markup=ReplyKeyboardRemove())


@dp.message(PrivateFilter(), Command(commands=["location"]))
async def location(message: Message, person: Person, state: FSMContext):
    await state.clear()

    user_locations = get_user_locations(person["id"])

    if not len(user_locations):
        await message.answer(
            "У тебя нет локаций. Чтобы создает её, напиши /new_location"
        )
        return

    builder = InlineKeyboardBuilder()

    for location in user_locations:
        builder.button(
            text=location["name"] or "Без названия",
            callback_data=f"edit-location:{location['id']}",
        )

    builder.adjust(3, 3)

    await message.answer("Твои локации:", reply_markup=builder.as_markup())


@dp.callback_query(
    lambda c: isinstance(c.data, str) and c.data.startswith("edit-location:")
)
async def handle_location_click(query: CallbackQuery):

    id = query.data.replace("edit-location:", "")

    if not id:
        return

    location = get_location_by_id(int(id))
    location_name = location["name"] or "Без названия"

    builder = InlineKeyboardBuilder()

    builder.button(
        text="Удалить",
        callback_data=f"delete-location:{location['id']}",
    )

    await bot.edit_message_text(
        f"Название локации: {location_name}",
        query.from_user.id,
        query.message.message_id,
        reply_markup=builder.as_markup(),
    )

    await bot.send_location(
        chat_id=query.message.chat.id,
        latitude=location["latitude"],
        longitude=location["longitude"],
    )


@dp.callback_query(
    lambda c: isinstance(c.data, str) and c.data.startswith("delete-location:")
)
async def handle_location_delete(query: CallbackQuery):

    id = query.data.replace("delete-location:", "")

    if not id:
        return

    delete_location_by_id(int(id))

    await bot.edit_message_text(
        f"Локация удалена",
        query.from_user.id,
        query.message.message_id,
        reply_markup=None,
    )


@dp.message(PrivateFilter(), Form.new_location)
async def process_location(message: Message, person: Person, state: FSMContext) -> None:
    if len(message.text) < 2:
        await message.answer("Слишком короткое название")
        return

    await state.set_data({"name": message.text})
    await state.set_state(Form.location)

    await message.answer(f"Ок! Теперь пришли локацию")


@dp.message(PrivateFilter(), Form.location)
async def process_location(message: Message, person: Person, state: FSMContext) -> None:
    if not message.location:
        await message.answer("Некорректная геолокация")
        return

    data = await state.get_data()
    await state.clear()

    insert_location(
        user_pk=person["id"],
        name=data.get("name", ""),
        latitude=message.location.latitude,
        longitude=message.location.longitude,
    )

    await message.answer(f"Ок! Новая локация сохранена")


@dp.message(PrivateFilter(), Command(commands=["clear"]))
async def clear(message: Message, state: FSMContext):
    await state.clear()

    await message.answer("Очищено", reply_markup=ReplyKeyboardRemove())


async def set_webhook(bot: Bot) -> None:
    # Check and set webhook for Telegram
    # await bot.delete_webhook(True)
    # await dp.start_polling(bot)
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
            drop_pending_updates=current_webhook_info.pending_update_count > 0,
        )

        logger.debug(f"Updated bot info: {await check_webhook()}")
    except Exception as e:
        logger.error(f"Can't set webhook - {e}")


async def set_bot_commands_menu(bot: Bot) -> None:
    commands = [
        BotCommand(command="/me", description="О тебе"),
        BotCommand(command="/start", description="📋 Меню"),
        BotCommand(command="/location", description="📍 Локации"),
        BotCommand(command="/new_location", description="Для создания локации"),
        BotCommand(command="/name", description="Изменение имени"),
        BotCommand(command="/status", description="Изменение семейного статуса"),
        BotCommand(command="/about", description="Изменение информации о себе"),
    ]
    try:
        await bot.set_my_commands(commands)
    except Exception as e:
        logger.error(f"Can't set commands - {e}")


async def start_telegram():
    await set_webhook(bot)
    await set_bot_commands_menu(bot)
