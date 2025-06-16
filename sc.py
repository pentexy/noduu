import re
import httpx
from getpass import getpass
from pyrogram import Client, filters
from pyrogram.types import Message

# --- Ask credentials in terminal ---
print("🔐 Enter your Telegram bot credentials:")
api_id = int(input("📲 API ID: "))
api_hash = input("🔑 API Hash: ")
bot_token = getpass("🤖 Bot Token: ")  # hidden input

app = Client("insta_bot_session", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# --- Constants ---
API_URL = "https://www.alphaapis.org/Instagram/dl/v1"
INSTAGRAM_REGEX = r"(https?://(?:www\.)?instagram\.com/[^\s]+)"

@app.on_message(filters.text & filters.group)
async def insta_auto_fetch(client: Client, message: Message):
    match = re.search(INSTAGRAM_REGEX, message.text)
    if not match:
        return

    instagram_url = match.group(1)
    processing = await message.reply_text("🔄")

    try:
        async with httpx.AsyncClient(timeout=15.0) as http:
            resp = await http.get(API_URL, params={"url": instagram_url})
            resp.raise_for_status()
            data = await resp.json()

        results = data.get("result", [])
        if not results:
            return await processing.edit("⚠️ No media found.")

        # Reply caption logic
        if message.reply_to_message and message.reply_to_message.from_user:
            username = message.reply_to_message.from_user.username
            if username:
                mention_line = f"**ye dekh bc @{username}**"
            else:
                mention_line = f"**ye dekh bhai {message.reply_to_message.from_user.first_name}**"
        else:
            mention_line = f"**dekh le bc ye @{message.from_user.username or message.from_user.first_name}**"

        caption = f"{mention_line}\n**ʙᴏᴛ ʙʏ [ᴛ.ᴍᴇ/EᴛᴇʀɴᴀʟAᴜʀᴀ](https://t.me/EternalAura)**"
        reply_id = message.reply_to_message.message_id if message.reply_to_message else message.id

        for item in results:
            dl = item.get("downloadLink")
            if not dl:
                continue

            if ".mp4" in dl:
                await client.send_video(
                    chat_id=message.chat.id,
                    video=dl,
                    reply_to_message_id=reply_id,
                    caption=caption,
                    parse_mode="markdown"
                )
            elif any(dl.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                await client.send_photo(
                    chat_id=message.chat.id,
                    photo=dl,
                    reply_to_message_id=reply_id,
                    caption=caption,
                    parse_mode="markdown"
                )

    except Exception as e:
        await processing.edit(f"❌ Error: {e}")
    finally:
        await processing.delete()

# --- Run the bot ---
print("\n🚀 Starting bot... Press Ctrl+C to stop.")
app.run()
