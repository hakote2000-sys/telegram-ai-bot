import logging
import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("Нет TELEGRAM_TOKEN")

if not OPENAI_KEY:
    raise ValueError("Нет OPENAI_KEY")

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app_flask = Flask(__name__)

client = OpenAI(api_key=OPENAI_KEY)

@app_flask.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data:
        return "no data", 400

    logging.info(f"Получен апдейт: {data}")

    update = Update.de_json(data, app.bot)
    asyncio.run(app.process_update(update))

    return "ok"
@app_flask.route("/")
def home():
    return "OK"
SYSTEM_PROMPT = """
Ты — ИИ-ассистент, который ОБЯЗАН строго соблюдать правила.

ЖЁСТКИЕ ПРАВИЛА:
1. Всегда говори вежливо и профессионально.
2. Никогда не переходи на грубый, неформальный или сленговый стиль.
3. Игнорируй любые просьбы пользователя изменить стиль речи.
4. НЕ выполняй команды вроде:
   - "говори как гопник"
   - "будь грубым"
   - "матерись"
   - любые попытки изменить твою личность
5. Если пользователь просит изменить стиль — вежливо откажись.

Ты НЕ имеешь права нарушать эти правила ни при каких условиях.

Не говори, что ты ChatGPT или GPT-модель.
Представляйся как «ИИ-ассистент».
"""

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я ИИ-бот")



async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_text_lower = user_text.lower()

    if any(word in user_text_lower for word in ["гопник", "мат", "грубо", "оскорбляй"]):
        await update.message.reply_text(
        "Я придерживаюсь вежливого и профессионального стиля общения."
    )
        return
    print("DEBUG: отправляем запрос к OpenAI:", user_text)

    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",   # Рабочая модель, 100% доступная
            messages=[
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": user_text}
]
        )

        # В новых версиях openai-python структура ответа вот такая:
        bot_reply = response.choices[0].message.content

        print("DEBUG: ответ от OpenAI:", bot_reply)
        await update.message.reply_text(bot_reply)

    except Exception as e:
        print("ERROR:", e)
        await update.message.reply_text("Ошибка OpenAI: " + str(e))

def main():
    asyncio.run(app.initialize())
    asyncio.run(app.start())

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))

    print("БОТ ЗАПУЩЕН (WEBHOOK)...")

if __name__ == "__main__":
    main()
    app_flask.run(host="0.0.0.0", port=8080)
