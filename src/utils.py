from aiogram.types import (
    Message,
    KeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
)
from person import PersonStatusLangs, PersonStatus
from config import MAP_URL


status_keyboard_list = [
    [
        KeyboardButton(text=PersonStatusLangs[PersonStatus.MARRIED]),
        KeyboardButton(text=PersonStatusLangs[PersonStatus.RELATIONSHIP]),
    ],
    [
        KeyboardButton(text=PersonStatusLangs[PersonStatus.ACTIVE]),
        KeyboardButton(text=PersonStatusLangs[PersonStatus.UNSET]),
    ],
]

status_keyboard_markup = ReplyKeyboardMarkup(
    keyboard=status_keyboard_list, resize_keyboard=True, one_time_keyboard=True
)


def get_status_from_message(message: Message):
    new_status: str | None = None
    for status, text in PersonStatusLangs.items():
        if text == message.text:
            new_status = status.value
            break

    return new_status


keyboard_list = [
    [
        KeyboardButton(text="🌎 Карта"),
        KeyboardButton(text="🏄 Обо мне"),
    ],
    [
        KeyboardButton(text="📍 Мои локации"),
        KeyboardButton(text="⚙️ Изменить информацию"),
    ],
]

common_keyboard_markup = ReplyKeyboardMarkup(
    keyboard=keyboard_list, resize_keyboard=True
)

inline_get_map_markup = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Перейти", url=MAP_URL)]]
)

change_me_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🏄 Имя",
                callback_data=f"edit-me:name",
            ),
            InlineKeyboardButton(
                text="🖥 Информацию",
                callback_data=f"edit-me:about",
            ),
            InlineKeyboardButton(
                text="♥️ Стаутс",
                callback_data=f"edit-me:status",
            ),
        ]
    ]
)

no_location_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📍 Добавить локацию",
                callback_data=f"edit-me:location",
            ),
        ]
    ]
)
