from telegram import ReplyKeyboardMarkup

async def handle(update, context, main_menu):
    text = update.message.text or ""

    if text == "Назад":
        context.user_data["section"] = "menu"
        await update.message.reply_text("Главное меню:", reply_markup=main_menu)
        return

    hotlines_text = (
        "☎️ Горячие линии помощи:\n\n"
        "📞 87081277302 — Консультант (военный психолог)\n"
        "   👤 Сарсенев Азамат Сабирович\n\n"
        "📞 87714776769 — Старший офицер (военный психолог)\n"
        "   👤 Мұханжар Азат Ағбайұлы\n\n"
           )

    back_menu = ReplyKeyboardMarkup([["Назад"]], resize_keyboard=True)
    await update.message.reply_photo(open("images/photo1.jpg", "rb"))

    # Сначала отправляем текст
    await update.message.reply_text(hotlines_text, reply_markup=back_menu)

    # Потом две картинки
