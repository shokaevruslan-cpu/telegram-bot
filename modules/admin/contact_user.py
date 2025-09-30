from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from utils.database import fetch_alert_users
from .common import get_admin_menu

async def handle(update, context):
    users = fetch_alert_users()
    if not users:
        await update.message.reply_text("⚡ Нет пользователей для связи.", reply_markup=get_admin_menu())
    else:
        keyboard = [
            [InlineKeyboardButton(f"Пользователь {uid}", callback_data=f"contact_user_{uid}")]
            for uid in users
        ]
        await update.message.reply_text(
            "Выбери пользователя для начала чата:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def handle_callback(update, context):
    query = update.callback_query
    await query.answer()

    user_id = int(query.data.split("_")[2])
    admin_id = query.from_user.id

    # Сохраняем сессию
    sessions = context.bot_data.setdefault("contact_sessions", {})
    sessions[admin_id] = user_id

    # Меню выхода из диалога
    exit_menu = ReplyKeyboardMarkup([["❌ Выйти из диалога"]], resize_keyboard=True)

    await query.message.reply_text(
        f"🔗 Начат диалог с пользователем {user_id}. Теперь все сообщения будут пересылаться.\n"
        "Нажми «❌ Выйти из диалога» чтобы завершить.",
        reply_markup=exit_menu
    )

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text="⚡ Администратор подключился к чату с тобой."
        )
    except Exception:
        await query.message.reply_text("❌ Пользователь недоступен.", reply_markup=get_admin_menu())
