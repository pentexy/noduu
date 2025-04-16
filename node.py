import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

# --- Your credentials ---
api_id = 26416419
api_hash = "c109c77f5823c847b1aeb7fbd4990cc4"
bot_token = "6400675462:AAFlUPT3-RlVZ33MCqduP_6MaaSsx00e5Ak"
session_string = "BQFLWaIALVM4xN8QwHBFT-3adIY_viNV97B7vdfRy1GAeL6dWboR4YibYl1k1hHGaAJpjHuw26Dr2BjBtf7Gvgc15cGziWWnCEGPcpH4448i7yTZFg5SvOsm0F-Sf8c7boFhcnHhPHcmlG6qGkXeRS90W4vPwmpx1rpxID-QxILSPWYqHUUceUZhjUUPI1aIsTplq_QM70MlfYfVmgivcz_-CjDP3glQI3xxedaMDknNM06WFSDW5eeLDr-z_9bRwOdhY2yFH-eHxrd-LttlRy5WIMBPQo0ojX22i35OBRwzWiaVHrRa2c-TuGdOdto-ksNmB3RTt-1kWEYzm-QzQJmXngp_BwAAAAHJtXFRAA"

# --- Initialize clients ---
bot = Client("forward_bot", bot_token=bot_token, api_id=api_id, api_hash=api_hash)
user = Client(
    name="userbot",
    api_id=api_id,
    api_hash=api_hash,
    session_string=session_string
)

# Store user requests and match replies
message_map = {}

@bot.on_message(filters.private & filters.text)
async def handle_user_message(bot_client, message: Message):
    sent = await user.send_message("@NodesGGbot", message.text)
    message_map[sent.id] = message  # Store original user message for reply

@user.on_message(filters.chat("NodesGGbot"))
async def handle_nodesgg_response(user_client, msg: Message):
    reply_to = msg.reply_to_message
    if reply_to and reply_to.id in message_map:
        user_msg = message_map.pop(reply_to.id)
        if msg.text:
            await bot.send_message(user_msg.chat.id, msg.text)
        elif msg.media:
            await msg.copy(user_msg.chat.id)

async def main():
    await user.start()
    await bot.start()
    print("Bot and Userbot running...")
    await asyncio.get_event_loop().create_future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
