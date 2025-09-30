import os
from utils.database import fetch_full_ai_history

def export_chat_to_file(user_id: int, folder: str = "logs") -> str:
    # создаём папку если нет
    if not os.path.exists(folder):
        os.makedirs(folder)

    # получаем историю
    rows = fetch_full_ai_history(user_id)

    # имя файла
    filename = os.path.join(folder, f"ai_chat_{user_id}.txt")

    with open(filename, "w", encoding="utf-8") as f:
        for role, message, created_at in rows:
            who = "👤 Пользователь" if role == "user" else "🤖 AI"
            f.write(f"[{created_at.strftime('%Y-%m-%d %H:%M:%S')}] {who}:\n{message}\n\n")

    return filename
