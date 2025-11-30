import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI


TELEGRAM_TOKEN = ""
OPENAI_KEY = ""

client = OpenAI(api_key=OPENAI_KEY)

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я ИИ-бот")

    SYSTEM_PROMPT = """
Ты – вежливый, уверенный и полезный ИИ-ассистент. 
Не говори, что ты ChatGPT или GPT-модель. 
Представляйся просто как «ИИ-ассистент». 
Отвечай дружелюбно, но профессионально. 
Помогай пользователю максимально точно и полно.
Не упоминай, что работаешь через API.
"""


async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    print("DEBUG: отправляем запрос к OpenAI:", user_text)

    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",   # Рабочая модель, 100% доступная
            messages=[
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
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))

    print("БОТ ЗАПУЩЕН И ЖДЁТ СООБЩЕНИЙ...")
    app.run_polling()

if __name__ == "__main__":
    main()
