import asyncio
import logging
import re
from telethon import TelegramClient, events

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# === Your Telegram API Credentials ===
api_id = 26416419
api_hash = "c109c77f5823c847b1aeb7fbd4990cc4"
session_name = "forward_to_nezuko"

# Create the client
client = TelegramClient(session_name, api_id, api_hash)

# Map to track forwarded messages
forward_map = {}

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    try:
        # Only handle private messages from real users
        if not event.is_private or not event.sender:
            return

        sender = await event.get_sender()
        if sender.bot:
            return

        # Forward message to bot
        fwd_msg = await client.send_message("im_NezukoBot", event.text)
        forward_map[fwd_msg.id] = event.sender_id
        logger.info(f"Forwarded message to @im_NezukoBot from {event.sender_id}")

    except Exception as e:
        logger.error(f"Error in handler: {e}")

@client.on(events.NewMessage(from_users="im_NezukoBot"))
async def handler_response(event):
    try:
        if event.is_private and event.reply_to_msg_id in forward_map:
            user_id = forward_map.pop(event.reply_to_msg_id)

            if event.text:
                response_text = event.text
                # Replace 'Nezuko' with 'Yor' (case-sensitive)
                response_text = response_text.replace("Nezuko", "Yor")
                # Replace @usernames with @WingedAura
                response_text = re.sub(r'@\w+', '@WingedAura', response_text)

                await client.send_message(user_id, response_text)
                logger.info(f"Replied to user {user_id}")
            elif event.media:
                await event.copy_to(user_id)
                logger.info(f"Copied media to user {user_id}")

    except Exception as e:
        logger.error(f"Error in response handler: {e}")

async def main():
    await client.start()
    print("Userbot is running. Waiting for messages...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
