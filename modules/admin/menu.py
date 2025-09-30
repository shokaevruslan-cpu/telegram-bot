from . import view_dialogs, contact_user, check_risks
from .common import get_admin_menu

async def handle(update, context, main_menu):
    text = update.message.text or ""
    user_id = update.message.from_user.id

    if text == "👁 Просмотреть диалоги":
        await view_dialogs.handle(update, context)

    elif text == "✉️ Написать пользователю":
        await contact_user.handle(update, context)

    elif text == "⚠️ Тревожные пользователи":
        await check_risks.handle(update, context)

    elif text == "Назад":
        context.user_data["section"] = "menu"
        await update.message.reply_text("Главное меню", reply_markup=main_menu)

    else:
        await update.message.reply_text("Выбери действие:", reply_markup=get_admin_menu())


async def handle_callback(update, context):
    query = update.callback_query
    if query.data.startswith("view_dialog_"):
        await view_dialogs.handle_callback(update, context)
    elif query.data.startswith("contact_user_"):
        await contact_user.handle_callback(update, context)
    elif query.data.startswith("risk_user_"):
        await check_risks.handle_callback(update, context)
