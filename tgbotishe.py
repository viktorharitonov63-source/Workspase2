import os
import requests
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"

# Функция для генерации текста через Perplexity API
def generate_post(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "Ты автор Telegram-канала. Пиши коротко, интересно, с эмодзи."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 300
    }

    response = requests.post(PERPLEXITY_URL, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Напиши мне, что сгенерировать для Telegram-канала, и я опубликую это."
    )

# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_prompt = update.message.text
    await update.message.reply_text("Генерирую пост, подожди... ⏳")

    try:
        text = generate_post(user_prompt)  # sync функция
        await update.message.reply_text(f"Сгенерированный пост:\n\n{text}")

        # Отправка в канал
        bot: Bot = context.bot
        await bot.send_message(chat_id=CHANNEL_ID, text=text)
        await update.message.reply_text("Пост опубликован в канале ✅")

    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {e}")

# Основной запуск бота
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Добавляем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")
    # На Windows просто запускаем без asyncio.run()
    app.run_polling()