import logging
import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import TELEGRAM_TOKEN

# Импорты из utils (каждый отдельно, чтобы не было циклов)
from utils import diary
from utils import support_ai
from utils import exercises
from utils import hotlines
from utils import admin

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def get_main_menu(user_id):
    from telegram import ReplyKeyboardMarkup
    return ReplyKeyboardMarkup(
        [
            ["Мой дневник", "💬 Поддержка"],
            ["🧘 Упражнения", "☎️ Горячая линия"],
            ["Админ панель"] if user_id in [admin.ADMIN_ID] else []
        ],
        resize_keyboard=True
    )

async def start(update, context):
    user_id = update.message.from_user.id
    context.user_data["section"] = "menu"
    await update.message.reply_text("Главное меню", reply_markup=get_main_menu(user_id))

async def message_handler(update, context):
    text = update.message.text or ""
    user_id = update.message.from_user.id

    # Главное меню
    if context.user_data.get("section") == "menu":
        if text == "Мой дневник":
            context.user_data["section"] = "diary"
            await diary.handle(update, context, get_main_menu(user_id))
        elif text == "💬 Поддержка":
            context.user_data["section"] = "support"
            await support_ai.handle(update, context, get_main_menu(user_id))
        elif text == "🧘 Упражнения":
            context.user_data["section"] = "exercises"
            await exercises.handle(update, context, get_main_menu(user_id))
        elif text == "☎️ Горячая линия":
            context.user_data["section"] = "hotlines"
            await hotlines.handle(update, context, get_main_menu(user_id))
        elif text == "Админ панель" and user_id in [admin.ADMIN_ID]:
            context.user_data["section"] = "admin"
            await admin.handle(update, context, get_main_menu(user_id))
        else:
            await update.message.reply_text("Выбери действие из меню", reply_markup=get_main_menu(user_id))

    # Подсекции
    elif context.user_data["section"] == "diary":
        await diary.handle(update, context, get_main_menu(user_id))

    elif context.user_data["section"] == "support":
        await support_ai.handle(update, context, get_main_menu(user_id))

    elif context.user_data["section"] == "exercises":
        await exercises.handle(update, context, get_main_menu(user_id))

    elif context.user_data["section"] == "video_exercises":   # 🔹 добавлено для видео
        await exercises.handle(update, context, get_main_menu(user_id))

    elif context.user_data["section"] == "hotlines":
        await hotlines.handle(update, context, get_main_menu(user_id))

    elif context.user_data["section"] == "admin":
        await admin.handle(update, context, get_main_menu(user_id))

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    logging.info("🚀 Бот запущен!")
    application.run_polling()

if __name__ == "__main__":
    main()
