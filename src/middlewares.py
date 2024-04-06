"""Аутентификация — пропускаем сообщения только от одного Telegram аккаунта"""

from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message

from person import get_user_by_id, insert_person


class AccessMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data,
    ):
        if event.from_user.is_bot:
            return
        person = get_user_by_id(int(event.from_user.id))

        if not person:
            if event.from_user and event.from_user.username == "matyagin":
                insert_person(event.from_user, is_admin=True)
                await event.answer("Привет. Добавил тебя в БД")
            else:
                await event.answer(
                    "Привет! Похоже, ты еще не серфер, но это легко исправить, пиши @aloaloaloaloe"
                )
                return

        data["person"] = person

        return await handler(event, data)
