import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from http.cookiejar import MozillaCookieJar

# ==== Replace with your bot token ====
API_ID = 26416419   # Get from https://my.telegram.org
API_HASH = "c109c77f5823c847b1aeb7fbd4990cc4"
BOT_TOKEN = "7660075641:AAEpTjnqCLR4M2_DsA6j5e6TRxPpsNUSqKc"
# =====================================

app = Client("yt_cookie_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Start command
@app.on_message(filters.command("start") & filters.private)
async def start(client, message: Message):
    await message.reply("👋 Send me your YouTube `cookies.txt` file, and I'll check if it's valid or expired.")

# File handler
@app.on_message(filters.document & filters.private)
async def handle_cookie_file(client, message: Message):
    if not message.document.file_name.endswith(".txt"):
        await message.reply("❌ Please send a valid `cookies.txt` file.")
        return

    file_path = f"downloads/{message.document.file_id}.txt"
    await message.download(file_path)

    try:
        # Load cookies
        cookie_jar = MozillaCookieJar()
        cookie_jar.load(file_path, ignore_discard=True, ignore_expires=True)

        # Set session
        session = requests.Session()
        session.cookies = cookie_jar

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        # Test login
        response = session.get("https://www.youtube.com/feed/subscriptions", headers=headers)

        if "Sign in" in response.text or "account-picker" in response.text:
            await message.reply("❌ Invalid or expired cookies.")
        else:
            await message.reply("✅ Cookies are valid and logged in!")

    except Exception as e:
        await message.reply(f"⚠️ Error while checking cookies:\n`{e}`")
    finally:
        os.remove(file_path)

# Run the bot
app.run()
