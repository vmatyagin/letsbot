"""Конфиги, переменные окружения задаются тут."""

import os

from dotenv import load_dotenv

load_dotenv(override=True)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/surfbot/webhook")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")
BASE_WEBHOOK_URL = os.getenv("BASE_WEBHOOK_URL", "")
