from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import asyncio
from datetime import datetime
import getpass

# Ask for bot token in terminal
BOT_TOKEN = getpass.getpass("Enter your bot token: ")
API_ID = 26416419  # Replace with your actual api_id
API_HASH = "c109c77f5823c847b1aeb7fbd4990cc4"  # Replace with your actual api_hash
OWNER_ID = 6748827895  # Replace with your Telegram user ID

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Database setup
conn = sqlite3.connect("users.db")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)")
conn.commit()

def add_user(user_id):
    cur.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
    conn.commit()

def get_all_users():
    cur.execute("SELECT id FROM users")
    return [row[0] for row in cur.fetchall()]

@app.on_message(filters.command("start"))
async def start(client, message):
    add_user(message.from_user.id)
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📈 Crypto News", callback_data="crypto_news"),
         InlineKeyboardButton("ℹ️ About", callback_data="about")]
    ])
    await message.reply_text(
        "👋 Hello Sir\n#Crypto #Ton #NOTCOIN #Durov",
        reply_markup=buttons
    )

@app.on_callback_query()
async def handle_callback(client, callback_query):
    data = callback_query.data
    if data == "crypto_news":
        await callback_query.answer()
        await callback_query.message.edit_text("🗞️ Latest Crypto News Coming Soon!")
    elif data == "about":
        await callback_query.answer()
        await callback_query.message.edit_text("ℹ️ This bot is made for share crypto news & updates.")

@app.on_message(filters.private & filters.user(OWNER_ID))
async def owner_panel(client, message):
    text = message.text
    if text == "/users":
        users = get_all_users()
        await message.reply(f"👥 Total Users: {len(users)}")
    elif text == "/list":
        users = get_all_users()
        await message.reply_text("🧾 User List:\n" + "\n".join([str(u) for u in users]))
    elif text.startswith("/broadcast "):
        msg = text.split(" ", 1)[1]
        users = get_all_users()
        success = 0
        fail = 0
        for uid in users:
            try:
                await client.send_message(uid, msg)
                success += 1
            except:
                fail += 1
        await message.reply(f"✅ Sent: {success}\n❌ Failed: {fail}")
    else:
        await message.reply("📌 Commands:\n/users – Show user count\n/list – List users\n/broadcast <msg> – Broadcast to all users")

app.run()
