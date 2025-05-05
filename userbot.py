import logging
import re
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto

# === Your Telegram credentials ===
api_id = 26416419
api_hash = "c109c77f5823c847b1aeb7fbd4990cc4"
session_name = "forward_to_nezuko"

# === Logging setup ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Text constants ===
WELCOME_TEXT = (
    "**ʏᴏᴜ ᴀʀᴇ ɴᴏᴡ ɢᴏɪɴɢ ᴛᴏ ᴛᴀʟᴋ ᴛᴏ ⧼ [ᴠɪʀᴛᴜᴀʟ ʏᴏʀ ғᴏʀɢᴇʀ](https://t.me/YorXMusicBot) ⧽ — ᴍɪɴᴅ ʏᴏᴜʀ ᴡᴏʀᴅs ʙᴇғᴏʀᴇ sᴘᴇᴀᴋɪɴɢ!**\n\n"
    "⌬ **ᴜsᴇ** `/pm off` **||** `/pm on` **ᴛᴏ ᴅɪsᴀʙʟᴇ ⊶ᴏʀ⊷ ᴇɴᴀʙʟᴇ ᴍᴇ.**\n\n"
    "**ᴍᴀᴅᴇ ᴡɪᴛʜ** [ᴅᴇᴠ](https://t.me/WingedAura)💗"
)

# === Runtime state ===
forward_map = {}             # {bot_msg_id: (user_id, original_user_msg_id)}
pm_enabled = {}              # {user_id: True/False}
welcomed_users = set()       # user_ids who got welcome

# === Initialize Telegram client ===
client = TelegramClient(session_name, api_id, api_hash)

@client.on(events.NewMessage(incoming=True))
async def handle_user_message(event):
    sender = await event.get_sender()
    if not event.is_private or sender.bot:
        return

    user_id = event.sender_id
    msg_text = event.raw_text.strip()

    # Handle PM toggle commands
    if msg_text.lower() == "/pm off":
        pm_enabled[user_id] = False
        await event.reply("**ᴠɪʀᴛᴜᴀʟ ʏᴏᴜʀ ᴘᴍ ᴍᴏᴅᴇ ɪs sᴜᴄᴄᴇssғᴜʟʟʏ ᴅɪsᴀʙʟᴇᴅ !**\n**ᴜsᴇ ➠** `/pm on` **ᴛᴏ ᴇɴᴀʙʟᴇ ɪᴛ ᴀɴʏᴛɪᴍᴇ **")
        logger.info(f"User {user_id} disabled PM mode.")
        return
    elif msg_text.lower() == "/pm on":
        pm_enabled[user_id] = True
        await event.reply("**ᴠɪʀᴛᴜᴀʟ ʏᴏᴜʀ ᴘᴍ ᴍᴏᴅᴇ ɪs ᴄᴜʀʀᴇɴᴛʟʏ ᴇɴᴀʙʟᴇᴅ,ᴛᴀʟᴋ ғʀᴇᴇʟʏ 💗 !**")
        logger.info(f"User {user_id} enabled PM mode.")
        return

    # PM mode check
    if not pm_enabled.get(user_id, True):
        return

    # Welcome user once
    if user_id not in welcomed_users:
        await event.reply(WELCOME_TEXT)
        welcomed_users.add(user_id)

    try:
        # Forward message to @im_NezukoBot
        if event.text:
            fwd = await client.send_message("im_NezukoBot", event.text)
        elif event.media:
            fwd = await event.forward_to("im_NezukoBot")
        else:
            return

        forward_map[fwd.id] = (user_id, event.id)
        logger.info(f"Forwarded message to @im_NezukoBot from {user_id}")

    except Exception as e:
        logger.error(f"Failed to forward: {e}")
        await event.reply("Something went wrong forwarding your message.")

@client.on(events.NewMessage(from_users="im_NezukoBot"))
async def handle_bot_response(event):
    try:
        if not event.is_reply:
            return

        reply_to = await event.get_reply_message()
        user_info = forward_map.pop(reply_to.id, None)

        if not user_info:
            return

        user_id, reply_msg_id = user_info

        # Simulate typing or recording action
        async with client.action(user_id, 'typing' if event.text else 'record-audio'):
            if event.text:
                # Replace "Nezuko" and usernames
                text = event.raw_text.replace("Nezuko", "Yor")
                if "Nezuko" in event.raw_text:
                    logger.info("Replacing 'Nezuko' with 'Yor'")
                if re.search(r"@\w+", text):
                    logger.info("Replacing usernames with @WingedAura")
                text = re.sub(r"@\w+", "@WingedAura", text)

                await client.send_message(user_id, text, reply_to=reply_msg_id)

            elif event.media:
                await event.forward_to(user_id)
                logger.info(f"Forwarded media to {user_id}")

        logger.info(f"Responded to user {user_id}")

    except Exception as e:
        logger.error(f"Error replying to user: {e}")

# === Start the client ===
client.start()
logger.info("Bot is running. Waiting for messages...")
client.run_until_disconnected()
