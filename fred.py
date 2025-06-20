import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
import os

# Ask for token in terminal
BOT_TOKEN = input("🔐 Enter your bot token: ").strip()

# You can hardcode or ask these too
API_ID = 26416419
API_HASH = "c109c77f5823c847b1aeb7fbd4990cc4"
OWNER_ID = 7339063037

MONGO_URI = "mongodb+srv://Axxa:Axxay@cluster0.veadsay.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["CryptoBot"]
users_collection = db["users"]

bot = Client("CryptoBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


async def add_user(user_id):
    if not users_collection.find_one({"user_id": user_id}):
        users_collection.insert_one({"user_id": user_id})


@bot.on_message(filters.command("start"))
async def start_handler(client, message: Message):
    await add_user(message.from_user.id)
    await message.reply(
        f"**Hey {message.from_user.mention}, welcome to our bot !**"
    )


@bot.on_message(filters.text & ~filters.command(["start"]))
async def normal_text(client, message: Message):
    await message.reply("**crypto**")


@bot.on_message(filters.command("panel") & filters.user(OWNER_ID))
async def owner_panel(client, message: Message):
    total = users_collection.count_documents({})
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 Real-Time Users", callback_data="user_count")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")]
    ])
    await message.reply(f"👑 Owner Panel\n\nTotal Users: `{total}`", reply_markup=keyboard)


@bot.on_callback_query(filters.user(OWNER_ID))
async def callback_handler(client, callback_query):
    data = callback_query.data
    if data == "user_count":
        total = users_collection.count_documents({})
        await callback_query.answer()
        await callback_query.message.edit(
            f"📊 Real-Time Users:\n\n👥 Total Saved Users: `{total}`",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="back")]
            ])
        )
    elif data == "broadcast":
        await callback_query.answer()
        await callback_query.message.reply("📨 Send the message to broadcast:")
    elif data == "back":
        total = users_collection.count_documents({})
        await callback_query.message.edit(
            f"👑 Owner Panel\n\nTotal Users: `{total}`",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👥 Real-Time Users", callback_data="user_count")],
                [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")]
            ])
        )


@bot.on_message(filters.text & filters.user(OWNER_ID))
async def handle_broadcast(client, message: Message):
    if message.reply_to_message and "Send the message to broadcast" in message.reply_to_message.text:
        total = 0
        failed = 0
        for user in users_collection.find():
            try:
                await client.send_message(user["user_id"], message.text)
                total += 1
                await asyncio.sleep(0.05)
            except:
                failed += 1
        await message.reply(f"✅ Broadcast Done\n\n✅ Sent: {total}\n❌ Failed: {failed}")


print("🚀 Bot is starting...")
bot.run()
