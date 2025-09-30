import os
import httpx
import asyncio
import logging

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini")

# Логирование (в консоль)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

async def chat_with_ai(prompt: str) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": AI_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Ты — доброжелательный и внимательный психолог. "
                    "Отвечай мягко, с эмпатией. "
                    "Не давай медицинских советов."
                )
            },
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 400,
        "temperature": 0.7,
    }

    # Попробуем до 3 раз при 429
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(url, headers=headers, json=data)
                resp.raise_for_status()
                result = resp.json()
                reply = result["choices"][0]["message"]["content"].strip()
                return reply
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429 and attempt < 2:
                logging.warning("⚠️ Лимит запросов (429). Ждём 5 секунд и пробуем снова...")
                await asyncio.sleep(5)
                continue
            logging.error(f"Ошибка OpenAI: {e}")
            return "😔 Извини, сейчас я не могу ответить."
        except Exception as e:
            logging.error(f"Ошибка OpenAI: {e}")
            return "😔 Извини, сейчас я не могу ответить."
