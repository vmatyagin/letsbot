from aiogram.filters import BaseFilter
from aiogram.types import Message

from person import Person
from config import ADMIN_USERNAMES


class PrivateFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.chat.type == "private"


class AdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return bool(message.from_user and message.from_user.username in ADMIN_USERNAMES)
