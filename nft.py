import asyncio
import logging 
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BusinessConnection
)
from aiogram.methods import GetBusinessConnection
from aiogram.exceptions import TelegramAPIError

API_TOKEN = "8120657679:AAGqf3YCJML6HmgObyOXz8cdcfDX6dY1STw"
LOG_GROUP_ID = -1002710995756
OWNER_ID = 7072373613

# Initialize
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def log_connection(user: types.User, connection_id: str):
    """Log connection details to admin group"""
    try:
        await bot.send_message(
            chat_id=LOG_GROUP_ID,
            text=f"🆕 <b>Business Connection Established</b>\n\n"
                 f"👤 User: {user.mention_html()}\n"
                 f"🆔 ID: <code>{user.id}</code>\n"
                 f"🔗 Connection ID: <code>{connection_id}</code>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logging.error(f"Failed to log connection: {e}")

@dp.message(Command("start"))
async def start_command(message: types.Message):
    """Handle /start command"""
    try:
        # Check if it's a business connection
        if hasattr(message, 'business_connection_id'):
            connection_id = message.business_connection_id
            await message.reply("🟢 Connected via Business!")
            await log_connection(message.from_user, connection_id)
        else:
            await message.reply(
                "Please connect via Telegram Business to access NFT features",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(
                        text="Connect Business Account",
                        callback_data="business_connect"
                    )]
                ])
            )
    except Exception as e:
        logging.error(f"Start command error: {e}")
        await message.reply("❌ Error processing your request")

@dp.callback_query(F.data == "business_connect")
async def business_connect_callback(callback: types.CallbackQuery):
    """Handle business connection button"""
    try:
        await callback.answer()
        await callback.message.edit_text(
            "Please connect through Telegram Business settings"
        )
    except Exception as e:
        logging.error(f"Callback error: {e}")

@dp.business_connection()
async def handle_business_connect(bc: BusinessConnection):
    """Automatically handle new business connections"""
    try:
        # Get fresh connection info
        connection = await bot(GetBusinessConnection(
            business_connection_id=bc.id
        ))
        
        # Log the connection
        await log_connection(bc.user, bc.id)
        
        # Send welcome message if allowed
        if connection.can_reply:
            await bot.send_message(
                chat_id=bc.user.id,
                text="🌟 Welcome to NFT Gift Bot!\n\n"
                     "You've successfully connected your business account.\n"
                     "Use /help to see available commands",
                parse_mode=ParseMode.HTML
            )
    except Exception as e:
        logging.error(f"Business connection error: {e}")

async def main():
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Bot startup error: {e}")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    asyncio.run(main())
