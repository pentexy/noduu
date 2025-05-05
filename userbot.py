import asyncio
import logging
import re
import time
import psutil
import os
import requests
from datetime import datetime
from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty

# **** Configuration ****
API_ID = 26416419
API_HASH = "c109c77f5823c847b1aeb7fbd4990cc4"
SESSION_NAME = "forward_to_nezuko"
OWNER_ID = 6748827895
VIRTUAL_BOT = "im_NezukoBot"

# **** Logging ****
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")

# **** Client Init ****
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
forward_map = {}
user_flags = {}
moderators = set()
start_time = time.time()

# **** Maintenance Mode ****
maintenance_mode = False
ai_module_on = True

# **** Startup Text ****
START_MSG = (
    "⧼ ᴠɪʀᴛᴜᴀʟ ʏᴏʀ ғᴏʀɢᴇʀ ⧽\n"
    "➤ ʏᴏᴜ'ʀᴇ ɴᴏᴡ ᴄᴏɴɴᴇᴄᴛᴇᴅ. ʙᴇ ᴍɪɴᴅꜰᴜʟ.\n"
    "➤ ᴜsᴇ /pm off or /pm on ᴛᴏ ᴛᴏɢɢʟᴇ ᴍᴇ.\n"
    "➤ ꜱᴇʀᴠᴇᴅ ʙʏ ᴅᴇᴠ ᴡɪᴛʜ ʟᴏᴠᴇ."
)

# **** Helper Functions ****
def is_owner_or_mod(user_id):
    return user_id == OWNER_ID or user_id in moderators

def get_uptime():
    return str(datetime.utcnow() - datetime.utcfromtimestamp(start_time)).split('.')[0]

async def get_dialog_count():
    dialogs = await client(GetDialogsRequest(offset_date=None, offset_id=0, offset_peer=InputPeerEmpty(), limit=100, hash=0))
    return len(dialogs.chats), len(dialogs.users)

# **** Typing Simulation ****
async def type_and_send(event, message, **kwargs):
    async with client.action(event.chat_id, "typing"):
        await asyncio.sleep(0.7)
        await event.reply(message, **kwargs)

# **** Main Message Handler ****
@client.on(events.NewMessage(incoming=True))
async def main_handler(event):
    sender = await event.get_sender()
    user_id = event.sender_id

    if not event.is_private or sender.bot:
        return

    if event.text.startswith("."):
        return

    if maintenance_mode or not ai_module_on or user_flags.get(user_id) == "off":
        return

    if user_id not in user_flags:
        user_flags[user_id] = "on"
        await type_and_send(event, START_MSG, link_preview=False)

    try:
        sent = await client.send_message(VIRTUAL_BOT, event.text)
        forward_map[sent.id] = (user_id, event.id)
        logger.info(f"Forwarded message to @{VIRTUAL_BOT} from {user_id}")
    except Exception as e:
        logger.error(f"Failed to forward: {e}")

# **** Response Handler ****
@client.on(events.NewMessage(from_users=VIRTUAL_BOT))
async def response_handler(event):
    if not event.is_reply:
        return

    original_msg = await event.get_reply_message()
    map_data = forward_map.pop(original_msg.id, None)

    if map_data is None:
        return

    user_id, reply_to = map_data

    if event.text:
        response_text = event.text.replace("Nezuko", "Yor")
        response_text = re.sub(r"@\w+", "@WingedAura", response_text)
        await client.send_message(user_id, f"**╭──『 ʀᴇᴘʟʏ 』──╮**\n{response_text}", reply_to=reply_to)
        logger.info(f"Replied to user {user_id} with text")
    elif event.media:
        file = await event.download_media()
        await client.send_file(user_id, file, voice_note=file.endswith(".ogg"), reply_to=reply_to)
        os.remove(file)
        logger.info(f"Replied to user {user_id} with media")

