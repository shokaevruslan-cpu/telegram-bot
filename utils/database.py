import psycopg2
from datetime import datetime, timedelta
import os

DB_NAME = os.getenv("DB_NAME", "bot_db")
DB_USER = os.getenv("DB_USER", "bot_user")
DB_PASS = os.getenv("DB_PASS", "bot_pass")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")


def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )


def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Таблица дневника
            cur.execute("""
                CREATE TABLE IF NOT EXISTS diary (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    rating INT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)

            # Таблица сообщений AI
            cur.execute("""
                CREATE TABLE IF NOT EXISTS ai_chat (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    role TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)

            # Таблица тревожных слов
            cur.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    message TEXT NOT NULL,
                    risk_type TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)

        conn.commit()


# =======================
# Работа с дневником
# =======================
def save_diary_entry(user_id, rating: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO diary (user_id, rating, created_at) VALUES (%s, %s, NOW())",
                (user_id, rating)
            )
        conn.commit()


def fetch_entries(user_id, days=7):
    """Возвращает все записи за N дней"""
    since = datetime.now() - timedelta(days=days)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT user_id, rating, created_at FROM diary WHERE user_id=%s AND created_at >= %s ORDER BY created_at DESC",
                (user_id, since)
            )
            return cur.fetchall()


def fetch_avg_ratings(user_id, days=30):
    """Возвращает средний рейтинг по дням за N дней"""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT DATE(created_at) AS day, ROUND(AVG(rating)::numeric, 2) AS avg_rating
                FROM diary
                WHERE user_id = %s AND created_at >= NOW() - INTERVAL '%s days'
                GROUP BY DATE(created_at)
                ORDER BY DATE(created_at);
                """,
                (user_id, days)
            )
            return cur.fetchall()


# =======================
# Работа с AI чатом
# =======================
def save_ai_message(user_id, role, message):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO ai_chat (user_id, role, message, created_at) VALUES (%s, %s, %s, NOW())",
                (user_id, role, message)
            )
        conn.commit()


def fetch_user_dialog(user_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT role, message, created_at FROM ai_chat WHERE user_id=%s ORDER BY created_at ASC",
                (user_id,)
            )
            return cur.fetchall()


# =======================
# Работа с тревожными словами
# =======================
def save_alert(user_id, message, risk_type="suicidal"):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO alerts (user_id, message, risk_type, created_at) VALUES (%s, %s, %s, NOW())",
                (user_id, message, risk_type)
            )
        conn.commit()


def fetch_alert_users():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT user_id FROM alerts ORDER BY user_id ASC")
            return [row[0] for row in cur.fetchall()]
