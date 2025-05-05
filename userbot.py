import asyncio
import logging
from telethon import TelegramClient, events
from collections import defaultdict

# === Configuration ===
API_ID = 26416419
API_HASH = "c109c77f5823c847b1aeb7fbd4990cc4"
SESSION_NAME = "forward_to_nezuko"

# === Setup logging ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Setup client ===
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# Store message links: forwarded_msg_id -> original_user_id
forward_map = {}

# === Start listening ===
@client.on(events.NewMessage(incoming=True))
async def handler(event):
    if not event.is_private:
        return

    try:
        sender = await event.get_sender()
        if sender.bot:
            return  # Ignore messages from bots

        user_id = sender.id
        message = event.message

        # Forward message to NezukoBot
        fwd_msg = await client.send_message("@im_NezukoBot", message.text)
        forward_map[fwd_msg.id] = user_id
        logger.info(f"Forwarded message to @im_NezukoBot from {user_id}")

    except Exception as e:
        logger.error(f"Error in handler: {e}")

@client.on(events.NewMessage(from_users="im_NezukoBot"))
async def response_handler(event):
    if not event.reply_to_msg_id:
        return  # Only handle replies

    replied_msg_id = event.reply_to_msg_id

    if replied_msg_id in forward_map:
        user_id = forward_map.pop(replied_msg_id)
        try:
            await client.send_message(user_id, event.text)
            logger.info(f"Replied to user {user_id}")
        except Exception as e:
            logger.error(f"Failed to reply to user {user_id}: {e}")

# === Start the client ===
logger.info("Starting the userbot...")
client.start()
logger.info("Userbot started. Waiting for messages...")
client.run_until_disconnected()
