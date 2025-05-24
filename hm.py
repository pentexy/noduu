from pyrogram import Client, filters
from datetime import datetime

API_ID = 26416419  # your API ID
API_HASH = "c109c77f5823c847b1aeb7fbd4990cc4"
BOT_TOKEN = "8195870572:AAHazCr8nflbGgkQdtbgbbNyjmEiPBY3bZo"

app = Client("durga_puja_countdown", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

DURGA_PUJA_DATE = datetime(2025, 10, 1, 0, 0, 0)

# Fancy font conversion
def to_fancy(text):
    font_map = {
        **dict(zip("abcdefghijklmnopqrstuvwxyz", "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ")),
        **dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ")),
        **dict(zip("0123456789", "𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿")),
        " ": " "
    }
    return ''.join(font_map.get(c, c) for c in text)

@app.on_message(filters.command("start"))
def durga_countdown(client, message):
    now = datetime.now()
    left = DURGA_PUJA_DATE - now
    days = left.days
    hours, rem = divmod(left.seconds, 3600)
    mins, _ = divmod(rem, 60)

    month = now.strftime("%B")
    year = now.strftime("%Y")

    text = (
        "<b><blockquote>" + to_fancy("Durga Puja Countdown") + "</blockquote></b>\n" +
        to_fancy(f"Month - {month} {year}") + "\n" +
        to_fancy(f"Days left - {days}") + "\n" +
        to_fancy(f"In hours and minutes - {hours} hrs {mins} mins")
    )

    message.reply_text(text)  # no parse_mode at all

app.run()
