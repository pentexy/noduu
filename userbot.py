import logging
import re
from telethon import TelegramClient, events

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Your Telegram credentials ===
api_id = 26416419
api_hash = "c109c77f5823c847b1aeb7fbd4990cc4"
session_name = "forward_to_nezuko"

# Initialize the client
client = TelegramClient(session_name, api_id, api_hash)

# Store mapping of forwarded messages to user
forward_map = {}

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    sender = await event.get_sender()
    if not event.is_private or sender.bot:
        return

    user_id = event.sender_id
    text = event.raw_text.strip()
    
    # Forward the user's message to @im_NezukoBot
    try:
        sent = await client.send_message("im_NezukoBot", text)
        forward_map[sent.id] = user_id
        logger.info(f"Forwarded message to @im_NezukoBot from {user_id}")
    except Exception as e:
        logger.error(f"Failed to forward message: {e}")
        await event.reply("Something went wrong forwarding your message.")

@client.on(events.NewMessage(from_users="im_NezukoBot"))
async def reply_from_bot(event):
    try:
        if not event.is_reply:
            return

        original_msg = await event.get_reply_message()
        user_id = forward_map.pop(original_msg.id, None)

        if user_id is None:
            return

        text = event.raw_text

        # Replace "Nezuko" with "Yor" and usernames with @WingedAura
        text = text.replace("Nezuko", "Yor")
        text = re.sub(r"@\w+", "@WingedAura", text)

        await client.send_message(user_id, text)
        logger.info(f"Replied to user {user_id}")
    except Exception as e:
        logger.error(f"Error replying to user: {e}")

client.start()
logger.info("Bot is running. Waiting for messages...")
client.run_until_disconnected()
