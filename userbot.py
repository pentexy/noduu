import logging
import os
import re
from telethon import TelegramClient, events
from telethon.tl.functions.messages import SetTypingRequest
from telethon.tl.types import SendMessageTypingAction, SendMessageRecordAudioAction

# === CONFIG ===
API_ID = 26416419
API_HASH = "c109c77f5823c847b1aeb7fbd4990cc4"
SESSION_NAME = "forward_to_nezuko"

# === LOGGING ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === CLIENT SETUP ===
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# === STATE ===
forward_map = {}  # Maps forwarded msg ID from bot -> (user_id, user_msg_id)
pm_enabled = {}   # Per-user toggle: user_id -> True/False

WELCOME_TEXT = (
    "**ʏᴏᴜ ᴀʀᴇ ɴᴏᴡ ɢᴏɪɴɢ ᴛᴏ ᴛᴀʟᴋ ᴛᴏ ⧼ ᴠɪʀᴛᴜᴀʟ ʏᴏʀ ғᴏʀɢᴇʀ ⧽ — "
    "ᴍɪɴᴅ ʏᴏᴜʀ ᴡᴏʀᴅs ʙᴇғᴏʀᴇ sᴘᴇᴀᴋɪɴɢ!**\n\n"
    "⌬ **ᴜsᴇ /pm `off` || `on` ᴛᴏ ᴅɪsᴀʙʟᴇ ⊶ᴏʀ⊷ ᴇɴᴀʙʟᴇ ᴍᴇ.**"
)

# === HANDLE USER MESSAGES ===
@client.on(events.NewMessage(incoming=True))
async def handle_user_message(event):
    sender = await event.get_sender()
    if not event.is_private or sender.bot:
        return

    user_id = event.sender_id
    msg_text = event.raw_text.strip()

    # Check PM toggle
    if msg_text.lower() == "/pm off":
        pm_enabled[user_id] = False
        await event.reply("Virtual Yor PM mode disabled.")
        logger.info(f"User {user_id} disabled PM mode.")
        return
    elif msg_text.lower() == "/pm on":
        pm_enabled[user_id] = True
        await event.reply("Virtual Yor PM mode enabled.")
        logger.info(f"User {user_id} enabled PM mode.")
        return

    if not pm_enabled.get(user_id, True):
        return

    # Send welcome message on first contact
    if user_id not in forward_map.values():
        await event.reply(WELCOME_TEXT)

    try:
        fwd = await client.send_message("im_NezukoBot", msg_text)
        forward_map[fwd.id] = (user_id, event.id)
        logger.info(f"Forwarded message to @im_NezukoBot from {user_id}")
    except Exception as e:
        logger.error(f"Failed to forward: {e}")
        await event.reply("Something went wrong forwarding your message.")

# === HANDLE BOT RESPONSES ===
@client.on(events.NewMessage(from_users="im_NezukoBot"))
async def handle_bot_reply(event):
    try:
        if not event.is_reply:
            return

        original = await event.get_reply_message()
        user_info = forward_map.pop(original.id, None)
        if not user_info:
            return

        user_id, user_msg_id = user_info

        # Typing action
        if event.text:
            await client(SetTypingRequest(user_id, SendMessageTypingAction()))
        else:
            await client(SetTypingRequest(user_id, SendMessageRecordAudioAction()))

        # Text reply
        if event.text:
            text = event.text

            if "Nezuko" in text:
                logger.info("Replacing 'Nezuko' with 'Yor'")
            text = text.replace("Nezuko", "Yor")

            if re.search(r"@\w+", text):
                logger.info("Replacing usernames with '@WingedAura'")
            text = re.sub(r"@\w+", "@WingedAura", text)

            await client.send_message(user_id, text, reply_to=user_msg_id)

        # Media reply
        elif event.media:
            path = await event.download_media()
            await client.send_file(user_id, path, reply_to=user_msg_id)
            os.remove(path)

        logger.info(f"Sent response to user {user_id}")

    except Exception as e:
        logger.error(f"Error in bot reply handler: {e}")

# === RUN ===
client.start()
logger.info("Bot is running...")
client.run_until_disconnected()
