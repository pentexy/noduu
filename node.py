import openai
import asyncio
from telethon import TelegramClient, events
import random
import os

# === CONFIGURATION ===
API_ID = 26416419
API_HASH = "c109c77f5823c847b1aeb7fbd4990cc4"
SESSION_NAME = "chatgpt_userbot"

# IMPORTANT: Replace with your real OpenAI API key
openai.api_key = "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"

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

    try:
        entity = await client.get_entity(event.chat_id)
        async with client.action(entity, 'typing'):
            await asyncio.sleep(random.uniform(1.0, 2.5))  # Simulate typing
    except Exception as e:
        print(f"[!] Typing simulation failed: {e}")

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
        print(f"[!] OpenAI Error: {e}")
        await event.reply("Sorry, I couldn’t respond due to an error.")

# === START BOT ===
print("Starting Telegram userbot...")
client.start()
print("Logged in successfully. Waiting for messages.")
client.run_until_disconnected()
