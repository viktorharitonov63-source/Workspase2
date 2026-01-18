import os
import requests
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"

# Словарь для хранения временных постов для согласования
pending_posts = {}

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
        "Привет! Напиши мне, что сгенерировать для Telegram-канала, и я пришлю на согласование."
    )

# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_prompt = update.message.text
    user_id = update.message.from_user.id

    await update.message.reply_text("Генерирую пост, подожди... ⏳")
    try:
        text = generate_post(user_prompt)
        # Сохраняем пост для согласования
        pending_posts[user_id] = text

        # Кнопки для подтверждения публикации
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Опубликовать", callback_data="publish")],
            [InlineKeyboardButton("❌ Отменить", callback_data="cancel")]
        ])

        await update.message.reply_text(f"Сгенерированный пост:\n\n{text}", reply_markup=keyboard)
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {e}")

# Обработка нажатий на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in pending_posts:
        await query.edit_message_text("У тебя нет ожидающих постов.")
        return

    if query.data == "publish":
        text = pending_posts.pop(user_id)
        bot: Bot = context.bot
        await bot.send_message(chat_id=CHANNEL_ID, text=text)
        await query.edit_message_text("Пост опубликован в канале ✅")
    elif query.data == "cancel":
        pending_posts.pop(user_id)
        await query.edit_message_text("Публикация отменена ❌")

# Основной запуск бота
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Добавляем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Бот запущен...")
    app.run_polling()