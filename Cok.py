from pyrogram import Client, filters
from pyrogram.types import Message

# Prompt user for credentials at runtime
API_ID = int(input("Enter your API ID: "))
API_HASH = input("Enter your API HASH: ")
BOT_TOKEN = input("Enter your Bot Token: ")

app = Client("hello_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.text)
async def non_command_message(client: Client, message: Message):
    # Ignore commands and any message containing '/'
    if '/' not in message.text:
        await message.reply("Hello , Hi...How Are You? , 🫂")

app.run()
