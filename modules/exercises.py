from telegram import ReplyKeyboardMarkup
import os

# Абсолютный путь к папке video внутри контейнера
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # путь до /app (где лежит bot.py и exercises.py)
VIDEO_PATH = os.path.join(BASE_DIR, "video")

# Главное меню упражнений
exercise_menu = ReplyKeyboardMarkup(
    [["Дыхание", "Медитация"],
     ["Релаксация", "🎥 Видео"],
     ["Назад"]],
    resize_keyboard=True
)

# Меню видео упражнений
video_menu = ReplyKeyboardMarkup(
    [["🎥 Видео дыхание", "🎥 Видео медитация"],
     ["🎥 Видео релаксация", "🎥 Видео сон"],
     ["Назад"]],
    resize_keyboard=True
)

async def handle(update, context, main_menu):
    text = update.message.text or ""
    section = context.user_data.get("section", "menu")

    # Вход в упражнения
    if text == "🧘 Упражнения":
        context.user_data["section"] = "exercises"
        await update.message.reply_text("Выбери упражнение:", reply_markup=exercise_menu)

    # ===== Текстовые упражнения =====
    elif section == "exercises":
        if text == "Дыхание":
            await update.message.reply_text(
                "🫁 Упражнение «4–7–8»:\n\n"
                "1) Вдох — 4 сек.\n2) Задержка — 7 сек.\n3) Выдох — 8 сек.\nПовтори 3–4 раза."
            )

        elif text == "Медитация":
            await update.message.reply_text(
                "🧘 Упражнение «Осознанность»:\n\n"
                "Сядь удобно, закрой глаза и наблюдай дыхание.\n"
                "Если мысли уходят — возвращай внимание к вдоху и выдоху."
            )

        elif text == "Релаксация":
            await update.message.reply_text(
                "🌙 «Напряжение и расслабление»:\n\n"
                "1) Напрягай мышцы рук на 5 сек → отпускай.\n"
                "2) Повтори с ногами и плечами.\n"
                "Снимает стресс."
            )

        elif text == "🎥 Видео":
            context.user_data["section"] = "video_exercises"
            await update.message.reply_text("Выбери видео упражнение:", reply_markup=video_menu)

        elif text == "Назад":
            context.user_data["section"] = "menu"
            await update.message.reply_text("Главное меню", reply_markup=main_menu)

    # ===== Видео упражнения =====
    elif section == "video_exercises":
        if text == "🎥 Видео дыхание":
            file_path = os.path.join(VIDEO_PATH, "breathing.mp4")
            await update.message.reply_text("Вот видео по дыханию 👇")
            await update.message.reply_video(video=open(file_path, "rb"))

        elif text == "🎥 Видео медитация":
            file_path = os.path.join(VIDEO_PATH, "meditation.mp4")
            await update.message.reply_text("Вот видео по медитации 👇")
            await update.message.reply_video(video=open(file_path, "rb"))

        elif text == "🎥 Видео релаксация":
            file_path = os.path.join(VIDEO_PATH, "relaxation.mp4")
            await update.message.reply_text("Вот видео по релаксации 👇")
            await update.message.reply_video(video=open(file_path, "rb"))

        elif text == "🎥 Видео сон":
            file_path = os.path.join(VIDEO_PATH, "sleep.mp4")
            await update.message.reply_text("Вот видео для быстрого засыпания 👇")
            await update.message.reply_video(video=open(file_path, "rb"))

        elif text == "Назад":
            context.user_data["section"] = "exercises"
            await update.message.reply_text("Возврат в меню упражнений:", reply_markup=exercise_menu)
