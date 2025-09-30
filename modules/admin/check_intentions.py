from utils.database import fetch_alert_users
from .common import get_admin_menu

async def handle(update, context):
    users = fetch_alert_users()
    if not users:
        await update.message.reply_text("⚡ Подозрительных сообщений не найдено.", reply_markup=get_admin_menu())
    else:
        msg = "🚨 Подозрительные пользователи:\n" + "\n".join([f"• {u}" for u in users])
        await update.message.reply_text(msg, reply_markup=get_admin_menu())
