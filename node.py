from pyrogram import Client, filters
from pyrogram.types import Message

# Ask for credentials in terminal
API_ID = int(input("Enter your API ID: "))
API_HASH = input("Enter your API HASH: ")
BOT_TOKEN = input("Enter your BOT TOKEN: ")

# Create Pyrogram Client
app = Client("PremiumFilterBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.private & ~filters.service)
async def handle_private(client: Client, message: Message):
    try:
        user = await client.get_users(message.from_user.id)

        if not user.is_premium:
            # Send warning (to delete it after)
            warning = await message.reply("`you have been blocklisted !`")

            # Delete bot reply from both sides
            await client.delete_messages(chat_id=message.chat.id, message_ids=warning.id, revoke=True)

            # Delete user's message from bot's side
            await client.delete_messages(chat_id=message.chat.id, message_ids=message.id)

    except Exception as e:
        print(f"Error: {e}")

app.run()
