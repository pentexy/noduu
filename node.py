import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

# === Config ===
api_id = 26416419
api_hash = "c109c77f5823c847b1aeb7fbd4990cc4"
bot_token = "6400675462:AAFlUPT3-RlVZ33MCqduP_6MaaSsx00e5Ak"
session_string = "BQFLWaIALVM4xN8QwHBFT-3adIY_viNV97B7vdfRy1GAeL6dWboR4YibYl1k1hHGaAJpjHuw26Dr2BjBtf7Gvgc15cGziWWnCEGPcpH4448i7yTZFg5SvOsm0F-Sf8c7boFhcnHhPHcmlG6qGkXeRS90W4vPwmpx1rpxID-QxILSPWYqHUUceUZhjUUPI1aIsTplq_QM70MlfYfVmgivcz_-CjDP3glQI3xxedaMDknNM06WFSDW5eeLDr-z_9bRwOdhY2yFH-eHxrd-LttlRy5WIMBPQo0ojX22i35OBRwzWiaVHrRa2c-TuGdOdto-ksNmB3RTt-1kWEYzm-QzQJmXngp_BwAAAAHJtXFRAA"

# === Clients ===
bot = Client("forwarder_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
userbot = Client("userbot", api_id=api_id, api_hash=api_hash, session_string=session_string)

# === Message Mapping ===
user_requests = {}  # Maps user_id and original message to track replies


@bot.on_message(filters.command("start") & filters.private)
async def start(client: Client, message: Message):
    await message.reply("Hey! Send a command and I’ll relay it to @NodesGGbot and send you the result.")


@bot.on_message(filters.private & filters.text & ~filters.command("start"))
async def handle_user_command(client: Client, message: Message):
    user_id = message.from_user.id
    user_msg = message.text

    sent = await userbot.send_message("NodesGGbot", user_msg)
    user_requests[sent.id] = (user_id, message.chat.id)


@userbot.on_message(filters.chat("NodesGGbot"))
async def handle_bot_response(client: Client, message: Message):
    reply_to = message.reply_to_message
    if not reply_to:
        return

    if reply_to.id in user_requests:
        user_id, chat_id = user_requests.pop(reply_to.id)

        # Send response from @NodesGGbot back to user
        if message.text:
            await bot.send_message(chat_id, message.text)
        elif message.media:
            await message.copy(chat_id)


# === Run ===
async def main():
    await userbot.start()
    await bot.start()
    print("Both bot and userbot are running.")
    await idle()
    await userbot.stop()
    await bot.stop()

from pyrogram.idle import idle
asyncio.run(main())
