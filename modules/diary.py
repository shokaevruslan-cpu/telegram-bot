import matplotlib.pyplot as plt
from telegram import ReplyKeyboardMarkup
from utils.database import save_diary_entry, fetch_entries, fetch_avg_ratings
import io

# Главное меню дневника
diary_menu = ReplyKeyboardMarkup(
    [["📝 Оценить настроение"], ["📜 История"], ["📊 График за 7 дней", "📊 График за 30 дней"], ["Назад"]],
    resize_keyboard=True
)

# Кнопки со смайликами для оценки
emoji_menu = ReplyKeyboardMarkup(
    [["😀", "🙂", "😐", "🙁", "😢"], ["Назад"]],
    resize_keyboard=True
)

emoji_ratings = {
    "😀": 5,
    "🙂": 4,
    "😐": 3,
    "🙁": 2,
    "😢": 1
}

async def handle(update, context, main_menu):
    text = update.message.text or ""
    user_id = update.message.from_user.id

    # --- шаг оценки ---
    if text in emoji_ratings:
        save_diary_entry(user_id, emoji_ratings[text])
        await update.message.reply_text("✅ Оценка сохранена!", reply_markup=diary_menu)
        return

    # Запросить меню оценки
    if text == "📝 Оценить настроение":
        await update.message.reply_text("Выбери смайлик для оценки:", reply_markup=emoji_menu)
        return

    # История
    if text == "📜 История":
        rows = fetch_entries(user_id, days=7)
        if not rows:
            await update.message.reply_text("⚡ История пуста.")
        else:
            history = "\n".join([f"{r[2].strftime('%Y-%m-%d %H:%M')} → {r[1]}" for r in rows])
            await update.message.reply_text(f"📜 История за 7 дней:\n\n{history}")
        return

    # Графики
    if text == "📊 График за 7 дней":
        rows = fetch_avg_ratings(user_id, days=7)
        if not rows:
            await update.message.reply_text("⚡ Нет данных для графика.")
            return
        await send_chart(update, rows, "📊 Средняя оценка за 7 дней")
        return

    if text == "📊 График за 30 дней":
        rows = fetch_avg_ratings(user_id, days=30)
        if not rows:
            await update.message.reply_text("⚡ Нет данных для графика.")
            return
        await send_chart(update, rows, "📊 Средняя оценка за 30 дней")
        return

    # Назад
    if text == "Назад":
        context.user_data["section"] = "menu"
        await update.message.reply_text("Главное меню:", reply_markup=main_menu)
        return

    # Если только зашёл в дневник
    await update.message.reply_text("📓 Дневник: выбери действие", reply_markup=diary_menu)


async def send_chart(update, rows, title):
    dates = [str(r[0]) for r in rows]
    ratings = [float(r[1]) for r in rows]

    plt.figure(figsize=(6, 4))
    plt.plot(dates, ratings, marker="o", linestyle="-")
    plt.title(title)
    plt.ylabel("Средняя оценка (1–5)")
    plt.xlabel("Дата")
    plt.ylim(1, 5)
    plt.grid(True)

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()

    await update.message.reply_photo(buf)
