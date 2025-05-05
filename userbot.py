import asyncio
import logging
import re
import time
import psutil
import os
import requests
from datetime import datetime
from telethon import TelegramClient, events

API_ID = 26416419
API_HASH = "c109c77f5823c847b1aeb7fbd4990cc4"
SESSION_NAME = "forward_to_nezuko"
OWNER_ID = 6748827895
VIRTUAL_BOT = "im_NezukoBot"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
forward_map = {}
user_flags = {}
moderators = set()
start_time = time.time()

maintenance_mode = False
ai_module_on = True

START_MSG = (
    "ʏᴏᴜ ᴀʀᴇ ɴᴏᴡ ᴛᴀʟᴋɪɴɢ ᴛᴏ ⧼ ᴠɪʀᴛᴜᴀʟ ʏᴏʀ ꜰᴏʀɢᴇʀ ⧽\n"
    "๏ ᴍɪɴᴅ ʏᴏᴜʀ ᴡᴏʀᴅꜱ ʙᴇꜰᴏʀᴇ ꜱᴘᴇᴀᴋɪɴɢ!\n\n"
    "⌬ ᴜꜱᴇ /pm on || /pm off ᴛᴏ ⊶ᴇɴᴀʙʟᴇ⊷ ᴏʀ ⊶ᴅɪꜱᴀʙʟᴇ⊷ ᴍᴇ.\n\n"
    "➪ ᴍᴀᴅᴇ ᴡɪᴛʜ ᴅᴇᴠ 💗"
)

def is_owner_or_mod(uid):
    return uid == OWNER_ID or uid in moderators

def get_uptime():
    return str(datetime.utcnow() - datetime.utcfromtimestamp(start_time)).split('.')[0]

async def get_dialog_stats():
    chats = 0
    users = 0
    admin_chats = []
    async for dialog in client.iter_dialogs():
        if dialog.is_group or dialog.is_channel:
            chats += 1
            if dialog.entity.admin_rights:
                admin_chats.append(dialog.name)
        elif dialog.is_user:
            users += 1
    return chats, users, admin_chats

# Main Handler
# ... [imports and constants stay unchanged above this point]

@client.on(events.NewMessage(from_users=VIRTUAL_BOT))
async def reply_handler(event):
    if not event.is_reply:
        return
    original = await event.get_reply_message()
    map_data = forward_map.pop(original.id, None)
    if not map_data:
        return

    uid, reply_to = map_data
    user = await client.get_entity(uid)

    try:
        if event.text:
            text = event.text.replace("Nezuko", "Yor")
            text = re.sub(r"@\w+", "@WingedAura", text)
            async with client.action(user.id, 'typing'):
                await asyncio.sleep(0.35)
            await client.send_message(user.id, text, reply_to=reply_to)

        elif event.media:
            file_path = await event.download_media()
            file_ext = os.path.splitext(file_path)[1].lower()
            is_voice = file_ext in [".ogg", ".mp3", ".wav", ".m4a"]

            action = 'record-audio' if is_voice else 'typing'
            async with client.action(user.id, action):
                await asyncio.sleep(0.35)
            await client.send_file(user.id, file_path, voice_note=is_voice, reply_to=reply_to)

            if os.path.exists(file_path):
                os.remove(file_path)

    except Exception as e:
        logger.error(f"Error in forwarding reply: {e}")

# ... [rest of your code stays unchanged below this point]

@client.on(events.NewMessage(from_users=VIRTUAL_BOT))
async def reply_handler(event):
    if not event.is_reply:
        return
    original = await event.get_reply_message()
    map_data = forward_map.pop(original.id, None)
    if not map_data:
        return
    uid, reply_to = map_data
    user = await client.get_entity(uid)
    if event.text:
        text = event.text.replace("Nezuko", "Yor")
        text = re.sub(r"@\w+", "@WingedAura", text)
        async with client.action(user.id, 'typing'):
            await asyncio.sleep(1)
        await client.send_message(user.id, text, reply_to=reply_to)
    elif event.media:
        file = await event.download_media()
        async with client.action(user.id, 'record-audio'):
            await asyncio.sleep(1)
        await client.send_file(user.id, file, voice_note=True, reply_to=reply_to)
        os.remove(file)

