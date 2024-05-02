import logging

from aiogram import Router, F
from aiogram.types import Message, LinkPreviewOptions
from aiogram.filters import MagicData
from aiogram.fsm.context import FSMContext
from filters import PrivateFilter
from person import Person, insert_location, update_person
from config import MAP_URL
from utils import (
    status_keyboard_markup,
    get_status_from_message,
    common_keyboard_markup,
)
from states import States
from aiogram.enums import ParseMode

logger = logging.getLogger(__name__)

router = Router(name=__name__)
router.message.filter(PrivateFilter(), MagicData(F.is_activated == False))


@router.message(States.wait_for_status)
async def process_register_status(
    message: Message, person: Person, state: FSMContext
) -> None:
    new_status = get_status_from_message(message=message)

    if not new_status:
        return

    update_person(id=person["id"], field="family_status", value=new_status)
    update_person(id=person["id"], field="is_activated", value="1")

    await state.clear()

    await message.answer(
        f"✅ <b>Отлично, теперь ты на карте!</b> Можешь посмотреть, что получилось <a href='{MAP_URL}'>сразу на карте</a>, или выбрать пункт «Обо мне» в меню.",
        link_preview_options=LinkPreviewOptions(
            is_disabled=True,
        ),
        reply_markup=common_keyboard_markup,
        parse_mode=ParseMode.HTML,
    )


@router.message(States.wait_for_about)
async def process_register_about(
    message: Message, person: Person, state: FSMContext
) -> None:
    if not message.text or message.text and len(message.text) < 1:
        return

    update_person(id=person["id"], field="about", value=message.text[:250])
    await state.set_state(States.wait_for_status)

    await message.answer(
        "♥️ <b>Семейный статус.</b> Не серфингом единым :) Выбери свой текущий семейный статус. Если понадобится, его можно будет изменить в главном меню.",
        reply_markup=status_keyboard_markup,
        parse_mode=ParseMode.HTML,
    )


@router.message(States.wait_for_location)
async def process_register_location(
    message: Message, person: Person, state: FSMContext
) -> None:
    if not message.location:
        await message.answer("Некорректная геолокация")
        return

    insert_location(
        user_pk=person["id"],
        name="",
        latitude=message.location.latitude,
        longitude=message.location.longitude,
    )

    await message.answer(
        "🖥 <b>Информация о себе.</b> Напиши, чем ты занимаешься в рабочее и не очень время.",
        parse_mode=ParseMode.HTML,
    )
    await state.set_state(States.wait_for_about)


@router.message()
async def unhandled(message: Message, state: FSMContext):
    logger.debug(f"unhandled, {__name__}")
    current_state = await state.get_state()

    if current_state == None and message.from_user and not message.from_user.is_bot:
        name = message.from_user.first_name
        await message.answer(
            f"""Алоха, {name} 🤙\n\nЭтот бот поможет тебе добавиться на карту <a href="{MAP_URL}">летссерферов</a> и немного рассказать о себе. На этой карте только свои, проверенные кемпами, серферы.\n\n<b>Что ты можешь добавить на карту:</b>\n\n<b>📍локацию</b>, хотя бы ориентировочную — чтобы показать своим, что ты рядом.\n\n<b>🖥  чем ты занимаешься</b> в рабочее и не очень время — чтобы найти компанию по интересам или решить профессиональные задачи.\n\n<b>♥️ семейный статус</b> — ну а вдруг, всякое бывает :)\n\nЭтот бот создан серфером из нашего сообщества в свободное время 🤍""",
            link_preview_options=LinkPreviewOptions(is_disabled=True),
            parse_mode=ParseMode.HTML,
        )
        await message.answer(
            "📍 <b>Добавляем локацию.</b> Нажми на скрепку 📎 и отправь мне свою локацию. Позже её можно будет изменить\n\n<i>Отправка местоположения может быть недоступна на десктоп устройствах</i>",
            parse_mode=ParseMode.HTML,
        )
        await state.set_state(States.wait_for_location)
