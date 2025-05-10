from pyrogram import Client, filters
from pyrogram.types import Message

# Ask for credentials in terminal
API_ID = int(input("Enter your API ID: "))
API_HASH = input("Enter your API HASH: ")
BOT_TOKEN = input("Enter your BOT TOKEN: ")

app = Client("PremiumBlockBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.private & ~filters.service)
async def block_non_premium(client: Client, message: Message):
    user = await client.get_users(message.from_user.id)
    if not user.is_premium:
        await message.reply("`you have been blocklisted !`", quote=True)
        await client.block_user(user.id)

app.run()
