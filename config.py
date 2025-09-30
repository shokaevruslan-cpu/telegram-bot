# config.py
import os
from dotenv import load_dotenv

# Загружаем .env в окружение
load_dotenv()

# 🔹 Основные настройки
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# 🔹 База данных
DATABASE_URL = os.getenv("DATABASE_URL", "postgres://bot_user:bot_pass@db:5432/bot_db")

# 🔹 AI провайдеры
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HF_API_KEY = os.getenv("HF_API_KEY")
DEEPINFRA_API_KEY = os.getenv("DEEPINFRA_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini")

# 🔹 Админы (через запятую в .env, например ADMINS=123456789,987654321)
ADMINS = [1068728951]
