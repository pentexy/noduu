import asyncio
from telethon import TelegramClient, events
import logging

logging.basicConfig(level=logging.INFO)

# === REQUIRED ===
API_ID = 26416419
API_HASH = "c109c77f5823c847b1aeb7fbd4990cc4"
SESSION_NAME = "forwarder_bot"

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

forwarded_messages = {}

@client.on(events.NewMessage(incoming=True))
async def forward_to_nezuko(event):
    if not event.is_private or event.sender_id == (await client.get_me()).id:
        return

    try:
        # Forward user's message to @im_NezukoBot
        fwd = await client.send_message("im_NezukoBot", event.text)
        forwarded_messages[fwd.id] = event.chat_id
        logging.info(f"Forwarded message to @im_NezukoBot: {event.text}")
    except Exception as e:
        await event.reply("Failed to forward message.")
        logging.error(e)

@client.on(events.NewMessage(from_users="im_NezukoBot"))
async def handle_bot_response(event):
    reply_to = event.reply_to_msg_id
    user_id = forwarded_messages.get(reply_to)

    if user_id:
        try:
            await client.send_message(user_id, event.text or "<Media received>")
            logging.info(f"Sent response to user {user_id}")
            del forwarded_messages[reply_to]
        except Exception as e:
            logging.error(e)

async def main():
    print("Logging in...")
    await client.start()
    print("Logged in successfully. Waiting for private messages...")
    await client.run_until_disconnected()

asyncio.run(main())
