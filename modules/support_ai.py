from telegram import ReplyKeyboardMarkup
from utils.openrouter_client import chat_with_ai
from utils.database import save_ai_message, save_alert
from utils.suicide_detector import detect_risk
from config import ADMINS

async def handle(update, context, main_menu):
    text = update.message.text or ""
    user_id = update.message.from_user.id

    # Вход в поддержку
    if text == "💬 Поддержка":
        context.user_data["mode"] = "chat_ai"
        context.user_data["section"] = "support"
        await update.message.reply_text(
            "Я здесь, чтобы поддержать тебя 💜 Напиши мне, как ты себя чувствуешь.\n\n"
            "Для выхода нажми «Назад».",
            reply_markup=ReplyKeyboardMarkup([["Назад"]], resize_keyboard=True)
        )

    # Выход в главное меню
    elif text == "Назад":
        context.user_data["mode"] = None
        context.user_data["section"] = "menu"
        await update.message.reply_text("Главное меню", reply_markup=main_menu)

    # Все остальные сообщения → проверка + AI
    elif context.user_data.get("mode") == "chat_ai":
        save_ai_message(user_id, "user", text)

        # Проверка на риски
        risk_type, excerpt = detect_risk(text)

        if risk_type == "self":  # 🚨 риск себе
            save_alert(user_id, excerpt, "suicide")
            for admin_id in ADMINS:
                try:
                    await context.bot.send_message(
                        chat_id=admin_id,
                        text=f"🚨 [Суицидальный риск] Пользователь {user_id}\nСообщение: {excerpt}"
                    )
                except Exception as e:
                    print(f"Не удалось уведомить {admin_id}: {e}")

            # 📞 номера поддержки
            await update.message.reply_text(
                "☎️ Горячие линии помощи:\n\n"
                "📞 87081277302 — Консультант (военный психолог)\n"
                "   👤 Сарсенев Азамат Сабирович\n\n"
                "📞 87714776769 — Старший офицер (военный психолог)\n"
                "   👤 Мұханжар Азат Ағбайұлы\n\n"
            )
            await update.message.reply_photo(open("images/photo1.jpg", "rb"))

            # 💡 дополнительный ответ от AI
            try:
                reply = await chat_with_ai(text)
            except Exception as e:
                print(f"Ошибка Ollama: {e}")
                reply = "💜 Я рядом, пожалуйста, не оставайся один. Ты важен."
            await update.message.reply_text(reply)
            save_ai_message(user_id, "assistant", reply)
            return

        elif risk_type == "aggression":  # ⚠️ агрессия
            save_alert(user_id, excerpt, "aggression")
            for admin_id in ADMINS:
                try:
                    await context.bot.send_message(
                        chat_id=admin_id,
                        text=f"⚠️ [Агрессия] Пользователь {user_id}\nСообщение: {excerpt}"
                    )
                except Exception as e:
                    print(f"Не удалось уведомить {admin_id}: {e}")

            await update.message.reply_text(
                "⚠️ Я заметил в твоём сообщении сильные эмоции. "
                "Попробуй рассказать подробнее, что именно тебя злит."
            )

            # 💡 ответ от AI
            try:
                reply = await chat_with_ai(text)
            except Exception as e:
                print(f"Ошибка Ollama: {e}")
                reply = "Я слышу твою злость. Давай попробуем вместе найти безопасный способ её выразить."
            await update.message.reply_text(reply)
            save_ai_message(user_id, "assistant", reply)
            return

        # Если риска нет → обычный AI
        try:
            reply = await chat_with_ai(text)
        except Exception as e:
            print(f"Ошибка Ollama: {e}")
            reply = "😔 Извини, сейчас я не могу ответить. Попробуй чуть позже."

        await update.message.reply_text(reply)
        save_ai_message(user_id, "assistant", reply)
