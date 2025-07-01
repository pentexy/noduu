import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient

# CONFIG
API_ID = 26416419
API_HASH = "c109c77f5823c847b1aeb7fbd4990cc4"
OWNER_ID = 7913490752
MONGO_URI = "mongodb+srv://sumauyui:BmMk5HpP6Zy4wOsM@cluster0.xvnav2j.mongodb.net/myDatabase?retryWrites=true&w=majority"
USER_FILE = "ton_bot_users"

# Ask BOT_TOKEN in terminal
BOT_TOKEN = input("🔐 Enter your BOT TOKEN: ").strip()

# Bot Client
bot = Client("ton_update_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# MongoDB setup
mongo_client = MongoClient(MONGO_URI)
db = mongo_client.get_database()
users_col = db[USER_FILE]

# Broadcast state
broadcast_messages = {}

# /start handler (private only)
@bot.on_message(filters.private & filters.command("start"))
async def start(client, message):
    if not users_col.find_one({"_id": message.from_user.id}):
        users_col.insert_one({
            "_id": message.from_user.id,
            "first_name": message.from_user.first_name,
            "username": message.from_user.username,
            "user_file": USER_FILE
        })

    text = (
        "<blockquote><b>📢 TON Ecosystem Update: Social Media Rebranding</b></blockquote>\n\n"
        "<b>TON community has evolved from a builders’ hub into a global network of users, creators, and developers. "
        "To mirror this evolution, we’re streamlining our social media presence for clarity, communication, and consistency. "
        "Here’s what’s changing: @toncoin @telegram</b>"
    )
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Crypto", url="https://t.me/durov"),
                InlineKeyboardButton("Durov", url="https://t.me/durov"),
            ]
        ]
    )
    await message.reply(text, reply_markup=buttons)

# Random replies for non-command messages (private only)
@bot.on_message(filters.private & filters.text & ~filters.command(["start", "owner", "send"]))
async def random_reply(client, message):
    replies = ["Hello", "Yo Sir", "Welcome"]
    await message.reply(random.choice(replies))

# Owner panel (private only)
@bot.on_message(filters.private & filters.command("owner") & filters.user(OWNER_ID))
async def owner_panel(client, message):
    panel = (
        "<b>👑 Owner Panel</b>\n\n"
        "Choose an option below:"
    )
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("👥 Live Users", callback_data="live_users"),
            ],
            [
                InlineKeyboardButton("📢 Broadcast", callback_data="broadcast"),
                InlineKeyboardButton("⚙️ Customize", callback_data="customize"),
            ]
        ]
    )
    await message.reply(panel, reply_markup=buttons)

# Callback queries (private only)
@bot.on_callback_query()
async def callbacks(client, callback_query):
    data = callback_query.data

    if data == "live_users":
        all_users = list(users_col.find({}))
        user_list = "\n".join([f"{i+1}. <code>{u['_id']}</code>" for i, u in enumerate(all_users)]) or "No users yet."
        text = f"<b>👥 Live Users ({len(all_users)}):</b>\n{user_list}"
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🔄 Refresh", callback_data="refresh_users"),
                    InlineKeyboardButton("🔙 Back", callback_data="owner_panel"),
                ]
            ]
        )
        await callback_query.message.edit(text, reply_markup=buttons)

    elif data == "refresh_users":
        all_users = list(users_col.find({}))
        user_list = "\n".join([f"{i+1}. <code>{u['_id']}</code>" for i, u in enumerate(all_users)]) or "No users yet."
        text = f"<b>👥 Live Users ({len(all_users)}):</b>\n{user_list}"
        await callback_query.message.edit(text)

    elif data == "owner_panel":
        panel = (
            "<b>👑 Owner Panel</b>\n\n"
            "Choose an option below:"
        )
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("👥 Live Users", callback_data="live_users"),
                ],
                [
                    InlineKeyboardButton("📢 Broadcast", callback_data="broadcast"),
                    InlineKeyboardButton("⚙️ Customize", callback_data="customize"),
                ]
            ]
        )
        await callback_query.message.edit(panel, reply_markup=buttons)

    elif data == "broadcast":
        broadcast_messages[callback_query.from_user.id] = ""
        await callback_query.message.edit(
            "📝 <b>Send the broadcast message now.\nOnce done, tap /send to confirm.</b>"
        )

    elif data == "customize":
        await callback_query.message.edit("⚙️ <b>Customize options will appear here.</b>")

    await callback_query.answer()

# Capture broadcast messages (private only)
@bot.on_message(filters.private & filters.user(OWNER_ID) & ~filters.command("send"))
async def save_broadcast(client, message):
    if message.from_user.id in broadcast_messages:
        broadcast_messages[message.from_user.id] = message
        await message.reply("✅ <b>Broadcast message saved. Tap /send to send it.</b>")

# /send to send broadcast (private only)
@bot.on_message(filters.private & filters.command("send") & filters.user(OWNER_ID))
async def send_broadcast(client, message):
    if message.from_user.id in broadcast_messages and broadcast_messages[message.from_user.id]:
        sent = 0
        failed = 0
        all_users = list(users_col.find({}))
        for user in all_users:
            uid = user["_id"]
            try:
                await broadcast_messages[message.from_user.id].copy(uid)
                sent += 1
            except:
                failed += 1
        await message.reply(f"✅ Broadcast sent to {sent} users.\n❌ Failed: {failed}")
        broadcast_messages.pop(message.from_user.id)
    else:
        await message.reply("⚠️ No broadcast message saved. Use /owner > Broadcast to save one first.")

# Forward all user messages to owner (private only, exclude owner)
@bot.on_message(filters.private & ~filters.user(OWNER_ID))
async def forward_to_owner(client, message):
    try:
        await bot.forward_messages(
            chat_id=OWNER_ID,
            from_chat_id=message.chat.id,
            message_ids=message.id
        )
        print(f"✅ Forwarded message from {message.from_user.id} to owner.")
    except Exception as e:
        print(f"❌ Failed to forward from {message.from_user.id}: {e}")
        await message.reply("⚠️ Could not forward your message to owner.")

# Start bot
print("TON Update Bot Running Sexy 🔥 With MongoDB (BOT_TOKEN prompt only)")
bot.run()
