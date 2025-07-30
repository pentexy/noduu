import logging
import aiohttp
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

BOT_TOKEN = "8120657679:AAGqf3YCJML6HmgObyOXz8cdcfDX6dY1STw"
LOG_GROUP_ID = -1002710995756

logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()


async def get_business_connection():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getBusinessConnection"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            return data


@dp.startup()
async def on_startup(bot: Bot):
    try:
        result = await get_business_connection()
        if result.get("ok") and result.get("result"):
            user = result["result"]["user"]
            perms = result["result"].get("permissions", [])
            text = (
                "🤖 <b>Bot connected via Telegram Business!</b>\n\n"
                f"👤 <b>User:</b> {user.get('first_name', '')} {user.get('last_name', '')}\n"
                f"🆔 <b>User ID:</b> <code>{user.get('id')}</code>\n"
                f"🎁 <b>Permissions:</b> {', '.join(perms)}"
            )
        else:
            text = f"⚠️ Could not fetch Business Connection.\n\n{result}"
        await bot.send_message(LOG_GROUP_ID, text)
    except Exception as e:
        logging.error(f"Failed to get business connection: {e}")


if __name__ == "__main__":
    dp.run_polling(bot)
