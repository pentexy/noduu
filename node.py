from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = int(input("Enter your API ID: "))
API_HASH = input("Enter your API HASH: ")
BOT_TOKEN = input("Enter your BOT TOKEN: ")

app = Client("PremiumEnforcer", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.private & ~filters.service)
async def handle_message(client: Client, message: Message):
    user = await client.get_users(message.from_user.id)

    if not user.is_premium:
        try:
            # Send blocklisted warning (will delete this too)
            warning = await message.reply("`you have been blocklisted !`")

            # Delete bot reply (from both sides)
            await client.delete_messages(chat_id=message.chat.id, message_ids=warning.id, revoke=True)

            # Delete user message (from bot's side only)
            await client.delete_messages(chat_id=message.chat.id, message_ids=message.id)

        except Exception as e:
            print(f"Error while deleting messages: {e}")

app.run()
