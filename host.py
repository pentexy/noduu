import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient

# CONFIG
API_ID = 26416419
API_HASH = "c109c77f5823c847b1aeb7fbd4990cc4"
OWNER_ID = 7072373613
MONGO_URI = "mongodb+srv://sumauyui:BmMk5HpP6Zy4wOsM@cluster0.xvnav2j.mongodb.net/myDatabase?retryWrites=true&w=majority"
USER_FILE = "crypto_news"

# Ask BOT_TOKEN in terminal
BOT_TOKEN = input("🔐 Enter your BOT TOKEN: ").strip()

# Bot Client
bot = Client("ton_update_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# MongoDB setup
mongo_client = MongoClient(MONGO_URI)
db = mongo_client.get_database()
users_col = db[USER_FILE]

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
        "<blockquote><b>🌟 TON + Telegram News: Changing the Internet Forever</b></blockquote>\n"
        "<b>Did you know? Telegram, under the visionary leadership of Pavel Durov, is integrating TON blockchain "
        "to empower millions with true decentralization and freedom. "
        "The world is witnessing a historic shift as Telegram becomes not just a messaging app, but a gateway to Web3. "
        "TON’s lightning-fast transactions, Telegram’s powerful user base, and Durov’s genius – what a combination! "
        "We salute Durov sir for redefining digital communication and finance. 🚀❤️ "
        "@toncoin @telegram</b>"
    )
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🌐 TONCOIN", url="https://t.me/toncoin"),
                InlineKeyboardButton("💎 DUROV SIR", url="https://t.me/durov"),
            ]
        ]
    )
    await message.reply(text, reply_markup=buttons)

# Random replies for non-command messages (private only)
@bot.on_message(filters.private & filters.text & ~filters.command(["start", "owner", "broadcast"]))
async def random_reply(client, message):
    replies = ["Hello 👋", "Yo Sir ✨", "Welcome 💎"]
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
            [InlineKeyboardButton("👥 Live Users", callback_data="live_users")],
            [InlineKeyboardButton("⚙️ Customize", callback_data="customize")],
        ]
    )
    await message.reply(panel, reply_markup=buttons)

# Callback queries (private only)
@bot.on_callback_query()
async def callbacks(client, callback_query):
    data = callback_query.data

    if data == "live_users":
        all_users = list(users_col.find({}))
        text = f"<b>👥 Live Users Count: {len(all_users)}</b>"
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
        text = f"<b>👥 Live Users Count: {len(all_users)}</b>"
        await callback_query.message.edit(text)

    elif data == "owner_panel":
        panel = (
            "<b>👑 Owner Panel</b>\n\n"
            "Choose an option below:"
        )
        buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("👥 Live Users", callback_data="live_users")],
                [InlineKeyboardButton("⚙️ Customize", callback_data="customize")],
            ]
        )
        await callback_query.message.edit(panel, reply_markup=buttons)

    elif data == "customize":
        await callback_query.message.edit("⚙️ <b>Customize options will appear here.</b>")

    await callback_query.answer()

# /broadcast command - reply to message to broadcast it (private only)
@bot.on_message(filters.private & filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_message(client, message):
    if message.reply_to_message:
        sent = 0
        failed = 0
        all_users = list(users_col.find({}))
        for user in all_users:
            uid = user["_id"]
            try:
                await message.reply_to_message.copy(uid)
                sent += 1
            except Exception as e:
                print(f"❌ Failed to send to {uid}: {e}")
                failed += 1
        await message.reply(f"✅ Broadcast sent to {sent} users.\n❌ Failed: {failed}")
    else:
        await message.reply("⚠️ Please reply to a message with /broadcast to send it to all users.")

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

# Start bot
print("TON Update Bot Running Sexy 🔥 With MongoDB (Broadcast reply-based)")
bot.run()
