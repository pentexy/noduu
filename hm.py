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

    heading = "<b><blockquote>" + to_fancy("Durga Puja Countdown") + "</blockquote></b>\n"
    body = (
        to_fancy(f"Month - {month} {year}") + "\n" +
        to_fancy(f"Days left - {days}") + "\n" +
        to_fancy(f"In hours, minutes, seconds - {hours} hrs {minutes} mins {seconds} secs")
    )
    return heading + body

def generate_routine():
    heading = "<b><blockquote>" + to_fancy("Durga Puja Routine 2025") + "</blockquote></b>\n"
    body = (
        to_fancy("• Maha Sashthi: 28 September 2025") + "\n" +
        to_fancy("• Maha Saptami: 29 September 2025") + "\n" +
        to_fancy("• Maha Asthami: 30 September 2025") + "\n" +
        to_fancy("• Maha Navami: 1 October 2025") + "\n" +
        to_fancy("• Vijaya Dashami: 2 October 2025") + "\n\n" +
        to_fancy("• Full Moon (Purnima): 17 October 2025")
    )
    return heading + body

def main_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("• ʀᴇғʀᴇsʜ •", callback_data="refresh_time"),
            InlineKeyboardButton("• ʀᴏᴜᴛɪɴᴇ •", callback_data="show_routine")
        ],
        [
            InlineKeyboardButton("• ᴏᴡɴᴇʀ •", url="tg://user?id=6748827895")
        ]
    ])

def routine_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("• ʙᴀᴄᴋ •", callback_data="back_to_countdown")],
        [InlineKeyboardButton("• ᴏᴡɴᴇʀ •", url="tg://user?id=6748827895")]
    ])

@app.on_message(filters.command("start"))
def on_start(client, message):
    caption = generate_countdown()
    client.send_video(
        chat_id=message.chat.id,
        video=VIDEO_LINK,
        caption=caption,
        reply_markup=main_keyboard()
    )

@app.on_callback_query()
async def on_callback(client, callback_query: CallbackQuery):
    data = callback_query.data

    if data == "refresh_time":
        new_caption = generate_countdown()
        await callback_query.message.edit_caption(new_caption, reply_markup=main_keyboard())
        await callback_query.answer("Refreshed!")

    elif data == "show_routine":
        routine_text = generate_routine()
        await callback_query.message.edit_caption(routine_text, reply_markup=routine_keyboard())
        await callback_query.answer()

    elif data == "back_to_countdown":
        countdown_text = generate_countdown()
        await callback_query.message.edit_caption(countdown_text, reply_markup=main_keyboard())
        await callback_query.answer()

app.run()
