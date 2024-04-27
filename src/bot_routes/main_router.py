import logging
from aiogram import F, Router
from aiogram.filters import MagicData
from aiogram.types import (
    Message,
    CallbackQuery,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from filters import PrivateFilter
from person import (
    Person,
    PersonStatus,
    PersonStatusLangs,
    delete_location_by_id,
    get_location_by_id,
    get_user_locations,
    insert_location,
    update_person,
)
from utils import (
    status_keyboard_markup,
    get_status_from_message,
    common_keyboard_markup,
    inline_get_map_markup,
    change_me_markup,
    no_location_markup,
)
from states import States

logger = logging.getLogger(__name__)


router = Router(name=__name__)
router.message.filter(PrivateFilter(), MagicData(F.is_activated == True))


@router.message(States.wait_for_name)
async def process_name(message: Message, person: Person, state: FSMContext) -> None:
    if not message.text or len(message.text.strip()) < 2:
        await message.answer(f"Слишком короткое имя")
        return

    await state.clear()
    update_person(id=person["id"], field="name", value=message.text)
    await message.answer(
        "Сохранено",
        reply_markup=common_keyboard_markup,
    )


@router.message(States.wait_for_about)
async def process_about(message: Message, person: Person, state: FSMContext) -> None:
    if not message.text:
        return
    await state.clear()
    update_person(id=person["id"], field="about", value=message.text)

    await message.answer(
        "Сохранено",
        reply_markup=common_keyboard_markup,
    )


@router.message(States.wait_for_status)
async def process_status(message: Message, person: Person, state: FSMContext) -> None:
    new_status = get_status_from_message(message=message)

    if not new_status:
        return

    await state.clear()

    update_person(id=person["id"], field="family_status", value=new_status)

    await message.answer(
        "Сохранено",
        reply_markup=common_keyboard_markup,
    )


@router.callback_query(
    lambda c: isinstance(c.data, str) and c.data.startswith("edit-location:")
)
async def handle_location_click(query: CallbackQuery):
    if not query.data or not query.bot or not query.message:
        return

    id = query.data.replace("edit-location:", "")

    if not id:
        return

    location = get_location_by_id(int(id))

    if not location:
        return

    location_name = location["name"] or "Без названия"

    builder = InlineKeyboardBuilder()

    builder.button(
        text="Удалить",
        callback_data=f"delete-location:{location['id']}",
    )

    await query.bot.edit_message_text(
        f"Название локации: {location_name}",
        query.from_user.id,
        query.message.message_id,
        reply_markup=builder.as_markup(),
    )

    await query.bot.send_location(
        chat_id=query.message.chat.id,
        latitude=location["latitude"],
        longitude=location["longitude"],
    )


@router.callback_query(
    lambda c: isinstance(c.data, str) and c.data.startswith("delete-location:")
)
async def handle_location_delete(query: CallbackQuery):
    if not query.data or not query.bot or not query.message:
        return

    id = query.data.replace("delete-location:", "")

    if not id:
        return

    delete_location_by_id(int(id))
    await query.bot.edit_message_text(
        f"Локация удалена",
        query.from_user.id,
        query.message.message_id,
        reply_markup=None,
    )


@router.message(States.wait_for_location_name)
async def process_location_name(
    message: Message, person: Person, state: FSMContext
) -> None:
    if not message.text or len(message.text) < 2:
        await message.answer("Слишком короткое название")
        return

    await state.set_data({"name": message.text})
    await state.set_state(States.wait_for_location)

    await message.answer(
        f"Выбери на карте точку, которую ты хочешь сделать своей локацией\n\n<i>Отправка местоположения может быть недоступна на десктоп устройствах</i>"
    )


@router.message(States.wait_for_location)
async def process_location(message: Message, person: Person, state: FSMContext) -> None:
    data = await state.get_data()

    if not message.location:
        await message.answer("Некорректная геолокация")
        return

    insert_location(
        user_pk=person["id"],
        name=data.get("name", ""),
        latitude=message.location.latitude,
        longitude=message.location.longitude,
    )

    await state.clear()
    await message.answer(f"Ок! Новая локация сохранена")


# КОЛБЭКИ НА КНОПКИ В ИЗМЕНЕНИИ ИНФОРМАЦИИ


@router.callback_query(
    lambda c: isinstance(c.data, str) and c.data.startswith("edit-me:")
)
async def handle_change_me(query: CallbackQuery, state: FSMContext):
    if not query.data or not query.bot or not query.message:
        return

    id = query.data.replace("edit-me:", "")

    if not id:
        return

    await query.bot.delete_message(
        query.from_user.id,
        query.message.message_id,
    )

    text: str = ""
    markup = None

    if id == "name":
        text = "Отправь мне новое имя."
        await state.set_state(States.wait_for_name)

    if id == "about":
        text = "Напиши, чем ты занимаешься в рабочее и не очень время."
        await state.set_state(States.wait_for_about)

    if id == "status":
        text = "Выбери свой текущий семейный статус."
        await state.set_state(States.wait_for_status)
        markup = status_keyboard_markup

    if id == "location":
        text = "Давай обзовем как-нибудь локацию? Пришли название"
        await state.set_state(States.wait_for_location_name)

    await query.bot.send_message(
        query.from_user.id,
        text,
        reply_markup=markup,
    )


# РЕАКЦИИ НА КНОПКИ


@router.message(F.text.contains("Обо мне"))
async def get_me(message: Message, person: Person, state: FSMContext):
    name = person.get("name", "")
    status = PersonStatusLangs.get(
        PersonStatus(person.get("family_status", PersonStatus.UNSET))
    )
    about = person.get("about", "")

    answer = f"Имя — {name}\nСемейный статус — {status}\nО тебе — {about}"

    if person["is_admin"]:
        answer += "\n\n А еще ты админ ❤️"

    await message.answer(
        answer,
        reply_markup=common_keyboard_markup,
    )


@router.message(F.text.contains("Карта"))
async def get_map(message: Message):
    await message.answer("Карта летсерферов", reply_markup=inline_get_map_markup)


@router.message(F.text.contains("Мои локации"))
async def get_locations(message: Message, person: Person, state: FSMContext):
    user_locations = get_user_locations(person["id"])

    if not len(user_locations):
        await message.answer("У тебя нет локаций", reply_markup=no_location_markup)
        return

    builder = InlineKeyboardBuilder()

    if len(user_locations) < 3:
        builder.button(
            text="📍 Добавить локацию",
            callback_data=f"edit-me:location",
        )

    for location in user_locations:
        builder.button(
            text=location["name"] or "Без названия",
            callback_data=f"edit-location:{location['id']}",
        )

    builder.adjust(3)

    await message.answer("Твои локации:", reply_markup=builder.as_markup())


@router.message(F.text.contains("Изменить информацию"))
async def change_me(message: Message, person: Person, state: FSMContext):
    await state.clear()
    await message.answer("Что изменить?", reply_markup=change_me_markup)


#


@router.message()
async def unhandled(message: Message, state: FSMContext):
    logger.debug(f"unhandled, {__name__}")
    await message.answer(
        f"Не понимаю тебя",
        reply_markup=common_keyboard_markup,
    )
