import os
import requests
from telegram import Bot
from dotenv import load_dotenv
import asyncio

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"

async def generate_post():
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "system",
                "content": "Ты автор Telegram-канала. Пиши коротко, интересно, с эмодзи."
            },
            {
                "role": "user",
                "content": "Напиши пост про ИИ и автоматизацию"
            }
        ],
        "max_tokens": 300
    }

    response = requests.post(PERPLEXITY_URL, json=payload, headers=headers)
    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]

async def post_to_channel():
    bot = Bot(token=BOT_TOKEN)
    text = await generate_post()
    await bot.send_message(chat_id=CHANNEL_ID, text=text)

asyncio.run(post_to_channel())