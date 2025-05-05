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
@client.on(events.NewMessage(from_users="im_NezukoBot"))
async def handler_response(event):
    try:
        if event.is_private and event.reply_to_msg_id in forward_map:
            user_id = forward_map.pop(event.reply_to_msg_id)

            if event.text:
                # Replacements
                response_text = event.text
                response_text = response_text.replace("Nezuko", "Yor")
                response_text = re.sub(r'@\w+', '@WingedAura', response_text)

                await client.send_message(user_id, response_text)
            elif event.media:
                await event.copy_to(user_id)

            logger.info(f"Replied to user {user_id}")

    except Exception as e:
        logger.error(f"Error in response handler: {e}")

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
