import asyncio
from telethon import TelegramClient, events
import logging

logging.basicConfig(level=logging.INFO)

API_ID = 26416419
API_HASH = "c109c77f5823c847b1aeb7fbd4990cc4"
SESSION_NAME = "forward_to_nezuko"

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# Mapping: message ID sent to Nezuko -> original user ID
message_map = {}

@client.on(events.NewMessage(incoming=True))
async def handle_private_message(event):
    if not event.is_private or event.sender_id == (await client.get_me()).id:
        return

    try:
        # Forward message content to @im_NezukoBot
        sent = await client.send_message("im_NezukoBot", event.text)
        message_map[sent.id] = event.sender_id
        logging.info(f"Forwarded message to @im_NezukoBot from {event.sender_id}")
    except Exception as e:
        logging.error(f"Error forwarding to NezukoBot: {e}")
        await event.reply("Error: Failed to forward message.")

@client.on(events.NewMessage(from_users="im_NezukoBot"))
async def handle_nezuko_response(event):
    # Get the original user based on reply_to_msg_id
    reply_to = event.reply_to_msg_id
    user_id = message_map.get(reply_to)

    if user_id:
        try:
            if event.text:
                await client.send_message(user_id, event.text)
            elif event.media:
                await client.send_file(user_id, event.media)

            logging.info(f"Replied to user {user_id}")
            del message_map[reply_to]  # Clean up
        except Exception as e:
            logging.error(f"Error sending response: {e}")

async def main():
    await client.start()
    print("Bot is running and waiting for private messages...")
    await client.run_until_disconnected()

asyncio.run(main())
