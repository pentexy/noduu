import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message

# Debug logs in terminal
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# Your session credentials
api_id = 26416419
api_hash = "c109c77f5823c847b1aeb7fbd4990cc4"
session_string = "BQFLWaIALVM4xN8QwHBFT-3adIY_viNV97B7vdfRy1GAeL6dWboR4YibYl1k1hHGaAJpjHuw26Dr2BjBtf7Gvgc15cGziWWnCEGPcpH4448i7yTZFg5SvOsm0F-Sf8c7boFhcnHhPHcmlG6qGkXeRS90W4vPwmpx1rpxID-QxILSPWYqHUUceUZhjUUPI1aIsTplq_QM70MlfYfVmgivcz_-CjDP3glQI3xxedaMDknNM06WFSDW5eeLDr-z_9bRwOdhY2yFH-eHxrd-LttlRy5WIMBPQo0ojX22i35OBRwzWiaVHrRa2c-TuGdOdto-ksNmB3RTt-1kWEYzm-QzQJmXngp_BwAAAAHJtXFRAA"

# Single App: acts as userbot (string session)
app = Client("NodesForwarder", api_id=api_id, api_hash=api_hash, session_string=session_string)

# Track which user message triggered which command
forwarded = {}

@app.on_message(filters.private & filters.command("start"))
async def start(_, msg: Message):
    await msg.reply("Send me any command and I’ll ask @NodesGGbot for you.")

@app.on_message(filters.private & filters.text & ~filters.command("start"))
async def forward_command(_, msg: Message):
    try:
        sent = await app.send_message("NodesGGbot", msg.text)
        forwarded[sent.id] = msg.chat.id
        logging.info(f"Forwarded to @NodesGGbot: {msg.text}")
    except Exception as e:
        await msg.reply(f"Error sending to NodesGGbot:\n`{e}`")
        logging.error(e)

@app.on_message(filters.chat("NodesGGbot"))
async def return_response(_, msg: Message):
    try:
        if msg.reply_to_message and msg.reply_to_message.id in forwarded:
            user_id = forwarded.pop(msg.reply_to_message.id)
            if msg.text:
                await app.send_message(user_id, msg.text)
            elif msg.media:
                await msg.copy(user_id)
            logging.info(f"Sent response to user {user_id}")
    except Exception as e:
        logging.error(f"Response error: {e}")

app.run()