# **** Command Handler ****
@client.on(events.NewMessage(pattern=r"^.([a-z]+)(?:\s+(.*))?", from_users=lambda u: True))
async def command_handler(event):
    cmd, arg = event.pattern_match.groups()
    user_id = event.sender_id
    is_mod = is_owner_or_mod(user_id)

    if cmd == "ping" and is_mod:
        start = time.time()
        msg = await event.reply("**ᴘɪɴɢɪɴɢ...**")
        end = time.time()
        await msg.edit(f"**ᴘᴏɴɢ!** 🏓 `{round((end-start)*1000)}ms`")

    elif cmd == "weather" and is_mod:
        if not arg:
            return await event.reply("**ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴄɪᴛʏ ɴᴀᴍᴇ.**")
        try:
            res = requests.get(f"https://wttr.in/{arg}?format=3").text
            await event.reply(f"**ᴡᴇᴀᴛʜᴇʀ ɪɴ {arg.title()}**\n{res}")
        except:
            await event.reply("**ғᴀɪʟᴇᴅ ᴛᴏ ꜰᴇᴛᴄʜ ᴡᴇᴀᴛʜᴇʀ.**")

    elif cmd == "start":
        if user_id == OWNER_ID:
            await event.reply(
                "**⫸ ʜᴇʟᴘ ᴘᴀɴᴇʟ ⫷**\n"
                "`• .start` - ꜱʜᴏᴡ ᴛʜɪꜱ ᴘᴀɴᴇʟ\n"
                "`• .ping` - ᴄʜᴇᴄᴋ ʀᴇꜱᴘᴏɴꜱᴇ ᴛɪᴍᴇ\n"
                "`• .weather <city>` - ɢᴇᴛ ᴡᴇᴀᴛʜᴇʀ\n"
                "`• .maintenance` - ᴛᴏɢɢʟᴇ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ\n"
                "`• .onall` - ʀᴇ-ᴇɴᴀʙʟᴇ ᴍᴏᴅᴜʟᴇꜱ\n"
                "`• /pm on | off` - ᴛᴏɢɢʟᴇ ᴜꜱᴇʀ ᴀᴄᴄᴇꜱꜱ\n"
                "`• .stats .broadcast .addmod .removemod`..."
            )
        else:
            await type_and_send(event, START_MSG)

    elif not is_mod:
        return

    elif cmd == "maintenance":
        global maintenance_mode
        maintenance_mode = not maintenance_mode
        await event.reply(f"**ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ:** `{maintenance_mode}`")

    elif cmd == "onall":
        global ai_module_on
        ai_module_on = True
        await event.reply("**ᴀʟʟ ᴍᴏᴅᴜʟᴇꜱ ᴀʀᴇ ʟɪᴠᴇ ᴀɢᴀɪɴ!**")

    elif cmd == "stats":
        ram = psutil.virtual_memory()
        chats, users = await get_dialog_count()
        await event.reply(
            f"**ꜱʏꜱᴛᴇᴍ ꜱᴛᴀᴛꜱ:**\n"
            f"**• ᴜᴘᴛɪᴍᴇ:** `{get_uptime()}`\n"
            f"**• ʀᴀᴍ ᴜꜱᴀɢᴇ:** `{ram.percent}%`\n"
            f"**• ᴄʜᴀᴛꜱ:** `{chats}`\n"
            f"**• ᴜꜱᴇʀꜱ:** `{users}`"
        )

    elif cmd == "broadcast":
        if not arg:
            return await event.reply("**ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀꜱᴛ.**")
        count = 0
        async for dialog in client.iter_dialogs():
            if dialog.is_user:
                try:
                    await client.send_message(dialog.id, arg)
                    count += 1
                except:
                    continue
        await event.reply(f"**ʙʀᴏᴀᴅᴄᴀꜱᴛᴇᴅ ᴛᴏ `{count}` ᴅᴍꜱ.**")

    elif cmd == "broadcastchats":
        if not arg:
            return await event.reply("**ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀꜱᴛ.**")
        count = 0
        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                try:
                    await client.send_message(dialog.id, arg)
                    count += 1
                except:
                    continue
        await event.reply(f"**ʙʀᴏᴀᴅᴄᴀꜱᴛᴇᴅ ᴛᴏ `{count}` ᴄʜᴀᴛꜱ.**")

    elif cmd == "addmod":
        if event.is_reply:
            replied = await event.get_reply_message()
            moderators.add(replied.sender_id)
            await event.reply(f"**ᴀᴅᴅᴇᴅ `{replied.sender_id}` ᴀꜱ ᴍᴏᴅᴇʀᴀᴛᴏʀ.**")
        elif arg:
            entity = await client.get_entity(arg)
            moderators.add(entity.id)
            await event.reply(f"**ᴀᴅᴅᴇᴅ `{entity.id}` ᴀꜱ ᴍᴏᴅᴇʀᴀᴛᴏʀ.**")

    elif cmd == "removemod":
        if event.is_reply:
            replied = await event.get_reply_message()
            moderators.discard(replied.sender_id)
            await event.reply(f"**ʀᴇᴍᴏᴠᴇᴅ `{replied.sender_id}` ꜰʀᴏᴍ ᴍᴏᴅꜱ.**")
        elif arg:
            entity = await client.get_entity(arg)
            moderators.discard(entity.id)
            await event.reply(f"**ʀᴇᴍᴏᴠᴇᴅ `{entity.id}` ꜰʀᴏᴍ ᴍᴏᴅꜱ.**")

# **** /pm on & off ****
@client.on(events.NewMessage(pattern=r"/pm (on|off)"))
async def toggle_pm(event):
    user_id = event.sender_id
    state = event.pattern_match.group(1)
    user_flags[user_id] = state
    await event.reply(f"ᴘʀɪᴠᴀᴛᴇ ᴍᴇꜱꜱᴀɢᴇꜱ {state} ꜰᴏʀ ʏᴏᴜ.")

# **** Start the Bot ****
client.start()
logger.info("Bot is running...")
client.run_until_disconnected()
