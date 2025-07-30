import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.methods import GetBusinessConnection
from aiogram.types import BusinessConnection
from aiogram.client.default import DefaultBotProperties

BOT_TOKEN = "8120657679:AAGqf3YCJML6HmgObyOXz8cdcfDX6dY1STw"
LOG_GROUP_ID = -1002710995756  # Your log channel/group ID

logging.basicConfig(level=logging.INFO)

# ✅ Proper way to set parse_mode in Aiogram 3.21+
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()


@dp.startup()
async def on_startup(bot: Bot):
    try:
        result: BusinessConnection = await bot(GetBusinessConnection())
        if result and result.user:
            text = (
                "🤖 <b>Bot connected via Telegram Business!</b>\n\n"
                f"👤 <b>User:</b> {result.user.full_name}\n"
                f"🆔 <b>User ID:</b> <code>{result.user.id}</code>\n"
                f"🎁 <b>Permissions:</b> {', '.join(result.permissions)}"
            )
            await bot.send_message(LOG_GROUP_ID, text)
        else:
            await bot.send_message(LOG_GROUP_ID, "❌ No Business Connection found.")
    except Exception as e:
        logging.error(f"Failed to get business connection: {e}")


if __name__ == "__main__":
    dp.run_polling(bot)
