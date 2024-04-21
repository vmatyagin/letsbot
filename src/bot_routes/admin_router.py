import logging

from aiogram import Router, F
from aiogram.types import (
    Message,
)
from aiogram.fsm.context import FSMContext
from filters import AdminFilter, PrivateFilter
from person import get_user_by_id, insert_person_by_contact

logger = logging.getLogger(__name__)

router = Router(name=__name__)
router.message.filter(PrivateFilter(), AdminFilter())


@router.message(F.contact)
async def parse_contact(message: Message, state: FSMContext):
    logger.debug(f"parse_contact, {__name__}")

    await state.clear()

    if message.contact:
        user = get_user_by_id(id=message.contact.user_id)

        if not user:
            insert_person_by_contact(message.contact)
            await message.answer("Ок, серфер добавлен")
        else:
            await message.answer("Такой серфер уже существует")
