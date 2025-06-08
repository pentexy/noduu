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

# Auto-fix function to format cookie lines properly
def fix_cookie_format(input_file, output_file):
    with open(input_file, "r") as f_in, open(output_file, "w") as f_out:
        for line in f_in:
            line = line.strip()
            if line.startswith("#") or line == "":
                f_out.write(line + "\n")
            else:
                parts = line.split()
                if len(parts) >= 7:
                    fixed_line = "\t".join(parts[:7]) + "\n"
                    f_out.write(fixed_line)

# /start command handler
@app.on_message(filters.command("start") & filters.private)
async def start(client, message: Message):
    await message.reply("👋 Send me your YouTube `cookies.txt` file, and I'll check if it's valid or expired.")

# File upload handler
@app.on_message(filters.document & filters.private)
async def handle_cookie_file(client, message: Message):
    if not message.document.file_name.endswith(".txt"):
        await message.reply("❌ Please send a valid `cookies.txt` file.")
        return

    os.makedirs("downloads", exist_ok=True)
    original_path = f"downloads/{message.document.file_id}.txt"
    fixed_path = f"downloads/{message.document.file_id}_fixed.txt"

    await message.download(original_path)

    try:
        # Fix the format
        fix_cookie_format(original_path, fixed_path)

        # Load fixed cookies
        cookie_jar = MozillaCookieJar()
        cookie_jar.load(fixed_path, ignore_discard=True, ignore_expires=True)

        session = requests.Session()
        session.cookies = cookie_jar

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        # Test URL
        response = session.get("https://www.youtube.com/feed/subscriptions", headers=headers)

        if "Sign in" in response.text or "account-picker" in response.text:
            await message.reply("❌ Invalid or expired cookies.")
        else:
            await message.reply("✅ Cookies are valid and you're logged in!")

    except Exception as e:
        await message.reply(f"⚠️ Error while checking cookies:\n`{e}`")

    finally:
        # Clean up both files
        for path in [original_path, fixed_path]:
            if os.path.exists(path):
                os.remove(path)

# Run the bot
app.run()
