"""Аутентификация — пропускаем сообщения только от одного Telegram аккаунта"""

from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message
from person import get_user_by_id, insert_person
from config import ADMIN_USERNAMES


class AccessMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data,
    ):
        if not event.from_user or event.from_user.is_bot:
            return

        person = get_user_by_id(
            int(event.from_user.id), username=event.from_user.username
        )

        if not person:
            if event.from_user and event.from_user.username in ADMIN_USERNAMES:
                insert_person(event.from_user, is_admin=True)
                await event.answer("<i>Добавил тебя в БД</i>")
                person = get_user_by_id(
                    int(event.from_user.id), username=event.from_user.username
                )
            else:
                await event.answer(
                    "Привет! Похоже, ты еще не серфер, но это легко исправить, пиши @aloaloaloaloe"
                )
                return

        if not person:
            return

        data["person"] = person
        data["is_activated"] = person["is_activated"]

        return await handler(event, data)
