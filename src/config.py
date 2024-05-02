"""Конфиги, переменные окружения задаются тут."""

import os

from dotenv import load_dotenv

load_dotenv(override=True)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/surfbot/webhook")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")
BASE_WEBHOOK_URL = os.getenv("BASE_WEBHOOK_URL", "")
ADMIN_USERNAMES = ["matyagin", "aloaloaloaloe"]
# MAP_URL = "https://vmatyagin.github.io/letssurf/"
MAP_URL = "https://letssurf.pro/page/map"

LETSSURF_ID = -1001154694579
TEST_GROUP_ID = -1002121489665

LETSSURF_GROUP_ID = (
    TEST_GROUP_ID if bool(os.getenv("IS_DEVELOPMENT", False)) else LETSSURF_ID
)
