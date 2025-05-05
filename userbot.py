import asyncio
import logging
import re
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaDocument

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
    
    try:
        sent = await client.send_message("im_NezukoBot", text)
        forward_map[sent.id] = (user_id, event.id)
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
        user_info = forward_map.pop(original_msg.id, None)

        if user_info is None:
            return

        user_id, reply_to_msg_id = user_info

        if event.text:
            text = event.raw_text
            if "Nezuko" in text:
                logger.info("Replacing 'Nezuko' with 'Yor'")
            text = text.replace("Nezuko", "Yor")

            if re.search(r"@\w+", text):
                logger.info("Replacing username with '@WingedAura'")
            text = re.sub(r"@\w+", "@WingedAura", text)

            async with client.action(user_id, 'typing'):
                await asyncio.sleep(1)
                await client.send_message(user_id, text, reply_to=reply_to_msg_id)

        elif event.media:
            async with client.action(user_id, 'record-audio'):
                path = await event.download_media()
                await client.send_file(user_id, path, reply_to=reply_to_msg_id)

        logger.info(f"Replied to user {user_id}")

    except Exception as e:
        logger.error(f"Error replying to user: {e}")

client.start()
logger.info("Bot is running. Waiting for messages...")
client.run_until_disconnected()
