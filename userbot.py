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

async def type_and_send(event, message, **kwargs):
    async with client.action(event.chat_id, "typing"):
        await asyncio.sleep(0.7)
        await event.reply(message, **kwargs)

# **** Message Handler ****
@client.on(events.NewMessage(incoming=True))
async def main_handler(event):
    sender = await event.get_sender()
    user_id = event.sender_id

    if not event.is_private or sender.bot:
        return
    if event.text and event.text.startswith("."):
        return
    if maintenance_mode or not ai_module_on or user_flags.get(user_id) == "off":
        return

    if user_id not in user_flags:
        user_flags[user_id] = "on"
        await type_and_send(event, START_MSG, link_preview=False)

    try:
        sent = await client.send_message(VIRTUAL_BOT, event.text)
        forward_map[sent.id] = (user_id, event.id)
        logger.info(f"Forwarded to @{VIRTUAL_BOT} from {user_id}")
    except Exception as e:
        logger.error(f"Forward failed: {e}")

# **** Response Handler from Nezuko ****
@client.on(events.NewMessage(incoming=True))
async def response_handler(event):
    if not event.is_private:
        return
    if not event.sender or event.sender.username != VIRTUAL_BOT.replace("@", ""):
        return
    if not event.is_reply:
        return

    original = await event.get_reply_message()
    data = forward_map.pop(original.id, None)
    if not data:
        return

    user_id, reply_to = data

    try:
        if event.text:
            text = event.text.replace("Nezuko", "Yor")
            text = re.sub(r"@\w+", "@WingedAura", text)
            await client.send_message(user_id, text, reply_to=reply_to)
        elif event.media:
            file = await event.download_media()
            await client.send_file(user_id, file, voice_note=file.endswith(".ogg"), reply_to=reply_to)
            os.remove(file)
        logger.info(f"Relayed response to {user_id}")
    except Exception as e:
        logger.error(f"Reply failed: {e}")

# **** Commands ****
@client.on(events.NewMessage(pattern=r"^.([a-z]+)(?:\s+(.*))?"))
async def command_handler(event):
    cmd, arg = event.pattern_match.groups()
    user_id = event.sender_id
    if not is_owner_or_mod(user_id):
        return

    if cmd == "ping":
        start = time.time()
        msg = await event.reply("**ᴘɪɴɢɪɴɢ...**")
        end = time.time()
        await msg.edit(f"**ᴘᴏɴɢ!** 🏓 `{round((end-start)*1000)}ms`")

    elif cmd == "weather":
        if not arg:
            return await event.reply("**ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴄɪᴛʏ.**")
        try:
            res = requests.get(f"https://wttr.in/{arg}?format=3").text
            await event.reply(f"**ᴡᴇᴀᴛʜᴇʀ:**\n{res}")
        except:
            await event.reply("**ғᴀɪʟᴇᴅ ᴛᴏ ꜰᴇᴛᴄʜ.**")

    elif cmd == "start":
        if user_id == OWNER_ID:
            await event.reply(
                "**⫸ ʜᴇʟᴘ ᴘᴀɴᴇʟ ⫷**\n"
                "`• .start` - Show this panel\n"
                "`• .ping` - Check response\n"
                "`• .weather <city>` - Weather info\n"
                "`• .maintenance` - Toggle mode\n"
                "`• .onall` - Reactivate AI\n"
                "`• .addmod / .removemod`\n"
                "`• .broadcast / .broadcastchats`\n"
                "`• .stats` - System stats"
            )
        else:
            await type_and_send(event, START_MSG)

    elif cmd == "maintenance":
        global maintenance_mode
        maintenance_mode = not maintenance_mode
        await event.reply(f"**ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ:** `{maintenance_mode}`")

    elif cmd == "onall":
        global ai_module_on
        ai_module_on = True
        await event.reply("**ᴀɪ ʀᴇᴇɴᴀʙʟᴇᴅ.**")

    elif cmd == "stats":
        ram = psutil.virtual_memory()
        chats, users = await get_dialog_count()
        await event.reply(
            f"**ꜱʏꜱᴛᴇᴍ ꜱᴛᴀᴛꜱ:**\n"
            f"• ᴜᴘᴛɪᴍᴇ: `{get_uptime()}`\n"
            f"• ʀᴀᴍ: `{ram.percent}%`\n"
            f"• ᴄʜᴀᴛꜱ: `{chats}` | ᴜꜱᴇʀꜱ: `{users}`"
        )

    elif cmd == "broadcast":
        if not arg:
            return await event.reply("**ᴘʟᴇᴀꜱᴇ ᴘʀᴏᴠɪᴅᴇ ᴛᴇxᴛ.**")
        count = 0
        async for dialog in client.iter_dialogs():
            if dialog.is_user:
                try:
                    await client.send_message(dialog.id, arg)
                    count += 1
                except:
                    continue
        await event.reply(f"**sᴇɴᴛ ᴛᴏ `{count}` ᴜꜱᴇʀꜱ.**")

    elif cmd == "broadcastchats":
        if not arg:
            return await event.reply("**ɢɪᴠᴇ ᴍᴇꜱꜱᴀɢᴇ.**")
        count = 0
        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                try:
                    await client.send_message(dialog.id, arg)
                    count += 1
                except:
                    continue
        await event.reply(f"**sᴇɴᴛ ᴛᴏ `{count}` ᴄʜᴀᴛꜱ.**")

    elif cmd == "addmod":
        if event.is_reply:
            r = await event.get_reply_message()
            moderators.add(r.sender_id)
            await event.reply(f"**ᴀᴅᴅᴇᴅ `{r.sender_id}`.**")
        elif arg:
            e = await client.get_entity(arg)
            moderators.add(e.id)
            await event.reply(f"**ᴀᴅᴅᴇᴅ `{e.id}`.**")

    elif cmd == "removemod":
        if event.is_reply:
            r = await event.get_reply_message()
            moderators.discard(r.sender_id)
            await event.reply(f"**ʀᴇᴍᴏᴠᴇᴅ `{r.sender_id}`.**")
        elif arg:
            e = await client.get_entity(arg)
            moderators.discard(e.id)
            await event.reply(f"**ʀᴇᴍᴏᴠᴇᴅ `{e.id}`.**")

# **** /pm on & off ****
@client.on(events.NewMessage(pattern=r"/pm (on|off)"))
async def toggle_pm(event):
    user_id = event.sender_id
    state = event.pattern_match.group(1)
    user_flags[user_id] = state
    await event.reply(f"ᴘʀɪᴠᴀᴛᴇ ᴍᴇꜱꜱᴀɢᴇꜱ `{state}` ꜰᴏʀ ʏᴏᴜ.")

# **** Start Bot ****
client.start()
logger.info("Bot is running...")
client.run_until_disconnected()
