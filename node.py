from pyrogram import Client, filters
from pyrogram.types import Message

# Prompt for credentials
API_ID = int(input("Enter your API ID: "))
API_HASH = input("Enter your API HASH: ")
BOT_TOKEN = input("Enter your BOT TOKEN: ")

app = Client("PremiumBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.private & ~filters.service)
async def delete_non_premium(client: Client, message: Message):
    user = await client.get_users(message.from_user.id)

    if not user.is_premium:
        try:
            # Send reply warning (can be revoked)
            reply = await message.reply("`you have been blocklisted !`")

            # Delete the bot's reply from both sides
            await client.delete_messages(chat_id=message.chat.id, message_ids=reply.id, revoke=True)

            # Delete the user's message (only from bot side)
            await client.delete_messages(chat_id=message.chat.id, message_ids=message.id)
        except Exception as e:
            print(f"Error: {e}")

app.run()
