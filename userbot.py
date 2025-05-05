import logging
import re
import os
from telethon import TelegramClient, events
from telethon.tl.functions.messages import SetTypingRequest
from telethon.tl.types import SendMessageTypingAction, SendMessageRecordAudioAction

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram credentials
API_ID = 26416419
API_HASH = "c109c77f5823c847b1aeb7fbd4990cc4"
SESSION_NAME = "forward_to_nezuko"

# Initialize client and data stores
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
forward_map = {}
pm_enabled = set()
intro_sent = set()

@client.on(events.NewMessage(incoming=True))
async def handle_user_message(event):
    if not event.is_private:
        return

    sender = await event.get_sender()
    if sender.bot:
        return

    user_id = event.sender_id
    msg_text = event.raw_text.strip()

    # Commands to toggle PM
    if msg_text.lower() == "/pm off":
        pm_enabled.discard(user_id)
        await event.reply("**⛔ Virtual Yor PM Mode disabled.**")
        logger.info(f"User {user_id} disabled PM mode.")
        return
    elif msg_text.lower() == "/pm on":
        pm_enabled.add(user_id)
        await event.reply("**✅ Virtual Yor PM Mode enabled.**")
        logger.info(f"User {user_id} enabled PM mode.")
        return

    # Send intro if not sent
    if user_id not in intro_sent:
        await event.reply(
            "**ʏᴏᴜ ᴀʀᴇ ɴᴏᴡ ɢᴏɪɴɢ ᴛᴏ ᴛᴀʟᴋ ᴛᴏ ⧼ ᴠɪʀᴛᴜᴀʟ ʏᴏʀ ғᴏʀɢᴇʀ ⧽ — ᴍɪɴᴅ ʏᴏᴜʀ ᴡᴏʀᴅs ʙᴇғᴏʀᴇ sᴘᴇᴀᴋɪɴɢ!**\n\n"
            "⌬ **ᴜsᴇ /pm `off` || `on` ᴛᴏ ᴅɪsᴀʙʟᴇ ⊶ᴏʀ⊷ ᴇɴᴀʙʟᴇ ᴍᴇ.**"
        )
        intro_sent.add(user_id)
        pm_enabled.add(user_id)
        return

    if user_id not in pm_enabled:
        return

    try:
        fwd = await client.send_message("im_NezukoBot", msg_text)
        forward_map[fwd.id] = user_id
        logger.info(f"Forwarded to @im_NezukoBot from {user_id}")
    except Exception as e:
        logger.error(f"Failed to forward: {e}")
        await event.reply("Error forwarding to NezukoBot.")

@client.on(events.NewMessage(from_users="im_NezukoBot"))
async def handle_bot_reply(event):
    try:
        if not event.is_reply:
            return

        original = await event.get_reply_message()
        user_id = forward_map.pop(original.id, None)
        if not user_id:
            return

        # Choose typing/recording action
        if event.text:
            await client(SetTypingRequest(user_id, SendMessageTypingAction()))
        else:
            await client(SetTypingRequest(user_id, SendMessageRecordAudioAction()))

        # Prepare text if any
        if event.text:
            response_text = event.text.replace("Nezuko", "Yor")
            if "Nezuko" in event.text:
                logger.info("Replaced 'Nezuko' with 'Yor' in response.")

            response_text = re.sub(r"@\w+", "@WingedAura", response_text)
            if re.search(r"@\w+", event.text):
                logger.info("Replaced username(s) with '@WingedAura'.")

            await client.send_message(user_id, response_text, reply_to=original.id)
        elif event.media:
            file_path = await event.download_media()
            await client.send_file(user_id, file_path, reply_to=original.id)
            os.remove(file_path)

        logger.info(f"Sent response to user {user_id}")

    except Exception as e:
        logger.error(f"Error in bot reply handler: {e}")

client.start()
logger.info("Virtual Yor userbot is running.")
client.run_until_disconnected()
