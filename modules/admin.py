from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from utils.database import fetch_alert_users, fetch_user_dialog
import os

def get_admin_menu():
    return ReplyKeyboardMarkup(
        [["📊 Проверить намеренья", "💬 Просмотреть диалоги"], ["Назад"]],
        resize_keyboard=True
    )

async def handle(update, context, main_menu):
    text = update.message.text or ""
    user_id = update.message.from_user.id

    if text == "📊 Проверить намеренья":
        users = fetch_alert_users()
        if not users:
            await update.message.reply_text("⚡ Подозрительных сообщений не найдено.", reply_markup=get_admin_menu())
        else:
            msg = "🚨 Подозрительные пользователи:\n" + "\n".join([f"• {u}" for u in users])
            await update.message.reply_text(msg, reply_markup=get_admin_menu())

    elif text == "💬 Просмотреть диалоги":
        users = fetch_alert_users()
        if not users:
            await update.message.reply_text("⚡ Нет диалогов для просмотра.", reply_markup=get_admin_menu())
        else:
            keyboard = [
                [InlineKeyboardButton(f"Пользователь {uid}", callback_data=f"view_dialog_{uid}")]
                for uid in users
            ]
            await update.message.reply_text(
                "Выбери пользователя для просмотра диалога:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    elif text == "Назад":
        context.user_data["section"] = "menu"
        await update.message.reply_text("Главное меню", reply_markup=main_menu)

    else:
        await update.message.reply_text("Выбери действие:", reply_markup=get_admin_menu())


# ===========================
# Обработчик Inline-кнопок
# ===========================
async def handle_callback(update, context):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("view_dialog_"):
        user_id = int(query.data.split("_")[2])
        dialog = fetch_user_dialog(user_id)

        if not dialog:
            await query.edit_message_text(f"Диалог пользователя {user_id} пуст.")
            return

        # формируем текст диалога
        parts = []
        for role, msg, created_at in dialog:
            who = "👤 Пользователь" if role == "user" else "🤖 AI"
            parts.append(f"[{created_at.strftime('%Y-%m-%d %H:%M')}] {who}:\n{msg}\n")
        dialog_text = "\n".join(parts)

        # сохраняем в файл
        os.makedirs("logs", exist_ok=True)
        file_path = f"logs/dialog_{user_id}.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(dialog_text)

        # редактируем сообщение
        await query.edit_message_text(f"📂 Диалог пользователя {user_id} готов.")

        # отправляем файл с красивым именем
        with open(file_path, "rb") as f:
            await context.bot.send_document(
                chat_id=query.message.chat_id,
                document=InputFile(f, filename=f"dialog_{user_id}.txt")
            )