@client.on(events.NewMessage(pattern=r"^.([a-z]+)(?:\s+(.*))?", incoming=True))
async def command_handler(event):
    cmd, arg = event.pattern_match.groups()
    uid = event.sender_id
    if not is_owner_or_mod(uid):
        return  # silently ignore for normal users

    if cmd == "start":
        await event.reply(
            "```⫷ ᴍᴀɪɴ ᴄᴏɴᴛʀᴏʟ ᴘᴀɴᴇʟ ⫸```\n"
            "• `.start` — **ꜱʜᴏᴡ ᴛʜɪꜱ ᴘᴀɴᴇʟ**\n"
            "• `.ping` — **ᴘɪɴɢ ᴛᴇꜱᴛ**\n"
            "• `.weather` <city> — **ᴄɪᴛʏ ᴡᴇᴀᴛʜᴇʀ**\n"
            "• `.maintenance` — **ᴛᴏɢɢʟᴇ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ**\n"
            "• `.onall` / `.offall` — **ᴀɪ ᴍᴏᴅᴜʟᴇ ᴛᴏɢɢʟᴇ**\n"
            "• `.stats` — ʙᴏᴛ ꜱᴛᴀᴛꜱ\n"
            "• `.broadcast` <text> — **ᴅᴍ ᴍᴇꜱꜱᴀɢᴇ**\n"
            "• `.broadcastchats` <text> — **ɢʀᴏᴜᴘ/ᴄʜᴀɴɴᴇʟ**\n"
            "• `.addmod` / `.removemod` — **ᴍᴏᴅ ᴍᴀɴᴀɢᴇ**\n"
            "• `/pm on` | `off` — **ᴜꜱᴇʀ ᴛᴏɢɢʟᴇ**"
        )
    elif cmd == "ping":
        start = time.time()
        msg = await event.reply("**ᴘɪɴɢɪɴɢ...**")
        end = time.time()
        await msg.edit(f"**ᴘᴏɴɢ! 🏓** `{round((end-start)*1000)}ms`")
    elif cmd == "weather":
        if not arg:
            return await event.reply("ᴘʀᴏᴠɪᴅᴇ ᴀ ᴄɪᴛʏ ɴᴀᴍᴇ.")
        try:
            res = requests.get(f"https://wttr.in/{arg}?format=3").text
            await event.reply(f"ᴡᴇᴀᴛʜᴇʀ ɪɴ {arg.title()}\n{res}")
        except:
            await event.reply("ᴇʀʀᴏʀ ꜰᴇᴛᴄʜɪɴɢ ᴡᴇᴀᴛʜᴇʀ.")
    elif cmd == "maintenance":
        global maintenance_mode
        maintenance_mode = not maintenance_mode
        await event.reply(f"ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ: {maintenance_mode}")
    elif cmd == "onall":
        global ai_module_on
        ai_module_on = True
        await event.reply("**ᴀʟʟ ᴍᴏᴅᴜʟᴇꜱ ᴀᴄᴛɪᴠᴀᴛᴇᴅ.**")
    elif cmd == "offall":
        ai_module_on = False
        await event.reply("**ᴀʟʟ ᴍᴏᴅᴜʟᴇꜱ ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ.**")
    elif cmd == "stats":
        ram = psutil.virtual_memory()
        chats, users, admins = await get_dialog_stats()
        admin_list = "\n".join(f"• {chat}" for chat in admins)
        await event.reply(
            f"ꜱʏꜱᴛᴇᴍ ꜱᴛᴀᴛꜱ:\n"
            f"• ᴜᴘᴛɪᴍᴇ: {get_uptime()}\n"
            f"• ʀᴀᴍ: {ram.percent}%\n"
            f"• ᴄʜᴀᴛꜱ: {chats}\n"
            f"• ᴜꜱᴇʀꜱ: {users}\n"
        )
    elif cmd == "broadcast":
        if not arg:
            return await event.reply("ᴇɴᴛᴇʀ ᴛᴇxᴛ ᴛᴏ ʙʀᴏᴀᴅᴄᴀꜱᴛ.")
        count = 0
        async for d in client.iter_dialogs():
            if d.is_user:
                try:
                    await client.send_message(d.id, arg)
                    count += 1
                except:
                    continue
        await event.reply(f"**ʙʀᴏᴀᴅᴄᴀꜱᴛᴇᴅ ᴛᴏ** `{count}` **ᴜꜱᴇʀꜱ.**")
    elif cmd == "broadcastchats":
        if not arg:
            return await event.reply("ᴇɴᴛᴇʀ ᴛᴇxᴛ ᴛᴏ ʙʀᴏᴀᴅᴄᴀꜱᴛ.")
        count = 0
        async for d in client.iter_dialogs():
            if d.is_group or d.is_channel:
                try:
                    await client.send_message(d.id, arg)
                    count += 1
                except:
                    continue
        await event.reply(f"**ʙʀᴏᴀᴅᴄᴀꜱᴛᴇᴅ ᴛᴏ** `{count}` **ᴄʜᴀᴛꜱ**.")
    elif cmd == "addmod":
        if event.is_reply:
            r = await event.get_reply_message()
            moderators.add(r.sender_id)
            await event.reply(f"ᴀᴅᴅᴇᴅ {r.sender_id} ᴀꜱ ᴍᴏᴅ.")
        elif arg:
            e = await client.get_entity(arg)
            moderators.add(e.id)
            await event.reply(f"**ᴀᴅᴅᴇᴅ {e.id} ᴀꜱ ᴍᴏᴅ.**")
    elif cmd == "removemod":
        if event.is_reply:
            r = await event.get_reply_message()
            moderators.discard(r.sender_id)
            await event.reply(f"ʀᴇᴍᴏᴠᴇᴅ {r.sender_id} ꜰʀᴏᴍ ᴍᴏᴅꜱ.")
        elif arg:
            e = await client.get_entity(arg)
            moderators.discard(e.id)
            await event.reply(f"ʀᴇᴍᴏᴠᴇᴅ {e.id} ꜰʀᴏᴍ ᴍᴏᴅꜱ.")

@client.on(events.NewMessage(pattern=r"/pm (on|off)"))
async def toggle_pm(event):
    uid = event.sender_id
    user_flags[uid] = event.pattern_match.group(1)
    await event.reply(f"ᴘʀɪᴠᴀᴛᴇ ᴍᴇꜱꜱᴀɢᴇꜱ {user_flags[uid]} ꜰᴏʀ ʏᴏᴜ.")

client.start()
logger.info("Bot running...")
client.run_until_disconnected()
