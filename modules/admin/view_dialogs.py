from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from utils.database import fetch_alert_users, fetch_user_dialog
import io

async def handle(update, context):
    users = fetch_alert_users()
    if not users:
        await update.message.reply_text("⚡ Нет пользователей с диалогами.")
    else:
        keyboard = [
            [InlineKeyboardButton(f"Пользователь {uid}", callback_data=f"view_dialog_{uid}")]
            for uid in users
        ]
        await update.message.reply_text(
            "Выбери пользователя для просмотра диалога:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def handle_callback(update, context):
    query = update.callback_query
    await query.answer()

    user_id = int(query.data.split("_")[2])
    dialog = fetch_user_dialog(user_id)

    if not dialog:
        await query.edit_message_text("⚡ Диалог пуст.")
        return

    # Собираем текст в файл
    lines = [f"[{d[2]}] {d[0]}: {d[1]}" for d in dialog]
    content = "\n".join(lines)

    buf = io.BytesIO(content.encode("utf-8"))
    buf.name = f"dialog_{user_id}.txt"

    await query.message.reply_document(buf, caption=f"Диалог пользователя {user_id}")
