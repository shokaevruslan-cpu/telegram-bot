import os
import psycopg2
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# --- Конфигурация ---
TOKEN = os.getenv("BOT_TOKEN")  # Токен Telegram
DB_URL = os.getenv("DATABASE_URL")  # URL Postgres от Render


# --- Подключение к БД ---
def get_conn():
    return psycopg2.connect(DB_URL, sslmode="require")


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mood_log (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            timestamp TIMESTAMP NOT NULL,
            mood INT NOT NULL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


def log_mood(user_id, mood_value):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO mood_log (user_id, timestamp, mood) VALUES (%s, %s, %s)",
        (user_id, datetime.now(), mood_value),
    )
    conn.commit()
    cur.close()
    conn.close()


def get_mood_history(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT timestamp, mood FROM mood_log WHERE user_id=%s ORDER BY timestamp DESC LIMIT 10",
        (user_id,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# --- Бот ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("😊 Записать настроение", callback_data="mood")],
        [InlineKeyboardButton("📊 История", callback_data="history")],
    ]
    await update.message.reply_text(
        "Привет! Я бот-дневник настроений.\nЧто хотите сделать?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "mood":
        await query.edit_message_text("Введите настроение от 1 до 10:")
        context.user_data["awaiting_mood"] = True

    elif query.data == "history":
        history = get_mood_history(query.from_user.id)
        if not history:
            await query.edit_message_text("История пуста.")
        else:
            text = "\n".join(
                [f"{t.strftime('%Y-%m-%d %H:%M')}: {m}" for t, m in history]
            )
            await query.edit_message_text("📊 Ваша история:\n" + text)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_mood"):
        try:
            mood_value = int(update.message.text)
            if 1 <= mood_value <= 10:
                log_mood(update.effective_user.id, mood_value)
                await update.message.reply_text("✅ Настроение сохранено!")
            else:
                await update.message.reply_text("Введите число от 1 до 10.")
        except ValueError:
            await update.message.reply_text("Введите число.")
        context.user_data["awaiting_mood"] = False


def main():
    init_db()
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()


if __name__ == "__main__":
    main()
