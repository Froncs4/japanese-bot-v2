import os
from dotenv import load_dotenv

# Определяем абсолютный путь к папке проекта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = os.getenv("DB_PATH", os.path.join(BASE_DIR, "japanese_bot.db"))

XP_CORRECT = 10
XP_STREAK_BONUS = 5
STREAK_BONUS_EVERY = 5
QUIZ_OPTIONS_COUNT = 4

ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "").split(",") if id.strip()]
QUIZ_COOLDOWN = int(os.getenv("QUIZ_COOLDOWN", 3600))
MAX_DAILY_QUIZZES = int(os.getenv("MAX_DAILY_QUIZZES", 5))
PENALTY_QUEUE_SIZE = 10
HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", 10))