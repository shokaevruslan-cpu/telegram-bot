from telegram import ReplyKeyboardMarkup

def get_admin_menu():
    return ReplyKeyboardMarkup(
        [
            ["👁 Просмотреть диалоги", "⚠️ Тревожные пользователи"],
            ["✉️ Написать пользователю"],
            ["Назад"]
        ],
        resize_keyboard=True
    )
