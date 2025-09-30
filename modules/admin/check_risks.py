from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from utils.database import fetch_alert_users
import psycopg2
from utils.database import get_connection

async def handle(update, context):
    users = fetch_alert_users()
    if not users:
        await update.message.reply_text("✅ Тревожных сообщений не найдено.")
    else:
        keyboard = [
            [InlineKeyboardButton(f"Пользователь {uid}", callback_data=f"risk_user_{uid}")]
            for uid in users
        ]
        await update.message.reply_text(
            "⚠️ Список тревожных пользователей:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def handle_callback(update, context):
    query = update.callback_query
    await query.answer()

    user_id = int(query.data.split("_")[2])

    # достаём все тревожные сообщения пользователя
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT message, created_at, risk_type FROM alerts WHERE user_id = %s ORDER BY created_at DESC",
                (user_id,)
            )
            rows = cur.fetchall()

    if not rows:
        await query.edit_message_text(f"⚡ У пользователя {user_id} тревожных сообщений нет.")
        return

    text = f"⚠️ Сообщения пользователя {user_id}:\n\n"
    for msg, created, risk in rows:
        text += f"[{created.strftime('%Y-%m-%d %H:%M')}] ({risk}) {msg}\n\n"

    await query.message.reply_text(text)
