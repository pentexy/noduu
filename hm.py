from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime

API_ID = 26416419
API_HASH = "c109c77f5823c847b1aeb7fbd4990cc4"
BOT_TOKEN = "8190514719:AAErWkT2S9CnXskl33bw1AC3_DBt17L3R1I"

app = Client("durga_puja_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

DURGA_PUJA_DATE = datetime(2025, 9, 28, 0, 0, 0)
VIDEO_LINK = "https://files.catbox.moe/h4wxhn.mp4"  # Replace with your actual video link

def to_fancy(text):
    font_map = {
        **dict(zip("abcdefghijklmnopqrstuvwxyz", "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ")),
        **dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ")),
        **dict(zip("0123456789", "𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿")),
        " ": " "
    }
    return ''.join(font_map.get(c, c) for c in text)

def generate_countdown():
    now = datetime.now()
    left = DURGA_PUJA_DATE - now
    days = left.days
    hours, rem = divmod(left.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    month = now.strftime("%B")
    year = now.strftime("%Y")

    return (
        "<b><blockquote>" + to_fancy("Durga Puja Countdown") + "</blockquote></b>\n" +
        to_fancy(f"**Month - {month} {year}**") + "\n" +
        to_fancy(f"**Days left - `{days}`") + "\n" +
        to_fancy(f"In hours, minutes, seconds - `{hours}`**hrs**`{minutes}` **mins** `{seconds}` **secs**")
    )

@app.on_message(filters.command("start"))
def on_start(client, message):
    caption = generate_countdown()
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("• ʀᴇғʀᴇsʜ •", callback_data="refresh_time")]]
    )
    client.send_video(
        chat_id=message.chat.id,
        video=VIDEO_LINK,
        caption=caption,
        reply_markup=keyboard
    )

@app.on_callback_query(filters.regex("refresh_time"))
def on_refresh(client, callback_query: CallbackQuery):
    new_caption = generate_countdown()
    callback_query.message.edit_caption(new_caption, reply_markup=callback_query.message.reply_markup)

app.run()
