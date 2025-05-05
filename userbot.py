import openai
import asyncio
from telethon import TelegramClient, events
import random

# === CONFIGURATION ===
API_ID = 26416419
API_HASH = "c109c77f5823c847b1aeb7fbd4990cc4"
SESSION_NAME = "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"

# === OPENAI KEY ===
openai.api_key = ""

# === SETUP TELEGRAM CLIENT ===
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# === MESSAGE HANDLER ===
@client.on(events.NewMessage(incoming=True))
async def chatgpt_reply(event):
    if not event.is_private:
        return  # Only respond in private chats

    if event.media or event.message.message.startswith("/"):
        return  # Ignore media and commands

    message_text = event.message.message.strip()

    async with event.client.action(event.chat_id, 'typing'):
        await asyncio.sleep(random.uniform(1.0, 3.0))  # Simulate typing delay

    try:
        reply = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": message_text}
            ],
            temperature=0.8,
        )

        response_text = reply['choices'][0]['message']['content']
        await event.reply(response_text)

    except Exception as e:
        await event.reply("Sorry, something went wrong with ChatGPT.")

# === START BOT ===
print("Starting Telegram userbot...")
client.start()
print("Logged in successfully. Waiting for private messages...")
client.run_until_disconnected()
