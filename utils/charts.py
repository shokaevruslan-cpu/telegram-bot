from io import BytesIO
from datetime import date, timedelta
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from utils.database import db_connect


def build_history_message(rows, reverse_map):
    """Собираем текст истории с эмодзи (за последние 7 дней)"""
    if not rows:
        return "История пуста."
    by_day = {}
    for rating, t, d in rows:
        by_day.setdefault(d, []).append((t, rating))
    parts = []
    for d in sorted(by_day.keys(), reverse=True):
        parts.append(f"📅 {d}:")
        for t, rating in sorted(by_day[d], reverse=True):
            emoji = reverse_map.get(rating, "❓")
            parts.append(f"{t.strftime('%H:%M')} — {emoji} ({rating}/5)")
        parts.append("")
    return "\n".join(parts).strip()


def compute_daily_average(user_id: int, days: int):
    """Считаем среднюю оценку за n дней"""
    conn = db_connect()
    cur = conn.cursor()
    since = (date.today() - timedelta(days=days - 1))
    cur.execute(
        """
        SELECT day, AVG(rating)::float
        FROM diary
        WHERE user_id=%s AND day >= %s
        GROUP BY day
        ORDER BY day
        """,
        (user_id, since)
    )
    rows = cur.fetchall()
    conn.close()

    avg_map = {d: avg for d, avg in rows}
    days_list = [since + timedelta(days=i) for i in range(days)]
    avgs = [avg_map.get(d, None) for d in days_list]
    return days_list, avgs


def plot_and_get_png(dates_list, values, title: str, y_max=5):
    """Строим график средних оценок и возвращаем PNG"""
    fig = plt.figure(figsize=(9, 4.5), dpi=150)
    xs = [d for d, v in zip(dates_list, values) if v is not None]
    ys = [v for v in values if v is not None]

    if xs and ys:
        plt.plot(xs, ys, marker="o")
        plt.ylim(1, y_max)
        plt.title(title)
        plt.xlabel("Дата")
        plt.ylabel(f"Оценка (1–{y_max})")
        plt.grid(True, alpha=0.3)

        # Подписи над точками (7 дней — все, 30 дней — через одну)
        step = 1 if len(xs) <= 10 else 2
        for i, (x, y) in enumerate(zip(xs, ys)):
            if i % step == 0:
                plt.text(x, y + 0.15, f"{y:.1f}", ha="center", fontsize=8)
    else:
        plt.title(title + " (нет данных)")
        plt.axis("off")

    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf
