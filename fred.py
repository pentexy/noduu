import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import os
import json

# === CONFIGURATION ===
BOT_TOKEN = input("🔐 Enter your bot token: ").strip()
API_ID = 26416419
API_HASH = "c109c77f5823c847b1aeb7fbd4990cc4"
OWNER_ID = 7703308577
USER_DATA_FILE = "users.json"

# === INIT BOT ===
bot = Client("CryptoBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# === HELPER FUNCTIONS ===
def load_users():
    if not os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "w") as f:
            json.dump([], f)
    with open(USER_DATA_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(users, f)

async def add_user(user_id):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        save_users(users)

# === HANDLERS ===

@bot.on_message(filters.command("start"))
async def start_handler(client, message: Message):
    await add_user(message.from_user.id)
    await message.reply(
        f"**Hey {message.from_user.mention}, welcome to our bot !**"
    )

@bot.on_message(filters.command("panel") & filters.user(OWNER_ID))
async def owner_panel(client, message: Message):
    total = len(load_users())
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 Real-Time Users", callback_data="user_count")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")]
    ])
    await message.reply(f"👑 Owner Panel\n\nTotal Users: `{total}`", reply_markup=keyboard)

@bot.on_callback_query(filters.user(OWNER_ID))
async def callback_handler(client, callback_query):
    data = callback_query.data
    if data == "user_count":
        total = len(load_users())
        await callback_query.answer()
        await callback_query.message.edit(
            f"📊 Real-Time Users:\n\n👥 Total Saved Users: `{total}`",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )
    elif data == "broadcast":
        await callback_query.answer()
        await callback_query.message.reply("📨 Send the message to broadcast:")
    elif data == "back":
        total = len(load_users())
        await callback_query.message.edit(
            f"👑 Owner Panel\n\nTotal Users: `{total}`",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👥 Real-Time Users", callback_data="user_count")],
                [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")]
            ])
        )

@bot.on_message(filters.text & filters.user(OWNER_ID))
async def handle_broadcast(client, message: Message):
    if message.reply_to_message and "Send the message to broadcast" in message.reply_to_message.text:
        users = load_users()
        total = 0
        failed = 0
        for user_id in users:
            try:
                await client.send_message(user_id, message.text)
                total += 1
                await asyncio.sleep(0.05)
            except:
                failed += 1
        await message.reply(f"✅ Broadcast Done\n\n✅ Sent: {total}\n❌ Failed: {failed}")

# Reply "Okay Sir!" in private chats when text message doesn't start with "/"
@bot.on_message(filters.private & filters.text & ~filters.command(["start", "panel"]))
async def handle_non_command_dm(client, message: Message):
    if not message.text.startswith("/"):
        await message.reply("**Okay Sir!**")

print("🚀 Bot is starting...")
bot.run()
