"""Аутентификация — пропускаем сообщения только от одного Telegram аккаунта"""

from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message
from person import get_user_by_id, insert_person, update_person
from config import ADMIN_USERNAMES, LETSSURF_GROUP_ID
from aiogram.enums import ParseMode


class AccessMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data,
    ):
        if not event.from_user or event.from_user.is_bot:
            return

        # достаем только по id
        person = get_user_by_id(int(event.from_user.id))

        if not person and event.bot and event.from_user:
            try:
                await event.bot.get_chat_member(
                    chat_id=LETSSURF_GROUP_ID, user_id=event.from_user.id
                )

                insert_person(
                    event.from_user,
                    is_admin=event.from_user.username in ADMIN_USERNAMES,
                )

                person = get_user_by_id(int(event.from_user.id))
            except Exception:
                await event.answer(
                    "Привет! Похоже, ты еще не серфер, но это легко исправить, пиши @aloaloaloaloe"
                )
                return

        tg_username = event.from_user.username

        # Пользователь создан из контакта, обновим сами
        if person["username"] != tg_username:
            update_person(
                id=person["id"], field="username", value=event.from_user.username
            )
        if person["name"] == "":
            user = event.from_user
            name = user.first_name
            if user.last_name:
                name += f" {user.last_name}"
            update_person(id=person["id"], field="name", value=name[:250])

        data["person"] = person
        data["is_activated"] = person["is_activated"]

        return await handler(event, data)
