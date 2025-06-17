import asyncio
import json
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

# ========= ASK CREDENTIALS =========
api_id = int(input("📟 Enter your API ID: ").strip())
api_hash = input("🔑 Enter your API Hash: ").strip()
bot_token = input("🤖 Enter your Bot Token: ").strip()
owner_id = int(input("👤 Enter your Telegram User ID (OWNER): ").strip())

# ========= INIT BOT =========
app = Client("bot_manager", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# ========= DATABASE =========
USERS_FILE = "users.json"
try:
    with open(USERS_FILE, "r") as f:
        USERS = set(json.load(f))
except:
    USERS = set()

broadcast_active = False


def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(list(USERS), f)


# ========= /start =========
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message: Message):
    user = message.from_user
    USERS.add(user.id)
    save_users()

    text = f"Hello {user.mention} 👋 welcome to our bot!"

    buttons = []
    if user.id == owner_id:
        buttons = [
            [InlineKeyboardButton("🔴 Live Users", callback_data="live_users")],
            [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")],
        ]

    await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons) if buttons else None)


# ========= Callback: Live Users =========
@app.on_callback_query(filters.regex("live_users"))
async def live_users(_, query: CallbackQuery):
    if query.from_user.id != owner_id:
        return await query.answer("Not for you!", show_alert=True)

    await query.answer()
    await query.edit_message_text(f"👥 Total users: {len(USERS)}")


# ========= Callback: Broadcast =========
@app.on_callback_query(filters.regex("broadcast"))
async def broadcast_entry(_, query: CallbackQuery):
    global broadcast_active

    if query.from_user.id != owner_id:
        return await query.answer("Not for you!", show_alert=True)

    broadcast_active = True
    await query.message.reply("📩 Send the message you want to broadcast.\n/cancel to stop.")


# ========= /cancel =========
@app.on_message(filters.command("cancel") & filters.private)
async def cancel_broadcast(_, message: Message):
    global broadcast_active
    if message.from_user.id != owner_id:
        return
    broadcast_active = False
    await message.reply("❌ Broadcast cancelled.")


# ========= Broadcast Message =========
@app.on_message(filters.private & ~filters.command(["start", "cancel"]))
async def broadcast_handler(_, message: Message):
    global broadcast_active
    if not broadcast_active or message.from_user.id != owner_id:
        return

    broadcast_active = False
    await message.reply("✅ Broadcasting...")

    success, fail = 0, 0
    for uid in list(USERS):
        try:
            await message.copy(chat_id=uid)
            success += 1
        except:
            fail += 1

    await message.reply(f"📢 Broadcast Complete!\n✅ Sent: {success}\n❌ Failed: {fail}")


# ========= RUN =========
print("✅ Starting bot...")
app.run()
